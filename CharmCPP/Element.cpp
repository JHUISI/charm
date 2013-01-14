
#include "CharmList.h"
#include <sstream>

void deserialize(Element & e, string s)
{
	size_t found = s.find(':'); // delimeter
	if(found != string::npos) {
		int type = atoi(s.substr(0, found).c_str());
		if(type >= ZR_t && type < Str_t) {
			e.type = type;
			Element_FromBytes(e, type, (unsigned char *) s.substr(found+1, s.size()).c_str());
		}
		else if(type == Str_t) {
			e.type = type;
			e = Element(s.substr(found+1, s.size()).c_str());
		}
		return;
	}

	e.type = None_t;
	return;
}

string serialize(Element & e)
{
	stringstream eSerialized;
	eSerialized << e.type << ":";
	if(e.type == Str_t)
		eSerialized << e.strPtr;
	else
		eSerialized << Element_ToBytes(e); // should be defined somewhere in each lower level interface
	return eSerialized.str();
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

Element::Element(CharmList & List)
{
	type 	 = list_t;
	aList   = List;
}

Element::Element(ZR & z)
{
	type = ZR_t;
	zr   = z;
}

Element::Element(CharmListZR & zList)
{
	type 	 = listZR_t;
	zrList   = zList;
}

Element::Element(CharmListG1 & gList)
{
	type 	 = listG1_t;
	g1List   = gList;
}

Element::Element(CharmListGT & gList)
{
	type 	 = listGT_t;
	gtList   = gList;
}

Element::Element(G1 & g)
{
	type = G1_t;
	g1   = g;
}

#if ASYMMETRIC == 1
Element::Element(G2 & g)
{
	type = G2_t;
	g2   = g;
}
#endif

Element::Element(GT & g)
{
	type = GT_t;
	gt   = g;
}

Element::Element(const Element& e)
{
	type = e.type;
	if(type == Str_t)
		strPtr = e.strPtr;
	else if(type == ZR_t)
		zr = e.zr;
	else if(type == listZR_t)
		zrList = e.zrList;
	else if(type == G1_t)
		g1 = e.g1;
	else if(type == listG1_t)
		g1List = e.g1List;
#if ASYMMETRIC == 1
	else if(type == G2_t)
		g2 = e.g2;
	else if(type == listG2_t)
		g2List = e.g2List;
#endif
	else if(type == GT_t)
		gt = e.gt;
	else if(type == listGT_t)
		gtList = e.gtList;
	else if(type == list_t)
		aList = e.aList;
}

CharmList Element::getList()
{   // only successful if the Element type is of list_t
	if(type == list_t) return aList;
	throw new string("invalid type.");
}

ZR Element::getZR()
{
	if(type == ZR_t) return zr;
	throw new string("invalid type.");
}

CharmListZR Element::getListZR()
{
	if(type == listZR_t) return zrList;
	throw new string("invalid type.");
}


ZR & Element::getRefZR()
{
	if(type == ZR_t) return zr;
	throw new string("invalid type.");
}

G1 Element::getG1()
{
	if(type == G1_t) return g1;
	throw new string("invalid type.");
}

CharmListG1 Element::getListG1()
{
	if(type == listG1_t) return g1List;
	throw new string("invalid type.");
}


#if ASYMMETRIC == 1
Element::Element(CharmListG2 & gList)
{
	type 	 = listG2_t;
	g2List   = gList;
}

G2 Element::getG2()
{
	if(type == G2_t) return g2;
	throw new string("invalid type.");
}

CharmListG2 Element::getListG2()
{
	if(type == listG2_t) return g2List;
	throw new string("invalid type.");
}

G2 & Element::getRefG2()
{
	if(type == G2_t) return g2;
	throw new string("invalid type.");
}
#endif

GT Element::getGT()
{
	if(type == GT_t) return gt;
	throw new string("invalid type.");
}

CharmListGT Element::getListGT()
{
	if(type == listGT_t) return gtList;
	throw new string("invalid type.");
}

string Element::str()
{
	stringstream ss;
	if(type == Str_t)
		ss << strPtr;
	else if(type == ZR_t)
		ss << zr;
	else if(type == listZR_t)
		ss << zrList;
	else if(type == G1_t)
		ss << convert_str(g1);
	else if(type == listG1_t)
		ss << g1List;
#if ASYMMETRIC == 1
	else if(type == G2_t)
		ss << convert_str(g2);
	else if(type == listG2_t)
		ss << g2List;
#endif
	else if(type == GT_t)
		ss << convert_str(gt);
	else if(type == listGT_t)
		ss << gtList;
	else if(type == list_t);
	    ss << aList;
	return ss.str();
}

Element::~Element()
{
}

Element Element::operator=(const Element& e)
{
	if(this == &e)
		return *this;

	type = e.type;
	if(type == Str_t)
		strPtr = e.strPtr;
	else if(type == ZR_t)
		zr = e.zr;
	else if(type == listZR_t)
		zrList = e.zrList;
	else if(type == G1_t)
		g1 = e.g1;
	else if(type == listG1_t)
		g1List = e.g1List;
#if ASYMMETRIC == 1
	else if(type == G2_t)
		g2 = e.g2;
	else if(type == listG2_t)
		g2List = e.g2List;
#endif
	else if(type == GT_t)
		gt = e.gt;
	else if(type == listGT_t)
		gtList = e.gtList;
	else if(type == list_t)
		aList = e.aList;
	return *this;
}

CharmList Element::operator+ (const Element& e) const
{
	CharmList c;
	if (this->type == Str_t)
	      	c.append(this->strPtr);
	else if(this->type == ZR_t)
		c.append(this->zr);
	else if(this->type == G1_t)
		c.append(this->g1);
#if ASYMMETRIC == 1
	else if(this->type == G2_t)
		c.append(this->g2);
#endif
	else if(this->type == GT_t)
		c.append(this->gt);

	if (e.type == Str_t)
     	c.append(e.strPtr);
	else if(e.type == ZR_t)
		c.append(e.zr);
	else if(e.type == G1_t)
		c.append(e.g1);
#if ASYMMETRIC == 1
	else if(e.type == G2_t)
		c.append(e.g2);
#endif
	else if(e.type == GT_t)
		c.append(e.gt);

	return c;
}

CharmList Element::operator+(const CharmList& c) const
{
	CharmList c2 = c;
	CharmList result;
	Element e2 = *this;

	result.append(e2);
	result.append(c2);

	return result;
}

ostream& operator<<(ostream& s, const Element& e)
{
	Element e2 = e;
	int t = e2.type;
	if(t == Str_t)
		s << "str: ";
	else if(t == ZR_t)
		s << "ZR: ";
	else if(t == G1_t)
		s << "G1: ";
#if ASYMMETRIC == 1
	else if(t == G2_t)
		s << "G2: ";
#endif
	else if(t == GT_t)
		s << "GT: ";
	s << e2.str();

	return s;
}

/* helper methods to assist with serializing and base-64 encoding group elements */
static const string base64_chars =
             "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
             "abcdefghijklmnopqrstuvwxyz"
             "0123456789+/";

/* Note that the following was borrowed from Copyright (C) 2004-2008 Ren Nyffenegger (*/

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
