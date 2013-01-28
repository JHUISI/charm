#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;

PairingGroup group(SS512);

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

void keygen(CharmList & gpk, CharmMetaList & msk, string & gid, CharmListStr & userS, CharmList & sk)
{
    G1 g;
    G1 h = group.init(G1_t);
    int Y = 0;
    string z;
    CharmListG1 K;
    
    g = gpk[0].getG1();
    h = group.hashListToG1(gid);
    Y = userS.length();
    for (int i = 0; i < Y; i++)
    {
        z = userS[i];
        K.insert(z, group.mul(group.exp(g, msk[z][0].getZR()), group.exp(h, msk[z][1].getZR())));
    }
    sk.insert(0, gid);
    sk.insert(1, K);
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

void decrypt(CharmList & sk, CharmListStr & userS, CharmList & ct, GT & M)
{
    string policy_str;
    GT C0;
    CharmListGT C1;
    CharmListG1 C2;
    CharmListG1 C3;
    string gid;
    CharmListG1 K;
    Policy policy;
    CharmListStr attrs;
    CharmDictZR coeff;
    G1 h_gid = group.init(G1_t);
    int Y = 0;
    GT dotProd = group.init(GT_t, 1);
    string kDecrypt;
    GT result0 = group.init(GT_t);
    GT result1 = group.init(GT_t);
    GT result2 = group.init(GT_t);
    GT numerator = group.init(GT_t);
    GT denominator0 = group.init(GT_t);
    GT denominator = group.init(GT_t);
    GT fraction = group.init(GT_t);
    
    policy_str = ct[0].strPtr;
    C0 = ct[1].getGT();
    C1 = ct[2].getListGT();
    C2 = ct[3].getListG1();
    C3 = ct[4].getListG1();
    
    gid = sk[0].strPtr;
    K = sk[1].getListG1();
    policy = util.createPolicy(policy_str);
    attrs = util.prune(policy, userS);
    coeff = util.getCoefficients(group, policy);
    h_gid = group.hashListToG1(gid);
    Y = attrs.length();
    group.init(dotProd, 1);
    for (int y = 0; y < Y; y++)
    {
        kDecrypt = GetString(attrs[y]);
        result0 = group.pair(h_gid, C3[kDecrypt]);
        result1 = group.exp(result0, coeff[kDecrypt]);
        result2 = group.exp(C1[kDecrypt], coeff[kDecrypt]);
        numerator = group.mul(result1, result2);
        denominator0 = group.pair(K[kDecrypt], C2[kDecrypt]);
        denominator = group.exp(denominator0, coeff[kDecrypt]);
        fraction = group.div(numerator, denominator);
        dotProd = group.mul(dotProd, fraction);
    }
    M = group.div(C0, dotProd);
    return;
}

int main()
{
	CharmMetaList msk, pk;
	CharmList gpk, sk, ct;
	CharmListStr authS, userS; // set this
	string gid = "john@example.com", policy_str = "((FOUR or THREE) and (TWO or ONE))"; // set this
	GT M, newM;

	// ['ONE', 'TWO', 'THREE', 'FOUR']
	authS.append("ONE");
	authS.append("TWO");
	authS.append("THREE");
	authS.append("FOUR");

	userS.append("ONE");
	userS.append("TWO");
	userS.append("THREE");

	setup(gpk);

	authsetup(gpk, authS, msk, pk);

	keygen(gpk, msk, gid, userS, sk);

	M = group.random(GT_t);
	encrypt(pk, gpk, M, policy_str, ct);

	decrypt(sk, userS, ct, newM);
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
