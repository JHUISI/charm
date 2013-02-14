#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;

PairingGroup group(AES_SECURITY);

SecretUtil util;

void setup(CharmList & gpk)
{
    G1 g = group.init(G1_t);
    g = group.random(G1_t);
    gpk.insert(0, g);
    return;
}

void authsetup(CharmList & gpk, CharmListStr & authS, CharmMetaList & msk, CharmMetaList & pk)
{
    G1 g;
    int Y = 0;
    ZR alpha = group.init(ZR_t);
    ZR y = group.init(ZR_t);
    string z;
    GT eggalph = group.init(GT_t);
    G1 gy = group.init(G1_t);
    CharmList tmpList0;
    CharmList tmpList1;
    
    g = gpk[0].getG1();
    Y = authS.length();
    for (int i = 0; i < Y; i++)
    {
        alpha = group.random(ZR_t);
        y = group.random(ZR_t);
        z = authS[i];
        eggalph = group.exp(group.pair(g, g), alpha);
        gy = group.exp(g, y);
        tmpList0.insert(0, alpha);
        tmpList0.insert(1, y);
        msk.insert(z, tmpList0);
        tmpList1.insert(0, eggalph);
        tmpList1.insert(1, gy);
        pk.insert(z, tmpList1);
    }
    return;
}

void keygen(CharmList & gpk, CharmMetaList & msk, string & gid, CharmListStr & userS, CharmListZR & blindingFactorKBlinded, CharmList & skBlinded)
{
    G1 g;
    G1 h = group.init(G1_t);
    int Y = 0;
    string z;
    CharmListG1 K;
    CharmListG1 KBlinded;
    
    g = gpk[0].getG1();
    h = group.hashListToG1(gid);
    Y = userS.length();
    for (int i = 0; i < Y; i++)
    {
        z = userS[i];
        K.insert(z, group.mul(group.exp(g, msk[z][0].getZR()), group.exp(h, msk[z][1].getZR())));
    }
    CharmList K_Keys_List = K.keys();
    int K_List_Length = K.length();
    for (int y_Temp_Loop_Var = 0; y_Temp_Loop_Var < K_List_Length; y_Temp_Loop_Var++)
    {
        y = K_Keys_List[y_Temp_Loop_Var];
        blindingFactorKBlinded.insert(y, group.random(ZR_t));
        KBlinded.insert(y, group.exp(K[y], group.div(1, blindingFactorKBlinded[y])));
    }
    skBlinded.insert(0, gid);
    skBlinded.insert(1, KBlinded);
    return;
}

void encrypt(CharmMetaList & pk, CharmList & gpk, GT & M, string & policy_str, CharmList & ct)
{
    G1 g;
    Policy policy;
    CharmListStr attrs;
    ZR s = group.init(ZR_t);
    int w = 0;
    CharmDictZR s_sh;
    CharmDictZR w_sh;
    int Y = 0;
    GT egg = group.init(GT_t);
    GT C0 = group.init(GT_t);
    ZR r = group.init(ZR_t);
    string k;
    CharmListGT C1;
    CharmListG1 C2;
    CharmListG1 C3;
    
    g = gpk[0].getG1();
    policy = util.createPolicy(policy_str);
    attrs = util.getAttributeList(policy);
    s = group.random(ZR_t);
    w = 0;
    s_sh = util.calculateSharesDict(group, s, policy);
    w_sh = util.calculateSharesDict(group, w, policy);
    Y = s_sh.length();
    egg = group.pair(g, g);
    C0 = group.mul(M, group.exp(egg, s));
    for (int y = 0; y < Y; y++)
    {
        r = group.random(ZR_t);
        k = attrs[y];
        C1.insert(k, group.mul(group.exp(egg, s_sh[k]), group.exp(pk[k][0].getGT(), r)));
        C2.insert(k, group.exp(g, r));
        C3.insert(k, group.mul(group.exp(pk[k][1].getG1(), r), group.exp(g, w_sh[k])));
    }
    ct.insert(0, policy_str);
    ct.insert(1, C0);
    ct.insert(2, C1);
    ct.insert(3, C2);
    ct.insert(4, C3);
    return;
}

void transform(CharmList & skBlinded, CharmListStr & userS, CharmList & ct, CharmList & transformOutputList, CharmDictZR & coeff, int Y)
{
