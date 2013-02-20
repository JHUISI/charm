#include "DFA/DFA_ASYMM.h"

void Dfa12::setup(CharmListStr & alphabet, CharmList & mpk, G1 & msk)
{
    G1 gG1;
    G2 gG2;
    ZR z;
    G1 zG1;
    G2 zG2;
    ZR hstart;
    G1 hstartG1;
    G2 hstartG2;
    ZR hend;
    G1 hendG1;
    G2 hendG2;
    int A = 0;
    string a;
    ZR ha;
    CharmListG1 hG1;
    CharmListG2 hG2;
    ZR alpha;
    GT egg = group.init(GT_t);
    gG1 = group.random(G1_t);
    gG2 = group.random(G2_t);
    z = group.random(ZR_t);
    zG1 = group.exp(gG1, z);
    zG2 = group.exp(gG2, z);
    hstart = group.random(ZR_t);
    hstartG1 = group.exp(gG1, hstart);
    hstartG2 = group.exp(gG2, hstart);
    hend = group.random(ZR_t);
    hendG1 = group.exp(gG1, hend);
    hendG2 = group.exp(gG2, hend);
    A = alphabet.length();
    for (int i = 0; i < A; i++)
    {
        a = dfaUtil.getString(alphabet[i]);
        ha = group.random(ZR_t);
        hG1.insert(a, group.exp(gG1, ha));
        hG2.insert(a, group.exp(gG2, ha));
    }
    alpha = group.random(ZR_t);
    egg = group.exp(group.pair(gG1, gG2), alpha);
    msk = group.exp(gG1, group.neg(alpha));
    mpk.insert(0, egg);
    mpk.insert(1, gG1);
    mpk.insert(2, gG2);
    mpk.insert(3, zG1);
    mpk.insert(4, zG2);
    mpk.insert(5, hG1);
    mpk.insert(6, hG2);
    mpk.insert(7, hstartG1);
    mpk.insert(8, hstartG2);
    mpk.insert(9, hendG1);
    mpk.insert(10, hendG2);
    return;
}

void Dfa12::keygen(CharmList & mpk, G1 & msk, CharmListInt & Q, CharmMetaListInt & T, CharmListInt & F, ZR & bf0, CharmList & skBlinded)
{
