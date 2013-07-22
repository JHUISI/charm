/*
 * Charm-Crypto is a framework for rapidly prototyping cryptosystems.
 *
 * Charm-Crypto is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * Charm-Crypto is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with Charm-Crypto. If not, see <http://www.gnu.org/licenses/>.
 *
 * Please contact the charm-crypto dev team at support@charm-crypto.com
 * for any questions.
 */

/*
*   @file    miracl_interface.h
*
*   @brief   charm interface over MIRACL's pairing-based crypto C++ classes
*
*   @author  ayo.akinyele@charm-crypto.com
*
************************************************************************/
#include <gmp.h>

typedef void pairing_t;
typedef void element_t;

#ifdef __cplusplus
extern "C" {
#endif

enum Curve {MNT, BN, SS, NONE_C}; // control what type of curve we are dealing with
#if (BUILD_MNT_CURVE == 1 || BUILD_BN_CURVE == 1)
enum Group {pyZR_t = 0, pyG1_t, pyG2_t, pyGT_t, NONE_G}; // clashes with types in pairing_3.h
#else
enum Group {pyZR_t = 0, pyG1_t, pyGT_t, NONE_G};
#define pyG2_t 	pyG1_t // for backwards compatibility
#define G2 	 	G1
#endif

typedef enum Group Group_t;
typedef enum Curve Curve_t;

#define TRUE		1
#define FALSE		0
#define CF        	2 // Co-factor = 2 in MNT curves
#define LEN_BITS	4
#define aes_block_size 16

pairing_t *pairing_init(int securitylevel);
void pairing_clear(pairing_t *pairing);
// to clean up the mriacl system completely.NOTE: Make sure miracl PFC classes are patched.
void miracl_clean(void);
element_t *order(pairing_t *pairing);
element_t *element_gt(const pairing_t *pairing);

element_t *element_init_ZR(int value);
element_t *_element_init_G1(void);
element_t *_element_init_G2(void);
element_t *_element_init_GT(const pairing_t *pairing);
int _element_pp_init(const pairing_t *pairing, Group_t type, element_t *e);
void element_random(Group_t type, const pairing_t *pairing, element_t *e);
void element_printf(Group_t type, const element_t *e);
int _element_length_to_str(Group_t type, const element_t *e);
int _element_to_str(unsigned char **data_str, Group_t type, const element_t *e);

void _element_add(Group_t type, element_t *c, const element_t *a, const element_t *b, const element_t *o); // c = a + b
void _element_sub(Group_t type, element_t *c, const element_t *a, const element_t *b, const element_t *o); // c = (a - b) % o
void _element_mul(Group_t type, element_t *c, const element_t *a, const element_t *b, const element_t *o);
void _element_mul_si(Group_t type, const pairing_t *pairing, element_t *c, const element_t *a, const signed long int b, const element_t *o);
void _element_mul_zn(Group_t type, const pairing_t *pairing, element_t *c, const element_t *a, const element_t *b, const element_t *o);
void _element_div(Group_t type, element_t *c, const element_t *a, const element_t *b, const element_t *o); // c = a / b

// c = a (G1, G2 or GT) ^ b (ZR)
element_t *_element_pow_zr(Group_t type, const pairing_t *pairing, element_t *a, element_t *b, element_t *o);
//element_t *_element_pow_zr(Group_t type, const pairing_t *pairing, const element_t *a, const element_t *b, const element_t *o);
element_t *_element_pow_zr_zr(Group_t type, const pairing_t *pairing, const element_t *a, const int b, const element_t *o);
element_t *_element_neg(Group_t type, const element_t *e, const element_t *o);
//void _element_inv(Group_t type, const element_t *a, element_t *b, element_t *o);
void _element_inv(Group_t type, const pairing_t *pairing, const element_t *a, element_t *b, element_t *o);

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

element_t *_element_pairing(const pairing_t *pairing, const element_t *in1, const element_t *in2);
element_t *_element_prod_pairing(const pairing_t *pairing, const element_t **in1, const element_t **in2, int length);

// I/O functions start
int _element_length_in_bytes(Curve_t ctype, Group_t type, element_t *e);
int _element_to_bytes(unsigned char *data, Curve_t ctype, Group_t type, element_t *e);
element_t *_element_from_bytes(Curve_t ctype, Group_t type, unsigned char *data);
// I/O functiond end

void element_delete(Group_t type, element_t *e);

void _init_hash(const pairing_t *pairing);
void _element_add_str_hash(const pairing_t *pairing, char *data, int len);
void _element_add_to_hash(Group_t type, const pairing_t *pairing, const element_t *e);
element_t *finish_hash(Group_t type, const pairing_t *pairing);

void _element_hash_key(const pairing_t *pairing, Group_t type, element_t *e, void *data, int len);

int aes_encrypt(char *key, char *message, int len, char **out);
int aes_decrypt(char *key, char *ciphertext, int len, char **out);

#ifdef __cplusplus
}
#endif

