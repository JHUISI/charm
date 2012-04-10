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


