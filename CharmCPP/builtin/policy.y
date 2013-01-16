%{
#include <stdio.h>
#include <ctype.h>
#include <string.h>
#include <stdint.h>
#include <stdarg.h>
        
#include "util.h"
#include "policy.h"

#define NUM_ARRAY_COMPONENTS    10
#define MAX_STR_SIZE                    200
        
typedef struct
{
        uint64_t value;
        int bits; /* zero if this is a flexint */
}
sized_integer_t;

typedef struct
{
        uint32 num_components;
        uint32 array_size;
        charm_attribute_subtree** components;
}
ptr_array_t;

charm_attribute_subtree* final_policy = 0;

int yylex();
void yyerror( const char* s );
sized_integer_t* expint( uint64_t value, uint64_t bits );
sized_integer_t* flexint( uint64_t value );
charm_attribute_subtree* leaf_policy( char* attr );
charm_attribute_subtree* kof2_policy( int k, charm_attribute_subtree* l, charm_attribute_subtree* r );
charm_attribute_subtree* kof_policy( int k, ptr_array_t* list );
charm_attribute_subtree* eq_policy( sized_integer_t* n, char* attr );
charm_attribute_subtree* lt_policy( sized_integer_t* n, char* attr );
charm_attribute_subtree* gt_policy( sized_integer_t* n, char* attr );
charm_attribute_subtree* le_policy( sized_integer_t* n, char* attr );
charm_attribute_subtree* ge_policy( sized_integer_t* n, char* attr );
ptr_array_t* ptr_array_new();
void ptr_array_add(ptr_array_t *ptr, charm_attribute_subtree* subtree);
char* s_string_new(int max);
void s_string_append_c(char *left, int max, char right);
char* s_strnfill(size_t num, char fill);
char* s_strdup_printf(char *, ...);
%}

%union
{
        char* str;
        uint64_t nat;
    sized_integer_t* sint;
        charm_attribute_subtree* tree;
        ptr_array_t* list;
}

%token <str>  TAG
%token <nat>  INTLIT
%type  <sint> number
%type  <tree> policy
%type  <list> arg_list

%left OR
%left AND
%token OF
%token LEQ
%token GEQ

%%

result: policy { final_policy = $1 }

number:   INTLIT '#' INTLIT          { $$ = expint($1, $3); }
        | INTLIT                     { $$ = flexint($1);    }

policy:   TAG                        { $$ = leaf_policy($1);        }
        | policy OR  policy          { $$ = kof2_policy(1, $1, $3); }
        | policy AND policy          { $$ = kof2_policy(2, $1, $3); }
        | INTLIT OF '(' arg_list ')' { $$ = kof_policy($1, $4);     }
        | TAG '=' number             { $$ = eq_policy($3, $1);      }
        | TAG '<' number             { $$ = lt_policy($3, $1);      }
        | TAG '>' number             { $$ = gt_policy($3, $1);      }
        | TAG LEQ number             { $$ = le_policy($3, $1);      }
        | TAG GEQ number             { $$ = ge_policy($3, $1);      }
        | number '=' TAG             { $$ = eq_policy($1, $3);      }
        | number '<' TAG             { $$ = gt_policy($1, $3);      }
        | number '>' TAG             { $$ = lt_policy($1, $3);      }
        | number LEQ TAG             { $$ = ge_policy($1, $3);      }
        | number GEQ TAG             { $$ = le_policy($1, $3);      }
        | '(' policy ')'             { $$ = $2;                     }

arg_list: policy                     { $$ = ptr_array_new();
                                       ptr_array_add($$, $1); }
        | arg_list ',' policy        { $$ = $1;
                                       ptr_array_add($$, $3); }
;

%%

void
die(char *fmt, ...)
{
        // char* str;
        va_list args;
        
        va_start( args, fmt );
        vfprintf( stderr, fmt, args );
        va_end( args );
        
        exit(1);
}

char* s_strnfill(size_t num, char fill)
{
        char* str;
        uint32 i;
        
        str = SAFE_MALLOC(num + 1);
        for (i = 0; i < num; i++) {
                str[i] = fill;
        }
        str[i] = '\0';
        return str;
}

