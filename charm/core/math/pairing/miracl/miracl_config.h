
/* auto-generated configuration */
#define BUILD_MNT_CURVE  0
#define BUILD_BN_CURVE	 1
#define PAD_SIZE		 2 // 2 bytes for zero padding on deserialization

#if BUILD_MNT_CURVE == 1
// k=6 MNT curve
#define MR_PAIRING_MNT
#define AES_SECURITY 	80 // for MNT-160
#define BIG_SIZE		20
#define MAX_LEN    		BIG_SIZE + PAD_SIZE // 20 bytes necessary for representation of ints

#elif BUILD_BN_CURVE == 1

#define MR_PAIRING_BN
#define AES_SECURITY 	128 // for BN-256
#define BIG_SIZE		32
#define MAX_LEN			BIG_SIZE + PAD_SIZE // 32 bytes necessary, 2 for zero padding on deserialization

#endif

#include "pairing_3.h"
