#include "sdlconfig.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;

int N = 2;

int secparam = 80;

PairingGroup group(AES_SECURITY);

void setup(G2 & g2)
{
    g2 = group.random(G2_t);
    return;
}

void keygen(G2 & g2, G2 & pk, ZR & sk)
{
    ZR alpha = group.init(ZR_t);
    alpha = group.random(ZR_t);
    sk = alpha;
    pk = group.exp(g2, alpha);
    return;
}

void sign(G2 & pk, ZR & sk, string & M, string & t1, string & t2, string & t3, G1 & sig)
{
    G1 a = group.init(G1_t);
    G1 h = group.init(G1_t);
    ZR b = group.init(ZR_t);
    a = group.hashListToG1(t1);
    h = group.hashListToG1(t2);
    b = group.hashListToZR((Element(M) + Element(t3)));
    sig = group.mul(group.exp(a, sk), group.exp(h, group.mul(sk, b)));
    return;
}

bool verify(G2 & pk, G2 & g2, G1 & sig, string & M, string & t1, string & t2, string & t3)
{
    G1 a = group.init(G1_t);
    G1 h = group.init(G1_t);
    ZR b = group.init(ZR_t);
    a = group.hashListToG1(t1);
    h = group.hashListToG1(t2);
    b = group.hashListToZR((Element(M) + Element(t3)));
    if ( ( (group.pair(sig, g2)) == (group.mul(group.pair(a, pk), group.exp(group.pair(h, pk), b))) ) )
    {
        return true;
    }
    else
    {
        return false;
    }
}

bool membership(G2 & g2, CharmListG2 & pklist, CharmListG1 & siglist)
{
    if ( ( (group.ismember(g2)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(pklist)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(siglist)) == (false) ) )
    {
        return false;
    }
    return true;
}

void dividenconquer(CharmListZR & delta, int startSigNum, int endSigNum, list<int> & incorrectIndices, CharmListG1 & dotACache, CharmListG2 & dotBCache, CharmListG2 & dotCCache, G2 & g2, G1 & a, G1 & h)
{
    G1 dotALoopVal = group.init(G1_t, 1);
    G2 dotBLoopVal = group.init(G2_t, 1);
    G2 dotCLoopVal = group.init(G2_t, 1);
    int midwayFloat = 0;
    int midway = 0;
    int midSigNum = 0;
    group.init(dotALoopVal, 1);
    group.init(dotBLoopVal, 1);
    group.init(dotCLoopVal, 1);
    for (int z = startSigNum; z < endSigNum; z++)
    {
        dotALoopVal = group.mul(dotALoopVal, dotACache[z]);
        dotBLoopVal = group.mul(dotBLoopVal, dotBCache[z]);
        dotCLoopVal = group.mul(dotCLoopVal, dotCCache[z]);
    }
    if ( ( (group.pair(dotALoopVal, g2)) == (group.mul(group.pair(a, dotBLoopVal), group.pair(h, dotCLoopVal))) ) )
    {
        return;
    }
    else
    {
        midwayFloat = group.div(group.sub(endSigNum, startSigNum), 2);
        midway = int(midwayFloat);
    }
    if ( ( (midway) == (0) ) )
    {
        incorrectIndices.push_back(startSigNum);
    }
    else
    {
        midSigNum = group.add(startSigNum, midway);
        dividenconquer(delta, startSigNum, midSigNum, incorrectIndices, dotACache, dotBCache, dotCCache, g2, a, h);
        dividenconquer(delta, midSigNum, endSigNum, incorrectIndices, dotACache, dotBCache, dotCCache, g2, a, h);
    }
    return;
}

bool batchverify(G2 & g2, CharmListG2 & pklist, string & t2, string & t3, string & t1, CharmListStr & Mlist, CharmListG1 & siglist, list<int> & incorrectIndices)
{
    CharmListZR delta;
    G1 a = group.init(G1_t);
    G1 h = group.init(G1_t);
    ZR b = group.init(ZR_t);
    CharmListG1 dotACache;
    CharmListG2 dotBCache;
    CharmListG2 dotCCache;
    for (int z = 0; z < N; z++)
    {
        delta[z] = SmallExp(secparam);
    }
    if ( ( (membership(g2, pklist, siglist)) == (false) ) )
    {
        return false;
    }
    a = group.hashListToG1(t1);
    h = group.hashListToG1(t2);
    for (int z = 0; z < N; z++)
    {
        b = group.hashListToZR((Element(Mlist[z]) + Element(t3)));
        dotACache[z] = group.exp(siglist[z], delta[z]);
        dotBCache[z] = group.exp(pklist[z], delta[z]);
        dotCCache[z] = group.exp(pklist[z], group.mul(b, delta[z]));
    }
    dividenconquer(delta, 0, N, incorrectIndices, dotACache, dotBCache, dotCCache, g2, a, h);
    return true;
}

int main()
{
	G1 sig0, sig1;
	G2 g2, pk0, pk1;
	ZR sk0, sk1;
	string t1 = "t1";
	string t2 = "t2";
	string t3 = "t3";
	string MI = "test1";
	string MII = "test2";

	setup(g2);

	keygen(g2, pk0, sk0);
	keygen(g2, pk1, sk1);

	sign(pk0, sk0, MI, t1, t2, t3, sig0);
	sign(pk1, sk1, MII, t1, t2, t3, sig1);

	cout << "signature := " << sig1.g << endl;

	if(verify(pk0, g2, sig0, MI, t1, t2, t3))
		cout << "Successful verification for sig0." << endl;
	else
		cout << "FAILED verification for sig0" << endl;

	if(verify(pk1, g2, sig1, MII, t1, t2, t3))
		cout << "Successful verification for sig1." << endl;
	else
		cout << "FAILED verification for sig1" << endl;


	list<int> incorrectIndices;
	CharmListG2 pklist;
	CharmListStr Mlist;
	CharmListG1 siglist;

	pklist[0] = pk0;
	pklist[1] = pk1;
	Mlist[0] = MI;
	Mlist[1] = MII;
	siglist[0] = sig0;
	siglist[1] = sig1;

	batchverify(g2, pklist, t2, t3, t1, Mlist, siglist, incorrectIndices);
	cout << "Incorrect indices: ";
	for (list<int>::iterator it = incorrectIndices.begin(); it != incorrectIndices.end(); it++)
		cout << *it << " ";
	cout << endl;

	return 0;
}