char* s_string_new(int max)
{
        char* g;
        
        g = SAFE_MALLOC(max);
        if(g == NULL) {
                fprintf(stderr, "g doesnt exist\n");
                return NULL;
        }
        memset(g, 0, max);
        
        return g;       
}

void s_string_append_c(char *left, int max, char right)
{
        size_t len;
        size_t dmax = max - 1;

        len = strlen(left);
        if ( len < dmax ) {
                left[len] = right;
                left[len+1] = 0;
        }
}

ptr_array_t* ptr_array_new()
{
        ptr_array_t* ptr = SAFE_MALLOC(sizeof(ptr_array_t));
        memset(ptr, 0, sizeof(ptr_array_t));
        ptr->num_components = 0;
        ptr->array_size = NUM_ARRAY_COMPONENTS;
        ptr->components = SAFE_MALLOC(sizeof(charm_attribute_subtree*) * NUM_ARRAY_COMPONENTS);
        return ptr;
}

void ptr_array_add(ptr_array_t *ptr, charm_attribute_subtree* subtree)
{
        charm_attribute_subtree **temp;
        uint32 i;
        
        if (ptr->num_components >= ptr->array_size) {
                temp = ptr->components;
                ptr->array_size += NUM_ARRAY_COMPONENTS;
                ptr->components = SAFE_MALLOC(ptr->array_size * sizeof(charm_attribute_subtree*));
                for (i = 0; i < ptr->num_components; i++) {
                        ptr->components[i] = temp[i];
                }
                SAFE_FREE(temp);
        }
        
        ptr->components[ptr->num_components] = subtree;
        ptr->num_components++;
}

sized_integer_t*
expint( uint64_t value, uint64_t bits )
{
        sized_integer_t* s;

        if( bits == 0 )
                die("error parsing policy: zero-length integer \"%llub%llu\"\n",
                                value, bits);
        else if( bits > 64 )
                die("error parsing policy: no more than 64 bits allowed \"%llub%llu\"\n",
                                value, bits);

        s = malloc(sizeof(sized_integer_t));
        s->value = value;
        s->bits = bits;

        return s;
}

char* s_strdup_printf(char *fmt, ...)
{
        char* str;
        va_list args;

        str = SAFE_MALLOC(MAX_STR_SIZE);
        va_start( args, fmt );
        vsprintf( str, fmt, args );
        va_end( args );
        
        return str;
}

sized_integer_t*
flexint( uint64_t value )
{
        sized_integer_t* s;

        s = malloc(sizeof(sized_integer_t));
        s->value = value;
        s->bits = 0;

        return s;
}

void
policy_free( charm_attribute_subtree* p )
{
        if( p != NULL ) {
                charm_attribute_subtree_clear(p);
        }

        free(p);
}

charm_attribute_subtree*
leaf_policy( char* attr )
{
        //printf("leaf_node => '%s\n", attr);
        return charm_policy_create_leaf(attr);
}

charm_attribute_subtree*
kof2_policy( int k, charm_attribute_subtree* l, charm_attribute_subtree* r )
{
        charm_attribute_subtree* attributes[2];
        CHARM_ATTRIBUTE_NODE_TYPE node_type;

        attributes[0] = l;
        attributes[1] = r;
        switch(k) {
        case 1:
                node_type = CHARM_ATTRIBUTE_POLICY_NODE_OR;
                break;
        case 2:
                node_type = CHARM_ATTRIBUTE_POLICY_NODE_AND;
                break;
        default:
                node_type = CHARM_ATTRIBUTE_POLICY_NODE_THRESHOLD;
                break;
        }

        return charm_policy_create_node(node_type, 2, k, attributes);
}

charm_attribute_subtree*
kof_policy( int m, ptr_array_t* list )
{
        charm_attribute_subtree **attributes;
        charm_attribute_subtree* p;
        uint32 i;
        uint32 k = (uint32) m;
        
        if( k < 1 )
                die("error parsing policy: trivially satisfied operator \"%dof\"\n", k);
        else if( k > list->num_components )
                die("error parsing policy: unsatisfiable operator \"%dof\" (only %d operands)\n",
                                k, list->num_components);
        else if( list->num_components == 1 )
                die("error parsing policy: identity operator \"%dof\" (only one operand)\n", k);

        attributes = SAFE_MALLOC(list->num_components * sizeof(charm_attribute_subtree*));

        for (i = 0; i < list->num_components; i++) {
                attributes[i] = list->components[i];
        }

        p = charm_policy_create_node(CHARM_ATTRIBUTE_POLICY_NODE_THRESHOLD, list->num_components, k, attributes);

        SAFE_FREE(attributes);

        return p;
}

