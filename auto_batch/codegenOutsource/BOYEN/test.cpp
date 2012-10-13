#include "sdlconfig.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;

int N = 100;

int secparam = 80;

PairingGroup group(AES_SECURITY);

ZR & SmallExp(int bits) {
    big t = mirvar(0);
    bigbits(bits, t);

    ZR *z = new ZR(t);
    mr_free(t);
    return *z;
}

void setup(CharmList & mpk)
{
    G1 *g1 = group.init(G1_t);
    G2 *g2 = group.init(G2_t);
    ZR *a0 = group.init(ZR_t);
    ZR *b0 = group.init(ZR_t);
    ZR *c0 = group.init(ZR_t);
    G1 *A0 = group.init(G1_t);
    G1 *B0 = group.init(G1_t);
    G1 *C0 = group.init(G1_t);
    G2 *At0 = group.init(G2_t);
    G2 *Bt0 = group.init(G2_t);
    G2 *Ct0 = group.init(G2_t);
    *g1 = group.random(G1_t);
    *g2 = group.random(G2_t);
    *a0 = group.random(ZR_t);
    *b0 = group.random(ZR_t);
    *c0 = group.random(ZR_t);
    *A0 = group.exp(*g1, *a0);
    *B0 = group.exp(*g1, *b0);
    *C0 = group.exp(*g1, *c0);
    *At0 = group.exp(*g2, *a0);
    *Bt0 = group.exp(*g2, *b0);
    *Ct0 = group.exp(*g2, *c0);
    mpk.append(A0);
    mpk.append(B0);
    mpk.append(C0);
    mpk.append(At0);
    mpk.append(Bt0);
    mpk.append(Ct0);
    return;
}

void keygen(G1 & g1, G2 & g2, CharmList & pk, CharmList & sk)
{
    ZR *a = group.init(ZR_t);
    ZR *b = group.init(ZR_t);
    ZR *c = group.init(ZR_t);
    G1 *A = group.init(G1_t);
    G2 *At = group.init(G2_t);
    G1 *B = group.init(G1_t);
    G2 *Bt = group.init(G2_t);
    G1 *C = group.init(G1_t);
    G2 *Ct = group.init(G2_t);
    *a = group.random(ZR_t);
    *b = group.random(ZR_t);
    *c = group.random(ZR_t);
    *A = group.exp(g1, *a);
    *At = group.exp(g2, *a);
    *B = group.exp(g1, *b);
    *Bt = group.exp(g2, *b);
    *C = group.exp(g1, *c);
    *Ct = group.exp(g2, *c);
    sk.append(a);
    sk.append(b);
    sk.append(c);
    pk.append(A);
    pk.append(B);
    pk.append(C);
    pk.append(At);
    pk.append(Bt);
    pk.append(Ct);
    return;
}

void sign(G1 & g1, CharmList & mpk, CharmListG1 & Alist, CharmListG1 & Blist, CharmListG1 & Clist, CharmList & sk, string M, int l, CharmListG1 & S, CharmListZR & t)
{
