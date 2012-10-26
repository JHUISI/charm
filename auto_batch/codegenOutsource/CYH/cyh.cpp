#include "sdlconfig.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;

int N = 2;

int l = 2;

int secparam = 80;

PairingGroup group(AES_SECURITY);

ZR & SmallExp(int bits) {
    big t = mirvar(0);
    bigbits(bits, t);

    ZR *z = new ZR(t);
    mr_free(t);
    return *z;
}

void setup(G2 & P, G2 & g, ZR & alpha)
{
    g = group.random(G2_t);
    alpha = group.random(ZR_t);
    P = group.exp(g, alpha);
    return;
}

void concat(CharmListStr & ID_list, string & L)
{
    int l = 0;
    L = "";
    l = ID_list.length();
    for (int y = 0; y < l; y++)
    {
        L = (L + ID_list[y]);
    }
    return;
}

void keygen(ZR & alpha, string ID, G1 & pk, G1 & sk)
{
    sk = group.exp(group.hashListToG1(ID), alpha);
    pk = group.hashListToG1(ID);
    return;
}

bool isNotEqual(string value1, string value2)
{
    string s1 = value1;
    string s2 = value2;
    if (strcmp(s1.c_str(), s2.c_str()) != 0)
	return true;
    else
	return false;
}

void sign(string ID, CharmListStr & ID_list, G1 & pk, G1 & sk, string M, string & Lt, CharmListG1 & pklist, CharmListG1 & u, G1 & S)
{
    CharmListZR h;
    int s = 0;
    ZR *r = group.init(ZR_t);
    G1 *dotProd = group.init(G1_t, 1);
    concat(ID_list, Lt); // need to change to follow C++ semantics
    for (int i = 0; i < l; i++)
    {
        if ( ( isNotEqual(ID, ID_list[i]) ) ) // add this call to api
        {
            u[i] = group.random(G1_t);
            h[i] = group.hashListToZR((Element(M) + Element(Lt) + Element(u[i])));
        }
        else
        {
            s = i;
        }
    }
    *r = group.random(ZR_t);
    for (int y = 0; y < l; y++)
    {
        pklist[y] = group.hashListToG1(ID_list[y]);
    }
    group.init(*dotProd, 1);
    for (int i = 0; i < l; i++)
    {
        if ( ( isNotEqual(ID, ID_list[i]) ) )
        {
            *dotProd = group.mul(*dotProd, group.mul(u[i], group.exp(pklist[i], h[i])));
        }
    }
    u[s] = group.mul(group.exp(pk, *r), group.exp(*dotProd, -1));
    h[s] = group.hashListToZR((Element(M) + Element(Lt) + Element(u[s])));
    S = group.exp(sk, group.add(h[s], *r));
    return;
}

bool verify(string & Lt, CharmListG1 & pklist, G2 & P, G2 & g, string M, CharmListG1 & u, G1 & S)
{
    CharmListZR h;
    G1 *dotProd = group.init(G1_t, 1);
    for (int y = 0; y < l; y++)
    {
        h[y] = group.hashListToZR((Element(M) + Element(Lt) + Element(u[y])));
    }
    group.init(*dotProd, 1);
    for (int y = 0; y < l; y++)
    {
        *dotProd = group.mul(*dotProd, group.mul(u[y], group.exp(pklist[y], h[y])));
    }
    if ( ( (group.pair(*dotProd, P)) == (group.pair(S, g)) ) )
    {
        return true;
    }
    else
    {
        return false;
    }
}

bool membership(G2 & P, CharmListG1 & Slist, G2 & g, CharmListG1 & pklist, CharmMetaListG1 & ulist)
{
    if ( ( (group.ismember(P)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(Slist)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(g)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(pklist)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(ulist)) == (false) ) )
    {
        return false;
    }
    return true;
}

