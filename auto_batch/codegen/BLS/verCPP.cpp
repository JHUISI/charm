#include "verCPP.h"

#define HASH(x, str) group.hash_and_map(x, (char *) string(str).c_str())
#define SmallExp(x, a)	\
	x = mirvar(0); \
	bigbits(AES_SECURITY, x); \
	a = Big(x);

#define pair(a, b) group.pairing(b, a)
#define group_mul(a, b) a = a + b
#define group_exp(c, a, b) c.g = b * a.g

using namespace std;

void verifySigsRecursive(map<int, map<string, G2> > pk, map<int, G1> sig, map<int, string> message, Group group, int startSigNum, int endSigNum, Big delta[], G1 dotA[], G1 dotB[])
{
	int z = 0;


	G1 dotA_loopVal;
	G1 dotB_loopVal;



	for (int index = startSigNum; index < endSigNum; index++){
		group_mul(dotA_loopVal, dotA[index]);
		group_mul(dotB_loopVal, dotB[index]);
	}


	if (  	pair( dotA_loopVal , pk [ z ]  [ "g^x" ] )== pair( dotB_loopVal , pk [ z ]  [ "g" ] )   )
		cout << "Signature batch is valid" << endl;
	else{
		int midWay = int( (endSigNum - startSigNum) / 2);
		if (midWay == 0){
			cout << " Invalid signature found:  number " << startSigNum << endl;
			return;}
		int midSigNum = startSigNum + midWay;
		verifySigsRecursive(pk, sig, message, group, startSigNum, midSigNum, delta, dotA, dotB);
		verifySigsRecursive(pk, sig, message, group, midSigNum, endSigNum, delta, dotA, dotB);
	}

}