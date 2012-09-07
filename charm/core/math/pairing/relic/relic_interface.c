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
*   @file    relic_interface.c
*
*   @brief   charm interface over RELIC's pairing-based crypto module
*
*   @author  ayo.akinyele@charm-crypto.com
*   @status  not complete: modular division operations not working correctly (as of 8/6/12)
*
************************************************************************/

#include "relic_interface.h"

void print_as_hex(uint8_t *data, size_t len)
{
	size_t i, j;

	for (i = 0; i < (len - 8); i += 8) {
		printf("%02X%02X%02X%02X%02X%02X%02X%02X ", data[i], data[i+1], data[i+2], data[i+3], data[i+4], data[i+5], data[i+6], data[i+7]);
	}

	for(j = i; j < len; j++) {
		printf("%02X", data[j]);
	}

	printf("\n");
}

int bn_is_one(bn_t a)
{
	if(a->used == 0) return 0; // false
	else if((a->used == 1) && (a->dp[0] == 1)) return 1; // true
	else return 0; // false
}

status_t pairing_init(void)
{
	int err_code = core_init();
	if(err_code != STS_OK) return ELEMENT_PAIRING_INIT_FAILED;

//	conf_print();
	pc_param_set_any(); // see if we can open this up?
	return ELEMENT_OK;
}

status_t pairing_clear(void)
{
	int err_code = core_clean();
	/* check error */
	if(err_code != STS_OK) return ELEMENT_PAIRING_INIT_FAILED;

	return ELEMENT_OK;
}

status_t element_init_Zr(element_t e, int init_value)
{
//	if(e->bn != NULL) bn_free(e->bn);
	bn_inits(e->bn);
	bn_inits(e->order);
	if(init_value == 0) /* default value */
		bn_zero(e->bn);
	else
		bn_set_dig(e->bn, (dig_t) init_value);

	g1_get_ord(e->order);
	e->isInitialized = TRUE;
	e->type = ZR;
    return ELEMENT_OK;
}

status_t element_init_G1(element_t e)
{
//	if(e->g1 != NULL) g1_free(e->g1);
	g1_inits(e->g1);
	bn_inits(e->order);
	g1_set_infty(e->g1);
	g1_get_ord(e->order);
	e->isInitialized = TRUE;
	e->type = G1;
    return ELEMENT_OK;
}

status_t element_init_G2(element_t e)
{
	g2_inits(e->g2);
	g2_set_infty(e->g2);
	bn_inits(e->order);
	g2_get_ord(e->order);
	e->isInitialized = TRUE;
	e->type = G2;
    return ELEMENT_OK;
}

status_t element_init_GT(element_t e)
{
	gt_inits(e->gt);
	bn_inits(e->order);
	gt_set_unity(e->gt);
	g1_get_ord(e->order);
	e->isInitialized = TRUE;
	e->type = GT;
    return ELEMENT_OK;
}

status_t element_random(element_t e)
{
	if(e->isInitialized == TRUE) {
		if(e->type == ZR) {
			bn_t n;
			bn_inits(n);
			g1_get_ord(n);

			bn_t t = e->bn;
			bn_rand(t, BN_POS, bn_bits(n));
			bn_mod(t,  t, n);
			bn_free(n);
		}
		else if(e->type == G1) {
			g1_rand(e->g1);
		}
		else if(e->type == G2) {
			g2_rand(e->g2);
		}
		else if(e->type == GT) {
			gt_rand(e->gt);
		}
		return ELEMENT_OK;
	}

	return ELEMENT_UNINITIALIZED;
}

status_t element_printf(const char *msg, element_t e)
{
    if(e->isInitialized == TRUE) {
    	printf("%s", msg);
    	if(e->type == ZR)
    		bn_print(e->bn);
    	else if(e->type == G1)
    		g1_print(e->g1);
    	else if(e->type == G2)
    		g2_print(e->g2);
    	else if(e->type == GT)
    		gt_print(e->gt);
    	return ELEMENT_OK;
    }

    return ELEMENT_INVALID_RESULT;
}