char*
bit_marker( char* base, char* tplate, int bit, char val )
{
        char* lx;
        char* rx;
        char* s;

        lx = s_strnfill(64 - bit - 1, 'x');
        rx = s_strnfill(bit, 'x');
        s = s_strdup_printf(tplate, base, lx, !!val, rx);
        free(lx);
        free(rx);

        return s;
}

charm_attribute_subtree*
eq_policy( sized_integer_t* n, char* attr )
{
        if( n->bits == 0 )
                return leaf_policy
                        (s_strdup_printf("%s_flexint_%llu", attr, n->value));
        else
                return leaf_policy
                        (s_strdup_printf("%s_expint%02d_%llu", attr, n->bits, n->value));

        return 0;
}

charm_attribute_subtree*
bit_marker_list( int gt, char* attr, char* tplate, int bits, uint64_t value )
{
        charm_attribute_subtree* p;
        int i;

        i = 0;
        while( gt ? (((uint64_t)1)<<i & value) : !(((uint64_t)1)<<i & value) )
                i++;

        p = leaf_policy(bit_marker(attr, tplate, i, gt));
        for( i = i + 1; i < bits; i++ )
                if( gt )
                        p = kof2_policy(((uint64_t)1<<i & value) ? 2 : 1, p,
                                                                                        leaf_policy(bit_marker(attr, tplate, i, gt)));
                else
                        p = kof2_policy(((uint64_t)1<<i & value) ? 1 : 2, p,
                                                                                        leaf_policy(bit_marker(attr, tplate, i, gt)));

        return p;
}

charm_attribute_subtree*
flexint_leader( int gt, char* attr, uint64_t value )
{
        // printf("called flexint_leader: gt=%d, attr=%s, value=%d\n", gt, attr, value);
        // charm_attribute_subtree* p;
        int k;
        charm_attribute_subtree* attributes[256];
        uint32 i = 0;

        for( k = 2; k <= 32; k *= 2 )
                if( ( gt && ((uint64_t)1<<k) >  value) ||(!gt && ((uint64_t)1<<k) >= value) )
                        attributes[i] = leaf_policy
                                 // (s_strdup_printf(gt ? "%s_ge_2^%02d" : "%s_lt_2^%02d", attr, k));
                                 (s_strdup_printf("%s_flexint_uint" , attr));
                        i++;

        //p->k = gt ? 1 : p->children->len;

        if( i == 0 )
        {
                return NULL;            
                //policy_free(p);
                //p = 0;
        }
        else if( i == 1 )
        {
                return attributes[0];
        }

        return charm_policy_create_node(CHARM_ATTRIBUTE_POLICY_NODE_THRESHOLD, i, (gt ? 1 : i), attributes);
}

charm_attribute_subtree*
cmp_policy( sized_integer_t* n, int gt, char* attr )
{
        charm_attribute_subtree* p;
        char* tplate;

        /* some error checking */

        if( gt && n->value >= ((uint64_t)1<<(n->bits ? n->bits : 64)) - 1 )
                die("error parsing policy: unsatisfiable integer comparison %s > %llu\n"
                                "(%d-bits are insufficient to satisfy)\n", attr, n->value,
                                n->bits ? n->bits : 64);
        else if( !gt && n->value == 0 )
                die("error parsing policy: unsatisfiable integer comparison %s < 0\n"
                                "(all numerical attributes are unsigned)\n", attr);
        else if( !gt && n->value > ((uint64_t)1<<(n->bits ? n->bits : 64)) - 1 )
                die("error parsing policy: trivially satisfied integer comparison %s < %llu\n"
                                "(any %d-bit number will satisfy)\n", attr, n->value,
                                n->bits ? n->bits : 64);

        /* create it */

        /* horrible */
        tplate = n->bits ?
                s_strdup_printf("%%s_expint%02d_%%s%%d%%s", n->bits) :
                strdup("%s_flexint_%s%d%s");
        p = bit_marker_list(gt, attr, tplate, n->bits ? n->bits :
                                                                                        (n->value >= ((uint64_t)1<<32) ? 64 :
                                                                                         n->value >= ((uint64_t)1<<16) ? 32 :
                                                                                         n->value >= ((uint64_t)1<< 8) ? 16 :
                                                                                         n->value >= ((uint64_t)1<< 4) ?  8 :
                                                                                         n->value >= ((uint64_t)1<< 2) ?  4 : 2), n->value);
        free(tplate);

        if( !n->bits )
        {
                charm_attribute_subtree* l;
                
                l = flexint_leader(gt, attr, n->value);
                if( l )
                        p = kof2_policy(gt ? 1 : 2, l, p);
        }

        return p;
}

