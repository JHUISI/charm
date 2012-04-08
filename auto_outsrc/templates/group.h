


#ifdef ASYMMETRIC
#define MR_PAIRING_MNT	// AES-80 security
#define AES_SECURITY 80
#endif

#ifdef SYMMETRIC
#define MR_PAIRING_KSS
#define AES_SECURITY 192
#endif

#include "pairing_3.h"


/* @description: wrapper around the MIRACL provided pairing-friendly class */
/* PairingGroup conforms to Charm-C++ API.
 */
class PairingGroup
{
public:
	PairingGroup(int);
	// generate random
	void random(Big&);
	void random(G1&);
	void random(G2&);
	void random(GT&);
	bool ismember(G1&);
	bool ismember(G2&);
	bool ismember(GT&);
	bool ismember(Big&);

	Big order(); // returns the order of the group

	// hash -- will take the most time to implement
	void hash(); // should accept a list of various types: str, ZR, G1, G2, GT and outputs ZR, G1 or G2
	void pair(G1&, G2&);
	void mul(G1&, G1&);
	void mul(G2&, G2&);
	void mul(GT&, GT&);

	void exp(G1&, Big&);
	void exp(G2&, Big&);
	void exp(GT&, Big&);

	void serialize(Big&);
	void serialize(G1&);
	void serialize(G2&);
	void serialize(GT&);

	void deserialize(Big&, char *);
	void deserialize(G1&, char *);
	void deserialize(G2&, char *);
	void deserialize(GT&, char *);
	~PairingGroup();
private:
	PFC pfcObject; // defined by above #defines SYMMETRIC or ASYMMETRIC (for now)
};