//TODO:
status_t element_to_str(char *data, int len, element_t e)
{
    if(e->isInitialized == TRUE) {
    	int str_len = element_length(e) * 2;
		if(str_len > len) return ELEMENT_INVALID_ARG;
		memset(data, 0, len);
    	uint8_t tmp1[str_len+1];
		memset(tmp1, 0, str_len);

    	if(e->type == ZR) {
    		bn_write_str(data, str_len, e->bn, BASE);
    	}
    	else if(e->type == G1) {
			g1_write_str(e->g1, tmp1, str_len);

			int dist_y = FP_STR;
			snprintf(data, len, "[%s, %s]", tmp1, &(tmp1[dist_y]));
    	}
    	else if(e->type == G2) {
			g2_write_str(e->g2, tmp1, str_len);

			int len2 = FP_STR;
			int dist_x1 = len2, dist_y0 = len2 * 2, dist_y1 = len2 * 3;
			snprintf(data, len, "[%s, %s, %s, %s]", tmp1, &(tmp1[dist_x1]), &(tmp1[dist_y0]), &(tmp1[dist_y1]));
    	}
    	else if(e->type == GT) {
			gt_write_str(e->gt, tmp1, str_len);

    		int len2 = FP_STR;
    		int dist_x01 = len2, dist_x10 = len2 * 2, dist_x11 = len2 * 3,
    			dist_x20 = len2 * 4, dist_x21 = len2 * 5, dist_y00 = len2 * 6,
    			dist_y01 = len2 * 7, dist_y10 = len2 * 8, dist_y11 = len2 * 9,
    			dist_y20 = len2 * 10, dist_y21 = len2 * 11;
			 snprintf(data, len, "[%s, %s, %s, %s, %s, %s], [%s, %s, %s, %s, %s, %s]",
    		 			  tmp1, &(tmp1[dist_x01]), &(tmp1[dist_x10]), &(tmp1[dist_x11]),
    					  &(tmp1[dist_x20]), &(tmp1[dist_x21]),
    					  &(tmp1[dist_y00]), &(tmp1[dist_y01]), &(tmp1[dist_y10]), &(tmp1[dist_y11]),
    					  &(tmp1[dist_y20]), &(tmp1[dist_y21]));
    	}
    }
    return ELEMENT_OK;
}

status_t element_clear(element_t e)
{
    if(e->isInitialized == TRUE) {
    	if(e->type == ZR) {
    		bn_free(e->bn);
    		bn_null(e->bn);
		}
    	else if(e->type == G1) {
    		g1_free(e->g1);
    		g1_null(e->g1);
    	}
    	else if(e->type == G2) {
    		g2_free(e->g2);
    		g2_null(e->g2);
    	}
    	else if(e->type == GT) {
    		gt_free(e->gt);
    		gt_null(e->gt);
    	}
    	else {
    		return ELEMENT_INVALID_TYPES;
    	}
		bn_free(e->order);
		bn_null(e->order);
    	e->isInitialized = FALSE;
    	e->type = NIL;
    }
    return ELEMENT_OK;
}

status_t element_add(element_t c, element_t a, element_t b)
{
	GroupType type = a->type;
	EXIT_IF_NOT_SAME(a, b);
	LEAVE_IF(a->isInitialized != TRUE || b->isInitialized != TRUE || c->isInitialized != TRUE, "uninitialized arguments.");

	if(type == ZR) {
		LEAVE_IF( c->type != ZR, "result initialized but invalid type.");
		bn_add(c->bn, a->bn, b->bn);
		bn_mod(c->bn, c->bn, c->order);
	}
	else if(type == G1) {
		LEAVE_IF( c->type != G1, "result initialized but invalid type.");
		g1_add(c->g1, a->g1, b->g1);
		g1_norm(c->g1, c->g1);
	}
	else if(type == G2) {
		LEAVE_IF( c->type != G2, "result initialized but invalid type.");
		g2_add(c->g2, a->g2, b->g2);
		g2_norm(c->g2, c->g2);
	}
	else {
		return ELEMENT_INVALID_TYPES;
	}

	return ELEMENT_OK;
}

status_t element_sub(element_t c, element_t a, element_t b)
{
	GroupType type = a->type;
	EXIT_IF_NOT_SAME(a, b);
	LEAVE_IF(a->isInitialized != TRUE || b->isInitialized != TRUE, "uninitialized arguments.");
	LEAVE_IF( c->type != type, "result initialized but invalid type.");

	if(type == ZR) {
		bn_sub(c->bn, a->bn, b->bn);
		bn_mod(c->bn, c->bn, c->order);
		if(bn_sign(c->bn) == BN_NEG) bn_add(c->bn, c->bn, a->order);

	}
	else if(type == G1) {
		g1_sub(c->g1, a->g1, b->g1);
		g1_norm(c->g1, c->g1);
	}
	else if(type == G2) {
		g2_sub(c->g2, a->g2, b->g2);
		g2_norm(c->g2, c->g2);
	}
	else {
		return ELEMENT_INVALID_TYPES;
	}

	return ELEMENT_OK;
}

status_t element_mul(element_t c, element_t a, element_t b)
{
	GroupType type = a->type;
	EXIT_IF_NOT_SAME(a, b);
	LEAVE_IF(a->isInitialized != TRUE || b->isInitialized != TRUE || c->isInitialized != TRUE, "uninitialized arguments.");
	LEAVE_IF( c->type != type, "result initialized but invalid type.");

	if(type == ZR) {
		bn_mul(c->bn, a->bn, b->bn);
		bn_mod(c->bn, c->bn, c->order);
	}
	else if(type == G1) {
		g1_add(c->g1, a->g1, b->g1);
		g1_norm(c->g1, c->g1);
	}
	else if(type == G2) {
		g2_add(c->g2, a->g2, b->g2);
		g2_norm(c->g2, c->g2);
	}
	else if(type == GT) {
		gt_mul(c->gt, a->gt, b->gt);
	}
	else {
		return ELEMENT_INVALID_TYPES;
	}

	return ELEMENT_OK;
}

