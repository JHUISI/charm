
#define AES_SECURITY 80

#ifdef ASYMMETRIC
#define MR_PAIRING_MNT	// AES-80 security
#include "pairing_3.h"
#endif

#ifdef SYMMETRIC
#define MR_PAIRING_SSP
#include "pairing_1.h"
#endif

#include <map>
#include <iostream>
#include <sstream>
#include <string>
//using namespace std;

//#include <iostream>
//using std::ostream;

#define ZR Big
#define str(point) point.g
enum Type { ZR_t = 0, G1_t, G2_t, GT_t, Str_t };
struct Element
{
	Type type;
	ZR *zr;
	G1 *g1;
#ifdef ASYMMETRIC
	G2 *g2;
#endif
	GT *gt;
	string *strPtr;
};

class CharmList
{
public:
	CharmList(void); // static list
	~CharmList();
	// consider adding remove
	void append(string str);
	void append(ZR&);
	void append(G1&);
#ifdef ASYMMETRIC
	void append(G2&);
#endif
	void append(GT&);
	int length(); // return length of lists
	void print();
	string printAtIndex(int index);

	// overload some operators here
	Element& get(int index);
	Element& operator[](const int index);
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
	char *serialize(G2&); // not done
	void deserialize(G2&, char *); // not done
	GT pair(G1&, G2&);
	void *hash(char *s, Type t);
#endif

	Big order(); // returns the order of the group

	ZR hashStringToZR(char *);
	G1 hashStringToG1(char *);
	G2 hashStringToG2(char *);

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
	char *serialize(ZR&);
	char *serialize(G1&);
	char *serialize(GT&);

	void deserialize(ZR&, char *);
	void deserialize(G1&, char *);
	void deserialize(GT&, char *);

private:
	PFC *pfcObject; // defined by above #defines SYMMETRIC or ASYMMETRIC (for now)
};

