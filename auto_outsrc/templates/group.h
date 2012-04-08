
#define AES_SECURITY 80

#ifdef ASYMMETRIC
#define MR_PAIRING_MNT	// AES-80 security
#include "pairing_3.h"
#endif

#ifdef SYMMETRIC
#define MR_PAIRING_SSP
#include "pairing_1.h"
#endif


#define ZR Big
#define str(point) point.g
// enum Type { ZR_t = 0, G1_t, G2_t, GT_t };

/* @description: wrapper around the MIRACL provided pairing-friendly class */
/* PairingGroup conforms to Charm-C++ API.
 */
class PairingGroup
{
public:
	PairingGroup(int);
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
	~PairingGroup();

private:
	PFC *pfcObject; // defined by above #defines SYMMETRIC or ASYMMETRIC (for now)
};
