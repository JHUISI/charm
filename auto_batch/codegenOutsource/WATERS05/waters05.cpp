#include "sdlconfig.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;

int N = 2;

int l = 5;
int zz = 32;

int secparam = 80;

PairingGroup group(AES_SECURITY);

ZR & SmallExp(int bits) {
    big t = mirvar(0);
    bigbits(bits, t);

    ZR *z = new ZR(t);
    mr_free(t);
    return *z;
}

void setup(CharmList & mpk, CharmListG1 & u, CharmListG2 & ub, G1 & msk)
{
    ZR *alpha = group.init(ZR_t);
    G1 *h = group.init(G1_t);
    G1 *g1 = group.init(G1_t);
    G2 *g2 = group.init(G2_t);
    GT *A = group.init(GT_t);
    CharmListZR y0;
    ZR *y1t = group.init(ZR_t);
    ZR *y2t = group.init(ZR_t);
    G1 *u1t = group.init(G1_t);
    G1 *u2t = group.init(G1_t);
    G2 *u1b = group.init(G2_t);
    G2 *u2b = group.init(G2_t);
    *alpha = group.random(ZR_t);
    *h = group.random(G1_t);
    *g1 = group.random(G1_t);
    *g2 = group.random(G2_t);
    *A = group.exp(group.pair(*h, *g2), *alpha);
    for (int i = 0; i < l; i++)
    {
        y0[i] = group.random(ZR_t);
        u[i] = group.exp(*g1, y0[i]);
        ub[i] = group.exp(*g2, y0[i]);
    }
    *y1t = group.random(ZR_t);
    *y2t = group.random(ZR_t);
    *u1t = group.exp(*g1, *y1t);
    *u2t = group.exp(*g1, *y2t);
    *u1b = group.exp(*g2, *y1t);
    *u2b = group.exp(*g2, *y2t);
    msk = group.exp(*h, *alpha);
    mpk.append(*g1);
    mpk.append(*g2);
    mpk.append(*A);
    mpk.append(*u1t);
    mpk.append(*u2t);
    mpk.append(*u1b);
    mpk.append(*u2b);
    return;
}

void keygen(CharmList & mpk, CharmListG1 & u, G1 & msk, string & ID, CharmList & sk)
{
    G1 g1;
    G2 g2;
    GT A;
    G1 u1t;
    G1 u2t;
    G2 u1b;
    G2 u2b;
    CharmListZR k;  // = group.init(CharmListZR_t);
    G1 *dotProd = group.init(G1_t, 1);
    ZR *r = group.init(ZR_t);
    G1 *k1 = group.init(G1_t);
    G1 *k2 = group.init(G1_t);
    
    g1 = mpk[0].getG1();
    g2 = mpk[1].getG2();
    A = mpk[2].getGT();
    u1t = mpk[3].getG1();
    u2t = mpk[4].getG1();
    u1b = mpk[5].getG2();
    u2b = mpk[6].getG2();
    stringToInt(group, ID, l, zz, k);
    group.init(*dotProd, 1);
    for (int i = 0; i < l; i++)
    {
        *dotProd = group.mul(*dotProd, group.exp(u[i], k[i]));
    }
    *r = group.random(ZR_t);
    *k1 = group.mul(msk, group.exp(group.mul(u1t, *dotProd), *r));
    *k2 = group.exp(g1, group.neg(*r));
    sk.append(*k1);
    sk.append(*k2);
    return;
}

void sign(CharmList & mpk, CharmListG1 & u, CharmList & sk, string & M, G1 & S1, G1 & S2, G1 & S3)
{
    G1 g1;
    G2 g2;
    GT A;
    G1 u1t;
    G1 u2t;
    G2 u1b;
    G2 u2b;
    CharmListZR m; // = group.init(CharmListZR_t);
    G1 k1;
    G1 k2;
    ZR *s = group.init(ZR_t);
    G1 *dotProd1 = group.init(G1_t, 1);
    
    g1 = mpk[0].getG1();
    g2 = mpk[1].getG2();
    A = mpk[2].getGT();
    u1t = mpk[3].getG1();
    u2t = mpk[4].getG1();
    u1b = mpk[5].getG2();
    u2b = mpk[6].getG2();
    stringToInt(group, M, l, zz, m);
    
    k1 = sk[0].getG1();
    k2 = sk[1].getG1();
    *s = group.random(ZR_t);
    group.init(*dotProd1, 1);
    for (int i = 0; i < l; i++)
    {
        *dotProd1 = group.mul(*dotProd1, group.exp(u[i], m[i]));
    }
    S1 = group.mul(k1, group.exp(group.mul(u2t, *dotProd1), *s));
    S2 = k2;
    S3 = group.exp(g1, group.neg(*s));
    return;
}

