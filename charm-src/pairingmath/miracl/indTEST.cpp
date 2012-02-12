#include <iostream>
#include <ctime>
#include <map>
#include <sstream>
#define MR_PAIRING_MNT
#define AES_SECURITY 80
#include "pairing_3.h"

int N = 2;
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

int main()
{
	time_t seed;
	Group group(AES_SECURITY);
	miracl *mip=get_mip();
	mip->IOBASE = 10;
	time(&seed);
	irand((long)seed);

	G1 h;

	map<int, string> message;
	map<int, G1> sig;
	message[0] = "hello hello worlds!!!";
	message[1] = "hello hello worlds!!! fail!";

	const char * g_key = "g";

	map<int, map<string, G2> > pk;
	group.random(pk[0][g_key]);
	group.random(pk[1]["g"]);

	map<int, Big> sk;
	group.random(sk[0]);
	group.random(sk[1]);

	pk[0]["g^x"].g = sk[0] * pk[0]["g"].g;
	pk[1]["g^x"].g = sk[1] * pk[1]["g"].g;

	G1 tmp;
	HASH(tmp, message[0]);
	sig[0].g = sk * tmp.g;

	HASH(tmp, message[1]);
	sig[1].g = sk * tmp.g;

	for (int z = 0; z < N; z++)
	{
		M = message[z];
		HASH(h, M);
		if pair ( sig[z] , pk[z] [ "g" ] ) == pair ( h , pk[z] [ "g^x" ] ) 
		{
			cout << "Signature verified!" << endl;
		}
		else
		{
			cout << "Signature failed!" << endl;
		}
	}
}
