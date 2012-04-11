#include "sdlconfig.h"
#include <sstream>

/* helper methods to assist with serializing and base-64 encoding group elements */
static const string base64_chars =
             "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
             "abcdefghijklmnopqrstuvwxyz"
             "0123456789+/";

/* Note that the following was borrowed from Copyright (C) 2004-2008 RenŽ Nyffenegger (*/

bool is_base64(unsigned char c) {
  return (isalnum(c) || (c == '+') || (c == '/'));
}

string _base64_encode(unsigned char const* bytes_to_encode, unsigned int in_len) {
  string ret;
  int i = 0;
  int j = 0;
  unsigned char char_array_3[3];
  unsigned char char_array_4[4];

  while (in_len--) {
    char_array_3[i++] = *(bytes_to_encode++);
    if (i == 3) {
      char_array_4[0] = (char_array_3[0] & 0xfc) >> 2;
      char_array_4[1] = ((char_array_3[0] & 0x03) << 4) + ((char_array_3[1] & 0xf0) >> 4);
      char_array_4[2] = ((char_array_3[1] & 0x0f) << 2) + ((char_array_3[2] & 0xc0) >> 6);
      char_array_4[3] = char_array_3[2] & 0x3f;

      for(i = 0; (i <4) ; i++)
        ret += base64_chars[char_array_4[i]];
      i = 0;
    }
  }

  if (i)
  {
    for(j = i; j < 3; j++)
      char_array_3[j] = '\0';

    char_array_4[0] = (char_array_3[0] & 0xfc) >> 2;
    char_array_4[1] = ((char_array_3[0] & 0x03) << 4) + ((char_array_3[1] & 0xf0) >> 4);
    char_array_4[2] = ((char_array_3[1] & 0x0f) << 2) + ((char_array_3[2] & 0xc0) >> 6);
    char_array_4[3] = char_array_3[2] & 0x3f;

    for (j = 0; (j < i + 1); j++)
      ret += base64_chars[char_array_4[j]];

    while((i++ < 3))
      ret += '=';

  }

  return ret;

}

string _base64_decode(string const& encoded_string) {
  int in_len = encoded_string.size();
  int i = 0;
  int j = 0;
  int in_ = 0;
  unsigned char char_array_4[4], char_array_3[3];
  std::string ret;

  while (in_len-- && ( encoded_string[in_] != '=') && is_base64(encoded_string[in_])) {
    char_array_4[i++] = encoded_string[in_]; in_++;
    if (i ==4) {
      for (i = 0; i <4; i++)
        char_array_4[i] = base64_chars.find(char_array_4[i]);

      char_array_3[0] = (char_array_4[0] << 2) + ((char_array_4[1] & 0x30) >> 4);
      char_array_3[1] = ((char_array_4[1] & 0xf) << 4) + ((char_array_4[2] & 0x3c) >> 2);
      char_array_3[2] = ((char_array_4[2] & 0x3) << 6) + char_array_4[3];

      for (i = 0; (i < 3); i++)
        ret += char_array_3[i];
      i = 0;
    }
  }

  if (i) {
    for (j = i; j <4; j++)
      char_array_4[j] = 0;

    for (j = 0; j <4; j++)
      char_array_4[j] = base64_chars.find(char_array_4[j]);

    char_array_3[0] = (char_array_4[0] << 2) + ((char_array_4[1] & 0x30) >> 4);
    char_array_3[1] = ((char_array_4[1] & 0xf) << 4) + ((char_array_4[2] & 0x3c) >> 2);
    char_array_3[2] = ((char_array_4[2] & 0x3) << 6) + char_array_4[3];

    for (j = 0; (j < i - 1); j++) ret += char_array_3[j];
  }

  return ret;
}

// Element implementation
Element::Element()
{
	type = None_t;
}

Element::Element(const char *s)
{
	type = Str_t;
	strPtr = string(s);
}

