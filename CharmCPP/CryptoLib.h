#ifndef CRYPTOLIB_H
#define CRYPTOLIB_H

#define MAX_LIST 	10000

#if BUILD_RELIC == 1
#define ASYMMETRIC	1 // meaningless for RELIC
#include "relic_api.h"

#elif BUILD_MIRACL == 1

#define PAD_SIZE		 2 // 2 bytes for zero padding on deserialization

#if BUILD_MNT_CURVE == 1
// k=6 MNT curve
#define MR_PAIRING_MNT
#define ASYMMETRIC		1
#define AES_SECURITY 	80 // for MNT-160
#define BIG_SIZE		20
#define MAX_LEN    		BIG_SIZE + PAD_SIZE // 20 bytes necessary for representation of ints
#include "miracl/pairing_3.h"

#elif BUILD_BN_CURVE == 1

#define MR_PAIRING_BN
#define ASYMMETRIC		1
#define AES_SECURITY 	128 // for BN-256
#define BIG_SIZE		32
#define MAX_LEN			BIG_SIZE + PAD_SIZE // 32 bytes necessary, 2 for zero padding on deserialization
#include "miracl/pairing_3.h"

#elif BUILD_SS_CURVE == 1
// super-singular curve over GF(P) where k=2 (large prime)
#define MR_PAIRING_SSP
#define ASYMMETRIC		0
#define AES_SECURITY	80 // 80 for SS512, 128 for SS1536 (BIG_SIZE 96)
#define BIG_SIZE		64
#define MAX_LEN			BIG_SIZE + PAD_SIZE // 64 bytes necessary, 2 for zero padding on deserialization
#include "miracl/pairing_1.h"
/* create symlink to ease user code.
 * G2 really maps to G1.
 */
#define G2  			G1
#define G2_t			G1_t
#define hashListToG2	hashListToG1
#endif

#define ZR Big

#include <map>
#include <vector>
#include <string>
#include <sstream>
#include <iostream>
#include <fstream>
#include <math.h>
extern "C" {
#include "common.h"
}
#define convert_str(point) point.g

#endif

#endif