charm_attribute_subtree*
lt_policy( sized_integer_t* n, char* attr )
{
        return cmp_policy(n, 0, attr);
}

charm_attribute_subtree*
gt_policy( sized_integer_t* n, char* attr )
{
        return cmp_policy(n, 1, attr);
}

charm_attribute_subtree*
le_policy( sized_integer_t* n, char* attr )
{
        n->value++;
        return cmp_policy(n, 0, attr);
}

charm_attribute_subtree*
ge_policy( sized_integer_t* n, char* attr )
{
        n->value--;
        return cmp_policy(n, 1, attr);
}

char* cur_string = 0;

#define PEEK_CHAR ( *cur_string ? *cur_string     : EOF )
#define NEXT_CHAR ( *cur_string ? *(cur_string++) : EOF )

int
yylex()
{
  int c;
        int r;

  while( isspace(c = NEXT_CHAR) );

        r = 0;
  if( c == EOF )
    r = 0;
        else if( c == '&' )
                r = AND;
        else if( c == '|' )
                r = OR;
        else if( strchr("(),=#", c) || (strchr("<>", c) && PEEK_CHAR != '=') )
                r = c;
        else if( c == '<' && PEEK_CHAR == '=' )
        {
                NEXT_CHAR;
                r = LEQ;
        }
        else if( c == '>' && PEEK_CHAR == '=' )
        {
                NEXT_CHAR;
                r = GEQ;
        }
        else if( isdigit(c) )
        {
                int len = 50;
                char *s = s_string_new(len);
                s[0] = c;
                while( isdigit(PEEK_CHAR) )
                        s_string_append_c(s, len, NEXT_CHAR);

                sscanf(s, "%llu", &(yylval.nat));

                free(s);
                r = INTLIT;
        }
        else if( isalpha(c) || c == '!')
        {
                int len = 50;
                char *s = s_string_new(len);
                memset(s, '\0', len);
                s[0] = c;
                while( isalnum(PEEK_CHAR) || PEEK_CHAR == '_' ) {
                        s_string_append_c(s, len, NEXT_CHAR);
                }
                                   
                if( !strcmp(s, "and") )
                {
                        r = AND;
                }
                else if( !strcmp(s, "or") )
                {
                        r = OR;
                }
                else if( !strcmp(s, "of") )
                {
                        r = OF;
                }
                else
                {
                        // printf("TAG\n");
                        yylval.str = strdup(s);
                        r = TAG;
                }
                free(s);
        }
        else
                die("syntax error at \"%c%s\"\n", c, cur_string);

        return r;
}

void
yyerror( const char* s )
{
  die("error parsing policy: %s\n", s);
}

#define POLICY_IS_OR(p)  (((charm_attribute_subtree*)(p))->k == 1 && ((charm_attribute_subtree*)(p))->children->len)
#define POLICY_IS_AND(p) (((charm_attribute_subtree*)(p))->k == ((charm_attribute_subtree*)(p))->children->len)

#if 0
int
cmp_tidy( const void* a, const void* b )
{
        charm_attribute_subtree* pa;
        charm_attribute_subtree* pb;

        pa = *((charm_attribute_subtree**) a);
        pb = *((charm_attribute_subtree**) b);

        if(      pa->children->len >  0 && pb->children->len == 0 )
                return -1;
        else if( pa->children->len == 0 && pb->children->len >  0 )
                return 1;
        else if( pa->children->len == 0 && pb->children->len == 0 )
                return strcmp(pa->attr, pb->attr);
        else
                return 0;       
}

