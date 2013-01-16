/* A Bison parser, made by GNU Bison 2.3.  */

/* Skeleton implementation for Bison's Yacc-like parsers in C

   Copyright (C) 1984, 1989, 1990, 2000, 2001, 2002, 2003, 2004, 2005, 2006
   Free Software Foundation, Inc.

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2, or (at your option)
   any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software
   Foundation, Inc., 51 Franklin Street, Fifth Floor,
   Boston, MA 02110-1301, USA.  */

/* As a special exception, you may create a larger work that contains
   part or all of the Bison parser skeleton and distribute that work
   under terms of your choice, so long as that work isn't itself a
   parser generator using the skeleton or a modified version thereof
   as a parser skeleton.  Alternatively, if you modify or redistribute
   the parser skeleton itself, you may (at your option) remove this
   special exception, which will cause the skeleton and the resulting
   Bison output files to be licensed under the GNU General Public
   License without this special exception.

   This special exception was added by the Free Software Foundation in
   version 2.2 of Bison.  */

/* C LALR(1) parser skeleton written by Richard Stallman, by
   simplifying the original so-called "semantic" parser.  */

/* All symbols defined below should begin with yy or YY, to avoid
   infringing on user name space.  This should be done even for local
   variables, as they might otherwise be expanded by user macros.
   There are some unavoidable exceptions within include files to
   define necessary library symbols; they are noted "INFRINGES ON
   USER NAME SPACE" below.  */

/* Identify Bison output.  */
#define YYBISON 1

/* Bison version.  */
#define YYBISON_VERSION "2.3"

/* Skeleton name.  */
#define YYSKELETON_NAME "yacc.c"

/* Pure parsers.  */
#define YYPURE 0

/* Using locations.  */
#define YYLSP_NEEDED 0



/* Tokens.  */
#ifndef YYTOKENTYPE
# define YYTOKENTYPE
   /* Put the tokens into the symbol table, so that GDB and other debuggers
      know about them.  */
   enum yytokentype {
     TAG = 258,
     INTLIT = 259,
     OR = 260,
     AND = 261,
     OF = 262,
     LEQ = 263,
     GEQ = 264
   };
#endif
/* Tokens.  */
#define TAG 258
#define INTLIT 259
#define OR 260
#define AND 261
#define OF 262
#define LEQ 263
#define GEQ 264




/* Copy the first part of user declarations.  */
#line 1 "policy.y"

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


/* Enabling traces.  */
#ifndef YYDEBUG
# define YYDEBUG 0
#endif

/* Enabling verbose error messages.  */
#ifdef YYERROR_VERBOSE
# undef YYERROR_VERBOSE
# define YYERROR_VERBOSE 1
#else
# define YYERROR_VERBOSE 0
#endif

/* Enabling the token table.  */
#ifndef YYTOKEN_TABLE
# define YYTOKEN_TABLE 0
#endif

#if ! defined YYSTYPE && ! defined YYSTYPE_IS_DECLARED
typedef union YYSTYPE
#line 52 "policy.y"
{
        char* str;
        uint64_t nat;
    sized_integer_t* sint;
        charm_attribute_subtree* tree;
        ptr_array_t* list;
}
/* Line 193 of yacc.c.  */
#line 172 "policy.tab.c"
	YYSTYPE;
# define yystype YYSTYPE /* obsolescent; will be withdrawn */
# define YYSTYPE_IS_DECLARED 1
# define YYSTYPE_IS_TRIVIAL 1
#endif



/* Copy the second part of user declarations.  */


/* Line 216 of yacc.c.  */
#line 185 "policy.tab.c"

#ifdef short
# undef short
#endif

#ifdef YYTYPE_UINT8
typedef YYTYPE_UINT8 yytype_uint8;
#else
typedef unsigned char yytype_uint8;
#endif

#ifdef YYTYPE_INT8
typedef YYTYPE_INT8 yytype_int8;
#elif (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
typedef signed char yytype_int8;
#else
typedef short int yytype_int8;
#endif

#ifdef YYTYPE_UINT16
typedef YYTYPE_UINT16 yytype_uint16;
#else
typedef unsigned short int yytype_uint16;
#endif

#ifdef YYTYPE_INT16
typedef YYTYPE_INT16 yytype_int16;
#else
typedef short int yytype_int16;
#endif

#ifndef YYSIZE_T
# ifdef __SIZE_TYPE__
#  define YYSIZE_T __SIZE_TYPE__
# elif defined size_t
#  define YYSIZE_T size_t
# elif ! defined YYSIZE_T && (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
#  include <stddef.h> /* INFRINGES ON USER NAME SPACE */
#  define YYSIZE_T size_t
# else
#  define YYSIZE_T unsigned int
# endif
#endif

#define YYSIZE_MAXIMUM ((YYSIZE_T) -1)

#ifndef YY_
# if defined YYENABLE_NLS && YYENABLE_NLS
#  if ENABLE_NLS
#   include <libintl.h> /* INFRINGES ON USER NAME SPACE */
#   define YY_(msgid) dgettext ("bison-runtime", msgid)
#  endif
# endif
# ifndef YY_
#  define YY_(msgid) msgid
# endif
#endif

/* Suppress unused-variable warnings by "using" E.  */
#if ! defined lint || defined __GNUC__
# define YYUSE(e) ((void) (e))
#else
# define YYUSE(e) /* empty */
#endif

/* Identity function, used to suppress warnings about constant conditions.  */
#ifndef lint
# define YYID(n) (n)
#else
#if (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
static int
YYID (int i)
#else
static int
YYID (i)
    int i;
#endif
{
  return i;
}
#endif

#if ! defined yyoverflow || YYERROR_VERBOSE

/* The parser invokes alloca or malloc; define the necessary symbols.  */

# ifdef YYSTACK_USE_ALLOCA
#  if YYSTACK_USE_ALLOCA
#   ifdef __GNUC__
#    define YYSTACK_ALLOC __builtin_alloca
#   elif defined __BUILTIN_VA_ARG_INCR
#    include <alloca.h> /* INFRINGES ON USER NAME SPACE */
#   elif defined _AIX
#    define YYSTACK_ALLOC __alloca
#   elif defined _MSC_VER
#    include <malloc.h> /* INFRINGES ON USER NAME SPACE */
#    define alloca _alloca
#   else
#    define YYSTACK_ALLOC alloca
#    if ! defined _ALLOCA_H && ! defined _STDLIB_H && (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
#     include <stdlib.h> /* INFRINGES ON USER NAME SPACE */
#     ifndef _STDLIB_H
#      define _STDLIB_H 1
#     endif
#    endif
#   endif
#  endif
# endif

