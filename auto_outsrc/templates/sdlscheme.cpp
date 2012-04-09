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
	cout << "ZR : c := " << c << endl;

	G1 g1;
	group.random(g1);
	cout << "G1 :=> " << str(g1) << endl;

	G2 g2;
	group.random(g2);
	cout << "G2 element => " << str(g2) << endl;

	G2 h2 = group.mul(g2, g2);
	cout << "G2 added to itself " << str(h2) << endl;

	h2 = group.div(h2, g2);
	cout << "h2 =?= g2 => " << str(h2) << endl;

	G2 c2 = group.exp(h2, c);
	cout << "G2 c2 := h2 ^ c => " << str(c2) << endl;

	cout << "Pairing test " << str( group.pair(g1, g2) ) << endl;

	CharmList s(1);

	cout << "\n\nPrint list..." << endl;
	s.append(string("hello world my name is this."));
	s.append(c);
	s.append(g1);
	s.append(g2);


	s.print();

	return 0;
}
