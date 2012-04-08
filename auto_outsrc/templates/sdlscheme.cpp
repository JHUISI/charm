#include <iostream>
#include <ctime>
#include <map>
#include <sstream>
#include "sdlconfig.h"

using namespace std;

int main()
{
	PairingGroup group(AES_SECURITY);

	ZR c;
	group.random(c);
	cout << "ZR => " << c << endl;
	cout << "Hello World! It worked!!!" << endl;

	G1 g1;
	group.random(g1);
	cout << "G1 element => " << str(g1) << endl;

	G2 g2;
	group.random(g2);
	cout << "G2 element => " << str(g2) << endl;

	G2 h2 = group.mul(g2, g2);
	cout << "G2 added to itself " << str(h2) << endl;

	cout << "Pairing test " << str( group.pair(g1, g2) ) << endl;

	return 0;
}
