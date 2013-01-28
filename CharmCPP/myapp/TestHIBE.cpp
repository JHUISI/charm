#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;

int l = 5; // output non-keyword global vars by default
int z = 32;

PairingGroup group(MNT160);

void setup(int l, int z, CharmList & mpk, CharmList & mk)
{
    ZR alpha = group.init(ZR_t);
    ZR beta = group.init(ZR_t);
    G1 g = group.init(G1_t);
    G2 gb = group.init(G2_t);
    G1 g1 = group.init(G1_t);
    G2 g1b = group.init(G2_t);
    CharmListZR delta;
    CharmListG1 h;
    CharmListG2 hb;
    G2 g0b = group.init(G2_t);
    GT v = group.init(GT_t);
    alpha = group.random(ZR_t);
    beta = group.random(ZR_t);
    g = group.random(G1_t);
    gb = group.random(G2_t);
    g1 = group.exp(g, alpha);
    g1b = group.exp(gb, alpha);
    for (int y = 0; y < l; y++)
    {
        delta.insert(y, group.random(ZR_t));
        h.insert(y, group.exp(g, delta[y]));
        hb.insert(y, group.exp(gb, delta[y]));
    }
    g0b = group.exp(gb, group.mul(alpha, beta));
    v = group.pair(g, g0b);
    mpk.insert(0, g);
    mpk.insert(1, g1);
    mpk.insert(2, h);
    mpk.insert(3, gb);
    mpk.insert(4, g1b);
    mpk.insert(5, hb);
    mpk.insert(6, v);
    mk.insert(0, g0b);
    return;
}

void keygen(CharmList & mpk, CharmList & mk, string & id, CharmList & pkBlinded, ZR & blindingFactor0Blinded, CharmList & skBlinded)
{
    ZR zz = group.init(ZR_t);
    G1 g;
    G1 g1;
    CharmListG1 h;
    G2 gb;
    G2 g1b;
    CharmListG2 hb;
    GT v;
    G2 g0b;
    CharmListZR Id;
    CharmListZR r;
    CharmListG2 d;
    CharmListG2 dBlinded; // = group.init(G2_t); // fix type from G2 to listG2
    G2 d0DotProdCalc = group.init(G2_t);
    G2 d0 = group.init(G2_t);
    G2 d0Blinded = group.init(G2_t);
    CharmList pk;
    blindingFactor0Blinded = group.random(ZR_t);
    zz = group.random(ZR_t);
    
    g = mpk[0].getG1();
    g1 = mpk[1].getG1();
    h = mpk[2].getListG1();
    gb = mpk[3].getG2();
    g1b = mpk[4].getG2();
    hb = mpk[5].getListG2();
    v = mpk[6].getGT();
    
    g0b = mk[0].getG2();
    Id = stringToInt(group, id, z, l);
    for (int y = 0; y < 5; y++)
    {
        r.insert(y, group.random(ZR_t));
        d.insert(y, group.exp(gb, r[y]));
    }
    dBlinded = d;
    //;
    for (int y = 0; y < 5; y++)
    {
        d0DotProdCalc = group.mul(d0DotProdCalc, group.exp(group.mul(group.exp(g1b, Id[y]), hb[y]), r[y]));
    }
    d0 = group.mul(g0b, d0DotProdCalc);
    d0Blinded = group.exp(d0, group.div(1, blindingFactor0Blinded));
    pk.insert(0, id);
    pkBlinded = pk;
    skBlinded.insert(0, d0Blinded);
    skBlinded.insert(1, dBlinded);
    return;
}

void encrypt(CharmList & mpk, CharmList & pk, GT & M, CharmList & ct)
{
    G1 g;
    G1 g1;
    CharmListG1 h;
    G2 gb;
    G2 g1b;
    CharmListG2 hb;
    GT v;
    string id;
    ZR s = group.init(ZR_t);
    GT A = group.init(GT_t);
    G1 B = group.init(G1_t);
    CharmListZR Id2;
    CharmListG1 C;
    
    g = mpk[0].getG1();
    g1 = mpk[1].getG1();
    h = mpk[2].getListG1();
    gb = mpk[3].getG2();
    g1b = mpk[4].getG2();
    hb = mpk[5].getListG2();
    v = mpk[6].getGT();
    
    id = pk[0].strPtr;
    s = group.random(ZR_t);
    A = group.mul(M, group.exp(v, s));
    B = group.exp(g, s);
    Id2 = stringToInt(group, id, z, l);
    for (int y = 0; y < 5; y++)
    {
        C.insert(y, group.exp(group.mul(group.exp(g1, Id2[y]), h[y]), s));
    }
    ct.insert(0, A);
    ct.insert(1, B);
    ct.insert(2, C);
    return;
}

void transform(CharmList & pk, CharmList & skBlinded, CharmList & ct, CharmList & transformOutputList)
{
    G2 d0Blinded;
    CharmListG2 dBlinded; // fix type
    GT A;
    G1 B;
    CharmListG1 C;
    
    d0Blinded = skBlinded[0].getG2();
    dBlinded = skBlinded[1].getListG2();
    
    A = ct[0].getGT();
    B = ct[1].getG1();
    C = ct[2].getListG1();
    transformOutputList.insert(0, group.mul(group.pair(C[0], dBlinded[0]), group.mul(group.pair(C[1], dBlinded[1]), group.mul(group.pair(C[2], dBlinded[2]), group.mul(group.pair(C[3], dBlinded[3]), group.pair(C[4], dBlinded[4]))))));
    transformOutputList.insert(1, group.pair(B, d0Blinded));
    transformOutputList.insert(2, A);
    return;
}

void decout(CharmList & pk, CharmList & transformOutputList, ZR & blindingFactor0Blinded, GT & M)
{
    GT D = group.init(GT_t);
    GT A = group.init(GT_t);
    GT denominator = group.init(GT_t);
    GT fraction = group.init(GT_t);
    D = transformOutputList[0].getGT();
    A = transformOutputList[2].getGT();
    denominator = group.exp(transformOutputList[1].getGT(), blindingFactor0Blinded);
    fraction = group.mul(D, group.exp(denominator, -1));
    M = group.mul(A, fraction);
    return;
}

int main()
{
	CharmList mk, mpk, pk, skBlinded, ct, transformOutputList;
	string id = "john@example.com";
	ZR blindingFactor0Blinded;
	GT M, newM;

	setup(l, z, mpk, mk);

	keygen(mpk, mk, id, pk, blindingFactor0Blinded, skBlinded);

	M = group.random(GT_t);
	encrypt(mpk, pk, M, ct);

	transform(pk, skBlinded, ct, transformOutputList);

	decout(pk, transformOutputList, blindingFactor0Blinded, newM);
    cout << convert_str(M) << endl;
    cout << convert_str(newM) << endl;
    if(M == newM) {
      cout << "Successful Decryption!" << endl;
    }
    else {
      cout << "FAILED Decryption." << endl;
    }
    return 0;
}
