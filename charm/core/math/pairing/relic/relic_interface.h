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
*   @file    relic_interface.h
*
*   @brief   charm interface over RELIC's pairing-based crypto module
*
*   @author  ayo.akinyele@charm-crypto.com
*
************************************************************************/

#ifndef RELIC_INTERFACE_H
#define RELIC_INTERFACE_H

#include <stdlib.h>
#include <math.h>
#include "relic.h"
/* make sure error checking enabled in relic_conf.h, ALLOC should be dynamic */

//#define DISABLE_CHECK  1
#define TRUE	1
#define FALSE	0
#define DBASE	16
#define MAX_BUF	1024
#define SHA_LEN  	32
#define SHA_FUNC	md_map_sh256
typedef enum _status_t { ELEMENT_OK = 2,
	   ELEMENT_INVALID_ARG,
	   ELEMENT_INVALID_ARG_LEN,
	   ELEMENT_INVALID_TYPES,
	   ELEMENT_INVALID_RESULT,
	   ELEMENT_PAIRING_INIT_FAILED,
	   ELEMENT_UNINITIALIZED,
	   ELEMENT_DIV_ZERO,
	   ELEMENT_INITIALIZED_ALRDY,
} status_t;

enum Group {ZR, G1, G2, GT, NONE_G};
typedef enum Group GroupType;

//new macros to fix Relic renaming
#define FP_BYTES RLC_FP_BYTES
#define fp_write fp_write_str
#define BN_BYTES (RLC_BN_DIGS * sizeof(dig_t))
#define BN_NEG RLC_NEG
#define BN_POS RLC_POS
#define STS_OK RLC_OK
#define G1_TABLE RLC_G1_TABLE
#define G2_TABLE RLC_G2_TABLE
#define CMP_GT RLC_GT
#define CMP_EQ RLC_EQ
//end new macros

#define FP_STR FP_BYTES * 2 + 1
#define G1_LEN (FP_BYTES * 2) + 2
#define G2_LEN (FP_BYTES * 4) + 4
#define GT_LEN (FP_BYTES * 12) + 12

struct element {
	int isInitialized;
	bn_t order;
	GroupType type;
	bn_t bn;
	g1_t g1;
	g2_t g2;
	gt_t gt;
};

struct object {
	int isInitialized;
	g1_t *t1;
	g2_t *t2;
};

typedef struct element element_t[1];
typedef struct element *element_ptr;
typedef struct object element_pp_t[1];
typedef bn_t integer_t;
int bn_is_one(bn_t a);

/* Initialize 'e' to be an element of the ring Z_r of pairing.
 * r is the order of the groups G1, G2 and GT that are involved in the pairing.
 */
status_t pairing_init(void); // must be able to set curve parameters dynamically
status_t pairing_clear(void);

status_t element_init_Zr(element_t e, int init_value);
/* Initialize 'e' to be an element of the group G1, G2 or GT of pairing. */
status_t element_init_G1(element_t e);
status_t element_init_G2(element_t e);
status_t element_init_GT(element_t e);
/* selects random element from a uniform distribution */
status_t element_random(element_t e);
/* print contents of ane element structure */
status_t element_printf(const char *msg, element_t e);
status_t element_to_str(char *data, int len, element_t e);
/* free mem. associated with a */
status_t element_clear(element_t e);

status_t element_pp_init(element_pp_t e_pp, element_t e);
status_t element_pp_pow(element_t o, element_pp_t e_pp, GroupType type, element_t e);
status_t element_pp_pow_int(element_t o, element_pp_t e_pp, GroupType type, integer_t bn);
status_t element_pp_clear(element_pp_t e_pp, GroupType type);

/* arithmetic operators over elements */
// c = a + b
status_t element_add(element_t c, element_t a, element_t b);
// c = a - b
status_t element_sub(element_t c, element_t a, element_t b);
// c = a * b
status_t element_mul(element_t c, element_t a, element_t b);
// c = a * Zr
status_t element_mul_zr(element_t c, element_t a, element_t b);
// c = a * int
status_t element_mul_int(element_t c, element_t a, integer_t b);
// c = a / b
status_t element_div(element_t c, element_t a, element_t b);
status_t element_div_int(element_t c, element_t a, integer_t b);
status_t element_int_div(element_t c, integer_t a, element_t b);

// c = -a
status_t element_neg(element_t c, element_t a);
// c = 1 / a
status_t element_invert(element_t c, element_t a);
// c = a ^ b ( where b is ZR)
status_t element_pow_zr(element_t c, element_t a, element_t b);
// c = a ^ b ( where b is int)
status_t element_pow_int(element_t c, element_t a, integer_t b);
// compare a & b returns 0 if a==b, -1 if a < b and 1 if a > b
int element_cmp(element_t a, element_t b);
// check if element is zero
int element_is_member(element_t e);
int get_order(integer_t x);

status_t pairing_apply(element_t et, element_t e1, element_t e2);

// adjustable key derivation function
status_t element_to_key(element_t e, uint8_t *data, int data_len, uint8_t label);
status_t hash_buffer_to_bytes(uint8_t *input, int input_len, uint8_t *output, int output_len, uint8_t label);

/* copy method: e = a */
status_t element_set(element_t e, element_t a);
status_t element_set_int(element_t e, integer_t x);
status_t element_to_int(integer_t x, element_t e);
status_t element_set_si(element_t e, unsigned int x);
// void element_init_same_as(element_t e, element_t e2)
int element_length(element_t e);
/* generate an element of a particular type from data */
status_t element_from_hash(element_t e, unsigned char *data, int len);
/* serialize to bytes */
status_t element_to_bytes(unsigned char *data, int data_len, element_t e);
/* de-serialize from bytes */
status_t element_from_bytes(element_t e, unsigned char *data, int data_len);

void print_as_hex(uint8_t *data, size_t len);
status_t charm_g1_read_bin(g1_t g, uint8_t *data, int data_len);
status_t charm_g1_write_bin(g1_t g, uint8_t *data, int data_len);
status_t charm_g1_write_str(g1_t g, uint8_t *data, int data_len);

status_t charm_g2_read_bin(g2_t g, uint8_t *data, int data_len);
status_t charm_g2_write_bin(g2_t g, uint8_t *data, int data_len);
status_t charm_g2_write_str(g2_t g, uint8_t *data, int data_len);

status_t charm_gt_read_bin(gt_t g, uint8_t *data, int data_len);
status_t charm_gt_write_bin(gt_t g, uint8_t *data, int data_len);
status_t charm_gt_write_str(gt_t g, uint8_t *data, int data_len);

#define bn_inits(b) \
		bn_null(b);	\
		bn_new(b);

#define g1_inits(g) \
		g1_null(g);	\
		g1_new(g);

#define g2_inits(g) \
		g2_null(g);	\
		g2_new(g);

#define gt_inits(g) \
		gt_null(g);	\
		gt_new(g);

#ifdef DISABLE_CHECK
#define LEAVE_IF(a, m)	/* empty */
#define EXIT_IF_NOT_SAME(a, b)  /* empty */
#else
#define EXIT_IF_NOT_SAME(a, b)		\
	if(a->type != b->type)	{		\
		return ELEMENT_INVALID_TYPES; }

#define LEAVE_IF(a, m)	\
		if(a) {			\
		  fprintf(stderr, "%s", m);	\
		  return ELEMENT_INVALID_ARG;	}

#endif

#endif
