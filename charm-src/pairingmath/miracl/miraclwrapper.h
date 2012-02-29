#include <gmp.h>

typedef void pairing_t;
typedef void element_t;

#ifdef __cplusplus
extern "C" {
#endif

enum Curve {MNT, KSS, BLS, NONE_C}; // control what type of curve we are dealing with
enum Group {ZR_t = 0, G1_t, G2_t, GT_t, NONE_G}; // clashes with types in pairing_3.h
typedef enum Group Group_t;
typedef enum Curve Curve_t;

#define TRUE		1
#define FALSE		0
#define CF        	2 // Co-factor = 2 in MNT curves
#define MAX_LEN		256
#define LEN_BITS	4

pairing_t *pairing_init(int securitylevel);
void pairing_clear(pairing_t *pairing);
element_t *order(pairing_t *pairing);

element_t *element_init_ZR(int value);
element_t *_element_init_G1(void);
element_t *_element_init_G2(void);
element_t *_element_init_GT(const pairing_t *pairing);
void element_random(Group_t type, const pairing_t *pairing, element_t *e);
void element_printf(Group_t type, const element_t *e);
int _element_length_to_str(Group_t type, const element_t *e);
int _element_to_str(unsigned char **data_str, Group_t type, const element_t *e);

void _element_add(Group_t type, element_t *c, const element_t *a, const element_t *b); // c = a + b
void _element_sub(Group_t type, element_t *c, const element_t *a, const element_t *b); // c = a - b
void _element_mul(Group_t type, element_t *c, const element_t *a, const element_t *b, const element_t *o);
void _element_mul_si(Group_t type, const pairing_t *pairing, element_t *c, const element_t *a, const signed long int b, const element_t *o);
void _element_mul_zn(Group_t type, const pairing_t *pairing, element_t *c, const element_t *a, const element_t *b, const element_t *o);
void _element_div(Group_t type, element_t *c, const element_t *a, const element_t *b); // c = a / b

// c = a (G1, G2 or GT) ^ b (ZR)
element_t *_element_pow_zr(Group_t type, const pairing_t *pairing, const element_t *a, const element_t *b);
element_t *_element_pow_zr_zr(Group_t type, const pairing_t *pairing, const element_t *a, const int b, const element_t *o);
element_t *_element_neg(Group_t type, const element_t *e, const element_t *o);
void _element_inv(Group_t type, const element_t *a, element_t *b, element_t *o);

element_t *hash_then_map(Group_t type, const pairing_t *pairing, char *data, int len);
element_t *_element_from_hash(Group_t type, const pairing_t *pairing, void *data, int len);

int element_is_member(Curve_t ctype, Group_t type, const pairing_t *pairing, element_t *e);
int element_is_value(Group_t type, element_t *n, int value);

int _element_cmp(Group_t type, element_t *a, element_t *b);
void _element_set_si(Group_t type, element_t *dst, const signed long int src);
int _element_setG1(Group_t type, element_t *c, const element_t *a, const element_t *b);
void _element_set(Curve_t ctype, Group_t type, element_t *dst, const element_t *src);
char *print_mpz(mpz_t x, int base);
void _element_set_mpz(Group_t type, element_t *dst, mpz_t src);
void _element_to_mpz(Group_t type, element_t *src, mpz_t dst);
element_t *_element_pairing_type3(const pairing_t *pairing, const element_t *in1, const element_t *in2);
element_t *_element_prod_pairing_type3(const pairing_t *pairing, const element_t **in1, const element_t **in2, int length);

// I/O functions start
int _element_length_in_bytes(Curve_t ctype, Group_t type, element_t *e);
int _element_to_bytes(unsigned char *data, Curve_t ctype, Group_t type, element_t *e);
element_t *_element_from_bytes(Curve_t ctype, Group_t type, unsigned char *data);
// I/O functiond end

void element_delete(Group_t type, element_t *e);

#ifdef __cplusplus
}
#endif