// aka scalar multiplication?
status_t element_mul_zr(element_t c, element_t a, element_t b)
{
	GroupType type = a->type;
	// TODO: c (type) = a (type) * b (ZR)
	LEAVE_IF(a->isInitialized != TRUE, "invalid argument.");
	LEAVE_IF(b->type != ZR || b->isInitialized != TRUE, "invalid type.");
	LEAVE_IF(c->isInitialized != TRUE || c->type != type, "result not initialized or invalid type.");

	if(type == G1) {
		g1_mul(c->g1, a->g1, b->bn);
	}
	else if(type == G2) {
		g2_mul(c->g2, a->g2, b->bn);
	}
	else if(type == GT) {
		gt_exp(c->gt, a->gt, b->bn);
	}
	else {
		return ELEMENT_INVALID_TYPES;
	}

	return ELEMENT_OK;
}

status_t element_mul_int(element_t c, element_t a, integer_t b)
{
	GroupType type = a->type;
	// TODO: c (type) = a (type) * b (ZR)
	LEAVE_IF(a->isInitialized != TRUE, "invalid argument.");
	LEAVE_IF(c->isInitialized != TRUE || c->type != type, "result not initialized or invalid type.");

	if(type == ZR) {
		bn_mul(c->bn, a->bn, b);
		bn_mod(c->bn, c->bn, c->order);
	}
	else if(type == G1) {
		g1_mul(c->g1, a->g1, b);
	}
	else if(type == G2) {
		g2_mul(c->g2, a->g2, b);
	}
	else if(type == GT) {
		gt_exp(c->gt, a->gt, b);
	}
	else {
		return ELEMENT_INVALID_TYPES;
	}

	return ELEMENT_OK;
}

status_t element_div(element_t c, element_t a, element_t b)
{
	GroupType type = a->type;
	EXIT_IF_NOT_SAME(a, b);
	LEAVE_IF(a->isInitialized != TRUE || b->isInitialized != TRUE || c->isInitialized != TRUE, "uninitialized arguments.");
	LEAVE_IF( c->type != type, "result initialized but invalid type.");

	if(type == ZR) {
		if(bn_is_zero(b->bn)) return ELEMENT_DIV_ZERO;
		// c = (1 / b) mod order
		element_invert(c, b);
		if(bn_is_one(a->bn))  return ELEMENT_OK;
//		bn_div(c->bn, a->bn, b->bn);
//		bn_mod(c->bn, c->bn, c->order);
		// remainder of ((a * c) / order)
		integer_t s;
		bn_inits(s);
		// c = (a * c) / order (remainder only)
		bn_mul(s, a->bn, c->bn);
		bn_div_rem(s, c->bn, s, a->order);
//		if(bn_sign(c->bn) == BN_NEG) bn_add(c->bn, c->bn, a->order);
		bn_free(s);


	}
	else if(type == G1) {
		g1_sub(c->g1, a->g1, b->g1);
		g1_norm(c->g1, c->g1);
	}
	else if(type == G2) {
		g2_sub(c->g2, a->g2, b->g2);
		g2_norm(c->g2, c->g2);
	}
	else if(type == GT) {
		gt_t t;
		gt_inits(t);
		gt_inv(t, b->gt);
		gt_mul(c->gt, a->gt, t);
		gt_free(t);
	}
	else {
		return ELEMENT_INVALID_TYPES;
	}

	return ELEMENT_OK;
}

// int appears on rhs
status_t element_div_int(element_t c, element_t a, integer_t b)
{
	GroupType type = a->type;
	EXIT_IF_NOT_SAME(c, a);
	LEAVE_IF( c->isInitialized != TRUE || a->isInitialized != TRUE, "uninitialized arguments.");
	LEAVE_IF( c->type != type, "result initialized but invalid type.");

	if(type == ZR) {
		if(bn_is_zero(b)) return ELEMENT_DIV_ZERO;
//		if(bn_is_one(a->bn)) {
//			element_set_int(a, b);
//			return element_invert(c, a); // not going to work
//		}

		integer_t s;
		bn_inits(s);
		// compute c = (1 / b) mod order
		bn_gcd_ext(s, c->bn, NULL, b, a->order);
		if(bn_sign(c->bn) == BN_NEG) bn_add(c->bn, c->bn, a->order);
		if(bn_is_one(a->bn) && bn_sign(a->bn) == BN_POS) {
			bn_free(s);
			return ELEMENT_OK;
		}
		// remainder of ((a * c) / order)
		// c = (a * c) / order (remainder only)
		bn_mul(s, a->bn, c->bn);
		bn_div_rem(s, c->bn, s, a->order);
//		if(bn_sign(c->bn) == BN_NEG) bn_add(c->bn, c->bn, a->order);
		bn_free(s);
//		bn_div(c->bn, a->bn, b);
//		bn_mod(c->bn, c->bn, c->order);
	}
	else if(type == G1 || type == G2 || type == GT) {
		if(bn_is_one(b)) {
			return element_set(c, a);
		}
		// TODO: other cases: b > 1 (ZR)?
	}
	else {
		return ELEMENT_INVALID_TYPES;
	}

	return ELEMENT_OK;
}

