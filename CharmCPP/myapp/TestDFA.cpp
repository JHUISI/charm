#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;

PairingGroup group(SS512);

DFA dfa;

void setup(CharmListStr & alphabet, CharmList & mpk, G1 & msk)
{
    G1 g = group.init(G1_t);
    G1 z = group.init(G1_t);
    G1 hstart = group.init(G1_t);
    G1 hend = group.init(G1_t);
    int A = 0;
    string a;
    CharmListG1 h;
    ZR alpha = group.init(ZR_t);
    GT egg = group.init(GT_t);
    g = group.random(G1_t);
    z = group.random(G1_t);
    hstart = group.random(G1_t);
    hend = group.random(G1_t);
    A = alphabet.length();
    for (int i = 0; i < A; i++)
    {
        a = GetString(alphabet[i]);
        h.insert(a, group.random(G1_t));
    }
    alpha = group.random(ZR_t);
    egg = group.exp(group.pair(g, g), alpha);
    msk = group.exp(g, group.neg(alpha));
    mpk.insert(0, egg);
    mpk.insert(1, g);
    mpk.insert(2, z);
    mpk.insert(3, h);
    mpk.insert(4, hstart);
    mpk.insert(5, hend);
    return;
}

void keygen(CharmList & mpk, G1 & msk, CharmListInt & Q, CharmMetaListInt & T, CharmListInt & F, CharmList & sk, CharmMetaListG1 & K)
{
    GT egg;
    G1 g;
    G1 z;
    CharmListG1 h;
    G1 hstart;
    G1 hend;
    int qlen = 0;
    CharmListG1 D;
    ZR rstart = group.init(ZR_t);
    G1 Kstart1 = group.init(G1_t);
    G1 Kstart2 = group.init(G1_t);
    int Tlen = 0;
    ZR r = group.init(ZR_t);
    CharmListInt t;
    int t0 = 0;
    int t1 = 0;
    string t2;
    string key;
    CharmListG1 tmpList0;
    int Flen = 0;
    int x = 0;
    ZR rx = group.init(ZR_t);
    CharmListG1 KendList1;
    CharmListG1 KendList2;
    
    egg = mpk[0].getGT();
    g = mpk[1].getG1();
    z = mpk[2].getG1();
    h = mpk[3].getListG1();
    hstart = mpk[4].getG1();
    hend = mpk[5].getG1();
    qlen = Q.length();
    for (int i = 0; i < qlen+1; i++)
    {
        D.insert(i, group.random(G1_t));
    }
    rstart = group.random(ZR_t);
    Kstart1 = group.mul(D[0], group.exp(hstart, rstart));
    Kstart2 = group.exp(g, rstart);
    Tlen = T.length();
    for (int i = 0; i < Tlen; i++)
    {
        r = group.random(ZR_t);
        t = T[i]; // fix type in SDL
        t0 = t[0];
        t1 = t[1];
        t2 = dfa.getString(t[2]); // convert int alphabet into string via DFA class
        key = dfa.hashToKey(t); // get key for the transition. basically, turn CharmListInt t into a string of form "(int,int,alphabet)"
        cout << "key: " << key << endl;
        //;
        K.insert(key, tmpList0);
        K[key][1] = group.mul(group.exp(D[t0], -1), group.exp(z, r));
        K[key][2] = group.exp(g, r);
        K[key][3] = group.mul(D[t1], group.exp(h[t2], r));
        cout << "K:\n" << K << endl;
    }
    Flen = F.length();
    for (int i = 0; i < Flen; i++)
    {
        x = F[i];
        rx = group.random(ZR_t);
        KendList1.insert(x, group.mul(msk, group.mul(D[x], group.exp(hend, rx))));
        KendList2.insert(x, group.exp(g, rx));
    }
    sk.insert(0, Kstart1);
    sk.insert(1, Kstart2);
    sk.insert(2, KendList1);
    sk.insert(3, KendList2);
    return;
}