# ifdef YYSTACK_ALLOC
   /* Pacify GCC's `empty if-body' warning.  */
#  define YYSTACK_FREE(Ptr) do { /* empty */; } while (YYID (0))
#  ifndef YYSTACK_ALLOC_MAXIMUM
    /* The OS might guarantee only one guard page at the bottom of the stack,
       and a page size can be as small as 4096 bytes.  So we cannot safely
       invoke alloca (N) if N exceeds 4096.  Use a slightly smaller number
       to allow for a few compiler-allocated temporary stack slots.  */
#   define YYSTACK_ALLOC_MAXIMUM 4032 /* reasonable circa 2006 */
#  endif
# else
#  define YYSTACK_ALLOC YYMALLOC
#  define YYSTACK_FREE YYFREE
#  ifndef YYSTACK_ALLOC_MAXIMUM
#   define YYSTACK_ALLOC_MAXIMUM YYSIZE_MAXIMUM
#  endif
#  if (defined __cplusplus && ! defined _STDLIB_H \
       && ! ((defined YYMALLOC || defined malloc) \
	     && (defined YYFREE || defined free)))
#   include <stdlib.h> /* INFRINGES ON USER NAME SPACE */
#   ifndef _STDLIB_H
#    define _STDLIB_H 1
#   endif
#  endif
#  ifndef YYMALLOC
#   define YYMALLOC malloc
#   if ! defined malloc && ! defined _STDLIB_H && (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
void *malloc (YYSIZE_T); /* INFRINGES ON USER NAME SPACE */
#   endif
#  endif
#  ifndef YYFREE
#   define YYFREE free
#   if ! defined free && ! defined _STDLIB_H && (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
void free (void *); /* INFRINGES ON USER NAME SPACE */
#   endif
#  endif
# endif
#endif /* ! defined yyoverflow || YYERROR_VERBOSE */


#if (! defined yyoverflow \
     && (! defined __cplusplus \
	 || (defined YYSTYPE_IS_TRIVIAL && YYSTYPE_IS_TRIVIAL)))

/* A type that is properly aligned for any stack member.  */
union yyalloc
{
  yytype_int16 yyss;
  YYSTYPE yyvs;
  };

/* The size of the maximum gap between one aligned stack and the next.  */
# define YYSTACK_GAP_MAXIMUM (sizeof (union yyalloc) - 1)

/* The size of an array large to enough to hold all stacks, each with
   N elements.  */
# define YYSTACK_BYTES(N) \
     ((N) * (sizeof (yytype_int16) + sizeof (YYSTYPE)) \
      + YYSTACK_GAP_MAXIMUM)

/* Copy COUNT objects from FROM to TO.  The source and destination do
   not overlap.  */
# ifndef YYCOPY
#  if defined __GNUC__ && 1 < __GNUC__
#   define YYCOPY(To, From, Count) \
      __builtin_memcpy (To, From, (Count) * sizeof (*(From)))
#  else
#   define YYCOPY(To, From, Count)		\
      do					\
	{					\
	  YYSIZE_T yyi;				\
	  for (yyi = 0; yyi < (Count); yyi++)	\
	    (To)[yyi] = (From)[yyi];		\
	}					\
      while (YYID (0))
#  endif
# endif

/* Relocate STACK from its old location to the new one.  The
   local variables YYSIZE and YYSTACKSIZE give the old and new number of
   elements in the stack, and YYPTR gives the new location of the
   stack.  Advance YYPTR to a properly aligned location for the next
   stack.  */
# define YYSTACK_RELOCATE(Stack)					\
    do									\
      {									\
	YYSIZE_T yynewbytes;						\
	YYCOPY (&yyptr->Stack, Stack, yysize);				\
	Stack = &yyptr->Stack;						\
	yynewbytes = yystacksize * sizeof (*Stack) + YYSTACK_GAP_MAXIMUM; \
	yyptr += yynewbytes / sizeof (*yyptr);				\
      }									\
    while (YYID (0))

#endif

/* YYFINAL -- State number of the termination state.  */
#define YYFINAL  15
/* YYLAST -- Last index in YYTABLE.  */
#define YYLAST   45

/* YYNTOKENS -- Number of terminals.  */
#define YYNTOKENS  17
/* YYNNTS -- Number of nonterminals.  */
#define YYNNTS  5
/* YYNRULES -- Number of rules.  */
#define YYNRULES  21
/* YYNRULES -- Number of states.  */
#define YYNSTATES  44

/* YYTRANSLATE(YYLEX) -- Bison symbol number corresponding to YYLEX.  */
#define YYUNDEFTOK  2
#define YYMAXUTOK   264

#define YYTRANSLATE(YYX)						\
  ((unsigned int) (YYX) <= YYMAXUTOK ? yytranslate[YYX] : YYUNDEFTOK)

/* YYTRANSLATE[YYLEX] -- Bison symbol number corresponding to YYLEX.  */
static const yytype_uint8 yytranslate[] =
{
       0,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,    10,     2,     2,     2,     2,
      11,    12,     2,     2,    16,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
      14,    13,    15,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     1,     2,     3,     4,
       5,     6,     7,     8,     9
};

#if YYDEBUG
/* YYPRHS[YYN] -- Index of the first RHS symbol of rule number YYN in
   YYRHS.  */
static const yytype_uint8 yyprhs[] =
{
       0,     0,     3,     5,     9,    11,    13,    17,    21,    27,
      31,    35,    39,    43,    47,    51,    55,    59,    63,    67,
      71,    73
};

/* YYRHS -- A `-1'-separated list of the rules' RHS.  */
static const yytype_int8 yyrhs[] =
{
      18,     0,    -1,    20,    -1,     4,    10,     4,    -1,     4,
      -1,     3,    -1,    20,     5,    20,    -1,    20,     6,    20,
      -1,     4,     7,    11,    21,    12,    -1,     3,    13,    19,
      -1,     3,    14,    19,    -1,     3,    15,    19,    -1,     3,
       8,    19,    -1,     3,     9,    19,    -1,    19,    13,     3,
      -1,    19,    14,     3,    -1,    19,    15,     3,    -1,    19,
       8,     3,    -1,    19,     9,     3,    -1,    11,    20,    12,
      -1,    20,    -1,    21,    16,    20,    -1
};

