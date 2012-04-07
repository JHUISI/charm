#include <iostream>
#include <ctime>
#include <map>
#include <sstream>
// #define MR_PAIRING_MNT	// AES-80 security
// #define AES_SECURITY 80
#define MR_PAIRING_KSS
#define AES_SECURITY 192
#include "pairing_3.h"

// mnt_pair.cpp, cp_pair.cpp, bn_pair.cpp, ssp_pair.cpp, ss2_pair.cpp, kss_pair.cpp


int N = 1;
#define HASH(x, str) group.hash_and_map(x, (char *) string(str).c_str())
#define Group PFC
#define SmallExp(x, a)	\
	x = mirvar(0); \
	bigbits(AES_SECURITY, x); \
	a = Big(x);

#define pair(a, b) group.pairing(b, a)
#define group_mul(a, b) a = a + b
#define group_exp(c, a, b) c.g = b * a.g

using namespace std;

int main() // M :=> array, sig :=> array, pk :=> array
{
	time_t seed;
	Group group(AES_SECURITY);  // initialise pairing-friendly curve
	miracl *mip=get_mip();  // get handle on mip (Miracl Instance Pointer)
	mip->IOBASE = 10;
	/* must happen after declaring PFC object */
	time(&seed);
    irand((long)seed);

	map<int, string> M;
	map<int, G1> sig;
	M[0] = "hello hello worlds!!!";
	M[1] = "hello hello worlds!!! fail!";

    // generate pub/priv keys, signature, etc
    G2 pk,g;
    Big sk;
    group.random(g);
    group.random(sk); // secret
    pk.g = sk * g.g;
    G1 tmp;
    HASH(tmp, M[0]);
    sig[0].g = sk * tmp.g; // H(M)^sk

//	int incorrectIndices[] = new int[N];
	Big delta[N];
	big t;

	for(int z = 0; z < N; z++) {
		SmallExp(t, delta[z]);
//		cout << "delta[" << z << "] = " << delta[z] << endl;
	}

	// group membership test on inputs
	G1 dotA[N], dotB[N], h;
	G1 dotA_result, dotB_result;

	for(int z = 0; z < N; z++) {
		HASH(h, M[z]);
		cout << "h :=" << h.g << endl;
		cout << "sig :=" << sig[z].g << endl;
		group_exp(dotA[z], h, delta[z]);
		group_exp(dotB[z], sig[z], delta[z]);

		group_mul(dotA_result, dotA[z]);
		group_mul(dotB_result, dotB[z]);
	}

	// call recursive algorithm here : pub.get('g'), pub.get('pk')
	if( pair(dotA_result, pk) == pair(dotB_result, g) )
		cout << "KSS: Signature verified in batch!" << endl;
	else
		cout << "Signature failed!! :-(" << endl;
}