// int appears on lhs (1 / [ZR, G1, G2, GT])
status_t element_int_div(element_t c, integer_t a, element_t b)
{
	GroupType type = b->type;
	EXIT_IF_NOT_SAME(c, b);
	LEAVE_IF( c->isInitialized != TRUE || b->isInitialized != TRUE, "uninitialized arguments.");
	LEAVE_IF( c->type != type, "result initialized but invalid type.");

	if(type == ZR) {
		if(bn_is_zero(b->bn)) return ELEMENT_DIV_ZERO;
		element_invert(c, b);
		if(bn_is_one(a)) return ELEMENT_OK;
		integer_t s;
		bn_inits(s);
		bn_mul(s, a, c->bn);
		bn_div_rem(s, c->bn, s, c->order);
//		if(bn_sign(c->bn) == BN_NEG) bn_add(c->bn, c->bn, c->order);
		bn_free(s);
//		bn_div(c->bn, a, b->bn);
//		bn_mod(c->bn, c->bn, c->order);
	}
	else if(type == G1 || type == G2 || type == GT) {
		if(bn_is_one(a)) {
			element_invert(c, b);
		}
		// TODO: other cases: a > 1 (ZR)?
	}

	return ELEMENT_OK;
}


status_t element_neg(element_t c, element_t a)
{
	GroupType type = a->type;
	EXIT_IF_NOT_SAME(a, c);

	if(type == ZR) {
		bn_neg(c->bn, a->bn);
		bn_add(c->bn, c->bn, a->order);
	}
	else if(type == G1) {
		g1_neg(c->g1, a->g1);
	}
	else if(type == G2) {
		g2_neg(c->g2, a->g2);
	}
	else if(type == GT) {
		gt_inv(c->gt, a->gt);
	}
	else {
		return ELEMENT_INVALID_TYPES;
	}
	return ELEMENT_OK;
}

status_t element_invert(element_t c, element_t a)
{
	GroupType type = a->type;
	EXIT_IF_NOT_SAME(a, c);

	if(type == ZR) {
		bn_t s;
		bn_inits(s);
		// compute c = (1 / a) mod n
		bn_gcd_ext(s, c->bn, NULL, a->bn, a->order);
		if(bn_sign(c->bn) == BN_NEG) bn_add(c->bn, c->bn, a->order);
		bn_free(s);
	}
	else if(type == G1) {
		g1_neg(c->g1, a->g1);
	}
	else if(type == G2) {
		g2_neg(c->g2, a->g2);
	}
	else if(type == GT) {
		gt_inv(c->gt, a->gt);
	}
	else {
		return ELEMENT_INVALID_TYPES;
	}
	return ELEMENT_OK;
}

status_t element_pow_zr(element_t c, element_t a, element_t b)
{
	GroupType type = a->type;
	// c (type) = a (type) ^ b (ZR)
	LEAVE_IF( c->isInitialized != TRUE || a->isInitialized != TRUE, "uninitialized argument.");
	EXIT_IF_NOT_SAME(c, a);
	LEAVE_IF(a->isInitialized != TRUE, "invalid argument.");
	LEAVE_IF(b->isInitialized != TRUE || b->type != ZR, "invalid type.");

	if(type == ZR) {
		bn_mxp(c->bn, a->bn, b->bn, a->order);
	}
	else if(type == G1) {
		g1_mul(c->g1, a->g1, b->bn);
	}
	else if(type == G2) {
		g2_mul(c->g2, a->g2, b->bn);
	}
	else if(type == GT) {
		gt_exp(c->gt, a->gt, b->bn);
	}
	else {
		return ELEMENT_INVALID_TYPES;
	}

	return ELEMENT_OK;
}

status_t element_pow_int(element_t c, element_t a, integer_t b)
{
	GroupType type = a->type;
	// TODO: c (type) = a (type) ^ b (ZR)
	LEAVE_IF( c->isInitialized != TRUE || a->isInitialized != TRUE, "uninitialized argument.");
	EXIT_IF_NOT_SAME(c, a);
	LEAVE_IF(b == NULL, "uninitialized integer.");

	status_t result = ELEMENT_OK;
	LEAVE_IF( c->type != type, "result initialized but invalid type.");

	switch(type) {
		case ZR: bn_mxp(c->bn, a->bn, b, a->order);
				 break;
		case G1: g1_mul(c->g1, a->g1, b);
				 break;
		case G2: g2_mul(c->g2, a->g2, b);
				 break;
		case GT: gt_exp(c->gt, a->gt, b);
				 break;
		default:
				 result = ELEMENT_INVALID_TYPES;
				 break;
	}

	return result;

}