/* YYRLINE[YYN] -- source line where rule number YYN was defined.  */
static const yytype_uint8 yyrline[] =
{
       0,    74,    74,    76,    77,    79,    80,    81,    82,    83,
      84,    85,    86,    87,    88,    89,    90,    91,    92,    93,
      95,    97
};
#endif

#if YYDEBUG || YYERROR_VERBOSE || YYTOKEN_TABLE
/* YYTNAME[SYMBOL-NUM] -- String name of the symbol SYMBOL-NUM.
   First, the terminals, then, starting at YYNTOKENS, nonterminals.  */
static const char *const yytname[] =
{
  "$end", "error", "$undefined", "TAG", "INTLIT", "OR", "AND", "OF",
  "LEQ", "GEQ", "'#'", "'('", "')'", "'='", "'<'", "'>'", "','", "$accept",
  "result", "number", "policy", "arg_list", 0
};
#endif

# ifdef YYPRINT
/* YYTOKNUM[YYLEX-NUM] -- Internal token number corresponding to
   token YYLEX-NUM.  */
static const yytype_uint16 yytoknum[] =
{
       0,   256,   257,   258,   259,   260,   261,   262,   263,   264,
      35,    40,    41,    61,    60,    62,    44
};
# endif

/* YYR1[YYN] -- Symbol number of symbol that rule YYN derives.  */
static const yytype_uint8 yyr1[] =
{
       0,    17,    18,    19,    19,    20,    20,    20,    20,    20,
      20,    20,    20,    20,    20,    20,    20,    20,    20,    20,
      21,    21
};

/* YYR2[YYN] -- Number of symbols composing right hand side of rule YYN.  */
static const yytype_uint8 yyr2[] =
{
       0,     2,     1,     3,     1,     1,     3,     3,     5,     3,
       3,     3,     3,     3,     3,     3,     3,     3,     3,     3,
       1,     3
};

/* YYDEFACT[STATE-NAME] -- Default rule to reduce with in state
   STATE-NUM when YYTABLE doesn't specify something else to do.  Zero
   means the default is an error.  */
static const yytype_uint8 yydefact[] =
{
       0,     5,     4,     0,     0,     0,     2,     0,     0,     0,
       0,     0,     0,     0,     0,     1,     0,     0,     0,     0,
       0,     0,     0,     4,    12,    13,     9,    10,    11,     0,
       3,    19,    17,    18,    14,    15,    16,     6,     7,    20,
       0,     8,     0,    21
};

/* YYDEFGOTO[NTERM-NUM].  */
static const yytype_int8 yydefgoto[] =
{
      -1,     4,     5,     6,    40
};

/* YYPACT[STATE-NUM] -- Index in YYTABLE of the portion describing
   STATE-NUM.  */
#define YYPACT_NINF -5
static const yytype_int8 yypact[] =
{
      -2,    -1,    -4,    -2,     4,     2,    17,     1,     1,     1,
       1,     1,    13,    29,    15,    -5,    32,    33,    34,    37,
      38,    -2,    -2,    35,    -5,    -5,    -5,    -5,    -5,    -2,
      -5,    -5,    -5,    -5,    -5,    -5,    -5,    19,    -5,    17,
      22,    -5,    -2,    17
};

/* YYPGOTO[NTERM-NUM].  */
static const yytype_int8 yypgoto[] =
{
      -5,    -5,    21,    -3,    -5
};

/* YYTABLE[YYPACT[STATE-NUM]].  What to do in state STATE-NUM.  If
   positive, shift that token.  If negative, reduce the rule which
   number is the opposite.  If zero, do what YYDEFACT says.
   If YYTABLE_NINF, syntax error.  */
#define YYTABLE_NINF -1
static const yytype_uint8 yytable[] =
{
      14,     1,     2,    12,    15,    23,    13,     7,     8,     3,
      16,    17,     9,    10,    11,    18,    19,    20,    37,    38,
      21,    22,    21,    22,    29,    22,    39,    31,    24,    25,
      26,    27,    28,    30,    41,    32,    33,    34,    42,    43,
      35,    36,     0,     0,     0,    13
};

static const yytype_int8 yycheck[] =
{
       3,     3,     4,     7,     0,     4,    10,     8,     9,    11,
       8,     9,    13,    14,    15,    13,    14,    15,    21,    22,
       5,     6,     5,     6,    11,     6,    29,    12,     7,     8,
       9,    10,    11,     4,    12,     3,     3,     3,    16,    42,
       3,     3,    -1,    -1,    -1,    10
};

/* YYSTOS[STATE-NUM] -- The (internal number of the) accessing
   symbol of state STATE-NUM.  */
static const yytype_uint8 yystos[] =
{
       0,     3,     4,    11,    18,    19,    20,     8,     9,    13,
      14,    15,     7,    10,    20,     0,     8,     9,    13,    14,
      15,     5,     6,     4,    19,    19,    19,    19,    19,    11,
       4,    12,     3,     3,     3,     3,     3,    20,    20,    20,
      21,    12,    16,    20
};

#define yyerrok		(yyerrstatus = 0)
#define yyclearin	(yychar = YYEMPTY)
#define YYEMPTY		(-2)
#define YYEOF		0

#define YYACCEPT	goto yyacceptlab
#define YYABORT		goto yyabortlab
#define YYERROR		goto yyerrorlab


/* Like YYERROR except do call yyerror.  This remains here temporarily
   to ease the transition to the new meaning of YYERROR, for GCC.
   Once GCC version 2 has supplanted version 1, this can go.  */

#define YYFAIL		goto yyerrlab

#define YYRECOVERING()  (!!yyerrstatus)

#define YYBACKUP(Token, Value)					\
do								\
  if (yychar == YYEMPTY && yylen == 1)				\
    {								\
      yychar = (Token);						\
      yylval = (Value);						\
      yytoken = YYTRANSLATE (yychar);				\
      YYPOPSTACK (1);						\
      goto yybackup;						\
    }								\
  else								\
    {								\
      yyerror (YY_("syntax error: cannot back up")); \
      YYERROR;							\
    }								\
while (YYID (0))


#define YYTERROR	1
#define YYERRCODE	256


/* YYLLOC_DEFAULT -- Set CURRENT to span from RHS[1] to RHS[N].
   If N is 0, then set CURRENT to the empty location which ends
   the previous symbol: RHS[0] (always defined).  */

