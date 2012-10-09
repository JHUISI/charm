#include "sdlconfig.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;

int N = 2;

int secparam = 80;

PairingGroup group(AES_SECURITY);

ZR & SmallExp(int bits) {
    big t = mirvar(0);
    bigbits(bits, t);

    ZR *z = new ZR(t);
    mr_free(t);
    return *z;
}

void setup(G2 & g2, ZR & alpha, G2 & P)
{
    g2 = group.random(G2_t);
    alpha = group.random(ZR_t);
    P = group.exp(g2, alpha);
    return;
}

void keygen(ZR & alpha, string ID, G1 & pk, G1 & sk)
{
    sk = group.exp(group.hashListToG1(ID), alpha);
    pk = group.hashListToG1(ID);
    return;
}

void sign(G1 & pk, G1 & sk, string M, G2 & g2, GT & S1, G1 & S2)
{
    G1 *h = new G1();
    ZR *s = new ZR();
    ZR *a = new ZR();
    *h = group.random(G1_t);
    *s = group.random(ZR_t);
    S1 = group.exp(group.pair(*h, g2), *s);
    *a = group.hashListToZR(( Element(M) + Element(S1) ));
    S2 = group.mul(group.exp(sk, *a), group.exp(*h, *s));
    return;
}

bool verify(G2 & P, G2 & g2, G1 & pk, string M, GT & S1, G1 & S2)
{
    ZR *a = new ZR();
    *a = group.hashListToZR(( Element(M) + Element(S1) ));
    if ( ( (group.pair(S2, g2)) == (group.mul(group.exp(group.pair(pk, P), *a), S1)) ) )
    {
        return true;
    }
    else
    {
        return false;
    }
}

bool membership(G2 & g2, CharmListG1 & pklist, CharmListStr & Mlist, G2 & P, CharmListGT & S1list, CharmListG1 & S2list)
{
    if ( ( (group.ismember(g2)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(pklist)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(Mlist)) == (false) ) )
    {
        return false;
    }
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
    return true;
}

void dividenconquer(CharmListZR & delta, int startSigNum, int endSigNum, list<int> & incorrectIndices, CharmListG1 & dotACache, CharmListG1 & dotBCache, CharmListGT & dotCCache, G2 & g2, CharmListG1 & pklist, CharmListStr & Mlist, G2 & P, CharmListGT & S1list, CharmListG1 & S2list)
{
    G1 *dotALoopVal = new G1();
    G1 *dotBLoopVal = new G1();
    GT *dotCLoopVal = new GT();
    int midwayFloat = 0;
    int midway = 0;
    int midSigNum = 0;
    for (int z = startSigNum; z < endSigNum; z++)
    {
        *dotALoopVal = group.mul(*dotALoopVal, dotACache[z]);
        *dotBLoopVal = group.mul(*dotBLoopVal, dotBCache[z]);
        *dotCLoopVal = group.mul(*dotCLoopVal, dotCCache[z]);
    }
    if ( ( (group.pair(*dotALoopVal, g2)) == (group.mul(group.pair(*dotBLoopVal, P), *dotCLoopVal)) ) )
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
        dividenconquer(delta, startSigNum, midway, incorrectIndices, dotACache, dotBCache, dotCCache, g2, pklist, Mlist, P, S1list, S2list);
        dividenconquer(delta, midSigNum, endSigNum, incorrectIndices, dotACache, dotBCache, dotCCache, g2, pklist, Mlist, P, S1list, S2list);
    }
    return;
}

bool batchverify(G2 & g2, CharmListG1 & pklist, CharmListStr & Mlist, G2 & P, CharmListGT & S1list, CharmListG1 & S2list, list<int> & incorrectIndices)
{
    CharmListZR delta;
    ZR *a = new ZR();
    CharmListG1 dotACache;
    CharmListG1 dotBCache;
    CharmListGT dotCCache;
    for (int z = 0; z < N; z++)
    {
        delta[z] = SmallExp(secparam);
    }
    if ( ( (membership(g2, pklist, Mlist, P, S1list, S2list)) == (false) ) )
    {
        return false;
    }
    for (int z = 0; z < N; z++)
    {
        *a = group.hashListToZR(( Element(Mlist[z]) + Element(S1list[z]) ));
        dotACache[z] = group.exp(S2list[z], delta[z]);
        dotBCache[z] = group.exp(pklist[z], group.mul(*a, delta[z]));
        dotCCache[z] = group.exp(S1list[z], delta[z]);
    }
    dividenconquer(delta, 0, N, incorrectIndices, dotACache, dotBCache, dotCCache, g2, pklist, Mlist, P, S1list, S2list);
    return true;
}

int main()
{
   G1 pk, sk;
   GT S1;
   G1 S2;
   GT S1_1;
   G1 S2_1;
   G2 g2, P;
   ZR alpha;
   string ID = "<somedude>@email.com";
   string MI = "test1";
   string MII = "test2";

   setup(g2, alpha, P);

   keygen(alpha, ID, pk, sk);

   cout << "sk :=" << convert_str(sk) << endl;

   sign(pk, sk, MI, g2, S1, S2);
   sign(pk, sk, MII, g2, S1_1, S2_1);

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

   batchverify(g2, pklist, Mlist, P, S1list, S2list, incorrectIndices);
   cout << "Incorrect indices: ";
   for (list<int>::iterator it = incorrectIndices.begin(); it != incorrectIndices.end(); it++)
        cout << *it << " ";
   cout << endl;

   return 0;
}