int element_cmp(element_t a, element_t b)
{
	GroupType type = a->type;
	LEAVE_IF(a->isInitialized != TRUE || b->isInitialized != TRUE, "uninitialized argument.");
	EXIT_IF_NOT_SAME(a, b);

	switch(type) {
		case ZR: return bn_cmp(a->bn, b->bn);
		case G1: return g1_cmp(a->g1, b->g1);
		case G2: return g2_cmp(a->g2, b->g2);
		case GT: return gt_cmp(a->gt, b->gt);
		default: break;
	}

	return ELEMENT_INVALID_TYPES;
}

// e = a
status_t element_set(element_t e, element_t a)
{
	GroupType type = a->type;
	LEAVE_IF(e->isInitialized != TRUE || a->isInitialized != TRUE, "uninitialized argument.");
	EXIT_IF_NOT_SAME(e, a);
	status_t result = ELEMENT_OK;

	switch(type) {
		case ZR: bn_copy(e->bn, a->bn);
				 break;
		case G1: g1_copy(e->g1, a->g1);
				 break;
		case G2: g2_copy(e->g2, a->g2);
				 break;
		case GT: gt_copy(e->gt, a->gt);
				 break;
		default:
				 result = ELEMENT_INVALID_TYPES;
				 break;
	}

	return result;
}

// copy x into e
status_t element_set_int(element_t e, integer_t x)
{
	LEAVE_IF(e->isInitialized != TRUE, "uninitialized argument.");
	if(e->type == ZR) {
		bn_copy(e->bn, x);
		return ELEMENT_OK;
	}

	return ELEMENT_INVALID_TYPES;
}

// x = e (copies for ZR, maps x-coordinate for G1, and not defined for G2 or GT)
status_t element_to_int(integer_t x, element_t e)
{
	LEAVE_IF(x == NULL || e->isInitialized != TRUE, "uninitialized argument.");

	if(e->type == ZR) {
		bn_copy(x, e->bn);
	}
	else if(e->type == G1) {
		fp_prime_back(x, e->g1->x);
	}
	else {
		return ELEMENT_INVALID_TYPES;
	}

	return ELEMENT_OK;
}

status_t element_set_si(element_t e, unsigned int x)
{
	LEAVE_IF(e->isInitialized != TRUE, "uninitialized argument.");
	if(e->type == ZR) {
		bn_set_dig(e->bn, x);
	}

	return ELEMENT_OK;
}

status_t element_from_hash(element_t e, unsigned char *data, int len)
{
	LEAVE_IF(e->isInitialized == FALSE, "uninitialized argument.");
	GroupType type = e->type;
	status_t result = ELEMENT_OK;
	int digest_len = SHA_LEN;
	unsigned char digest[digest_len + 1];
	memset(digest, 0, digest_len);
	SHA_FUNC(digest, data, len);

#ifdef DEBUG
	printf("%s: digest: ", __FUNCTION__);
	print_as_hex(digest, digest_len);
#endif

	switch(type) {
		case ZR: bn_read_bin(e->bn, digest, digest_len);
				 if(bn_cmp(e->bn, e->order) == CMP_GT) bn_mod(e->bn, e->bn, e->order);
				 break;
		case G1: g1_map(e->g1, digest, digest_len);
				 break;
		case G2: g2_map(e->g2, digest, digest_len);
				 break;
		default:
				 result = ELEMENT_INVALID_TYPES;
				 break;
	}

	return result;
}

int element_length(element_t e)
{

   if(e->isInitialized == TRUE) {
	switch(e->type) {
		case ZR: return BN_BYTES + 1; // null bytes included
		case G1: return G1_LEN; // (FP_BYTES * 2) + 2;
		case G2: return G2_LEN; // (FP_BYTES * 4) + 4;
		case GT: return GT_LEN; // (FP_BYTES * 12) + 12;
		default: break;
	}
   }
	return 0;
}

status_t g1_read_bin(g1_t g, uint8_t *data, int data_len)
{
	if(g == NULL) return ELEMENT_UNINITIALIZED;
	fp_read_bin(g->x, data, FP_BYTES);
	fp_read_bin(g->y, &(data[FP_BYTES + 1]), FP_BYTES);
	fp_zero(g->z);
	fp_set_dig(g->z, 1);

	return ELEMENT_OK;
}

status_t g1_write_bin(g1_t g, uint8_t *data, int data_len)
{
	if(g == NULL) return ELEMENT_UNINITIALIZED;
	if(data_len < G1_LEN) return ELEMENT_INVALID_ARG_LEN;
	uint8_t *d = data;
	memset(d, 0, G1_LEN);

	fp_write_bin(d, FP_BYTES, g->x);
	fp_write_bin(&(d[FP_BYTES + 1]), FP_BYTES, g->y);

#ifdef DEBUG
	printf("%s: size for x & y :=> '%d'\n", __FUNCTION__, FP_BYTES);

	uint8_t *d2 = data;
	int i;
	for(i = 0; i < 2; i++) {
		print_as_hex(d2, FP_BYTES+1);
		d2 = &(d2[FP_BYTES + 1]);
	}
#endif

	return ELEMENT_OK;
}

