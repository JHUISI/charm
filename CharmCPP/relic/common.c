#include "common.h"

int compute_length(int type)
{
	switch(type) {
		case ZR_t: return BN_BYTES + 1; // null bytes included
		case G1_t: return G1_LEN; // (FP_BYTES * 2) + 2;
		case G2_t: return G2_LEN; // (FP_BYTES * 4) + 4;
		case GT_t: return GT_LEN; // (FP_BYTES * 12) + 12;
		default: break;
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
#if defined(EP_KBLTZ) && FP_PRIME == 256
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
#else
	return g1_read_bin(g, data, data_len);
//	return ELEMENT_INVALID_RESULT;
#endif
}

status_t g2_write_bin(g2_t g, uint8_t *data, int data_len)
{
#if defined(EP_KBLTZ) && FP_PRIME == 256
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
#else
	return g1_write_bin(g, data, data_len);
//	return ELEMENT_INVALID_RESULT;
#endif
}

status_t g2_write_str(g2_t g, uint8_t *data, int data_len)
{
#if defined(EP_KBLTZ) && FP_PRIME == 256
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
#else
	return g1_write_str(g, data, data_len);
//	return ELEMENT_INVALID_RESULT;
#endif
}


status_t gt_read_bin(gt_t g, uint8_t *data, int data_len)
{
#if defined(EP_KBLTZ) && FP_PRIME == 256
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
#else
	return g1_read_bin(g, data, data_len);
//	return ELEMENT_INVALID_RESULT;
#endif
}

status_t gt_write_bin(gt_t g, uint8_t *data, int data_len)
{
#if defined(EP_KBLTZ) && FP_PRIME == 256
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

#ifdef DEBUG
	uint8_t *d2 = data;
	int i;
	for(i = 0; i < 12; i++) {
		print_as_hex(d2, FP_BYTES+1);
		d2 = &(d2[FP_BYTES + 1]);
	}
#endif
	memset(d, 0, GT_LEN);
	return ELEMENT_OK;
#else
	return g1_write_bin(g, data, data_len);
//	return ELEMENT_INVALID_RESULT;
#endif
}

status_t gt_write_str(gt_t g, uint8_t *data, int data_len)
{
#if defined(EP_KBLTZ) && FP_PRIME == 256
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
#else
	return g1_write_str(g, data, data_len);
//	return ELEMENT_INVALID_RESULT;
#endif
}

status_t hash_buffer_to_bytes(uint8_t *input, int input_len, uint8_t *output, int output_len, uint8_t label)
{
	//LEAVE_IF(input == NULL || output == NULL, "uninitialized argument.");
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
			input2[i] = input[i-1];
#ifdef DEBUG
		printf("%s: original input: ", __FUNCTION__);
		print_as_hex(input, input_len);

		printf("%s: new input: ", __FUNCTION__);
		print_as_hex(input2, input_len + 1);
#endif
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
