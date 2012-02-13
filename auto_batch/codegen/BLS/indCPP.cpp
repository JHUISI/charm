#include "verCPP.h"

int N = 2;

#define HASH(x, str) group.hash_and_map(x, (char *) string(str).c_str())
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
	string M;
	map<int, map<string, G2> > pk;

	for (int z = 0; z < N; z++)
	{
		M = message[z];
		HASH(h, M);
		if (pair ( sig[z] , pk[z] [ "g" ] ) == pair ( h , pk[z] [ "g^x" ] ) )
		{
			cout << "Signature verified!" << endl;
		}
		else
		{
			cout << "Signature failed!" << endl;
		}
	}

	return 0;
}