status_t g1_write_str(g1_t g, uint8_t *data, int data_len)
{
	if(g == NULL) return ELEMENT_UNINITIALIZED;
	if(data_len < G1_LEN*2) return ELEMENT_INVALID_ARG_LEN;
	char *d = (char *) data;

	int len = FP_BYTES*2+1;

	fp_write(d, len, g->x, BASE);
	fp_write(&(d[len]), len, g->y, BASE);

	return ELEMENT_OK;
}


status_t g2_read_bin(g2_t g, uint8_t *data, int data_len)
{
	if(g == NULL) return ELEMENT_UNINITIALIZED;
	if(data_len < G2_LEN) return ELEMENT_INVALID_ARG_LEN;

	uint8_t *d = data;
	fp_read_bin(g->x[0], d, FP_BYTES);
	d = &(d[FP_BYTES + 1]);
	fp_read_bin(g->x[1], d, FP_BYTES);
	d = &(d[FP_BYTES + 1]);
	fp_read_bin(g->y[0], d, FP_BYTES);
	d = &(d[FP_BYTES + 1]);
	fp_read_bin(g->y[1], d, FP_BYTES);

	fp_zero(g->z[0]);
	fp_zero(g->z[1]);
	fp_set_dig(g->z[0], 1);

	return ELEMENT_OK;
}

status_t g2_write_bin(g2_t g, uint8_t *data, int data_len)
{
	if(g == NULL) return ELEMENT_UNINITIALIZED;
//	int out_len = (FP_BYTES * 4) + 4;
	if(data_len < G2_LEN) return ELEMENT_INVALID_ARG_LEN;
	uint8_t d[G2_LEN+1];
	memset(d, 0, G2_LEN);

	fp_write_bin(d, FP_BYTES, g->x[0]);
	uint8_t *d1 = &(d[FP_BYTES + 1]);
	fp_write_bin(d1, FP_BYTES, g->x[1]);
	d1 = &(d1[FP_BYTES + 1]);
	fp_write_bin(d1, FP_BYTES, g->y[0]);
	d1 = &(d1[FP_BYTES + 1]);
	fp_write_bin(d1, FP_BYTES, g->y[1]);

	memcpy(data, d, data_len);

#ifdef DEBUG
	printf("%s: size for x & y :=> '%d'\n", __FUNCTION__, FP_BYTES);

	uint8_t *d2 = data;
	int i;
	for(i = 0; i < 4; i++) {
		print_as_hex(d2, FP_BYTES+1);
		d2 = &(d2[FP_BYTES + 1]);
	}
#endif
	memset(d, 0, G2_LEN);
	return ELEMENT_OK;
}

status_t g2_write_str(g2_t g, uint8_t *data, int data_len)
{
	if(g == NULL) return ELEMENT_UNINITIALIZED;
	int G2_STR = G2_LEN*4;
	if(data_len < G2_STR) return ELEMENT_INVALID_ARG_LEN;
	char *d = (char *) data;

	int len = FP_BYTES*2 + 1;
	fp_write(d, len, g->x[0], BASE);
	d += len;
	fp_write(d, len, g->x[1], BASE);
	d += len;
	fp_write(d, len, g->y[0], BASE);
	d += len;
	fp_write(d, len, g->y[1], BASE);

	return ELEMENT_OK;
}


status_t gt_read_bin(gt_t g, uint8_t *data, int data_len)
{
	if(g == NULL) return ELEMENT_UNINITIALIZED;
	if(data_len < GT_LEN) return ELEMENT_INVALID_ARG_LEN;

	uint8_t *d = data;
	fp_read_bin(g[0][0][0], d, FP_BYTES);
	d = &(d[FP_BYTES + 1]);
	fp_read_bin(g[0][0][1], d, FP_BYTES);
	d = &(d[FP_BYTES + 1]);
	fp_read_bin(g[0][1][0], d, FP_BYTES);
	d = &(d[FP_BYTES + 1]);
	fp_read_bin(g[0][1][1], d, FP_BYTES);
	d = &(d[FP_BYTES + 1]);
	fp_read_bin(g[0][2][0], d, FP_BYTES);
	d = &(d[FP_BYTES + 1]);
	fp_read_bin(g[0][2][1], d, FP_BYTES);

	d = &(d[FP_BYTES + 1]);
	fp_read_bin(g[1][0][0], d, FP_BYTES);
	d = &(d[FP_BYTES + 1]);
	fp_read_bin(g[1][0][1], d, FP_BYTES);
	d = &(d[FP_BYTES + 1]);
	fp_read_bin(g[1][1][0], d, FP_BYTES);
	d = &(d[FP_BYTES + 1]);
	fp_read_bin(g[1][1][1], d, FP_BYTES);
	d = &(d[FP_BYTES + 1]);
	fp_read_bin(g[1][2][0], d, FP_BYTES);
	d = &(d[FP_BYTES + 1]);
	fp_read_bin(g[1][2][1], d, FP_BYTES);

//	fp_zero(g->z[0]);
//	fp_zero(g->z[1]);
//	fp_set_dig(g->z[0], 1);

	return ELEMENT_OK;
}