#define YYRHSLOC(Rhs, K) ((Rhs)[K])
#ifndef YYLLOC_DEFAULT
# define YYLLOC_DEFAULT(Current, Rhs, N)				\
    do									\
      if (YYID (N))                                                    \
	{								\
	  (Current).first_line   = YYRHSLOC (Rhs, 1).first_line;	\
	  (Current).first_column = YYRHSLOC (Rhs, 1).first_column;	\
	  (Current).last_line    = YYRHSLOC (Rhs, N).last_line;		\
	  (Current).last_column  = YYRHSLOC (Rhs, N).last_column;	\
	}								\
      else								\
	{								\
	  (Current).first_line   = (Current).last_line   =		\
	    YYRHSLOC (Rhs, 0).last_line;				\
	  (Current).first_column = (Current).last_column =		\
	    YYRHSLOC (Rhs, 0).last_column;				\
	}								\
    while (YYID (0))
#endif


/* YY_LOCATION_PRINT -- Print the location on the stream.
   This macro was not mandated originally: define only if we know
   we won't break user code: when these are the locations we know.  */

#ifndef YY_LOCATION_PRINT
# if defined YYLTYPE_IS_TRIVIAL && YYLTYPE_IS_TRIVIAL
#  define YY_LOCATION_PRINT(File, Loc)			\
     fprintf (File, "%d.%d-%d.%d",			\
	      (Loc).first_line, (Loc).first_column,	\
	      (Loc).last_line,  (Loc).last_column)
# else
#  define YY_LOCATION_PRINT(File, Loc) ((void) 0)
# endif
#endif


/* YYLEX -- calling `yylex' with the right arguments.  */

#ifdef YYLEX_PARAM
# define YYLEX yylex (YYLEX_PARAM)
#else
# define YYLEX yylex ()
#endif

/* Enable debugging if requested.  */
#if YYDEBUG

# ifndef YYFPRINTF
#  include <stdio.h> /* INFRINGES ON USER NAME SPACE */
#  define YYFPRINTF fprintf
# endif

# define YYDPRINTF(Args)			\
do {						\
  if (yydebug)					\
    YYFPRINTF Args;				\
} while (YYID (0))

# define YY_SYMBOL_PRINT(Title, Type, Value, Location)			  \
do {									  \
  if (yydebug)								  \
    {									  \
      YYFPRINTF (stderr, "%s ", Title);					  \
      yy_symbol_print (stderr,						  \
		  Type, Value); \
      YYFPRINTF (stderr, "\n");						  \
    }									  \
} while (YYID (0))


/*--------------------------------.
| Print this symbol on YYOUTPUT.  |
`--------------------------------*/

/*ARGSUSED*/
#if (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
static void
yy_symbol_value_print (FILE *yyoutput, int yytype, YYSTYPE const * const yyvaluep)
#else
static void
yy_symbol_value_print (yyoutput, yytype, yyvaluep)
    FILE *yyoutput;
    int yytype;
    YYSTYPE const * const yyvaluep;
#endif
{
  if (!yyvaluep)
    return;
# ifdef YYPRINT
  if (yytype < YYNTOKENS)
    YYPRINT (yyoutput, yytoknum[yytype], *yyvaluep);
# else
  YYUSE (yyoutput);
# endif
  switch (yytype)
    {
      default:
	break;
    }
}


/*--------------------------------.
| Print this symbol on YYOUTPUT.  |
`--------------------------------*/

#if (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
static void
yy_symbol_print (FILE *yyoutput, int yytype, YYSTYPE const * const yyvaluep)
#else
static void
yy_symbol_print (yyoutput, yytype, yyvaluep)
    FILE *yyoutput;
    int yytype;
    YYSTYPE const * const yyvaluep;
#endif
{
  if (yytype < YYNTOKENS)
    YYFPRINTF (yyoutput, "token %s (", yytname[yytype]);
  else
    YYFPRINTF (yyoutput, "nterm %s (", yytname[yytype]);

  yy_symbol_value_print (yyoutput, yytype, yyvaluep);
  YYFPRINTF (yyoutput, ")");
}

/*------------------------------------------------------------------.
| yy_stack_print -- Print the state stack from its BOTTOM up to its |
| TOP (included).                                                   |
`------------------------------------------------------------------*/

#if (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
static void
yy_stack_print (yytype_int16 *bottom, yytype_int16 *top)
#else
static void
yy_stack_print (bottom, top)
    yytype_int16 *bottom;
    yytype_int16 *top;
#endif
{
  YYFPRINTF (stderr, "Stack now");
  for (; bottom <= top; ++bottom)
    YYFPRINTF (stderr, " %d", *bottom);
  YYFPRINTF (stderr, "\n");
}

# define YY_STACK_PRINT(Bottom, Top)				\
do {								\
  if (yydebug)							\
    yy_stack_print ((Bottom), (Top));				\
} while (YYID (0))


/*------------------------------------------------.
| Report that the YYRULE is going to be reduced.  |
`------------------------------------------------*/

#if (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
static void
yy_reduce_print (YYSTYPE *yyvsp, int yyrule)
#else
static void
yy_reduce_print (yyvsp, yyrule)
    YYSTYPE *yyvsp;
    int yyrule;
#endif
{
  int yynrhs = yyr2[yyrule];
  int yyi;
  unsigned long int yylno = yyrline[yyrule];
  YYFPRINTF (stderr, "Reducing stack by rule %d (line %lu):\n",
	     yyrule - 1, yylno);
  /* The symbols being reduced.  */
  for (yyi = 0; yyi < yynrhs; yyi++)
    {
      fprintf (stderr, "   $%d = ", yyi + 1);
      yy_symbol_print (stderr, yyrhs[yyprhs[yyrule] + yyi],
		       &(yyvsp[(yyi + 1) - (yynrhs)])
		       		       );
      fprintf (stderr, "\n");
    }
}

# define YY_REDUCE_PRINT(Rule)		\
do {					\
  if (yydebug)				\
    yy_reduce_print (yyvsp, Rule); \
} while (YYID (0))

/* Nonzero means print parse trace.  It is left uninitialized so that
   multiple parsers can coexist.  */
int yydebug;
#else /* !YYDEBUG */
# define YYDPRINTF(Args)
# define YY_SYMBOL_PRINT(Title, Type, Value, Location)
# define YY_STACK_PRINT(Bottom, Top)
# define YY_REDUCE_PRINT(Rule)
#endif /* !YYDEBUG */


/* YYINITDEPTH -- initial size of the parser's stacks.  */
#ifndef	YYINITDEPTH
# define YYINITDEPTH 200
#endif

/* YYMAXDEPTH -- maximum size the stacks can grow to (effective only
   if the built-in stack extension method is used).

   Do not make this value too large; the results are undefined if
   YYSTACK_ALLOC_MAXIMUM < YYSTACK_BYTES (YYMAXDEPTH)
   evaluated with infinite-precision integer arithmetic.  */