bool verify(GT & A, G2 & g2, CharmListG2 & ub, G2 & u1b, G2 & u2b, string & ID, string & M, G1 & S1, G1 & S2, G1 & S3)
{
    CharmListZR kver; // = group.init(CharmListZR_t);
    CharmListZR mver; // = group.init(CharmListZR_t);
    G2 *dotProd2 = group.init(G2_t, 1);
    G2 *dotProd3 = group.init(G2_t, 1);
    stringToInt(group, ID, l, zz, kver);
    stringToInt(group, M, l, zz, mver);
    group.init(*dotProd2, 1);
    group.init(*dotProd3, 1);
    for (int i = 0; i < l; i++)
    {
        *dotProd2 = group.mul(*dotProd2, group.exp(ub[i], kver[i]));
        *dotProd3 = group.mul(*dotProd3, group.exp(ub[i], mver[i]));
    }
    if ( ( (group.mul(group.pair(S1, g2), group.mul(group.pair(S2, group.mul(u1b, *dotProd2)), group.pair(S3, group.mul(u2b, *dotProd3))))) == (A) ) )
    {
        return true;
    }
    else
    {
        return false;
    }
}

bool membership(GT & A, CharmListG1 & S1list, CharmListG1 & S2list, CharmListG1 & S3list, G2 & g2, G2 & u1b, G2 & u2b, CharmListG2 & ub)
{
    if ( ( (group.ismember(A)) == (false) ) )
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
    if ( ( (group.ismember(S3list)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(g2)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(u1b)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(u2b)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(ub)) == (false) ) )
    {
        return false;
    }
    return true;
}

void dividenconquer(CharmListZR & delta, int startSigNum, int endSigNum, list<int> & incorrectIndices, CharmListG1 & dotBCache, CharmListG1 & dotACache, CharmListZR & sumECache, CharmListG1 & dotDCache, GT & A, CharmListStr & IDlist, CharmListStr & Mlist, CharmListG1 & S1list, CharmListG1 & S2list, CharmListG1 & S3list, G2 & g2, G2 & u1b, G2 & u2b, CharmListG2 & ub)
{

    G1 *dotBLoopVal = group.init(G1_t, 1);
    G1 *dotALoopVal = group.init(G1_t, 1);
    ZR *sumELoopVal = group.init(ZR_t, 0);
    G1 *dotDLoopVal = group.init(G1_t, 1);
    GT *dotFLoopVal = group.init(GT_t, 1);
    G1 *dotCLoopVal = group.init(G1_t, 1);
    CharmListZR k; // = group.init(CharmListZR_t);
    CharmListZR m; // = group.init(CharmListZR_t);
    int midwayFloat = 0;
    int midway = 0;
    int midSigNum = 0;
    group.init(*dotBLoopVal, 1);
    group.init(*dotALoopVal, 1);
    group.init(*sumELoopVal, 0);
    group.init(*dotDLoopVal, 1);
    for (int z = startSigNum; z < endSigNum; z++)
    {
        *dotBLoopVal = group.mul(*dotBLoopVal, dotBCache[z]);
        *dotALoopVal = group.mul(*dotALoopVal, dotACache[z]);
        *sumELoopVal = group.add(*sumELoopVal, sumECache[z]);
        *dotDLoopVal = group.mul(*dotDLoopVal, dotDCache[z]);
    }
    group.init(*dotFLoopVal, 1);
    for (int y = 0; y < l; y++)
    {
        group.init(*dotCLoopVal, 1);
        for (int z = startSigNum; z < endSigNum; z++)
        {
            stringToInt(group, IDlist[z], l, zz, k); // need to fix refs in SDL
            stringToInt(group, Mlist[z], l, zz, m); // need to fix refs in SDL
            *dotCLoopVal = group.mul(*dotCLoopVal, group.mul(group.exp(S2list[z], group.mul(delta[z], k[y])), group.exp(S3list[z], group.mul(delta[z], m[y]))));
        }
        *dotFLoopVal = group.mul(*dotFLoopVal, group.pair(*dotCLoopVal, ub[y]));
    }
    if ( ( (group.mul(group.pair(*dotALoopVal, g2), group.mul(group.mul(group.pair(*dotBLoopVal, u1b), *dotFLoopVal), group.pair(*dotDLoopVal, u2b)))) == (group.exp(A, *sumELoopVal)) ) )
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
        dividenconquer(delta, startSigNum, midway, incorrectIndices, dotBCache, dotACache, sumECache, dotDCache, A, IDlist, Mlist, S1list, S2list, S3list, g2, u1b, u2b, ub);
        dividenconquer(delta, midSigNum, endSigNum, incorrectIndices, dotBCache, dotACache, sumECache, dotDCache, A, IDlist, Mlist, S1list, S2list, S3list, g2, u1b, u2b, ub);
    }
    return;
}