status_t gt_write_bin(gt_t g, uint8_t *data, int data_len)
{
	if(g == NULL) return ELEMENT_UNINITIALIZED;
	if(data_len < GT_LEN) return ELEMENT_INVALID_ARG_LEN;
	uint8_t d[GT_LEN+1];
	uint8_t *d1 = NULL;
	memset(d, 0, GT_LEN);

#ifdef DEBUG
	printf("%s: size for x & y :=> '%d'\n", __FUNCTION__, FP_BYTES);
#endif
	// write the x-coordinate
	fp_write_bin(d, FP_BYTES, g[0][0][0]);
	d1 = &(d[FP_BYTES + 1]);
	fp_write_bin(d1, FP_BYTES, g[0][0][1]);
	d1 = &(d1[FP_BYTES + 1]);
	fp_write_bin(d1, FP_BYTES, g[0][1][0]);
	d1 = &(d1[FP_BYTES + 1]);
	fp_write_bin(d1, FP_BYTES, g[0][1][1]);
	d1 = &(d1[FP_BYTES + 1]);
	fp_write_bin(d1, FP_BYTES, g[0][2][0]);
	d1 = &(d1[FP_BYTES + 1]);
	fp_write_bin(d1, FP_BYTES, g[0][2][1]);
	d1 = &(d1[FP_BYTES + 1]);
	fp_write_bin(d1, FP_BYTES, g[1][0][0]);
	d1 = &(d1[FP_BYTES + 1]);
	fp_write_bin(d1, FP_BYTES, g[1][0][1]);
	d1 = &(d1[FP_BYTES + 1]);
	fp_write_bin(d1, FP_BYTES, g[1][1][0]);
	d1 = &(d1[FP_BYTES + 1]);
	fp_write_bin(d1, FP_BYTES, g[1][1][1]);
	d1 = &(d1[FP_BYTES + 1]);
	fp_write_bin(d1, FP_BYTES, g[1][2][0]);
	d1 = &(d1[FP_BYTES + 1]);
	fp_write_bin(d1, FP_BYTES, g[1][2][1]);

	memcpy(data, d, data_len);

	uint8_t *d2 = data;
	int i;
	for(i = 0; i < 12; i++) {
		print_as_hex(d2, FP_BYTES+1);
		d2 = &(d2[FP_BYTES + 1]);
	}

	memset(d, 0, GT_LEN);
	return ELEMENT_OK;
}

status_t gt_write_str(gt_t g, uint8_t *data, int data_len)
{
	if(g == NULL) return ELEMENT_UNINITIALIZED;
	if(data_len < GT_LEN*3) return ELEMENT_INVALID_ARG_LEN;

	int len = FP_BYTES*2 + 1;
	char *d1 = (char *) data;

	// write the x-coordinate
	fp_write(d1, len, g[0][0][0], BASE);
	d1 += len;
	fp_write(d1, len, g[0][0][1], BASE);
	d1 += len;
	fp_write(d1, len, g[0][1][0], BASE);
	d1 += len;
	fp_write(d1, len, g[0][1][1], BASE);
	d1 += len;
	fp_write(d1, len, g[0][2][0], BASE);
	d1 += len;
	fp_write(d1, len, g[0][2][1], BASE);
	d1 += len;
	fp_write(d1, len, g[1][0][0], BASE);
	d1 += len;
	fp_write(d1, len, g[1][0][1], BASE);
	d1 += len;
	fp_write(d1, len, g[1][1][0], BASE);
	d1 += len;
	fp_write(d1, len, g[1][1][1], BASE);
	d1 += len;
	fp_write(d1, len, g[1][2][0], BASE);
	d1 += len;
	fp_write(d1, len, g[1][2][1], BASE);

	return ELEMENT_OK;
}

status_t element_from_bytes(element_t e, unsigned char *data, int data_len)
{
	LEAVE_IF(e->isInitialized != TRUE, "uninitialized argument.");
	GroupType type = e->type;
	if(type == ZR) {
		bn_read_bin(e->bn, data, data_len);
	}
	else if(type == G1) {
		return g1_read_bin(e->g1, data, data_len); // x & y
	}
	else if(type == G2) {
		return g2_read_bin(e->g2, data, data_len); // x1, y1  & x2, y2
	}
	else if(type == GT) {
		return gt_read_bin(e->gt, data, data_len); // x1-6 && y1-6
	}
	else {
		return ELEMENT_INVALID_TYPES;
	}

	return ELEMENT_OK;
}