void encrypt(CharmList & mpk, CharmListStr & w, GT & M, CharmList & ct, GT & Cm, CharmMetaListG1 & C)
{
    GT egg;
    G1 g;
    G1 z;
    CharmListG1 h;
    G1 hstart;
    G1 hend;
    int l = 0;
    CharmListZR s;
    CharmListG1 tmpList1;
    string a;
    CharmListG1 tmpList2;
    G1 Cend1 = group.init(G1_t);
    G1 Cend2 = group.init(G1_t);
    
    egg = mpk[0].getGT();
    g = mpk[1].getG1();
    z = mpk[2].getG1();
    h = mpk[3].getListG1();
    hstart = mpk[4].getG1();
    hend = mpk[5].getG1();
    l = w.length();
    for (int i = 0; i < l+1; i++)
    {
        s.insert(i, group.random(ZR_t));
    }
    Cm = group.mul(M, group.exp(egg, s[l]));
    //;
    C.insert(0, tmpList1);
    C[0][1] = group.exp(g, s[0]);
    C[0][2] = group.exp(hstart, s[0]);

    for (int i = 1; i < l+1; i++)
    {
        a = dfa.getString(w[i]); // remember to make w (one-indexed)
        cout << "i=" << i << ", w=" << a << endl;
        //;
        C.insert(i, tmpList2);
        C[i][1] = group.exp(g, s[i]);
        C[i][2] = group.mul(group.exp(h[a], s[i]), group.exp(z, s[i-1]));
    }
    Cend1 = group.exp(g, s[l]);
    Cend2 = group.exp(hend, s[l]);
    ct.insert(0, Cend1);
    ct.insert(1, Cend2);
    ct.insert(2, w);
    return;
}

bool decrypt(CharmList & sk, CharmMetaListG1 & K, CharmList & ct, GT & Cm, CharmMetaListG1 & C, GT & M) // fix type
{
    G1 Kstart1;
    G1 Kstart2;
    CharmListG1 KendList1;
    CharmListG1 KendList2;
    G1 Cend1;
    G1 Cend2;
    CharmListStr w;
    int l = 0;
    CharmMetaListInt Ti; // fix type in SDL
    CharmListGT B;
    string key;
    int j = 0;
    GT result0 = group.init(GT_t);
    int x = 0;
    GT result1 = group.init(GT_t);
    GT Bend = group.init(GT_t);
    
    Kstart1 = sk[0].getG1();
    Kstart2 = sk[1].getG1();
    KendList1 = sk[2].getListG1();
    KendList2 = sk[3].getListG1();
    
    Cend1 = ct[0].getG1();
    Cend2 = ct[1].getG1();
    w = ct[2].getListStr();
    l = w.length();
    if ( ( (dfa.accept(w)) == (false) ) ) // TODO: swap real func
    {
        return false;
    }
    Ti = dfa.getTransitions(w); // TODO: swap real func
    cout << "Transitions for w...Ti:\n" << Ti << endl;
    B.insert(0, group.mul(group.pair(C[0][1], Kstart1), group.exp(group.pair(C[0][2], Kstart2), -1)));
    for (int i = 1; i < l+1; i++)
    {
        key = dfa.hashToKey(Ti[i]);
        cout << "key: " << key << endl;
        j = group.sub(i, 1); // fix in SDL
        result0 = group.mul(group.pair(C[j][1], K[key][1]), group.mul(group.exp(group.pair(C[i][2], K[key][2]), -1), group.pair(C[i][1], K[key][3])));
        B.insert(i, group.mul(B[i-1], result0));
    }
    x = dfa.getAcceptState(Ti); // TODO: swap real func
    cout << "acceptState: " << x << endl;
    result1 = group.mul(group.exp(group.pair(Cend1, KendList1[x]), -1), group.pair(Cend2, KendList2[x]));
    Bend = group.mul(B[l], result1);
    M = group.div(Cm, Bend);
    return true;
}

int main()
{
	dfa.constructDFA("ab*a");
	CharmList mpk, sk, ct;
	CharmListStr alphabet = dfa.getAlphabet();
	CharmListStr w;
	CharmListInt Q = dfa.getStates(), F = dfa.getAcceptStates(); // get all states, and all accept states
	CharmMetaListInt T = dfa.getTransitions(); // get all transitions in DFA
	CharmMetaListG1 K, C;
	G1 msk;
	GT M, newM, Cm;

	cout << "Q:\n" << Q << endl;
	cout << "F:\n" << F << endl;
	cout << "T:\n" << T << endl;

	setup(alphabet, mpk, msk);

	cout << "MPK:\n" << mpk << endl;
	cout << "MSK:\n" << convert_str(msk) << endl;
	keygen(mpk, msk, Q, T, F, sk, K);

	cout << "SK:\n" << sk << endl;

	// build w
	w = dfa.getSymbols("aba");
	M = group.random(GT_t);
	encrypt(mpk, w, M, ct, Cm, C);

	decrypt(sk, K, ct, Cm, C, newM);
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
