#include "sdlconfig.h"
#include <iostream>
#include <sstream>
#include <string>
using namespace std;

ZR SmallExp(int bits) {
	big t = mirvar(0);
	bigbits(bits, t);
    ZR zr(t);
    mr_free(t);
	return zr;
}


void keygen(PairingGroup & group, G2 & pk, ZR & sk, G2 & g) {
    ZR *x = new ZR();
    
    g = group.random(G2_t);
    *x = group.random(ZR_t);
    pk = group.exp(g, *x); // make sure group operations return dynamic memory
    sk = *x;
     
    return;
}

void sign(PairingGroup & group, ZR & sk, string M, G1 & sig) 
{
    G1 h = group.hashListToG1(M);
    sig = group.exp(h, sk); 

    return;
}

void verify(PairingGroup & group, G2 & pk, G2 & g, G1 & sig, string M, bool & output) {
   G1 h = group.hashListToG1(M);
   if(group.pair(sig, g) == group.pair(h, pk)) {
      cout << "Successful Verification" << endl;
      output = true;
   }
   else {
      output = false;
   }
}

CharmListZR testRetByValueZR(CharmListZR & s)
{
	CharmListZR x(s);

	return x;
}

CharmListG1 testRetByValueG1(CharmListG1 & s)
{
	CharmListG1 x(s);
	return x;
}

CharmListG2 testRetByValueG2(CharmListG2 & s)
{
	CharmListG2 x(s);
	return x;
}

CharmListGT testRetByValueGT(CharmListGT & s)
{
	CharmListGT x(s);
	return x;
}


int main()
{
	// example for using CharmList* data structures
    PairingGroup group(AES_SECURITY);

    int N = 2;
    CharmListZR sk0;
    CharmListG1 g1_0;
    CharmListG2 g2_0;
    CharmListGT gt_0;


    for(int z = 0; z < N; z++) {
    	sk0[z] = SmallExp(80);
    }

    cout << "list of deltas: " << endl;
    cout << sk0 << endl;

    CharmListZR sk1 = testRetByValueZR(sk0);

    cout << "new list of deltas: " << endl;
    cout << sk1 << endl;

    // test CharmListG1 ****************************** //
    for(int z = 0; z < N; z++) {
    	g1_0[z] = group.random(G1_t);
    }

    cout << "list of G1: " << endl;
    cout << g1_0 << endl;

    CharmListG1 g1_1 = testRetByValueG1(g1_0);
    cout << "new list of G1: " << endl;
    cout << g1_1 << endl;


    // test CharmListG2 ****************************** //
    for(int z = 0; z < N; z++) {
    	g2_0[z] = group.random(G2_t);
    }

    cout << "list of G2: " << endl;
    cout << g2_0 << endl;

    CharmListG2 g2_1 = testRetByValueG2(g2_0);
    cout << "new list of G2: " << endl;
    cout << g2_1 << endl;


    // test CharmListGT ****************************** //
    for(int z = 0; z < N; z++) {
    	gt_0[z] = group.random(GT_t);
    }

    cout << "list of GT: " << endl;
    cout << gt_0 << endl;

    CharmListGT gt_1 = testRetByValueGT(gt_0);
    cout << "new list of GT: " << endl;
    cout << gt_1 << endl;


    return 0;
}