#ifndef YYMAXDEPTH
# define YYMAXDEPTH 10000
#endif



#if YYERROR_VERBOSE

# ifndef yystrlen
#  if defined __GLIBC__ && defined _STRING_H
#   define yystrlen strlen
#  else
/* Return the length of YYSTR.  */
#if (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
static YYSIZE_T
yystrlen (const char *yystr)
#else
static YYSIZE_T
yystrlen (yystr)
    const char *yystr;
#endif
{
  YYSIZE_T yylen;
  for (yylen = 0; yystr[yylen]; yylen++)
    continue;
  return yylen;
}
#  endif
# endif

# ifndef yystpcpy
#  if defined __GLIBC__ && defined _STRING_H && defined _GNU_SOURCE
#   define yystpcpy stpcpy
#  else
/* Copy YYSRC to YYDEST, returning the address of the terminating '\0' in
   YYDEST.  */
#if (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
static char *
yystpcpy (char *yydest, const char *yysrc)
#else
static char *
yystpcpy (yydest, yysrc)
    char *yydest;
    const char *yysrc;
#endif
{
  char *yyd = yydest;
  const char *yys = yysrc;

  while ((*yyd++ = *yys++) != '\0')
    continue;

  return yyd - 1;
}
#  endif
# endif

# ifndef yytnamerr
/* Copy to YYRES the contents of YYSTR after stripping away unnecessary
   quotes and backslashes, so that it's suitable for yyerror.  The
   heuristic is that double-quoting is unnecessary unless the string
   contains an apostrophe, a comma, or backslash (other than
   backslash-backslash).  YYSTR is taken from yytname.  If YYRES is
   null, do not copy; instead, return the length of what the result
   would have been.  */
static YYSIZE_T
yytnamerr (char *yyres, const char *yystr)
{
  if (*yystr == '"')
    {
      YYSIZE_T yyn = 0;
      char const *yyp = yystr;

      for (;;)
	switch (*++yyp)
	  {
	  case '\'':
	  case ',':
	    goto do_not_strip_quotes;

	  case '\\':
	    if (*++yyp != '\\')
	      goto do_not_strip_quotes;
	    /* Fall through.  */
	  default:
	    if (yyres)
	      yyres[yyn] = *yyp;
	    yyn++;
	    break;

	  case '"':
	    if (yyres)
	      yyres[yyn] = '\0';
	    return yyn;
	  }
    do_not_strip_quotes: ;
    }

  if (! yyres)
    return yystrlen (yystr);

  return yystpcpy (yyres, yystr) - yyres;
}
# endif

/* Copy into YYRESULT an error message about the unexpected token
   YYCHAR while in state YYSTATE.  Return the number of bytes copied,
   including the terminating null byte.  If YYRESULT is null, do not
   copy anything; just return the number of bytes that would be
   copied.  As a special case, return 0 if an ordinary "syntax error"
   message will do.  Return YYSIZE_MAXIMUM if overflow occurs during
   size calculation.  */
static YYSIZE_T
yysyntax_error (char *yyresult, int yystate, int yychar)
{
  int yyn = yypact[yystate];

  if (! (YYPACT_NINF < yyn && yyn <= YYLAST))
    return 0;
  else
    {
      int yytype = YYTRANSLATE (yychar);
      YYSIZE_T yysize0 = yytnamerr (0, yytname[yytype]);
      YYSIZE_T yysize = yysize0;
      YYSIZE_T yysize1;
      int yysize_overflow = 0;
      enum { YYERROR_VERBOSE_ARGS_MAXIMUM = 5 };
      char const *yyarg[YYERROR_VERBOSE_ARGS_MAXIMUM];
      int yyx;

# if 0
      /* This is so xgettext sees the translatable formats that are
	 constructed on the fly.  */
      YY_("syntax error, unexpected %s");
      YY_("syntax error, unexpected %s, expecting %s");
      YY_("syntax error, unexpected %s, expecting %s or %s");
      YY_("syntax error, unexpected %s, expecting %s or %s or %s");
      YY_("syntax error, unexpected %s, expecting %s or %s or %s or %s");
# endif
      char *yyfmt;
      char const *yyf;
      static char const yyunexpected[] = "syntax error, unexpected %s";
      static char const yyexpecting[] = ", expecting %s";
      static char const yyor[] = " or %s";
      char yyformat[sizeof yyunexpected
		    + sizeof yyexpecting - 1
		    + ((YYERROR_VERBOSE_ARGS_MAXIMUM - 2)
		       * (sizeof yyor - 1))];
      char const *yyprefix = yyexpecting;

      /* Start YYX at -YYN if negative to avoid negative indexes in
	 YYCHECK.  */
      int yyxbegin = yyn < 0 ? -yyn : 0;

      /* Stay within bounds of both yycheck and yytname.  */
      int yychecklim = YYLAST - yyn + 1;
      int yyxend = yychecklim < YYNTOKENS ? yychecklim : YYNTOKENS;
      int yycount = 1;

      yyarg[0] = yytname[yytype];
      yyfmt = yystpcpy (yyformat, yyunexpected);

      for (yyx = yyxbegin; yyx < yyxend; ++yyx)
	if (yycheck[yyx + yyn] == yyx && yyx != YYTERROR)
	  {
	    if (yycount == YYERROR_VERBOSE_ARGS_MAXIMUM)
	      {
		yycount = 1;
		yysize = yysize0;
		yyformat[sizeof yyunexpected - 1] = '\0';
		break;
	      }
	    yyarg[yycount++] = yytname[yyx];
	    yysize1 = yysize + yytnamerr (0, yytname[yyx]);
	    yysize_overflow |= (yysize1 < yysize);
	    yysize = yysize1;
	    yyfmt = yystpcpy (yyfmt, yyprefix);
	    yyprefix = yyor;
	  }

      yyf = YY_(yyformat);
      yysize1 = yysize + yystrlen (yyf);
      yysize_overflow |= (yysize1 < yysize);
      yysize = yysize1;

      if (yysize_overflow)
	return YYSIZE_MAXIMUM;

      if (yyresult)
	{
	  /* Avoid sprintf, as that infringes on the user's name space.
	     Don't have undefined behavior even if the translation
	     produced a string with the wrong number of "%s"s.  */
	  char *yyp = yyresult;
	  int yyi = 0;
	  while ((*yyp = *yyf) != '\0')
	    {
	      if (*yyp == '%' && yyf[1] == 's' && yyi < yycount)
		{
		  yyp += yytnamerr (yyp, yyarg[yyi++]);
		  yyf += 2;
		}
	      else
		{
		  yyp++;
		  yyf++;
		}
	    }
	}
      return yysize;
    }
}
#endif /* YYERROR_VERBOSE */