void dividenconquer(CharmListZR & delta, int startSigNum, int endSigNum, list<int> & incorrectIndices, CharmListG1 & dotBCache, CharmListG1 & dotCCache, G2 & P, G2 & g)
{
    G1 *dotBLoopVal = group.init(G1_t, 1);
    G1 *dotCLoopVal = group.init(G1_t, 1);
    int midwayFloat = 0;
    int midway = 0;
    int midSigNum = 0;
    group.init(*dotBLoopVal, 1);
    group.init(*dotCLoopVal, 1);
    for (int z = startSigNum; z < endSigNum; z++)
    {
        *dotBLoopVal = group.mul(*dotBLoopVal, dotBCache[z]);
        *dotCLoopVal = group.mul(*dotCLoopVal, dotCCache[z]);
    }
    if ( ( (group.pair(*dotBLoopVal, P)) == (group.pair(*dotCLoopVal, g)) ) )
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
        dividenconquer(delta, startSigNum, midway, incorrectIndices, dotBCache, dotCCache, P, g);
        dividenconquer(delta, midSigNum, endSigNum, incorrectIndices, dotBCache, dotCCache, P, g);
    }
    return;
}

bool batchverify(string & Lt, CharmListStr & Mlist, G2 & P, CharmListG1 & Slist, G2 & g, CharmListG1 & pklist, CharmMetaListG1 & ulist, list<int> & incorrectIndices)
{
    CharmListZR delta;
    G1 *dotALoopVal = group.init(G1_t, 1);
    ZR *h = group.init(ZR_t);
    CharmListG1 dotBCache;
    CharmListG1 dotCCache;
    for (int z = 0; z < N; z++)
    {
        delta[z] = SmallExp(secparam);
    }
    if ( ( (membership(P, Slist, g, pklist, ulist)) == (false) ) )
    {
        return false;
    }
    for (int z = 0; z < N; z++)
    {
        group.init(*dotALoopVal, 1);
        for (int y = 0; y < l; y++)
        {
            *h = group.hashListToZR((Element(Mlist[z]) + Element(Lt) + Element(ulist[z][y])));
            *dotALoopVal = group.mul(*dotALoopVal, group.mul(group.exp(ulist[z][y], delta[z]), group.exp(pklist[y], group.mul(*h, delta[z]))));
        }
        dotBCache[z] = *dotALoopVal;
        dotCCache[z] = group.exp(Slist[z], delta[z]);
    }
    dividenconquer(delta, 0, N, incorrectIndices, dotBCache, dotCCache, P, g);
    return true;
}

int main()
{
    G2 P;
    G2 g;
    ZR alpha;

    setup(P, g, alpha);

    string id0 = "alice";
    string id1 = "bob";

    string m0 = "message 0";
    string m1 = "message 1";
    CharmListStr ID_list;
    ID_list.append(id0);
    ID_list.append(id1);

    G1 pk;
    G1 sk;
    string Lt;
    CharmListG1 pklist;
    CharmListG1 u0, u1;
    CharmMetaListG1 ulist;
    G1 S;
    CharmListG1 Slist;

    keygen(alpha, id0, pk, sk);
    sign(id0, ID_list, pk, sk, m0, Lt, pklist, u0, Slist[0]);
    sign(id0, ID_list, pk, sk, m1, Lt, pklist, u1, Slist[1]);

    bool status = verify(Lt, pklist, P, g, m0, u0, Slist[0]);

    if (status == true)
  	cout << "True!" << endl;
    else
	cout << "FALSE!!" << endl;

    bool status2 = verify(Lt, pklist, P, g, m1, u1, Slist[1]);

    if (status2 == true)
  	cout << "True!" << endl;
    else
	cout << "FALSE!!" << endl;

    list<int> incorrectIndices;
    CharmListStr Mlist;
    Mlist[0] = m0;
    Mlist[1] = m1;
    ulist[0] = u0;
    ulist[1] = u1;
    
    batchverify(Lt, Mlist, P, Slist, g, pklist, ulist, incorrectIndices);
    cout << "Incorrect indices: ";
    for (list<int>::iterator it = incorrectIndices.begin(); it != incorrectIndices.end(); it++)
             cout << *it << " ";
    cout << endl;

    return 0;
}
