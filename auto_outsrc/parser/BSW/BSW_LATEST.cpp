#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;

PairingGroup group(AES_SECURITY);

SecretUtil util;

void setup(CharmList & mk, CharmList & pk)
{
    G1 g = group.init(G1_t);
    ZR alpha = group.init(ZR_t);
    ZR beta = group.init(ZR_t);
    G1 h = group.init(G1_t);
    G1 i = group.init(G1_t);
    GT egg = group.init(GT_t);
    g = group.random(G1_t);
    alpha = group.random(ZR_t);
    beta = group.random(ZR_t);
    h = group.exp(g, beta);
    i = group.exp(g, alpha);
    egg = group.exp(group.pair(g, g), alpha);
    mk.insert(0, beta);
    mk.insert(1, i);
    pk.insert(0, g);
    pk.insert(1, h);
    pk.insert(2, egg);
    return;
}

void keygen(CharmList & pk, CharmList & mk, CharmListStr & S, ZR & bf0, CharmList & skBlinded)
{
    G1 g;
    G1 h;
    GT egg;
    ZR beta;
    G1 i;
    ZR r = group.init(ZR_t);
    G1 p0 = group.init(G1_t);
    G1 D = group.init(G1_t);
    G1 DBlinded = group.init(G1_t);
    int Y = 0;
    ZR sUSy = group.init(ZR_t);
    string y0;
    CharmListG1 Dj;
    CharmListG1 Djp;
    CharmListZR blindingFactorDjBlinded;
    CharmListG1 DjBlinded;
    CharmListZR blindingFactorDjpBlinded;
    CharmListG1 DjpBlinded;
    bf0 = group.random(ZR_t);
    
    g = pk[0].getG1();
    h = pk[1].getG1();
    egg = pk[2].getGT();
    
    beta = mk[0].getZR();
    i = mk[1].getG1();
    r = group.random(ZR_t);
    p0 = group.exp(h, r);
    D = group.exp(group.mul(i, p0), group.div(1, beta));
    DBlinded = group.exp(D, group.div(1, bf0));
    Y = S.length();
    for (int y = 0; y < Y; y++)
    {
        sUSy = group.random(ZR_t);
        y0 = S[y];
        Dj.insert(y0, group.mul(p0, group.exp(group.hashListToG1(y0), sUSy)));
        Djp.insert(y0, group.exp(g, sUSy));
    }
    CharmList Dj_Keys_List = Dj.keys();
    int Dj_List_Length = Dj.length();
    for (int y_Temp_Loop_Var = 0; y_Temp_Loop_Var < Dj_List_Length; y_Temp_Loop_Var++)
    {
        y = Dj_Keys_List[y_Temp_Loop_Var];
        blindingFactorDjBlinded.insert(y, bf0);
        DjBlinded.insert(y, group.exp(Dj[y], group.div(1, blindingFactorDjBlinded[y].getZR())));
    }
    CharmList Djp_Keys_List = Djp.keys();
    int Djp_List_Length = Djp.length();
    for (int y_Temp_Loop_Var = 0; y_Temp_Loop_Var < Djp_List_Length; y_Temp_Loop_Var++)
    {
        y = Djp_Keys_List[y_Temp_Loop_Var];
        blindingFactorDjpBlinded.insert(y, bf0);
        DjpBlinded.insert(y, group.exp(Djp[y], group.div(1, blindingFactorDjpBlinded[y].getZR())));
    }
    skBlinded.insert(0, DBlinded);
    skBlinded.insert(1, DjBlinded);
    skBlinded.insert(2, DjpBlinded);
    return;
}

void encrypt(CharmList & pk, GT & M, string & policyUSstr, CharmList & ct)
{
