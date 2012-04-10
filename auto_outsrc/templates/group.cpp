#include "sdlconfig.h"
#include <sstream>

// Element implementation
Element::Element()
{
	type = None_t;
}
Element::Element(string s)
{
	type = Str_t;
	strPtr = new string(s);
}

Element::Element(ZR & z)
{
	type = ZR_t;
	zr   = &z;
}

Element::Element(G1 & g)
{
	type = G1_t;
	g1   = &g;
}

Element::Element(G2 & g)
{
	type = G2_t;
	g2   = &g;
}

Element::Element(GT & g)
{
	type = GT_t;
	gt   = &g;
}

Element::~Element()
{
	type = None_t;
	strPtr = 0;
	zr = 0;
	g1 = 0;
	g2 = 0;
	gt = 0;
}

ostream& operator<<(ostream& s, const Element& e)
{
	Type t = e.type;
	string elem_str = "E: ";
	s << "T: ";
	if(t == Str_t) {
		s << "str_t, " << elem_str << *e.strPtr;
	}
	else if(t == ZR_t) {
		s << "ZR_t, " << elem_str << *e.zr;
	}
	else if(t == G1_t) {
		s << "G1_t, " << elem_str << e.g1->g;
	}
#ifdef ASYMMETRIC
	else if(t == G2_t) {
		s << "G2_t, " << elem_str << e.g2->g;
	}
#endif
	else if(t == GT_t) {
		s << "GT_t, " << elem_str << e.gt->g;
	}

	return s;
}

string Element::serialize(PairingGroup & group, Element e)
{
	// blah
	if(type == str)
}

// CharmList implementation

CharmList::CharmList(void)
{
	// increases as elements are appended
	cur_index = 0;
}

CharmList::~CharmList()
{
	for(int i = 0; i < (int) list.size(); i++)
		list.erase(i);
}

void CharmList::append(string strs)
{
	Element elem;

	// init elem here
	elem.type = Str_t;
	elem.strPtr  = &strs;

	list[cur_index] = elem;
	cur_index++;
}

void CharmList::append(ZR & zr)
{
	Element elem(zr);
	list[cur_index] = elem;
	cur_index++;
}

void CharmList::append(G1 & g1)
{
	Element elem(g1);
	list[cur_index] = elem;
	cur_index++;
}

#ifdef ASYMMETRIC
void CharmList::append(G2 & g2)
{
	Element elem(g2);

	list[cur_index] = elem;
	cur_index++;
}
#endif

void CharmList::append(GT & gt)
{
	Element elem(gt);

	list[cur_index] = elem;
	cur_index++;
}

Element& CharmList::operator[](const int index)
{
	int len = (int) list.size();
	if(index >= 0 && index < len) {
		return list[index];
	}
	else {
		throw new string("Invalid access.\n");
	}
}

int CharmList::length()
{
	return (int) list.size();
}

ostream& operator<<(ostream& s, const CharmList& cList)
{
	CharmList cList2 = cList;
	for(int i = 0; i < cList2.length(); i++) {
		s << i << ": " << cList2.printAtIndex(i) << endl;
	}

	return s;
}

//void CharmList::print()
//{
//	for(int i = 0; i < cur_index; i++) {
//		Type t = list[i].type;
//		cout << i << ": ";
//		if(t == Str_t) {
//			cout << *list[i].strPtr << endl;
//		}
//		else if(t == ZR_t) {
//			cout << *list[i].zr << endl;
//		}
//		else if(t == G1_t) {
//			cout << list[i].g1->g << endl;
//		}
//#ifdef ASYMMETRIC
//		else if(t == G2_t) {
//			cout << list[i].g2->g << endl;
//		}
//#endif
//		else if(t == GT_t) {
//			cout << list[i].gt->g << endl;
//		}
//		else {
//			cout << "invalid type" << endl;
//		}
//	}
//}

string CharmList::printAtIndex(int index)
{
	stringstream ss;
	int i;

	if(index >= 0 && index < (int) list.size()) {
		i = index;
		Type t = list[i].type;
		if(t == Str_t) {
			ss << *list[i].strPtr;
		}
		else if(t == ZR_t) {
			ss << *list[i].zr;
		}
		else if(t == G1_t) {
			ss << list[i].g1->g;
		}
#ifdef ASYMMETRIC
		else if(t == G2_t) {
			ss << list[i].g2->g;
		}
#endif
		else if(t == GT_t) {
			ss << list[i].gt->g;
		}
	}

	string s = ss.str();
	return s;
}