bool batchverify(GT & A, CharmListStr & IDlist, CharmListStr & Mlist, CharmListG1 & S1list, CharmListG1 & S2list, CharmListG1 & S3list, G2 & g2, G2 & u1b, G2 & u2b, CharmListG2 & ub, list<int> & incorrectIndices)
{
    CharmListZR delta;
    CharmListG1 dotBCache;
    CharmListG1 dotACache;
    CharmListZR sumECache;
    CharmListG1 dotDCache;
    for (int z = 0; z < N; z++)
    {
        delta[z] = SmallExp(secparam);
    }
    if ( ( (membership(A, S1list, S2list, S3list, g2, u1b, u2b, ub)) == (false) ) )
    {
        return false;
    }
    for (int z = 0; z < N; z++)
    {
        dotBCache[z] = group.exp(S2list[z], delta[z]);
        dotACache[z] = group.exp(S1list[z], delta[z]);
        sumECache[z] = delta[z];
        dotDCache[z] = group.exp(S3list[z], delta[z]);
    }
    dividenconquer(delta, 0, N, incorrectIndices, dotBCache, dotACache, sumECache, dotDCache, A, IDlist, Mlist, S1list, S2list, S3list, g2, u1b, u2b, ub);
    return true;
}

int main()
{
    G1 msk;
    G2 g2, u1b, u2b;
    GT A;
    CharmList mpk, sk;
    CharmListG1 u;
    CharmListG2 ub;
    string id0 = "janedoe@email.com";
    string id1 = "johnsmith@email.com";
    string m0 = "message0";
    string m1 = "message1";
    CharmListG1 S1list, S2list, S3list;
    bool status;
     
    setup(mpk, u, ub, msk);

    
    keygen(mpk, u, msk, id0, sk);

    sign(mpk, u, sk, m0, S1list[0], S2list[0], S3list[0]);
    sign(mpk, u, sk, m1, S1list[1], S2list[1], S3list[1]);
    g2 = mpk[1].getG2();
    A = mpk[2].getGT();
    u1b = mpk[5].getG2();
    u2b = mpk[6].getG2();

    status = verify(A, g2, ub, u1b, u2b, id0, m0, S1list[0], S2list[0], S3list[0]);

    if(status == true)
       cout << "True!" << endl;
    else
       cout << "False!" << endl;

    status = verify(A, g2, ub, u1b, u2b, id0, m1, S1list[1], S2list[1], S3list[1]);

    if(status == true)
       cout << "True!" << endl;
    else
       cout << "False!" << endl;


    list<int> incorrectIndices;
    CharmListStr IDlist, Mlist;
    IDlist[0] = id0;
    IDlist[1] = id0;
    Mlist[0] = m0;
    Mlist[1] = m1; 
    batchverify(A, IDlist, Mlist, S1list, S2list, S3list, g2, u1b, u2b, ub, incorrectIndices);
    cout << "Incorrect indices: ";
    for (list<int>::iterator it = incorrectIndices.begin(); it != incorrectIndices.end(); it++)
             cout << *it << " ";
    cout << endl;

    return 0;
}