Element::Element(string s)
{
	type = Str_t;
	strPtr = s;
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
//	if(type == Str_t) delete strPtr;
	type = None_t;
//	strPtr = 0;
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
		s << "str_t, " << elem_str << e.strPtr;
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

string Element::serialize(Element & e)
{
	stringstream eSerialized;
	eSerialized << e.type << ":";
	if(e.type == Str_t)
		eSerialized << e.strPtr;
	else
		eSerialized << element_to_bytes(e);
	return eSerialized.str();
}

//TODO: add thorough error checking to deserialize functions
Element Element::deserialize(string & s)
{
	Element elem;
	size_t found = s.find(':'); // delimeter

	if(found != string::npos) {
		int type = atoi(s.substr(0, found).c_str());
		if(type >= ZR_t && type < Str_t)
			return element_from_bytes((Type) type, (unsigned char *) s.substr(found+1, s.size()).c_str());
		else if(type == Str_t) {
//			string s2 = ;
			return Element(s.substr(found+1, s.size()).c_str());
		}
	}

	throw new string("Invalid bytes.\n");
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

void CharmList::append(const char *s)
{
	Element elem(s);
	list[cur_index] = elem;
	cur_index++;
}

void CharmList::append(string strs)
{
	Element elem(strs);

	// init elem here
//	elem.type = Str_t;
//	elem.strPtr  = strs;

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

string CharmList::printAtIndex(int index)
{
	stringstream ss;
	int i;

	if(index >= 0 && index < (int) list.size()) {
		i = index;
		Type t = list[i].type;
		if(t == Str_t) {
			ss << list[i].strPtr;
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

// end CharmList implementation

// start CharmDict implementation

CharmDict::CharmDict()
{

}

CharmDict::~CharmDict()
{
	emap.clear();
}

int CharmDict::length()
{
	return (int) emap.size();
}

CharmList CharmDict::keys()
{
	CharmList s;
	map<string, Element>::iterator iter;
	for(iter = emap.begin(); iter != emap.end(); iter++) {
		// s.push_back(iter->first);
		const char *ptr = iter->first.c_str();
		s.append( ptr );
	}

	return s;
}

string CharmDict::printAll()
{
	stringstream ss;
	map<string, Element, cmp_str>::iterator iter;
	for(iter = emap.begin(); iter != emap.end(); iter++) {
		ss << "key = " << iter->first << ", value = " << iter->second << endl;
	}

	string s = ss.str();
	return s;
}

void CharmDict::set(string key, Element& value)
{
	emap.insert(pair<string, Element>(key, value));
}

Element& CharmDict::operator[](const string key)
{
	map<string, Element, cmp_str>::iterator iter;
	for(iter = emap.begin(); iter != emap.end(); iter++) {
		if (key.c_str() == iter->first.c_str()) {
			return iter->second;
		} // strcmp(key.c_str(), iter->first.c_str())
	}

	// means it's a new index so set it
	throw new string("Invalid access.\n");
}

ostream& operator<<(ostream& s, const CharmDict& e)
{
	CharmDict e2 = e;
	s << e2.printAll();
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
			ZR tmp = pfcObject->hash_to_group( (char *) e.strPtr.c_str());
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
			ZR tmp = pfcObject->hash_to_group( (char *) e.strPtr.c_str());
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
			ZR tmp = pfcObject->hash_to_group( (char *) e.strPtr.c_str());
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

string element_to_bytes(Element & e) {
	string t;
	Type type = e.type;

	if(type == ZR_t) {
		Big s = *e.zr;
		t.append(bigToBytes(s));
		string encoded = _base64_encode(reinterpret_cast<const unsigned char*>(t.c_str()), t.size());
		return encoded;
	}
	else if(type == G1_t) {
		G1 p = *e.g1;
		Big x, y;
		p.g.get(x, y);
		string t;
		t.append(bigToBytes(x));
		t.append(bigToBytes(y));

		string encoded = _base64_encode(reinterpret_cast<const unsigned char*>(t.c_str()), t.size());
		return encoded;
	}
#ifdef ASYMMETRIC
	else if(type == G2_t) {
		G2 P = *e.g2; // embeds an ECn3 element (for MNT curves)
		ZZn3 x, y;
			// ZZn a,b,c;
 		ZZn *a = new ZZn[6];
		P.g.get(x, y); // get ZZn3's
		x.get(a[0], a[1], a[2]); // get coordinates for each ZZn
		y.get(a[3], a[4], a[5]);

		string t;
		for(int i = 0; i < 6; i++) {

			t.append( bigToBytes( Big(a[i]) ) );
		}
			// base64 encode t and return
		string encoded = _base64_encode(reinterpret_cast<const unsigned char*>(t.c_str()), t.size());
 		delete [] a;
		return encoded;
	}
#endif
	else if(type == GT_t) {
		GT P = *e.gt; // embeds an ZZn6 element (for MNT curves) is equivalent to
			// control this w/ a flag
#ifdef ASYMMETRIC
		ZZn2 x, y, z; // each zzn2 has a (x,y) coordinates of type Big
		Big *a = new Big[6];
		P.g.get(x, y, z); // get ZZn2's

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
		delete [] a;
		return encoded;
#else
		// it must be symmetric
#endif
	}

	throw new string("element_to_bytes: invalid type specified");
}

Element element_from_bytes(Type type, unsigned char *data)
{
	if(type == ZR_t) {
		if(is_base64((unsigned char) data[0])) {
			string b64_encoded((char *) data);
			string s = _base64_decode(b64_encoded);
			int cnt = 0;
			Big *b = bytesToBig(s, &cnt);
			Element elem(*b);
			delete b;
			return elem;
		}
	}
	else if(type == G1_t) {
		if(is_base64((unsigned char) data[0])) {
		string b64_encoded((char *) data);
		string s = _base64_decode(b64_encoded);

		int cnt = 0;
		Big *x, *y;
		x = bytesToBig(s, &cnt);
		s = s.substr(cnt);
		y = bytesToBig(s, &cnt);
//		cout << "point => (" << x << ", " << y << ")" << endl;
		G1 *p = new G1();
		p->g.set(*x, *y);
		delete x;
		delete y;
		Element elem(*p);
		delete p;
		return elem;
		}
	}
#ifdef ASYMMETRIC
	else if(type == G2_t) {
		if(is_base64((unsigned char) data[0])) {
			string b64_encoded((char *) data);
			string s = _base64_decode(b64_encoded);
	//		cout << "original => " << s << endl;
			int cnt = 0;
			ZZn *a = new ZZn[6];
			for(int i = 0; i < 6; i++) {
				Big *b = bytesToBig(s, &cnt);
				a[i] = ZZn( *b ); // retrieve all six coordinates
				s = s.substr(cnt);
				delete b;
			}
			ZZn3 x (a[0], a[1], a[2]);
			ZZn3 y (a[3], a[4], a[5]);

			G2 *point = new G2();
			point->g.set(x, y);
			delete [] a;
			// cout << "Recovered pt => " << point->g << endl;
			Element elem(*point);
			delete point;
			return elem;
		}
	}
#endif
	else if(type == GT_t) {
		if(is_base64((unsigned char) data[0])) {
			string b64_encoded((char *) data);
			string s = _base64_decode(b64_encoded);
	//		cout << "original => " << s << endl;
			int cnt = 0;
#ifdef ASYMMETRIC
			Big *a = new Big[6];
			for(int i = 0; i < 6; i++) {
//				// cout << "buffer => ";
//			    // printf_buffer_as_hex((uint8_t *) s.c_str(), s.size());
				Big *b = bytesToBig(s, &cnt);
				a[i] =  Big(*b); // retrieve all six coordinates
				s = s.substr(cnt);
				delete b;
//				// cout << "i => " << a[i] << endl;
			}
			ZZn2 x, y, z;
			x.set(a[0], a[1]);
			y.set(a[2], a[3]);
			z.set(a[4], a[5]);

			GT *point = new GT();
			point->g.set(x, y, z);
			Element elem (*point);
			delete [] a;
//			delete point;
			return elem;
#else
		// must be symmetric
#endif
		}
	}

	throw new string("Invalid type specified.\n");
}



