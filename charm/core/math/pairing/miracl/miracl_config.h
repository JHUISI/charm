
/* auto-generated configuration */
//#define BUILD_MNT_CURVE  0
//#define BUILD_BN_CURVE   0
#define PAD_SIZE		 2 // 2 bytes for zero padding on deserialization

#if BUILD_MNT_CURVE == 1
// k=6 MNT curve
#define MR_PAIRING_MNT
#define ASYMMETRIC		1
#define AES_SECURITY 	80 // for MNT-160
#define BIG_SIZE		20
#define MAX_LEN    		BIG_SIZE + PAD_SIZE // 20 bytes necessary for representation of ints

#include "pairing_3.h"

#elif BUILD_BN_CURVE == 1

#define MR_PAIRING_BN
#define ASYMMETRIC		1
#define AES_SECURITY 	128 // for BN-256
#define BIG_SIZE		32
#define MAX_LEN			BIG_SIZE + PAD_SIZE // 32 bytes necessary, 2 for zero padding on deserialization

#include "pairing_3.h"

#elif BUILD_SS_CURVE == 1
// super-singular curve over GF(P) where k=2 (large prime)
#define MR_PAIRING_SSP
#define ASYMMETRIC		0
#define AES_SECURITY	80 // for SS512, 128 for SS1536
#define BIG_SIZE		64
#define MAX_LEN			BIG_SIZE + PAD_SIZE // 64 bytes necessary, 2 for zero padding on deserialization
#include "pairing_1.h"

#endif