// defines the PairingGroup class

PairingGroup::PairingGroup(int sec_level)
{
	cout << "Initializing underlying curve." << endl;
	pfcObject = new PFC(sec_level);
	miracl *mip=get_mip();  // get handle on mip (Miracl Instance Pointer)
	mip->IOBASE = 10;

	time_t seed;
	time(&seed);
    irand((long)seed);
}

PairingGroup::~PairingGroup()
{
	delete pfcObject;
}

void PairingGroup::random(Big & b)
{
	pfcObject->random(b);
}

void PairingGroup::random(G1 & g)
{
	pfcObject->random(g);
}

void PairingGroup::random(GT & g)
{
	// retrieve g1 & g2
	// choose rand ZR
}

#ifdef ASYMMETRIC
void PairingGroup::random(G2 & g)
{
	pfcObject->random(g);
}

bool PairingGroup::ismember(G2& g)
{
	return true; // add code to check
}

G2 PairingGroup::mul(G2 & g, G2& h)
{
	G2 l(g + h);
	return l;
}

G2 PairingGroup::div(G2 & g, G2& h)
{
	G2 l(g + -h);
	return l;
}

G2 PairingGroup::exp(G2 & g, ZR & r)
{
	// g ^ r == g * r OR scalar multiplication
	G2 l = pfcObject->mult(g, r);
	return l;
}

GT PairingGroup::pair(G1 & g, G2 & h)
{
	GT gt = pfcObject->pairing(h, g);
	return gt;
}

// G2 PairingGroup::hashListToG2(CharmList & items)
//G2 PairingGroup::hashStringToG2(char *s)
//{
////	for(int i = 0; i < items.length())
//	G2 g2;
//	pfcObject->hash_and_map(g2, s);
//	return g2;
//}
#endif

ZR PairingGroup::order()
{
	return ZR(pfcObject->order());
}

#ifdef SYMMETRIC
GT PairingGroup::pair(G1 & g, G1 & h)
{
	GT gt = pfcObject->pairing(g, h);
	return gt;
}
#endif

// mul for G1 & GT
G1 PairingGroup::mul(G1 & g, G1 & h)
{
	G1 l(g + h);
	return l;
}

GT PairingGroup::mul(GT & g, GT & h)
{
	GT l(g * h);
	return l;
}

// div for G1 & GT
G1 PairingGroup::div(G1 & g, G1 & h)
{
	G1 l(g + -h);
	return l;
}

GT PairingGroup::div(GT & g, GT & h)
{
	GT l(g / h);
	return l;
}

// exp for G1 & GT
G1 PairingGroup::exp(G1 & g, ZR & r)
{
	// g ^ r == g * r OR scalar multiplication
	G1 l = pfcObject->mult(g, r);
	return l;
}

GT PairingGroup::exp(GT & g, ZR & r)
{
	// g ^ r == g * r OR scalar multiplication
	GT l = pfcObject->power(g, r);
	return l;
}

// serialize helper methods for going from Big to bytes and back
string bigToBytes(Big x)
{
	char c[MAX_LEN+1];
	memset(c, 0, MAX_LEN);
	int size = to_binary(x, MAX_LEN, c, FALSE);
	string bytes(c, size);
//	printf("bigToBytes before => ");
//	_printf_buffer_as_hex((uint8_t *) bytes.c_str(), size);
	stringstream ss;
	ss << size << ":" << bytes << "\0";
//	printf("bigToBytes after => ");
//	_printf_buffer_as_hex((uint8_t *) ss.str().c_str(), ss.str().size());
	return ss.str();
}

Big *bytesToBig(string str, int *counter)
{
	int pos = str.find_first_of(':');
	int len = atoi( str.substr(0, pos).c_str() );
	const char *elem = str.substr(pos+1, pos + len).c_str();
//		cout << "pos of elem => " << pos << endl;
//		cout << "elem => " << elem << endl;
//	printf("bytesToBig before => ");
//	_printf_buffer_as_hex((uint8_t *) elem, len);
	Big x = from_binary(len, (char *) elem);
//	cout << "Big => " << x << endl;
	Big *X  = new Big(x);
	*counter  = pos + len + 1;
	return X;
}


