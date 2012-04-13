#include "sdlconfig.h"
#include <iostream>
#include <sstream>
#include <string>
using namespace std;

int main()
{
	PairingGroup group(AES_SECURITY);

	GT gt1, gt2;
	group.random(gt1);
	group.random(gt2);
	cout << "GT random 1 :=> " << convert_str(gt1) << endl;
	cout << "GT random 2 :=> " << convert_str(gt2) << endl;

	cout << endl << endl << endl;
	string a_str = "hello world!";
	string d_str = "0:MjA6CIstIwcCehomqrSKPPs0Otew830="; // serialized element from Charm
			// "2:MjA6Qqfj17s9Bxt0yS6CIz1VN4NzkHsyMDqd9jTKvmMnR7Va/SORAMDU0QPKHDIwOq0SKwqF/URSqlezeqcsa8iPWuv1MjA6d1YBErAg2NQ7IxAxHqofFkAbfTkyMDpC+dAMjK+Xvlx4xisj5b5leBjAyzIwOm5GeaPurBZFi5c9mNPLfPb+MaEf";
			// "1:MjA6DOrerG4SkBuqW73/IDSVHRsN+gUyMDpsNNOfurZNeaJlNb5E4ATJAxfnMA==";

	CharmList s;
	s.append(a_str);

	ZR zr2 = group.hashListToZR(s);
	G1 g1  = group.hashListToG1(s);
	G2 g2  = group.hashListToG2(s);
	cout << "hash str to ZR := " << zr2 << endl;
	cout << "hash str to G1 := " << convert_str(g1) << endl;
	cout << "hash str to G2 := " << convert_str(g2) << endl;

	Element elem(zr2);
	string zr2_str = Element::serialize(elem);
	cout << "a serialized := '" << zr2_str << "'" << endl;

	if(strcmp(d_str.c_str(), zr2_str.c_str()) == 0) {
		cout << "Serialization test passed!" << endl;
	}
	else {
		cout << "Serialization test FAILED!!!!!" << endl;
	}

	Element elem2;
	Element::deserialize(elem2, d_str);

	cout << "s2 := " << elem2 << endl;
	Element elem3 = elem2;
	cout << "s3 := " << elem3 << endl;

	return 0;
}