/*-----------------------------------------------.
| Release the memory associated to this symbol.  |
`-----------------------------------------------*/

/*ARGSUSED*/
#if (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
static void
yydestruct (const char *yymsg, int yytype, YYSTYPE *yyvaluep)
#else
static void
yydestruct (yymsg, yytype, yyvaluep)
    const char *yymsg;
    int yytype;
    YYSTYPE *yyvaluep;
#endif
{
  YYUSE (yyvaluep);

  if (!yymsg)
    yymsg = "Deleting";
  YY_SYMBOL_PRINT (yymsg, yytype, yyvaluep, yylocationp);

  switch (yytype)
    {

      default:
	break;
    }
}


/* Prevent warnings from -Wmissing-prototypes.  */

#ifdef YYPARSE_PARAM
#if defined __STDC__ || defined __cplusplus
int yyparse (void *YYPARSE_PARAM);
#else
int yyparse ();
#endif
#else /* ! YYPARSE_PARAM */
#if defined __STDC__ || defined __cplusplus
int yyparse (void);
#else
int yyparse ();
#endif
#endif /* ! YYPARSE_PARAM */



/* The look-ahead symbol.  */
int yychar;

/* The semantic value of the look-ahead symbol.  */
YYSTYPE yylval;

/* Number of syntax errors so far.  */
int yynerrs;



/*----------.
| yyparse.  |
`----------*/

#ifdef YYPARSE_PARAM
#if (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
int
yyparse (void *YYPARSE_PARAM)
#else
int
yyparse (YYPARSE_PARAM)
    void *YYPARSE_PARAM;
#endif
#else /* ! YYPARSE_PARAM */
#if (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
int
yyparse (void)
#else
int
yyparse ()