void
tidy( charm_attribute_subtree* p )
{
        int i;

        for( i = 0; i < p->children->len; i++ )
                tidy(g_ptr_array_index(p->children, i));

        if( p->children->len > 0 )
                qsort(p->children->pdata, p->children->len,
                                        sizeof(charm_attribute_subtree*), cmp_tidy);
}
#endif

char*
format_policy_postfix( charm_attribute_subtree* p )
{
        size_t i;
        char* r;
        char* s;
        char* t;

        if( p->num_subnodes == 0 )
                return strdup((char*)(p->attribute.attribute_str));

        r = format_policy_postfix(p->subnode[0]);
        for( i = 1; i < p->num_subnodes; i++ )
        {
                s = format_policy_postfix(p->subnode[i]);
                t = SAFE_MALLOC(strlen(r) + strlen(s) + 2);
                strcpy(t, " ");
                strcat(t, r);
                strcat(t, s);
                free(r);
                free(s);
                r = t;
        }
        
        t = s_strdup_printf("%s %dof%d", r, p->threshold_k, p->num_subnodes);
        free(r);

        return t;
}

/*
        Crufty.
*/
int
actual_bits( uint64_t value )
{
        int i;

        for( i = 32; i >= 1; i /= 2 )
                if( value >= ((uint64_t)1<<i) )
                        return i * 2;

        return 1;
}

#if 0
/*
        It is pretty crufty having this here since it is only used in
        keygen. Maybe eventually there will be a separate .c file with the
        policy_lang module.
*/
void
parse_attribute( GSList** l, char* a )
{
        if( !strchr(a, '=') )
                *l = g_slist_append(*l, a);
        else
        {
                int i;
                char* s;
                char* tplate;
                uint64_t value;
                int bits;

                s = malloc(sizeof(char) * strlen(a));

                if( sscanf(a, " %s = %llu # %u ", s, &value, &bits) == 3 )
                {
                        /* expint */

                        if( bits > 64 )
                                die("error parsing attribute \"%s\": 64 bits is the maximum allowed\n",
                                                a, value, bits);

                        if( value >= ((uint64_t)1<<bits) )
                                die("error parsing attribute \"%s\": value %llu too big for %d bits\n",
                                                a, value, bits);

                        tplate = s_strdup_printf("%%s_expint%02d_%%s%%d%%s", bits);
                        for( i = 0; i < bits; i++ )
                                *l = g_slist_append
                                        (*l, bit_marker(s, tplate, i, !!((uint64_t)1<<i & value)));
                        free(tplate);

                        *l = g_slist_append
                                (*l, s_strdup_printf("%s_expint%02d_%llu", s, bits, value));
                }
                else if( sscanf(a, " %s = %llu ", s, &value) == 2 )
                {
                        /* flexint */

                        for( i = 2; i <= 32; i *= 2 )
                                *l = g_slist_append
                                        (*l, s_strdup_printf
                                         (value < ((uint64_t)1<<i) ? "%s_lt_2^%02d" : "%s_ge_2^%02d", s, i));

                        for( i = 0; i < 64; i++ )
                                *l = g_slist_append
                                        (*l, bit_marker(s, "%s_flexint_%s%d%s", i, !!((uint64_t)1<<i & value)));

                        *l = g_slist_append
                                (*l, s_strdup_printf("%s_flexint_%llu", s, value));
                }
                else
                        die("error parsing attribute \"%s\"\n"
                                        "(note that numerical attributes are unsigned integers)\n",     a);

                free(s);
        }       
}
#endif

charm_attribute_subtree*
parse_policy_lang( char* s )
{
        // char* parsed_policy;
        
        cur_string = s;
        
        yyparse();
        charm_policy_compact(final_policy);
        //tidy(final_policy);
        
        //policy_free(final_policy);
        
        return final_policy;
}


char*
parse_policy_lang_as_str( char* s )
{
        char* parsed_policy;

        cur_string = s;

        yyparse();
        charm_policy_compact(final_policy);
        //tidy(final_policy);
        parsed_policy = format_policy_postfix(final_policy);

        policy_free(final_policy);

        return parsed_policy;
}