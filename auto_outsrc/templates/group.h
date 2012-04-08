
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
	char *serialize(G2&);
	void deserialize(G2&, char *);
	GT pair(G1&, G2&);
#endif

	Big order(); // returns the order of the group

	// hash -- will take the most time to implement
	void hash(); // should accept a list of various types: str, ZR, G1, G2, GT and outputs ZR, G1 or G2
	void pair(G1&, G1&);
	G1 mul(G1&, G1&);
	GT mul(GT&, GT&);

	G1 exp(G1&, ZR&);
	GT exp(GT&, ZR&);

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