#endif
#endif
{
  
  int yystate;
  int yyn;
  int yyresult;
  /* Number of tokens to shift before error messages enabled.  */
  int yyerrstatus;
  /* Look-ahead token as an internal (translated) token number.  */
  int yytoken = 0;
#if YYERROR_VERBOSE
  /* Buffer for error messages, and its allocated size.  */
  char yymsgbuf[128];
  char *yymsg = yymsgbuf;
  YYSIZE_T yymsg_alloc = sizeof yymsgbuf;
#endif

  /* Three stacks and their tools:
     `yyss': related to states,
     `yyvs': related to semantic values,
     `yyls': related to locations.

     Refer to the stacks thru separate pointers, to allow yyoverflow
     to reallocate them elsewhere.  */

  /* The state stack.  */
  yytype_int16 yyssa[YYINITDEPTH];
  yytype_int16 *yyss = yyssa;
  yytype_int16 *yyssp;

  /* The semantic value stack.  */
  YYSTYPE yyvsa[YYINITDEPTH];
  YYSTYPE *yyvs = yyvsa;
  YYSTYPE *yyvsp;



#define YYPOPSTACK(N)   (yyvsp -= (N), yyssp -= (N))

  YYSIZE_T yystacksize = YYINITDEPTH;

  /* The variables used to return semantic value and location from the
     action routines.  */
  YYSTYPE yyval;


  /* The number of symbols on the RHS of the reduced rule.
     Keep to zero when no symbol should be popped.  */
  int yylen = 0;

  YYDPRINTF ((stderr, "Starting parse\n"));

  yystate = 0;
  yyerrstatus = 0;
  yynerrs = 0;
  yychar = YYEMPTY;		/* Cause a token to be read.  */

  /* Initialize stack pointers.
     Waste one element of value and location stack
     so that they stay on the same level as the state stack.
     The wasted elements are never initialized.  */

  yyssp = yyss;
  yyvsp = yyvs;

  goto yysetstate;

/*------------------------------------------------------------.
| yynewstate -- Push a new state, which is found in yystate.  |
`------------------------------------------------------------*/
 yynewstate:
  /* In all cases, when you get here, the value and location stacks
     have just been pushed.  So pushing a state here evens the stacks.  */
  yyssp++;

 yysetstate:
  *yyssp = yystate;

  if (yyss + yystacksize - 1 <= yyssp)
    {
      /* Get the current used size of the three stacks, in elements.  */
      YYSIZE_T yysize = yyssp - yyss + 1;

#ifdef yyoverflow
      {
	/* Give user a chance to reallocate the stack.  Use copies of
	   these so that the &'s don't force the real ones into
	   memory.  */
	YYSTYPE *yyvs1 = yyvs;
	yytype_int16 *yyss1 = yyss;


	/* Each stack pointer address is followed by the size of the
	   data in use in that stack, in bytes.  This used to be a
	   conditional around just the two extra args, but that might
	   be undefined if yyoverflow is a macro.  */
	yyoverflow (YY_("memory exhausted"),
		    &yyss1, yysize * sizeof (*yyssp),
		    &yyvs1, yysize * sizeof (*yyvsp),

		    &yystacksize);

	yyss = yyss1;
	yyvs = yyvs1;
      }
#else /* no yyoverflow */
# ifndef YYSTACK_RELOCATE
      goto yyexhaustedlab;
# else
      /* Extend the stack our own way.  */
      if (YYMAXDEPTH <= yystacksize)
	goto yyexhaustedlab;
      yystacksize *= 2;
      if (YYMAXDEPTH < yystacksize)
	yystacksize = YYMAXDEPTH;

      {
	yytype_int16 *yyss1 = yyss;
	union yyalloc *yyptr =
	  (union yyalloc *) YYSTACK_ALLOC (YYSTACK_BYTES (yystacksize));
	if (! yyptr)
	  goto yyexhaustedlab;
	YYSTACK_RELOCATE (yyss);
	YYSTACK_RELOCATE (yyvs);

#  undef YYSTACK_RELOCATE
	if (yyss1 != yyssa)
	  YYSTACK_FREE (yyss1);
      }
# endif
#endif /* no yyoverflow */

      yyssp = yyss + yysize - 1;
      yyvsp = yyvs + yysize - 1;


      YYDPRINTF ((stderr, "Stack size increased to %lu\n",
		  (unsigned long int) yystacksize));

      if (yyss + yystacksize - 1 <= yyssp)
	YYABORT;
    }

  YYDPRINTF ((stderr, "Entering state %d\n", yystate));

  goto yybackup;

/*-----------.
| yybackup.  |
`-----------*/
yybackup:

  /* Do appropriate processing given the current state.  Read a
     look-ahead token if we need one and don't already have one.  */

  /* First try to decide what to do without reference to look-ahead token.  */
  yyn = yypact[yystate];
  if (yyn == YYPACT_NINF)
    goto yydefault;

  /* Not known => get a look-ahead token if don't already have one.  */

  /* YYCHAR is either YYEMPTY or YYEOF or a valid look-ahead symbol.  */
  if (yychar == YYEMPTY)
    {
      YYDPRINTF ((stderr, "Reading a token: "));
      yychar = YYLEX;
    }

  if (yychar <= YYEOF)
    {
      yychar = yytoken = YYEOF;
      YYDPRINTF ((stderr, "Now at end of input.\n"));
    }
  else
    {
      yytoken = YYTRANSLATE (yychar);
      YY_SYMBOL_PRINT ("Next token is", yytoken, &yylval, &yylloc);
    }

  /* If the proper action on seeing token YYTOKEN is to reduce or to
     detect an error, take that action.  */
  yyn += yytoken;
  if (yyn < 0 || YYLAST < yyn || yycheck[yyn] != yytoken)
    goto yydefault;
  yyn = yytable[yyn];
  if (yyn <= 0)
    {
      if (yyn == 0 || yyn == YYTABLE_NINF)
	goto yyerrlab;
      yyn = -yyn;
      goto yyreduce;
    }

  if (yyn == YYFINAL)
    YYACCEPT;

  /* Count tokens shifted since error; after three, turn off error
     status.  */
  if (yyerrstatus)
    yyerrstatus--;

  /* Shift the look-ahead token.  */
  YY_SYMBOL_PRINT ("Shifting", yytoken, &yylval, &yylloc);

  /* Discard the shifted token unless it is eof.  */
  if (yychar != YYEOF)
    yychar = YYEMPTY;

  yystate = yyn;
  *++yyvsp = yylval;

  goto yynewstate;


/*-----------------------------------------------------------.
| yydefault -- do the default action for the current state.  |
`-----------------------------------------------------------*/
yydefault:
  yyn = yydefact[yystate];
  if (yyn == 0)
    goto yyerrlab;
  goto yyreduce;


/*-----------------------------.
| yyreduce -- Do a reduction.  |
`-----------------------------*/
yyreduce:
  /* yyn is the number of a rule to reduce with.  */
  yylen = yyr2[yyn];

  /* If YYLEN is nonzero, implement the default value of the action:
     `$$ = $1'.

     Otherwise, the following line sets YYVAL to garbage.
     This behavior is undocumented and Bison
     users should not rely upon it.  Assigning to YYVAL
     unconditionally makes the parser a bit smaller, and it avoids a
     GCC warning that YYVAL may be used uninitialized.  */
  yyval = yyvsp[1-yylen];


  YY_REDUCE_PRINT (yyn);
  switch (yyn)
    {
        case 2:
#line 74 "policy.y"
    { final_policy = (yyvsp[(1) - (1)].tree) ;}
    break;

  case 3:
#line 76 "policy.y"
    { (yyval.sint) = expint((yyvsp[(1) - (3)].nat), (yyvsp[(3) - (3)].nat)); ;}
    break;

  case 4:
#line 77 "policy.y"
    { (yyval.sint) = flexint((yyvsp[(1) - (1)].nat));    ;}
    break;

  case 5:
#line 79 "policy.y"
    { (yyval.tree) = leaf_policy((yyvsp[(1) - (1)].str));        ;}
    break;

  case 6:
#line 80 "policy.y"
    { (yyval.tree) = kof2_policy(1, (yyvsp[(1) - (3)].tree), (yyvsp[(3) - (3)].tree)); ;}
    break;

  case 7:
#line 81 "policy.y"
    { (yyval.tree) = kof2_policy(2, (yyvsp[(1) - (3)].tree), (yyvsp[(3) - (3)].tree)); ;}
    break;

  case 8:
#line 82 "policy.y"
    { (yyval.tree) = kof_policy((yyvsp[(1) - (5)].nat), (yyvsp[(4) - (5)].list));     ;}
    break;

  case 9:
#line 83 "policy.y"
    { (yyval.tree) = eq_policy((yyvsp[(3) - (3)].sint), (yyvsp[(1) - (3)].str));      ;}
    break;

  case 10:
#line 84 "policy.y"
    { (yyval.tree) = lt_policy((yyvsp[(3) - (3)].sint), (yyvsp[(1) - (3)].str));      ;}
    break;

  case 11:
#line 85 "policy.y"
    { (yyval.tree) = gt_policy((yyvsp[(3) - (3)].sint), (yyvsp[(1) - (3)].str));      ;}
    break;

  case 12:
#line 86 "policy.y"
    { (yyval.tree) = le_policy((yyvsp[(3) - (3)].sint), (yyvsp[(1) - (3)].str));      ;}
    break;

  case 13:
#line 87 "policy.y"
    { (yyval.tree) = ge_policy((yyvsp[(3) - (3)].sint), (yyvsp[(1) - (3)].str));      ;}
    break;

  case 14:
#line 88 "policy.y"
    { (yyval.tree) = eq_policy((yyvsp[(1) - (3)].sint), (yyvsp[(3) - (3)].str));      ;}
    break;

  case 15:
#line 89 "policy.y"
    { (yyval.tree) = gt_policy((yyvsp[(1) - (3)].sint), (yyvsp[(3) - (3)].str));      ;}
    break;

  case 16:
#line 90 "policy.y"
    { (yyval.tree) = lt_policy((yyvsp[(1) - (3)].sint), (yyvsp[(3) - (3)].str));      ;}
    break;

  case 17:
#line 91 "policy.y"
    { (yyval.tree) = ge_policy((yyvsp[(1) - (3)].sint), (yyvsp[(3) - (3)].str));      ;}
    break;

  case 18:
#line 92 "policy.y"
    { (yyval.tree) = le_policy((yyvsp[(1) - (3)].sint), (yyvsp[(3) - (3)].str));      ;}
    break;

  case 19:
#line 93 "policy.y"
    { (yyval.tree) = (yyvsp[(2) - (3)].tree);                     ;}
    break;

  case 20:
#line 95 "policy.y"
    { (yyval.list) = ptr_array_new();
                                       ptr_array_add((yyval.list), (yyvsp[(1) - (1)].tree)); ;}
    break;

  case 21:
#line 97 "policy.y"
    { (yyval.list) = (yyvsp[(1) - (3)].list);
                                       ptr_array_add((yyval.list), (yyvsp[(3) - (3)].tree)); ;}
    break;


/* Line 1267 of yacc.c.  */
#line 1504 "policy.tab.c"
      default: break;
    }
  YY_SYMBOL_PRINT ("-> $$ =", yyr1[yyn], &yyval, &yyloc);

  YYPOPSTACK (yylen);
  yylen = 0;
  YY_STACK_PRINT (yyss, yyssp);

  *++yyvsp = yyval;


  /* Now `shift' the result of the reduction.  Determine what state
     that goes to, based on the state we popped back to and the rule
     number reduced by.  */

  yyn = yyr1[yyn];

  yystate = yypgoto[yyn - YYNTOKENS] + *yyssp;
  if (0 <= yystate && yystate <= YYLAST && yycheck[yystate] == *yyssp)
    yystate = yytable[yystate];
  else
    yystate = yydefgoto[yyn - YYNTOKENS];

  goto yynewstate;


/*------------------------------------.
| yyerrlab -- here on detecting error |
`------------------------------------*/
yyerrlab:
  /* If not already recovering from an error, report this error.  */
  if (!yyerrstatus)
    {
      ++yynerrs;
#if ! YYERROR_VERBOSE
      yyerror (YY_("syntax error"));
#else
      {
	YYSIZE_T yysize = yysyntax_error (0, yystate, yychar);
	if (yymsg_alloc < yysize && yymsg_alloc < YYSTACK_ALLOC_MAXIMUM)
	  {
	    YYSIZE_T yyalloc = 2 * yysize;
	    if (! (yysize <= yyalloc && yyalloc <= YYSTACK_ALLOC_MAXIMUM))
	      yyalloc = YYSTACK_ALLOC_MAXIMUM;
	    if (yymsg != yymsgbuf)
	      YYSTACK_FREE (yymsg);
	    yymsg = (char *) YYSTACK_ALLOC (yyalloc);
	    if (yymsg)
	      yymsg_alloc = yyalloc;
	    else
	      {
		yymsg = yymsgbuf;
		yymsg_alloc = sizeof yymsgbuf;
	      }
	  }

	if (0 < yysize && yysize <= yymsg_alloc)
	  {
	    (void) yysyntax_error (yymsg, yystate, yychar);
	    yyerror (yymsg);
	  }
	else
	  {
	    yyerror (YY_("syntax error"));
	    if (yysize != 0)
	      goto yyexhaustedlab;
	  }
      }
#endif
    }



  if (yyerrstatus == 3)
    {
      /* If just tried and failed to reuse look-ahead token after an
	 error, discard it.  */

      if (yychar <= YYEOF)
	{
	  /* Return failure if at end of input.  */
	  if (yychar == YYEOF)
	    YYABORT;
	}
      else
	{
	  yydestruct ("Error: discarding",
		      yytoken, &yylval);
	  yychar = YYEMPTY;
	}
    }

  /* Else will try to reuse look-ahead token after shifting the error
     token.  */
  goto yyerrlab1;


/*---------------------------------------------------.
| yyerrorlab -- error raised explicitly by YYERROR.  |
`---------------------------------------------------*/
yyerrorlab:

  /* Pacify compilers like GCC when the user code never invokes
     YYERROR and the label yyerrorlab therefore never appears in user
     code.  */
  if (/*CONSTCOND*/ 0)
     goto yyerrorlab;

  /* Do not reclaim the symbols of the rule which action triggered
     this YYERROR.  */
  YYPOPSTACK (yylen);
  yylen = 0;
  YY_STACK_PRINT (yyss, yyssp);
  yystate = *yyssp;
  goto yyerrlab1;


/*-------------------------------------------------------------.
| yyerrlab1 -- common code for both syntax error and YYERROR.  |
`-------------------------------------------------------------*/
yyerrlab1:
  yyerrstatus = 3;	/* Each real token shifted decrements this.  */

  for (;;)
    {
      yyn = yypact[yystate];
      if (yyn != YYPACT_NINF)
	{
	  yyn += YYTERROR;
	  if (0 <= yyn && yyn <= YYLAST && yycheck[yyn] == YYTERROR)
	    {
	      yyn = yytable[yyn];
	      if (0 < yyn)
		break;
	    }
	}

      /* Pop the current state because it cannot handle the error token.  */
      if (yyssp == yyss)
	YYABORT;


      yydestruct ("Error: popping",
		  yystos[yystate], yyvsp);
      YYPOPSTACK (1);
      yystate = *yyssp;
      YY_STACK_PRINT (yyss, yyssp);
    }

  if (yyn == YYFINAL)
    YYACCEPT;

  *++yyvsp = yylval;


  /* Shift the error token.  */
  YY_SYMBOL_PRINT ("Shifting", yystos[yyn], yyvsp, yylsp);

  yystate = yyn;
  goto yynewstate;


/*-------------------------------------.
| yyacceptlab -- YYACCEPT comes here.  |
`-------------------------------------*/
yyacceptlab:
  yyresult = 0;
  goto yyreturn;

/*-----------------------------------.
| yyabortlab -- YYABORT comes here.  |
`-----------------------------------*/
yyabortlab:
  yyresult = 1;
  goto yyreturn;

#ifndef yyoverflow
/*-------------------------------------------------.
| yyexhaustedlab -- memory exhaustion comes here.  |
`-------------------------------------------------*/
yyexhaustedlab:
  yyerror (YY_("memory exhausted"));
  yyresult = 2;
  /* Fall through.  */
#endif

yyreturn:
  if (yychar != YYEOF && yychar != YYEMPTY)
     yydestruct ("Cleanup: discarding lookahead",
		 yytoken, &yylval);
  /* Do not reclaim the symbols of the rule which action triggered
     this YYABORT or YYACCEPT.  */
  YYPOPSTACK (yylen);
  YY_STACK_PRINT (yyss, yyssp);
  while (yyssp != yyss)
    {
      yydestruct ("Cleanup: popping",
		  yystos[*yyssp], yyvsp);
      YYPOPSTACK (1);
    }
#ifndef yyoverflow
  if (yyss != yyssa)
    YYSTACK_FREE (yyss);
#endif
#if YYERROR_VERBOSE
  if (yymsg != yymsgbuf)
    YYSTACK_FREE (yymsg);
#endif
  /* Make sure YYID is used.  */
  return YYID (yyresult);
}


#line 101 "policy.y"


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
