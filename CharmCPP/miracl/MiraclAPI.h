#ifndef MIRACLAPI_H
#define MIRACLAPI_H

extern "C" {
#include "common.h"
}
#include <map>
#include <vector>
#include <sstream>
#include <string>
#include <fstream>
#include <math.h>
class Element;
class CharmList;
class CharmListStr;
class CharmMetaListZR;
class CharmMetaListG1;
class CharmMetaListG2;
class CharmMetaListGT;

#define stringify(s)  #s
#define setDict(k, v) \
     Element v##_tmp = Element(*v); \
     k.set(stringify(v), v##_tmp);

// group sizes
#define MNT_G2_SIZE		6
#define MNT_GT_SIZE		6
#define BN_G2_SIZE		4
#define BN_GT_SIZE		12
// SS G1=G2
#define SS_GT_SIZE		2

/* @description: wrapper around the MIRACL provided pairing-friendly class */
/* PairingGroup conforms to Charm-C++ API.
 */
class PairingGroup
{
public:
	PairingGroup();
	PairingGroup(int);
	~PairingGroup();
	// generate random
	void init(ZR&, char*);
	void init(ZR&, int);
	void init(G1&, int);
	void init(GT&, int);

	ZR init(ZR_type);
	ZR init(ZR_type, int);
	G1 init(G1_type);
	G1 init(G1_type, int);
	GT init(GT_type);
	GT init(GT_type, int);

	ZR random(ZR_type);
	G1 random(G1_type);
	GT random(GT_type);
	bool ismember(CharmMetaListZR&);
	bool ismember(CharmMetaListG1&);
	bool ismember(CharmMetaListGT&);
	bool ismember(CharmList&);
	bool ismember(CharmListStr&);
	bool ismember(CharmListZR&);
	bool ismember(CharmListG1&);
	bool ismember(CharmListGT&);
	bool ismember(ZR&);
	bool ismember(G1&);
	bool ismember(GT&);

#if ASYMMETRIC == 1
	G2 init(G2_type);
	G2 init(G2_type, int);
	void init(G2&, int);
	G2 random(G2_type);
	bool ismember(G2&);
	bool ismember(CharmListG2&);
	bool ismember(CharmMetaListG2&);
	G2 mul(G2, G2);
	G2 div(G2, G2);
	G2 exp(G2, ZR);
	G2 exp(G2, int);
	GT pair(G1, G2);
	G2 hashListToG2(string);
	G2 hashListToG2(CharmList);
#endif

	ZR order(); // returns the order of the group

	// hash -- not done
	ZR hashListToZR(string);
	G1 hashListToG1(string);

	ZR hashListToZR(CharmList);
	G1 hashListToG1(CharmList);

	GT pair(G1, G1);
	int mul(int, int);
	ZR mul(ZR, ZR);
	G1 mul(G1, G1);
	GT mul(GT, GT);
	int div(int, int);
	ZR div(int, ZR);
	ZR div(ZR, ZR);
	G1 div(G1, G1);
	GT div(GT, GT);

	ZR exp(ZR, int);
	ZR exp(ZR, ZR);
	G1 exp(G1, ZR);
	G1 exp(G1, int);
	GT exp(GT, ZR);
	GT exp(GT, int);

	ZR add(ZR, ZR);
	int add(int, int);
	int sub(int, int);
	ZR sub(ZR, ZR);
	ZR neg(ZR);
	ZR inv(ZR);
	string aes_key(GT & g);

private:
	PFC *pfcObject; // defined by above #defines SYMMETRIC or ASYMMETRIC (for now)
	GT *gt, *gt_id;
};

CharmListZR stringToInt(PairingGroup & group, string strID, int z, int l);
ZR SmallExp(int bits);
ZR ceillog(int base, int value);

#endif
