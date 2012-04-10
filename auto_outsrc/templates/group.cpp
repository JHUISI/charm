#include "sdlconfig.h"
#include <sstream>

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
	elem.strPtr  = &strs; // new string(str);

	list[cur_index] = elem;
	cur_index++;
}

void CharmList::append(ZR & zr)
{
	Element elem;
	elem.type = ZR_t;
	elem.zr   = &zr; // new ZR(zr);

	list[cur_index] = elem;
	cur_index++;
}

void CharmList::append(G1 & g1)
{
	Element elem;
	elem.type = G1_t;
	elem.g1   = &g1; // new G1(g1);

	list[cur_index] = elem;
	cur_index++;
}

#ifdef ASYMMETRIC
void CharmList::append(G2 & g2)
{
	Element elem;
	elem.type = G2_t;
	elem.g2   =  &g2; // new G2(g2);

	list[cur_index] = elem;
	cur_index++;
}
#endif

void CharmList::append(GT & gt)
{
	Element elem;
	elem.type = GT_t;
	elem.gt   = new GT(gt);

	list[cur_index] = elem;
	cur_index++;
}

Element& CharmList::get(int index)
{
	int len = (int) list.size();
	if(index >= 0 && index < len) {
		return list[index];
	}
}

Element& CharmList::operator[](const int index)
{
	int len = (int) list.size();
	if(index >= 0 && index < len) {
		return list[index];
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

void CharmList::print()
{
	for(int i = 0; i < cur_index; i++) {
		Type t = list[i].type;
		cout << i << ": ";
		if(t == Str_t) {
			cout << *list[i].strPtr << endl;
		}
		else if(t == ZR_t) {
			cout << *list[i].zr << endl;
		}
		else if(t == G1_t) {
			cout << list[i].g1->g << endl;
		}
#ifdef ASYMMETRIC
		else if(t == G2_t) {
			cout << list[i].g2->g << endl;
		}
#endif
		else if(t == GT_t) {
			cout << list[i].gt->g << endl;
		}
		else {
			cout << "invalid type" << endl;
		}
	}
}

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
	// follow above approach but hash and map to G1 instead
	//	pfcObject->hash_and_map(g1, s);
}

#ifdef ASYMMETRIC
G2 PairingGroup::hashListToG2(CharmList & list)
{
	// follow above approach but hash and map to G2 instead
}
#endif


