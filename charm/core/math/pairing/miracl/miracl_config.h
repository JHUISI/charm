
/* auto-generated configuration */
#define BUILD_MNT_CURVE  0
#define BUILD_BN_CURVE	 1

#if BUILD_MNT_CURVE == 1
// k=6 MNT curve
#define MR_PAIRING_MNT
#define AES_SECURITY 80

#elif BUILD_BN_CURVE == 1

#define MR_PAIRING_BN
#define AES_SECURITY 128
#endif

#include "pairing_3.h"
