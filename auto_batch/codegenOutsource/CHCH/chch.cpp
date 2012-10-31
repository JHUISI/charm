#include "sdlconfig.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;

int N = 2;

int secparam = 80;

PairingGroup group(AES_SECURITY);

void setup(G2 & g2, ZR & alpha, G2 & P)
{
    g2 = group.random(G2_t);
    alpha = group.random(ZR_t);
    P = group.exp(g2, alpha);
    return;
}

void keygen(ZR & alpha, string & ID, G1 & pk, G1 & sk)
{
    sk = group.exp(group.hashListToG1(ID), alpha);
    pk = group.hashListToG1(ID);
    return;
}

void sign(G1 & pk, G1 & sk, string & M, G1 & S1, G1 & S2)
{
    ZR s = group.init(ZR_t);
    ZR a = group.init(ZR_t);
    s = group.random(ZR_t);
    S1 = group.exp(pk, s);
    a = group.hashListToZR((Element(M) + Element(S1)));
    S2 = group.exp(sk, group.add(s, a));
    return;
}

bool verify(G2 & P, G2 & g2, G1 & pk, string & M, G1 & S1, G1 & S2)
{
    ZR a = group.init(ZR_t);
    a = group.hashListToZR((Element(M) + Element(S1)));
    if ( ( (group.pair(S2, g2)) == (group.pair(group.mul(S1, group.exp(pk, a)), P)) ) )
    {
        return true;
    }
    else
    {
        return false;
    }
}

bool membership(G2 & P, CharmListG1 & S1list, CharmListG1 & S2list, G2 & g2, CharmListG1 & pklist)
{
    if ( ( (group.ismember(P)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(S1list)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(S2list)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(g2)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(pklist)) == (false) ) )
    {
        return false;
    }
    return true;
}

void dividenconquer(CharmListZR & delta, int startSigNum, int endSigNum, list<int> & incorrectIndices, CharmListG1 & dotACache, CharmListG1 & dotBCache, G2 & g2, G2 & P)
{
    G1 dotALoopVal = group.init(G1_t, 1);
    G1 dotBLoopVal = group.init(G1_t, 1);
    int midwayFloat = 0;
    int midway = 0;
    int midSigNum = 0;
    group.init(dotALoopVal, 1);
    group.init(dotBLoopVal, 1);
    for (int z = startSigNum; z < endSigNum; z++)
    {
        dotALoopVal = group.mul(dotALoopVal, dotACache[z]);
        dotBLoopVal = group.mul(dotBLoopVal, dotBCache[z]);
    }
    if ( ( (group.pair(dotALoopVal, g2)) == (group.pair(dotBLoopVal, P)) ) )
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
        dividenconquer(delta, startSigNum, midway, incorrectIndices, dotACache, dotBCache, g2, P);
        dividenconquer(delta, midSigNum, endSigNum, incorrectIndices, dotACache, dotBCache, g2, P);
    }
    return;
}

bool batchverify(CharmListStr & Mlist, G2 & P, CharmListG1 & S1list, CharmListG1 & S2list, G2 & g2, CharmListG1 & pklist, list<int> & incorrectIndices)
{
    CharmListZR delta;
    ZR a = group.init(ZR_t);
    CharmListG1 dotACache;
    CharmListG1 dotBCache;
    for (int z = 0; z < N; z++)
    {
        delta[z] = SmallExp(secparam);
    }
    if ( ( (membership(P, S1list, S2list, g2, pklist)) == (false) ) )
    {
        return false;
    }
    for (int z = 0; z < N; z++)
    {
        a = group.hashListToZR((Element(Mlist[z]) + Element(S1list[z])));
        dotACache[z] = group.exp(S2list[z], delta[z]);
        dotBCache[z] = group.mul(group.exp(S1list[z], delta[z]), group.exp(pklist[z], group.mul(a, delta[z])));
    }
    dividenconquer(delta, 0, N, incorrectIndices, dotACache, dotBCache, g2, P);
    return true;
}

int main()
{
	   G1 pk, sk;
	   G1 S1, S2;
	   G1 S1_1, S2_1;
	   G2 g2, P;
	   ZR alpha;
	   string ID = "<somedude>@email.com";
	   string MI = "test1";
	   string MII = "test2";

	   setup(g2, alpha, P);

	   keygen(alpha, ID, pk, sk);

	   cout << "sk :=" << convert_str(sk) << endl;

	   sign(pk, sk, MI, S1, S2);
	   sign(pk, sk, MII, S1_1, S2_1);

	   cout << "S1 := " << convert_str(S1) << endl;
	   cout << "S2 := " << convert_str(S2) << endl;

	   if(verify(P, g2, pk, MI, S1, S2))
		   cout << "Successful Verification!!" << endl;
	   else
		   cout << "FAILED verification!!" << endl;

	   list<int> incorrectIndices;
	   CharmListG1 pklist;
	   CharmListStr Mlist;
	   CharmListG1 S1list;
	   CharmListG1 S2list;

	   pklist[0] = pk;
	   pklist[1] = pk;
	   Mlist[0] = MI;
	   Mlist[1] = MII;
	   S1list[0] = S1;
	   S1list[1] = S1_1;
	   S2list[0] = S2;
	   S2list[1] = S2_1;

	   batchverify(Mlist, P, S1list, S2list, g2, pklist, incorrectIndices);
	   cout << "Incorrect indices: ";
	   for (list<int>::iterator it = incorrectIndices.begin(); it != incorrectIndices.end(); it++)
	        cout << *it << " ";
	   cout << endl;

	   return 0;
}
