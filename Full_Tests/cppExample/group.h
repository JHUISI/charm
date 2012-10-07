
#define AES_SECURITY 80
#define MAX_LEN 256

#ifdef ASYMMETRIC
#define MR_PAIRING_MNT	// AES-80 security
#include "pairing_3.h"
#define MNT160 AES_SECURITY
#endif

#ifdef SYMMETRIC
#define MR_PAIRING_SSP
#include "pairing_1.h"
#endif

#include <map>
#include <vector>
#include <string>
#include <fstream>

#define ZR Big
#define convert_str(point) point.g
#define stringify(s)  #s
#define setDict(k, v) \
     Element v##_tmp = Element(*v); \
     k.set(stringify(v), v##_tmp);
#define deleteDict(k, v) \
     delete k[v].delGroupElement();

//enum Type { ZR_t = 0, G1_t, G2_t, GT_t, Str_t, None_t };
enum ZR_type { ZR_t = 0 };
enum G1_type { G1_t = 1 };
enum G2_type { G2_t = 2 };
enum GT_type { GT_t = 3 };
enum Str_type { Str_t = 4 };
enum None_type { None_t = 5 };

string _base64_encode(unsigned char const* bytes_to_encode, unsigned int in_len);
string _base64_decode(string const& encoded_string);
bool is_base64(unsigned char c);

class Element
{
public:
	// public values for now
	int type;
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
 	G2 getG2(); // returns value (or copy)
 	G2& getRefG2(); // returns reference for G2 (for cleanup)
	void createNew(G2);
#endif

	Element(GT&);
 	Element(const Element& e);
 	ZR getZR(); // returns value (or copy)
 	ZR& getRefZR(); // returns reference for ZR (for cleanup)
 	G1 getG1(); // getter methods
 	G1& getRefG1(); // getter methods
 	GT getGT();
 	GT& getRefGT();
	string str();
	void createNew(ZR&);
	void createNew(G1);
	void createNew(GT);
	void delGroupElement();

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
void element_from_bytes(Element&, int type, unsigned char *data);

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

class CharmListStr
{
public:
	CharmListStr(void); // static list
	~CharmListStr();
	void append(string&);
	int length(); // return length of lists
	string printAtIndex(int index);

	// retrieve a particular index
	string& operator[](const int index);
    friend ostream& operator<<(ostream&, const CharmListStr&);
private:
	int cur_index;
	map<int, string> list;
};

class CharmListZR
{
public:
	CharmListZR(void); // static list
	~CharmListZR();
	void append(ZR&);
	int length(); // return length of lists
	string printAtIndex(int index);

	// retrieve a particular index
	ZR& operator[](const int index);
    friend ostream& operator<<(ostream&, const CharmListZR&);
private:
	int cur_index;
	map<int, ZR> list;
};

class CharmListG1
{
public:
	CharmListG1(void); // static list
	~CharmListG1();
	void append(G1&);
	int length(); // return length of lists
	string printAtIndex(int index);

	// retrieve a particular index
	G1& operator[](const int index);
    friend ostream& operator<<(ostream&, const CharmListG1&);
private:
	int cur_index;
	map<int, G1> list;
};

class CharmListG2
{
public:
	CharmListG2(void); // static list
	~CharmListG2();
	void append(G2&);
	int length(); // return length of lists
	string printAtIndex(int index);

	// retrieve a particular index
	G2& operator[](const int index);
    friend ostream& operator<<(ostream&, const CharmListG2&);
private:
	int cur_index;
	map<int, G2> list;
};

class CharmListGT
{
public:
	CharmListGT(void); // static list
	~CharmListGT();
	void append(GT&);
	int length(); // return length of lists
	string printAtIndex(int index);

	// retrieve a particular index
	GT& operator[](const int index);
    friend ostream& operator<<(ostream&, const CharmListGT&);
private:
	int cur_index;
	map<int, GT> list;
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
	void init(ZR&, char*);
	//void random(ZR&);
	//void random(G1&);
	//void random(GT&);
	ZR random(ZR_type);
	G1 random(G1_type);
	GT random(GT_type);
	bool ismember(CharmList&);
	bool ismember(CharmListZR&);
	bool ismember(CharmListG1&);
	bool ismember(CharmListG2&);
	bool ismember(ZR&);
	bool ismember(G1&);
	bool ismember(GT&);

#ifdef ASYMMETRIC
	G2 random(G2_type);
	bool ismember(G2&);
	G2 mul(G2, G2);
	G2 div(G2, G2);
	G2 exp(G2, ZR);
	GT pair(G1, G2);
#endif

	Big order(); // returns the order of the group

	// hash -- not done
	ZR hashListToZR(string);
	G1 hashListToG1(string);
	G2 hashListToG2(string);

	ZR & hashListToZR(CharmList&);
	G1 & hashListToG1(CharmList&);
	G2 & hashListToG2(CharmList&);

	GT pair(G1, G1);
	ZR mul(ZR, ZR);
	G1 mul(G1, G1);
	GT mul(GT, GT);
	ZR div(ZR, ZR);
	G1 div(G1, G1);
	GT div(GT, GT);

	ZR exp(ZR, ZR);
	G1 exp(G1, ZR);
	GT exp(GT, ZR);

	int add(int, int);
	int sub(int, int);
	int mul(int, int);
	int div(int, int);
	string aes_key(GT & g);

private:
	PFC *pfcObject; // defined by above #defines SYMMETRIC or ASYMMETRIC (for now)
	GT *gt;
};

#define aes_block_size 16

class SymmetricEnc
{
public:
	SymmetricEnc(); // take Mode,
	~SymmetricEnc();
	// wrapper around AES code
	string encrypt(char *key, char *message, int len); // generate iv internally
	string decrypt(char *key, char *ciphertext, int len);
	static string pad(string s);

private:
	int keysize;
	int mode;
	char iv[aes_block_size];
	bool aes_initialized;
	aes a;
};

// to support codegen
void parsePartCT(const char *filename, CharmDict & d);
void parseKeys(const char *filename, ZR & sk, GT & pk);
string SymDec(string k, string c_encoded);
