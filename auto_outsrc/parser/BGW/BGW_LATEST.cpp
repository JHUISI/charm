#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;

PairingGroup group(AES_SECURITY);

void setup(int n, CharmList & pk, CharmList & msk)
{
    G1 g = group.init(G1_t);
    ZR alpha = group.init(ZR_t);
    int endIndexOfList = 0;
    CharmListG1 giValues;
    ZR gamma = group.init(ZR_t);
    G1 v = group.init(G1_t);
    g = group.random(G1_t);
    alpha = group.random(ZR_t);
    endIndexOfList = group.add(group.mul(2, n), 1);
    for (int i = 1; i < endIndexOfList; i++)
    {
        giValues.insert(i, group.exp(g, group.exp(alpha, i)));
    }
    gamma = group.random(ZR_t);
    v = group.exp(g, gamma);
    pk.insert(0, g);
    pk.insert(1, giValues);
    pk.insert(2, v);
    msk.insert(0, gamma);
    return;
}

void keygen(CharmList & pk, CharmList & msk, int n, ZR & bf0, CharmList & skCompleteBlinded)
{
    G1 g;
    CharmListG1 giValues;
    G1 v;
    ZR gamma;
    CharmListG1 sk;
    CharmListZR blindingFactorskBlinded;
    CharmListG1 skBlinded;
    bf0 = group.random(ZR_t);
    
    g = pk[0].getG1();
    giValues = pk[1].getListG1();
    v = pk[2].getG1();
    
    gamma = msk[0].getZR();
    for (int i = 1; i < n+1; i++)
    {
        sk.insert(i, group.exp(giValues[i], gamma));
    }
    CharmList sk_Keys_List = sk.keys();
    int sk_List_Length = sk.length();
    for (int y_Temp_Loop_Var = 0; y_Temp_Loop_Var < sk_List_Length; y_Temp_Loop_Var++)
    {
        y = sk_Keys_List[y_Temp_Loop_Var];
        blindingFactorskBlinded.insert(y, bf0);
        skBlinded.insert(y, group.exp(sk[y], group.div(1, blindingFactorskBlinded[y].getZR())));
    }
    skCompleteBlinded.insert(0, skBlinded);
    return;
}

void encrypt(CharmListInt & S, CharmList & pk, int n, CharmList & ct)
{
    G1 g;
    CharmListG1 giValues;
    G1 v;
    ZR t = group.init(ZR_t);
    GT K = group.init(GT_t);
    G1 dotProdEncrypt = group.init(G1_t, 1);
    G1 Hdr2 = group.init(G1_t);
    G1 Hdr1 = group.init(G1_t);
    CharmList Hdr;
    
    g = pk[0].getG1();
    giValues = pk[1].getListG1();
    v = pk[2].getG1();
    t = group.random(ZR_t);
    K = group.exp(group.pair(giValues[n], giValues[1]), t);
    group.init(dotProdEncrypt, 1);
    CharmList S_Keys_List = S.keys();
    int S_List_Length = S.length();
    for (int jEncrypt_Temp_Loop_Var = 0; jEncrypt_Temp_Loop_Var < S_List_Length; jEncrypt_Temp_Loop_Var++)
    {
        jEncrypt = S_Keys_List[jEncrypt_Temp_Loop_Var];
        dotProdEncrypt = group.mul(dotProdEncrypt, giValues[n+1-jEncrypt]);
    }
    Hdr2 = group.exp(group.mul(v, dotProdEncrypt), t);
    Hdr1 = group.exp(g, t);
    Hdr.insert(0, Hdr1);
    Hdr.insert(1, Hdr2);
    ct.insert(0, Hdr);
    ct.insert(1, K);
    return;
}

void transform(CharmListInt & S, int i, int n, CharmList & Hdr, CharmList & pk, CharmList & skCompleteBlinded, CharmList & transformOutputList)
{
    G1 Hdr1;
    G1 Hdr2;
    G1 g;
    CharmListG1 giValues;
    G1 v;
    CharmListG1 skBlinded;
    GT numerator = group.init(GT_t);
    G1 dotProdDecrypt = group.init(G1_t, 1);
    
    Hdr1 = Hdr[0].getG1();
    Hdr2 = Hdr[1].getG1();
    
    g = pk[0].getG1();
    giValues = pk[1].getListG1();
    v = pk[2].getG1();
    
    skBlinded = skCompleteBlinded[0].getListG1();
    transformOutputList.insert(0, group.pair(giValues[i], Hdr2));
    numerator = transformOutputList[0].getGT();
    transformOutputList.insert(1, group.init(G1_t));
    dotProdDecrypt = transformOutputList[1].getG1();
    CharmList S_Keys_List = S.keys();
    int S_List_Length = S.length();
    for (int jDecrypt_Temp_Loop_Var = 0; jDecrypt_Temp_Loop_Var < S_List_Length; jDecrypt_Temp_Loop_Var++)
    {
        jDecrypt = S_Keys_List[jDecrypt_Temp_Loop_Var];
        if ( ( (jDecrypt) != (i) ) )
        {
cout << ;
            transformOutputList.insert(2, group.mul(dotProdDecrypt, giValues[n+1-jDecrypt+i]));
            dotProdDecrypt = transformOutputList[2].getG1();
        }
    }
    transformOutputList.insert(3, group.pair(skBlinded[i], Hdr1));
    transformOutputList.insert(4, group.pair(dotProdDecrypt, Hdr1));
    return;
}

void decout(CharmListInt & S, int i, int n, CharmList & Hdr, CharmList & pk, CharmList & skCompleteBlinded, CharmList & transformOutputList, ZR & bf0, NO_TYPE & M)
{
    G1 Hdr1;
    G1 Hdr2;
    G1 g;
    CharmListG1 giValues;
    G1 v;
    CharmListG1 skBlinded;
    GT numerator = group.init(GT_t);
    G1 dotProdDecrypt = group.init(G1_t, 1);
    GT denominator = group.init(GT_t);
    GT KDecrypt = group.init(GT_t);
    
    Hdr1 = Hdr[0].getG1();
    Hdr2 = Hdr[1].getG1();
    
    g = pk[0].getG1();
    giValues = pk[1].getListG1();
    v = pk[2].getG1();
    
    skBlinded = skCompleteBlinded[0].getListG1();
    numerator = transformOutputList[0].getGT();
    dotProdDecrypt = transformOutputList[1].getG1();
    CharmList S_Keys_List = S.keys();
    int S_List_Length = S.length();
    for (int jDecrypt_Temp_Loop_Var = 0; jDecrypt_Temp_Loop_Var < S_List_Length; jDecrypt_Temp_Loop_Var++)
    {
        jDecrypt = S_Keys_List[jDecrypt_Temp_Loop_Var];
        if ( ( (jDecrypt) != (i) ) )
        {
cout << ;
            dotProdDecrypt = transformOutputList[2].getG1();
        }
    }
    denominator = group.mul(group.exp(transformOutputList[3].getGT(), bf0), transformOutputList[4].getGT());
    KDecrypt = group.mul(numerator, group.exp(denominator, -1));
    return;
}

int main()
{
    return 0;
}