ZR PairingGroup::hashListToZR(CharmList & list)
{
	int len = list.length();
	pfcObject->start_hash();
	for(int i = 0; i < len; i++) {
		Element e = list[i];
		if(e.type == Str_t) {
			ZR tmp = pfcObject->hash_to_group( (char *) e.strPtr->c_str());
			pfcObject->add_to_hash(tmp);
		}
		else if(e.type == ZR_t)
			pfcObject->add_to_hash(*e.zr);
		else if(e.type == G1_t)
			pfcObject->add_to_hash(*e.g1);
		else if(e.type == G2_t)
			pfcObject->add_to_hash(*e.g2);
		else if(e.type == GT_t)
			pfcObject->add_to_hash(*e.gt);
	}

	ZR result = pfcObject->finish_hash_to_group();
	return result;
}

G1 PairingGroup::hashListToG1(CharmList & list)
{
	int len = list.length();
	pfcObject->start_hash();
	for(int i = 0; i < len; i++) {
		Element e = list[i];
		if(e.type == Str_t) {
			ZR tmp = pfcObject->hash_to_group( (char *) e.strPtr->c_str());
			pfcObject->add_to_hash(tmp);
		}
		else if(e.type == ZR_t)
			pfcObject->add_to_hash(*e.zr);
		else if(e.type == G1_t)
			pfcObject->add_to_hash(*e.g1);
		else if(e.type == G2_t)
			pfcObject->add_to_hash(*e.g2);
		else if(e.type == GT_t)
			pfcObject->add_to_hash(*e.gt);
	}

	ZR tmp1 = pfcObject->finish_hash_to_group();
	G1 g1;
	// convert result to bytes and hash to G1
	pfcObject->hash_and_map(g1, (char *) bigToBytes(tmp1).c_str());
	return g1;
}

#ifdef ASYMMETRIC
G2 PairingGroup::hashListToG2(CharmList & list)
{
	int len = list.length();
	pfcObject->start_hash();
	for(int i = 0; i < len; i++) {
		Element e = list[i];
		if(e.type == Str_t) {
			ZR tmp = pfcObject->hash_to_group( (char *) e.strPtr->c_str());
			pfcObject->add_to_hash(tmp);
		}
		else if(e.type == ZR_t)
			pfcObject->add_to_hash(*e.zr);
		else if(e.type == G1_t)
			pfcObject->add_to_hash(*e.g1);
		else if(e.type == G2_t)
			pfcObject->add_to_hash(*e.g2);
		else if(e.type == GT_t)
			pfcObject->add_to_hash(*e.gt);
	}

	ZR tmp1 = pfcObject->finish_hash_to_group();
	G2 g2;
	// convert result to bytes and hash to G2
	pfcObject->hash_and_map(g2, (char *) bigToBytes(tmp1).c_str());
	return g2;
}
#endif

