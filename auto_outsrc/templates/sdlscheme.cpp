#include "sdlconfig.h"
#include <iostream>
#include <sstream>
#include <string>
using namespace std;

int main()
{
	PairingGroup group(AES_SECURITY);

	ZR c;
	group.random(c);
	cout << "ZR : c := " << c << endl;

	G1 g1;
	group.random(g1);
	cout << "G1 :=> " << convert_str(g1) << endl;

	G2 g2;
	group.random(g2);
	cout << "G2 element => " << convert_str(g2) << endl;

	G2 h2 = group.mul(g2, g2);
	cout << "G2 added to itself " << convert_str(h2) << endl;

	h2 = group.div(h2, g2);
	cout << "h2 =?= g2 => " << convert_str(h2) << endl;

	G2 c2 = group.exp(h2, c);
	cout << "G2 c2 := h2 ^ c => " << convert_str(c2) << endl;

	GT gt = group.pair(g1, g2);
	cout << "Pairing test " << convert_str(gt) << endl;

	string str1 = "hello world my name is....";

	CharmList s;
	s.append(str1);
	s.append(c);
	s.append(g1);
	s.append(g2);
	s.append(gt);

	cout << "\nPrint list so far...\n";
	cout << s << endl;

	// how to hash elements
	ZR zr2 = group.hashListToZR(s);
	G1 h1  = group.hashListToG1(s);
	G2 h3  = group.hashListToG2(s);
	cout << "ZR zr2 := " << zr2 << endl;
	cout << "G1 h1  := " << convert_str(h1) << endl;
	cout << "G2 h3  := " << convert_str(h3) << endl;

	string str2 = "hello world!!!";
	s[0] = Element(str2);

	cout << s << endl;

	cout << s[3] << endl;

//	cout << "Serialize/Deserialize tests..." << endl;
//	string serObj = Element::serialize(s[1]);
//	cout << serObj << endl;
//
//	cout << "Deserialized : " << Element::deserialize(serObj) << endl;

	cout << "CharmDict tests...." << endl << endl;
	CharmDict d;

	Element elem("hello this is another message");
	d.set("100", elem);
	d.set("102", s[1]);
	d.set("103", s[2]);

	cout << d << endl;
//
//	// vector<string>
//	CharmList s3 = d.keys();
//	for(int i = 0; i < s3.length(); i++)
//		cout << "Keys: " << s3[i] << endl;

	cout << "Test 1: " << d["100"] << endl;
	cout << "Test 2: " << convert_str(d["103"].getG1()) << endl;

	return 0;
}