status_t element_to_bytes(unsigned char *data, int data_len, element_t e)
{
	LEAVE_IF(e->isInitialized != TRUE, "uninitialized argument.");
	GroupType type = e->type;
	if(type == ZR) {
		bn_write_bin(data, data_len, e->bn);
	}
	else if(type == G1) {
		return g1_write_bin(e->g1, data, data_len); // x & y
	}
	else if(type == G2) {
		return g2_write_bin(e->g2, data, data_len); // x1, y1  & x2, y2
	}
	else if(type == GT) {
		return gt_write_bin(e->gt, data, data_len); // x1-6 && y1-6
	}
	else {
		return ELEMENT_INVALID_TYPES;
	}

	return ELEMENT_OK;
}

status_t element_to_key(element_t e, uint8_t *data, int data_len, uint8_t label)
{
	LEAVE_IF(e->isInitialized != TRUE, "uninitialized argument.");
	// adds an extra null byte by default - will use this last byte for the label
	int d_len = element_length(e), digest_len = SHA_LEN;

	uint8_t d[d_len + 1];
	memset(d, 0, d_len);
	// write e to a tmp buf
	if(d_len > 0 && digest_len <= data_len) {
		element_to_bytes(d, d_len, e);
		d[d_len-1] = label;
#ifdef DEBUG
		printf("%s: bytes form....\n", __FUNCTION__);
		print_as_hex(d, d_len);
#endif
		// hash buf using md_map_sh256 and store data_len bytes in data
		uint8_t digest[digest_len + 1];
		memset(digest, 0, digest_len);
		SHA_FUNC(digest, d, d_len);
		memcpy(data, digest, digest_len);
#ifdef DEBUG
		printf("%s: digest: ", __FUNCTION__);
		print_as_hex(data, digest_len);
#endif
		return ELEMENT_OK;
	}
	return ELEMENT_INVALID_ARG;
}

status_t hash_buffer_to_bytes(uint8_t *input, int input_len, uint8_t *output, int output_len, uint8_t label)
{
	LEAVE_IF(input == NULL || output == NULL, "uninitialized argument.");
	// adds an extra null byte by default - will use this last byte for the label
	int digest_len = SHA_LEN, i;

	if(digest_len <= output_len) {
		// hash buf using md_map_sh256 and store data_len bytes in data
		uint8_t digest[digest_len + 1];
		uint8_t input2[input_len + 2];
		memset(input2, 0, input_len + 1);
		// set prefix
		input2[0] = 0xFF & label;
		// copy remaining bytes
		for(i = 1; i <= input_len; i++)
			input2[i] = input[i];
		memset(digest, 0, digest_len);
		SHA_FUNC(digest, input2, input_len+1);
		memcpy(output, digest, digest_len);
#ifdef DEBUG
		printf("%s: digest: ", __FUNCTION__);
		print_as_hex(output, digest_len);
#endif
		return ELEMENT_OK;
	}
	return ELEMENT_INVALID_ARG;
}

status_t pairing_apply(element_t et, element_t e1, element_t e2)
{
	LEAVE_IF(e1->isInitialized != TRUE || e2->isInitialized != TRUE || et->isInitialized != TRUE, "uninitialized arguments.");
	if(e1->type == G1 && e2->type == G2 && et->type == GT) {
		/* compute optimal ate pairing */
		pp_map_oatep(et->gt, e1->g1, e2->g2);
		return ELEMENT_OK;
	}
	return ELEMENT_INVALID_ARG;
}

int element_is_member(element_t e)
{
	LEAVE_IF(e->isInitialized != TRUE, "uninitialized argument.");
	int result;

	if(e->type == ZR) {
		if(bn_cmp(e->bn, e->order) <= CMP_EQ)
			result = TRUE;
		else
			result = FALSE;
	}
	else if(e->type == G1) {
		g1_t r;
		g1_inits(r);

		g1_mul(r, e->g1, e->order);
		if(g1_is_infty(r) == 1)
			result = TRUE;
		else
			result = FALSE;
		g1_free(r);
	}
	else if(e->type == G2) {
		g2_t r;
		g2_inits(r);

		g2_mul(r, e->g2, e->order);
		if(g2_is_infty(r) == 1)
			result = TRUE;
		else
			result = FALSE;
		g2_free(r);
	}
	else if(e->type == GT) {
		gt_t r;
		gt_inits(r);

		gt_exp(r, e->gt, e->order);
		if(gt_is_unity(r) == 1)
			result = TRUE;
		else
			result = FALSE;
		gt_free(r);
	}
	else {
		result = ELEMENT_INVALID_ARG;
	}

	return result;
}

int get_order(integer_t x)
{
	if(x != NULL) {
		g1_get_ord(x);
		return TRUE;
	}
	return FALSE;
}
