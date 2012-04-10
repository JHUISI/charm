
#define AES_SECURITY 80
#define MAX_LEN 256

#ifdef ASYMMETRIC
#define MR_PAIRING_MNT	// AES-80 security
#include "pairing_3.h"
#endif

#ifdef SYMMETRIC
#define MR_PAIRING_SSP
#include "pairing_1.h"
#endif

#include <map>

#define ZR Big
#define convert_str(point) point.g
enum Type { ZR_t = 0, G1_t, G2_t, GT_t, Str_t, None_t };

string _base64_encode(unsigned char const* bytes_to_encode, unsigned int in_len);
string _base64_decode(string const& encoded_string);
bool is_base64(unsigned char c);

class Element
{
public:
	// public values for now
	Type type;
	ZR *zr;
	G1 *g1;
	G2 *g2;
	GT *gt;
	string *strPtr;
	Element();
	~Element();
	Element(string);
	Element(ZR&);
	Element(G1&);
	Element(G2&);
	Element(GT&);

	static string serialize(Element&);
	static Element deserialize(string);

    friend ostream& operator<<(ostream&, const Element&);
private:
	// None
};

string element_to_bytes(Element & e);
Element element_from_bytes(Type type, unsigned char *data);

class CharmList
{
public:
	CharmList(void); // static list
	~CharmList();
	// consider adding remove
	void append(string);
	void append(ZR&);
	void append(G1&);
#ifdef ASYMMETRIC
	void append(G2&);
#endif
	void append(GT&);
	Element& newElement(string);
	int length(); // return length of lists
	void print();
	string printAtIndex(int index);

	// retrieve a particular index
	Element& operator[](const int index);
	// Element& operator=()
    friend ostream& operator<<(ostream&, const CharmList&);
private:
	int cur_index;
	map<int, Element> list;
};


/* @description: wrapper around the MIRACL provided pairing-friendly class */
/* PairingGroup conforms to Charm-C++ API.
 */
class PairingGroup
{
public:
	PairingGroup(int);
	~PairingGroup();
	// generate random
	void random(ZR&);
	void random(G1&);
	void random(GT&);
	bool ismember(G1&);
	bool ismember(GT&);
	bool ismember(ZR&);

#ifdef ASYMMETRIC
	void random(G2&);
	bool ismember(G2&);
	G2 mul(G2&, G2&);
	G2 div(G2&, G2&);
	G2 exp(G2&, ZR&);
//	char *serialize(G2&); // not done
//	void deserialize(G2&, char *); // not done
	GT pair(G1&, G2&);
	void *hash(char *s, Type t);
#endif

	Big order(); // returns the order of the group

	// hash -- not done
	ZR hashListToZR(CharmList&);
	G1 hashListToG1(CharmList&);
	G2 hashListToG2(CharmList&);

	GT pair(G1&, G1&);
	G1 mul(G1&, G1&);
	GT mul(GT&, GT&);
	G1 div(G1&, G1&);
	GT div(GT&, GT&);

	G1 exp(G1&, ZR&);
	GT exp(GT&, ZR&);

	// not done
//	char *serialize(ZR&);
//	char *serialize(G1&);
//	char *serialize(GT&);

//	void deserialize(ZR&, char *);
//	void deserialize(G1&, char *);
//	void deserialize(GT&, char *);

private:
	PFC *pfcObject; // defined by above #defines SYMMETRIC or ASYMMETRIC (for now)
};
