
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
#include <vector>
#include <string>

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
	string strPtr;
	Element();
	~Element();
	Element(const char *);
	Element(string);
	Element(ZR&);
	Element(G1&);
#ifdef ASYMMETRIC
	Element(G2&);
 	G2 getG2();
	void createNew(G2);
#endif

	Element(GT&);
 	Element(const Element& e);
 	G1 getG1(); // getter methods
 	GT getGT();
	string str();
	void createNew(ZR&);
	void createNew(G1);
	void createNew(GT);

	static string serialize(Element&);
	static void deserialize(Element&, string&);

 	Element operator=(const Element& e);
    friend ostream& operator<<(ostream&, const Element&);
private:
    bool isAllocated; // if True, means Element class responsible
    // for releasing the memory.
    // False means Element field just holds a reference
};

string element_to_bytes(Element & e);
void element_from_bytes(Element&, Type type, unsigned char *data);

class CharmList
{
public:
	CharmList(void); // static list
	~CharmList();
	// consider adding remove
	void append(const char *);
	void append(string);
	void append(ZR&);
	void append(G1&);
#ifdef ASYMMETRIC
	void append(G2&);
#endif
	void append(GT&);
	int length(); // return length of lists
	string printAtIndex(int index);

	// retrieve a particular index
	Element& operator[](const int index);
    friend ostream& operator<<(ostream&, const CharmList&);
private:
	int cur_index;
	map<int, Element> list;
};

struct cmp_str
{
	bool operator()(const string a, const string b) {
		return strcmp(a.c_str(), b.c_str()) < 0;
	}
};

class CharmDict
{
public:
	CharmDict(void); // static list
	~CharmDict();
	// consider adding remove
	void set(string key, Element& value);
	int length(); // return length of lists
	CharmList keys(); // vector<string>
	string printAll();

	// retrieve a particular index
	Element& operator[](const string key);
    friend ostream& operator<<(ostream&, const CharmDict&);

private:
	map<string, Element, cmp_str> emap;
};

#define DeriveKey	group.aes_key

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
	bool ismember(G2);
	G2 mul(G2, G2);
	G2 div(G2, G2);
	G2 exp(G2, ZR);
	GT pair(G1, G2);
	void *hash(char *s, Type t);
#endif

	Big order(); // returns the order of the group

	// hash -- not done
	ZR hashListToZR(CharmList&);
	G1 hashListToG1(CharmList&);
	G2 hashListToG2(CharmList&);

	GT pair(G1, G1);
	G1 mul(G1, G1);
	GT mul(GT, GT);
	G1 div(G1, G1);
	GT div(GT, GT);

	G1 exp(G1, ZR);
	GT exp(GT, ZR);
	string aes_key(GT & g);

private:
	PFC *pfcObject; // defined by above #defines SYMMETRIC or ASYMMETRIC (for now)
	GT *gt;
};