int element_to_bytes(unsigned char *data, Curve_t ctype, Group_t type, Element & e) {
	char c[MAX_LEN+1];
	memset(c, 0, MAX_LEN);
	int enc_len;
	string t;

	if(type == ZR_t) {
		Big *s = (Big *) e;
		t.append(bigToBytes(*s));
		string encoded = _base64_encode(reinterpret_cast<const unsigned char*>(t.c_str()), t.size());
		enc_len = encoded.size();
		memcpy(data, encoded.c_str(), enc_len);
		data[enc_len] = '\0';
//		printf("Result => ");
//		_printf_buffer_as_hex((uint8_t *) data, enc_len);
//		printf("\n");
		return enc_len;
	}
	else if(type == G1_t) {
		G1 *p = (G1 *) e;
		Big x, y;
		p->g.get(x, y);
		string t;
		t.append(bigToBytes(x));
		t.append(bigToBytes(y));

		string encoded = _base64_encode(reinterpret_cast<const unsigned char*>(t.c_str()), t.size());
		enc_len = encoded.size();
		memcpy(data, encoded.c_str(), enc_len);
		data[enc_len] = '\0';
		return enc_len;
	}
	else if(type == G2_t) {
#ifdef ASYMMETRIC
		G2 *P = (G2 *) e; // embeds an ECn3 element (for MNT curves)
		ZZn3 x, y;
			// ZZn a,b,c;
		ZZn *a = new ZZn[6];
		P->g.get(x, y); // get ZZn3's
		x.get(a[0], a[1], a[2]); // get coordinates for each ZZn
		y.get(a[3], a[4], a[5]);

		string t;
		for(int i = 0; i < 6; i++) {
			t.append( bigToBytes(Big(a[i])) );
		}
			// base64 encode t and return
		string encoded = _base64_encode(reinterpret_cast<const unsigned char*>(t.c_str()), t.size());
		enc_len = encoded.size();
		memcpy(data, encoded.c_str(), enc_len);
		data[enc_len] = '\0';
		return enc_len;
#else
		// if symmetric curve
#endif
	}
	else if(type == GT_t) {
#ifdef ASYMMETRIC
		GT *P = (GT *) e; // embeds an ZZn6 element (for MNT curves) is equivalent to
			// control this w/ a flag
		ZZn2 x, y, z; // each zzn2 has a (x,y) coordinates of type Big
		Big *a = new Big[6];
		P->g.get(x, y, z); // get ZZn2's

		x.get(a[0], a[1]); // get coordinates for each ZZn2
		y.get(a[2], a[3]);
		z.get(a[4], a[5]);
	//	    cout << "Point => (" << x << ", " << y << ", " << z << ")" << endl;
		string t;
		for(int i = 0; i < 6; i++) {
		    t.append( bigToBytes(a[i]) );
		}
//		    cout << "Pre-encoding => ";
//		    _printf_buffer_as_hex((uint8_t *) t.c_str(), t.size());
			// base64 encode t and return
		string encoded = _base64_encode(reinterpret_cast<const unsigned char*>(t.c_str()), t.size());
		enc_len = encoded.size();
		memcpy(data, encoded.c_str(), enc_len);
		data[enc_len] = '\0';
		return enc_len;
#else
		// it must be symmetric
#endif
		}
	}

	return 0;
}


Element& *_element_from_bytes(Curve_t ctype, Type type, unsigned char *data)
{
	if(type == ZR_t) {
		if(is_base64((unsigned char) data[0])) {
			string b64_encoded((char *) data);
			string s = _base64_decode(b64_encoded);
			int cnt = 0;
			Big *X = bytesToBig(s, &cnt);
			return Element(X);
		}
	}
	else if(type == G1_t) {
		if(is_base64((unsigned char) data[0])) {
		string b64_encoded((char *) data);
		string s = _base64_decode(b64_encoded);

		int cnt = 0;
		Big x,y;
		x = *bytesToBig(s, &cnt);
		s = s.substr(cnt);
		y = *bytesToBig(s, &cnt);
//		cout << "point => (" << x << ", " << y << ")" << endl;
		G1 *p = new G1();
		p->g.set(x,y);
		return (element_t *) p;
		}
	}
	else if(type == G2_t) {
		if(ctype == MNT && is_base64((unsigned char) data[0])) {
			string b64_encoded((char *) data);
			string s = _base64_decode(b64_encoded);
	//		cout << "original => " << s << endl;
			int cnt = 0;
			ZZn *a = new ZZn[6];
			for(int i = 0; i < 6; i++) {
				a[i] = ZZn(*bytesToBig(s, &cnt) ); // retrieve all six coordinates
				s = s.substr(cnt);
			}
			ZZn3 x (a[0], a[1], a[2]);
			ZZn3 y (a[3], a[4], a[5]);

			G2 *point = new G2();
			point->g.set(x, y);
			// cout << "Recovered pt => " << point->g << endl;
			return (element_t *) point;
		}
	}
	else if(type == GT_t) {
		if(ctype == MNT && is_base64((unsigned char) data[0])) {
			string b64_encoded((char *) data);
			string s = _base64_decode(b64_encoded);
	//		cout << "original => " << s << endl;
			int cnt = 0;
			Big *a = new Big[6];
			for(int i = 0; i < 6; i++) {
				// cout << "buffer => ";
			    // printf_buffer_as_hex((uint8_t *) s.c_str(), s.size());
				a[i] = *bytesToBig(s, &cnt); // retrieve all six coordinates
				s = s.substr(cnt);
				// cout << "i => " << a[i] << endl;
			}
			ZZn2 x, y, z;
			x.set(a[0], a[1]);
			y.set(a[2], a[3]);
			z.set(a[4], a[5]);

			GT *point = new GT();
			point->g.set(x, y, z);
			return (element_t *) point;
		}
	}

	return NULL;
}



