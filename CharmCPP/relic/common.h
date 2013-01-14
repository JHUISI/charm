#ifndef COMMON_H
#define COMMON_H

#include "relic_conf.h"
#include "relic/relic.h"

#define DECIMAL 10
#define BASE	16
#define MAX_BUF	1024
#define SHA_LEN  	32
#define SHA_FUNC	md_map_sh256
#define HASH_FUNCTION_STRINGS			"0"
#define HASH_FUNCTION_STR_TO_Zr_CRH		"1"
#define HASH_FUNCTION_Zr_TO_G1_ROM		"2"
#define HASH_FUNCTION_Zr_TO_G2_ROM		"3"

typedef enum _status_t { ELEMENT_OK = 2,
	   ELEMENT_INVALID_ARG,
	   ELEMENT_INVALID_ARG_LEN,
	   ELEMENT_INVALID_TYPES,
	   ELEMENT_INVALID_RESULT,
	   ELEMENT_PAIRING_INIT_FAILED,
	   ELEMENT_UNINITIALIZED,
	   ELEMENT_DIV_ZERO,
} status_t;

enum ZR_type { ZR_t = 0, listZR_t = 1 };
enum G1_type { G1_t = 2, listG1_t = 3 };
enum G2_type { G2_t = 4, listG2_t = 5 };
enum GT_type { GT_t = 6, listGT_t = 7 };
enum Other_type { Str_t = 8, listStr_t = 9, list_t = 10, None_t = 11 };

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

#define FP_STR FP_BYTES * 2 + 1
#define G1_LEN (FP_BYTES * 2) + 2
#if defined(EP_KBLTZ) && FP_PRIME == 256
/* BN_P256 */
#define G2_LEN (FP_BYTES * 4) + 4
#define GT_LEN (FP_BYTES * 12) + 12
#elif defined(EP_KBLTZ) && FP_PRIME == 508
/* KSS_P508 */
#define G2_LEN G1_LEN
#define GT_LEN G1_LEN
#endif

status_t g1_read_bin(g1_t g, uint8_t *data, int data_len);
status_t g1_write_bin(g1_t g, uint8_t *data, int data_len);
status_t g1_write_str(g1_t g, uint8_t *data, int data_len);

status_t g2_read_bin(g2_t g, uint8_t *data, int data_len);
status_t g2_write_bin(g2_t g, uint8_t *data, int data_len);
status_t g2_write_str(g2_t g, uint8_t *data, int data_len);

status_t gt_read_bin(gt_t g, uint8_t *data, int data_len);
status_t gt_write_bin(gt_t g, uint8_t *data, int data_len);
status_t gt_write_str(gt_t g, uint8_t *data, int data_len);
int compute_length(int type);

#endif
