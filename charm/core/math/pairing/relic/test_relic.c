#include <stdio.h>
#include <sys/time.h>
#include "relic_interface.h"

/* prime curves */
#define DEBUG		1
#define TRIALS		1
#define HEX		16

//void printf_as_hex(unsigned char *buf, size_t len)
//{
//    size_t i;
//    for(i = 0; i < len; i += 4)
//    	printf("%02X%02X%02X%02X ", buf[i], buf[i+1], buf[i+2], buf[i+3]);
//    printf("\n");
//}

//double calc_usecs(bench_t *start, bench_t *stop) {
//	double usec_per_second = 1000000; // 1 000 000
//	double result = usec_per_second * (stop->tv_sec - start->tv_sec);
//
//	if(stop->tv_usec >= stop->tv_usec) {
//		result += (stop->tv_usec - start->tv_usec);
//	}
//	else {
//		result -= (start->tv_usec - stop->tv_usec);
//	}
//
//	return result / usec_per_second;
//}

/*
double calc_msecs(bench_t *start, bench_t *stop) {
	double msec_per_second = 1000; // 1 000 000
	double usec_per_second = 1000000; // 1 000 000
	double result1 = start->tv_sec + (start->tv_usec / usec_per_second);
	double result2 = stop->tv_sec + (stop->tv_usec / usec_per_second);
	return (result2 - result1) * msec_per_second;
}
*/

int main(int argc, char *argv[])
{
	status_t result;
	result = pairing_init();

	if(result == ELEMENT_OK)
		printf("pairing init: SUCCESS.\n");
	else
		printf("pairing init: FAILED!\n");


	element_ptr e0 = (element_ptr) malloc(sizeof(element_t));
	element_t e; // , e1, e2, e3;

	/* Start ZR init & operations */
	element_init_Zr(e, 0);
	element_init_Zr(e0, 1234567890);

	element_random(e);

	element_printf("e  -> ZR :=> ", e);
	element_printf("e0 -> ZR :=> ", e0);

	element_add(e, e, e0);
	element_printf("Add ZR :=> ", e);
	element_sub(e0, e, e0);
	element_printf("Sub ZR :=> ", e);

	element_clear(e);
	element_clear(e0);

	/* End of ZR operations */


	element_t g1_0, g1_1, g1_2, g2_1, g2_2, g2_nil, gt_1, gt_2;
	/* Start G1 init & operations */
	element_init_G1(g1_0);
	element_printf("Identity G1 :=> \n", g1_0);
	element_init_G1(g1_1);
	element_init_G1(g1_2);
	element_init_G2(g2_1);
	element_init_G2(g2_2);
	element_init_G2(g2_nil);
	element_init_GT(gt_1);
	element_init_GT(gt_2);
	element_init_Zr(e0, 0);

//	element_random(g1_0);
//	element_random(g1_1);
//
//	element_add(g1_2, g1_0, g1_1);
//	element_printf("Add G1 :=> \n", g1_2);
//
//	element_sub(g1_2, g1_2, g1_0);
//	element_printf("Sub G1 :=> \n", g1_2);
//
//
	unsigned char *msg = "hello world!";
	element_from_hash(e0, msg, strlen((char *) msg));
	element_from_hash(g1_2, msg, strlen((char *) msg));
	element_from_hash(g2_2, msg, strlen((char *) msg));

	element_printf("Hash into e0 :=> \n", e0);
	element_printf("Hash into g1 :=> \n", g1_2);
	element_printf("Hash into g2 :=> \n", g2_2);

	printf("cmp elements ok! :=> '%d'\n", element_cmp(g1_2, g1_2));
	printf("cmp elements fail:=> '%d'\n", element_cmp(g1_1, g1_2));

	int d_len = element_length(g1_1);
	if(d_len > 0) {
		printf("%s: g1 d_len :=> '%d'\n", __FUNCTION__, d_len);
		uint8_t data[d_len + 1];
		element_to_bytes(data, d_len, g1_1);

		element_from_bytes(g1_2, data, d_len);
		element_printf("rec g1 :=> \n", g1_2);
		printf("cmp elements after deserialize :=> '%d'\n", element_cmp(g1_1, g1_2));
	}

	d_len = element_length(g2_2);
	if(d_len > 0) {
		element_printf("g2 write bin :=> \n", g2_2);
		printf("%s: g2 d_len :=> '%d'\n", __FUNCTION__, d_len);
		uint8_t data[d_len + 1];
		element_to_bytes(data, d_len, g2_2);

		element_from_bytes(g2_1, data, d_len);
		element_printf("Rec g2 :=> \n", g2_1);
		printf("cmp elements after deserialize :=> '%d'\n", element_cmp(g2_1, g2_2));

	}

	element_random(gt_1);
	d_len = element_length(gt_1);
	if(d_len > 0) {
		element_printf("gt print :=> \n", gt_1);
		printf("%s: g2 d_len :=> '%d'\n", __FUNCTION__, d_len);
		uint8_t data[d_len + 1];
		element_to_bytes(data, d_len, gt_1);

		element_from_bytes(gt_2, data, d_len);

		element_printf("Rec gt :=> \n", gt_2);
		printf("cmp elements after deserialize :=> '%d'\n", element_cmp(gt_1, gt_2));

	}

	element_pairing(gt_1, g1_1, g2_1);
	element_printf("Pairing result :=> \n", gt_1);

	element_printf("g2 :=> \n", g2_nil);
	element_pairing(gt_2, g1_1, g2_nil);
	element_printf("Pairing result :=> \n", gt_2);

	element_clear(e0);
	element_clear(g1_0);
	element_clear(g1_1);
	element_clear(g1_2);
	element_clear(g2_1);
	element_clear(g2_2);
	element_clear(g2_nil);
	element_clear(gt_1);
	element_clear(gt_2);
	/* End of G1 operations */

	pairing_clear();
	return 0;
}

