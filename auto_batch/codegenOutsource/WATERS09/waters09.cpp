#include "sdlconfig.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;

int N = 2;

int secparam = 80;

PairingGroup group(AES_SECURITY);

void keygen(CharmList & pk, CharmList & sk)
{
    G1 g1 = group.init(G1_t);
    G2 g2 = group.init(G2_t);
    ZR a1 = group.init(ZR_t);
    ZR a2 = group.init(ZR_t);
    ZR b = group.init(ZR_t);
    ZR alpha = group.init(ZR_t);
    ZR wExp = group.init(ZR_t);
    ZR hExp = group.init(ZR_t);
    ZR vExp = group.init(ZR_t);
    ZR v1Exp = group.init(ZR_t);
    ZR v2Exp = group.init(ZR_t);
    ZR uExp = group.init(ZR_t);
    G2 vG2 = group.init(G2_t);
    G2 v1G2 = group.init(G2_t);
    G2 v2G2 = group.init(G2_t);
    G1 wG1 = group.init(G1_t);
    G1 hG1 = group.init(G1_t);
    G2 w = group.init(G2_t);
    G2 h = group.init(G2_t);
    G1 uG1 = group.init(G1_t);
    G2 u = group.init(G2_t);
    G2 tau1 = group.init(G2_t);
    G2 tau2 = group.init(G2_t);
    G1 g1b = group.init(G1_t);
    G1 g1a1 = group.init(G1_t);
    G1 g1a2 = group.init(G1_t);
    G1 g1ba1 = group.init(G1_t);
    G1 g1ba2 = group.init(G1_t);
    G2 tau1b = group.init(G2_t);
    G2 tau2b = group.init(G2_t);
    GT A = group.init(GT_t);
    G2 g2AlphaA1 = group.init(G2_t);
    G2 g2b = group.init(G2_t);
    g1 = group.random(G1_t);
    g2 = group.random(G2_t);
    a1 = group.random(ZR_t);
    a2 = group.random(ZR_t);
    b = group.random(ZR_t);
    alpha = group.random(ZR_t);
    wExp = group.random(ZR_t);
    hExp = group.random(ZR_t);
    vExp = group.random(ZR_t);
    v1Exp = group.random(ZR_t);
    v2Exp = group.random(ZR_t);
    uExp = group.random(ZR_t);
    vG2 = group.exp(g2, vExp);
    v1G2 = group.exp(g2, v1Exp);
    v2G2 = group.exp(g2, v2Exp);
    wG1 = group.exp(g1, wExp);
    hG1 = group.exp(g1, hExp);
    w = group.exp(g2, wExp);
    h = group.exp(g2, hExp);
    uG1 = group.exp(g1, uExp);
    u = group.exp(g2, uExp);
    tau1 = group.mul(vG2, group.exp(v1G2, a1));
    tau2 = group.mul(vG2, group.exp(v2G2, a2));
    g1b = group.exp(g1, b);
    g1a1 = group.exp(g1, a1);
    g1a2 = group.exp(g1, a2);
    g1ba1 = group.exp(g1, group.mul(b, a1));
    g1ba2 = group.exp(g1, group.mul(b, a2));
    tau1b = group.exp(tau1, b);
    tau2b = group.exp(tau2, b);
    A = group.exp(group.pair(g1, g2), group.mul(alpha, group.mul(a1, b)));
    g2AlphaA1 = group.exp(g2, group.mul(alpha, a1));
    g2b = group.exp(g2, b);
    pk.append(g1);
    pk.append(g2);
    pk.append(g1b);
    pk.append(g1a1);
    pk.append(g1a2);
    pk.append(g1ba1);
    pk.append(g1ba2);
    pk.append(tau1);
    pk.append(tau2);
    pk.append(tau1b);
    pk.append(tau2b);
    pk.append(uG1);
    pk.append(u);
    pk.append(wG1);
    pk.append(hG1);
    pk.append(w);
    pk.append(h);
    pk.append(A);
    sk.append(g2AlphaA1);
    sk.append(g2b);
    sk.append(vG2);
    sk.append(v1G2);
    sk.append(v2G2);
    sk.append(alpha);
    return;
}

void sign(CharmList & pk, CharmList & sk, string & m, G2 & S1, G2 & S2, G2 & S3, G2 & S4, G2 & S5, G1 & S6, G1 & S7, G2 & SK, ZR & tagk)
{
    G1 g1;
    G2 g2;
    G1 g1b;
    G1 g1a1;
    G1 g1a2;
    G1 g1ba1;
    G1 g1ba2;
    G2 tau1;
    G2 tau2;
    G2 tau1b;
    G2 tau2b;
    G1 uG1;
    G2 u;
    G1 wG1;
    G1 hG1;
    G2 w;
    G2 h;
    GT A;
    G2 g2AlphaA1;
    G2 g2b;
    G2 vG2;
    G2 v1G2;
    G2 v2G2;
    ZR alpha;
    ZR r1 = group.init(ZR_t);
    ZR r2 = group.init(ZR_t);
    ZR z1 = group.init(ZR_t);
    ZR z2 = group.init(ZR_t);
    ZR r = group.init(ZR_t);
    ZR M = group.init(ZR_t);
    
    g1 = pk[0].getG1();
    g2 = pk[1].getG2();
    g1b = pk[2].getG1();
    g1a1 = pk[3].getG1();
    g1a2 = pk[4].getG1();
    g1ba1 = pk[5].getG1();
    g1ba2 = pk[6].getG1();
    tau1 = pk[7].getG2();
    tau2 = pk[8].getG2();
    tau1b = pk[9].getG2();
    tau2b = pk[10].getG2();
    uG1 = pk[11].getG1();
    u = pk[12].getG2();
    wG1 = pk[13].getG1();
    hG1 = pk[14].getG1();
    w = pk[15].getG2();
    h = pk[16].getG2();
    A = pk[17].getGT();
    
    g2AlphaA1 = sk[0].getG2();
    g2b = sk[1].getG2();
    vG2 = sk[2].getG2();
    v1G2 = sk[3].getG2();
    v2G2 = sk[4].getG2();
    alpha = sk[5].getZR();
    r1 = group.random(ZR_t);
    r2 = group.random(ZR_t);
    z1 = group.random(ZR_t);
    z2 = group.random(ZR_t);
    tagk = group.random(ZR_t);
    r = group.add(r1, r2);
    M = group.hashListToZR(m);
    S1 = group.mul(g2AlphaA1, group.exp(vG2, r));
    S2 = group.mul(group.exp(g2, group.neg(alpha)), group.mul(group.exp(v1G2, r), group.exp(g2, z1)));
    S3 = group.exp(g2b, group.neg(z1));
    S4 = group.mul(group.exp(v2G2, r), group.exp(g2, z2));
    S5 = group.exp(g2b, group.neg(z2));
    S6 = group.exp(g1b, r2);
    S7 = group.exp(g1, r1);
    SK = group.exp(group.mul(group.mul(group.exp(u, M), group.exp(w, tagk)), h), r1);
    return;
}

bool verify(G1 & g1, G2 & g2, G1 & g1b, G1 & g1a1, G1 & g1a2, G1 & g1ba1, G1 & g1ba2, G2 & tau1, G2 & tau2, G2 & tau1b, G2 & tau2b, G2 & u, G2 & w, G2 & h, GT & A, G2 & S1, G2 & S2, G2 & S3, G2 & S4, G2 & S5, G1 & S6, G1 & S7, G2 & SK, ZR & tagk, string & m)
{
    ZR s1 = group.init(ZR_t);
    ZR s2 = group.init(ZR_t);
    ZR t = group.init(ZR_t);
    ZR tagc = group.init(ZR_t);
    ZR s = group.init(ZR_t);
    ZR M = group.init(ZR_t);
    ZR theta = group.init(ZR_t);
    s1 = group.random(ZR_t);
    s2 = group.random(ZR_t);
    t = group.random(ZR_t);
    tagc = group.random(ZR_t);
    s = group.add(s1, s2);
    M = group.hashListToZR(m);
    theta = group.exp(group.sub(tagc, tagk), -1);
    if ( ( (group.mul(group.pair(group.exp(g1b, s), S1), group.mul(group.pair(group.exp(g1ba1, s1), S2), group.mul(group.pair(group.exp(g1a1, s1), S3), group.mul(group.pair(group.exp(g1ba2, s2), S4), group.pair(group.exp(g1a2, s2), S5)))))) == (group.mul(group.pair(S6, group.mul(group.exp(tau1, s1), group.exp(tau2, s2))), group.mul(group.pair(S7, group.mul(group.exp(tau1b, s1), group.mul(group.exp(tau2b, s2), group.exp(w, group.neg(t))))), group.mul(group.exp(group.mul(group.pair(S7, group.mul(group.mul(group.exp(u, group.mul(M, t)), group.exp(w, group.mul(tagc, t))), group.exp(h, t))), group.pair(group.exp(g1, group.neg(t)), SK)), theta), group.exp(A, s2))))) ) )
    {
        return true;
    }
    else
    {
        return false;
    }
}

bool membership(GT & A, CharmListG2 & S1list, CharmListG2 & S2list, CharmListG2 & S3list, CharmListG2 & S4list, CharmListG2 & S5list, CharmListG1 & S6list, CharmListG1 & S7list, CharmListG2 & SKlist, G1 & g1, G1 & g1a1, G1 & g1a2, G1 & g1b, G1 & g1ba1, G1 & g1ba2, G2 & g2, G2 & h, CharmListZR & tagklist, G2 & tau1, G2 & tau1b, G2 & tau2, G2 & tau2b, G2 & u, G2 & w)
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
    if ( ( (group.ismember(S4list)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(S5list)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(S6list)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(S7list)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(SKlist)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(g1)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(g1a1)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(g1a2)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(g1b)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(g1ba1)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(g1ba2)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(g2)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(h)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(tagklist)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(tau1)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(tau1b)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(tau2)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(tau2b)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(u)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(w)) == (false) ) )
    {
        return false;
    }
    return true;
}

void dividenconquer(CharmListZR & delta, int startSigNum, int endSigNum, list<int> & incorrectIndices, CharmListG2 & dotACache, CharmListG2 & dotBCache, CharmListG2 & dotCCache, CharmListG2 & dotDCache, CharmListG2 & dotECache, CharmListG1 & dotFCache, CharmListG1 & dotGCache, CharmListG1 & dotHCache, CharmListG1 & dotICache, CharmListG1 & dotJCache, CharmListG1 & dotKCache, CharmListG1 & dotLCache, CharmListG2 & dotMCache, CharmListZR & sumNCache, G1 & g1b, G1 & g1ba1, G1 & g1a1, G1 & g1ba2, G1 & g1a2, G2 & tau1, G2 & tau2, G2 & tau1b, G2 & tau2b, G2 & w, G2 & u, G2 & h, G1 & g1, GT & A)
{
    G2 dotALoopVal = group.init(G2_t, 1);
    G2 dotBLoopVal = group.init(G2_t, 1);
    G2 dotCLoopVal = group.init(G2_t, 1);
    G2 dotDLoopVal = group.init(G2_t, 1);
    G2 dotELoopVal = group.init(G2_t, 1);
    G1 dotFLoopVal = group.init(G1_t, 1);
    G1 dotGLoopVal = group.init(G1_t, 1);
    G1 dotHLoopVal = group.init(G1_t, 1);
    G1 dotILoopVal = group.init(G1_t, 1);
    G1 dotJLoopVal = group.init(G1_t, 1);
    G1 dotKLoopVal = group.init(G1_t, 1);
    G1 dotLLoopVal = group.init(G1_t, 1);
    G2 dotMLoopVal = group.init(G2_t, 1);
    ZR sumNLoopVal = group.init(ZR_t, 0);
    int midwayFloat = 0;
    int midway = 0;
    int midSigNum = 0;
    group.init(dotALoopVal, 1);
    group.init(dotBLoopVal, 1);
    group.init(dotCLoopVal, 1);
    group.init(dotDLoopVal, 1);
    group.init(dotELoopVal, 1);
    group.init(dotFLoopVal, 1);
    group.init(dotGLoopVal, 1);
    group.init(dotHLoopVal, 1);
    group.init(dotILoopVal, 1);
    group.init(dotJLoopVal, 1);
    group.init(dotKLoopVal, 1);
    group.init(dotLLoopVal, 1);
    group.init(dotMLoopVal, 1);
    group.init(sumNLoopVal, 0);
    for (int z = startSigNum; z < endSigNum; z++)
    {
        dotALoopVal = group.mul(dotALoopVal, dotACache[z]);
        dotBLoopVal = group.mul(dotBLoopVal, dotBCache[z]);
        dotCLoopVal = group.mul(dotCLoopVal, dotCCache[z]);
        dotDLoopVal = group.mul(dotDLoopVal, dotDCache[z]);
        dotELoopVal = group.mul(dotELoopVal, dotECache[z]);
        dotFLoopVal = group.mul(dotFLoopVal, dotFCache[z]);
        dotGLoopVal = group.mul(dotGLoopVal, dotGCache[z]);
        dotHLoopVal = group.mul(dotHLoopVal, dotHCache[z]);
        dotILoopVal = group.mul(dotILoopVal, dotICache[z]);
        dotJLoopVal = group.mul(dotJLoopVal, dotJCache[z]);
        dotKLoopVal = group.mul(dotKLoopVal, dotKCache[z]);
        dotLLoopVal = group.mul(dotLLoopVal, dotLCache[z]);
        dotMLoopVal = group.mul(dotMLoopVal, dotMCache[z]);
        sumNLoopVal = group.add(sumNLoopVal, sumNCache[z]);
    }
    if ( ( (group.mul(group.pair(g1b, dotALoopVal), group.mul(group.pair(g1ba1, dotBLoopVal), group.mul(group.pair(g1a1, dotCLoopVal), group.mul(group.pair(g1ba2, dotDLoopVal), group.pair(g1a2, dotELoopVal)))))) == (group.mul(group.pair(dotFLoopVal, tau1), group.mul(group.pair(dotGLoopVal, tau2), group.mul(group.pair(dotHLoopVal, tau1b), group.mul(group.pair(dotILoopVal, tau2b), group.mul(group.pair(dotJLoopVal, w), group.mul(group.pair(dotKLoopVal, u), group.mul(group.pair(dotLLoopVal, h), group.mul(group.pair(g1, dotMLoopVal), group.exp(A, sumNLoopVal)))))))))) ) )
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
        dividenconquer(delta, startSigNum, midway, incorrectIndices, dotACache, dotBCache, dotCCache, dotDCache, dotECache, dotFCache, dotGCache, dotHCache, dotICache, dotJCache, dotKCache, dotLCache, dotMCache, sumNCache, g1b, g1ba1, g1a1, g1ba2, g1a2, tau1, tau2, tau1b, tau2b, w, u, h, g1, A);
        dividenconquer(delta, midSigNum, endSigNum, incorrectIndices, dotACache, dotBCache, dotCCache, dotDCache, dotECache, dotFCache, dotGCache, dotHCache, dotICache, dotJCache, dotKCache, dotLCache, dotMCache, sumNCache, g1b, g1ba1, g1a1, g1ba2, g1a2, tau1, tau2, tau1b, tau2b, w, u, h, g1, A);
    }
    return;
}

bool batchverify(GT & A, CharmListG2 & S1list, CharmListG2 & S2list, CharmListG2 & S3list, CharmListG2 & S4list, CharmListG2 & S5list, CharmListG1 & S6list, CharmListG1 & S7list, CharmListG2 & SKlist, G1 & g1, G1 & g1a1, G1 & g1a2, G1 & g1b, G1 & g1ba1, G1 & g1ba2, G2 & g2, G2 & h, CharmListStr & mlist, CharmListZR & tagklist, G2 & tau1, G2 & tau1b, G2 & tau2, G2 & tau2b, G2 & u, G2 & w, list<int> & incorrectIndices)
{
    CharmListZR delta;
    ZR s2 = group.init(ZR_t);
    ZR s1 = group.init(ZR_t);
    ZR M = group.init(ZR_t);
    ZR s = group.init(ZR_t);
    ZR t = group.init(ZR_t);
    ZR tagc = group.init(ZR_t);
    ZR theta = group.init(ZR_t);
    CharmListG2 dotACache;
    CharmListG2 dotBCache;
    CharmListG2 dotCCache;
    CharmListG2 dotDCache;
    CharmListG2 dotECache;
    CharmListG1 dotFCache;
    CharmListG1 dotGCache;
    CharmListG1 dotHCache;
    CharmListG1 dotICache;
    CharmListG1 dotJCache;
    CharmListG1 dotKCache;
    CharmListG1 dotLCache;
    CharmListG2 dotMCache;
    CharmListZR sumNCache;
    for (int z = 0; z < N; z++)
    {
        delta[z] = SmallExp(secparam);
    }
    if ( ( (membership(A, S1list, S2list, S3list, S4list, S5list, S6list, S7list, SKlist, g1, g1a1, g1a2, g1b, g1ba1, g1ba2, g2, h, tagklist, tau1, tau1b, tau2, tau2b, u, w)) == (false) ) )
    {
        return false;
    }
    for (int z = 0; z < N; z++)
    {
        s2 = group.random(ZR_t);
        s1 = group.random(ZR_t);
        M = group.hashListToZR(mlist[z]);
        s = group.add(s1, s2);
        t = group.random(ZR_t);
        tagc = group.random(ZR_t);
        theta = group.exp(group.sub(tagc, tagklist[z]), -1);
        dotACache[z] = group.exp(S1list[z], group.mul(s, delta[z]));
        dotBCache[z] = group.exp(S2list[z], group.mul(s1, delta[z]));
        dotCCache[z] = group.exp(S3list[z], group.mul(s1, delta[z]));
        dotDCache[z] = group.exp(S4list[z], group.mul(s2, delta[z]));
        dotECache[z] = group.exp(S5list[z], group.mul(s2, delta[z]));
        dotFCache[z] = group.exp(S6list[z], group.mul(delta[z], s1));
        dotGCache[z] = group.exp(S6list[z], group.mul(delta[z], s2));
        dotHCache[z] = group.exp(S7list[z], group.mul(delta[z], s1));
        dotICache[z] = group.exp(S7list[z], group.mul(delta[z], s2));
        dotJCache[z] = group.exp(S7list[z], group.add(group.mul(delta[z], group.neg(t)), group.mul(group.mul(theta, delta[z]), group.mul(tagc, t))));
        dotKCache[z] = group.exp(S7list[z], group.mul(group.mul(theta, delta[z]), group.mul(M, t)));
        dotLCache[z] = group.exp(S7list[z], group.mul(group.mul(theta, delta[z]), t));
        dotMCache[z] = group.exp(SKlist[z], group.mul(group.neg(t), group.mul(theta, delta[z])));
        sumNCache[z] = group.mul(s2, delta[z]);
    }
    dividenconquer(delta, 0, N, incorrectIndices, dotACache, dotBCache, dotCCache, dotDCache, dotECache, dotFCache, dotGCache, dotHCache, dotICache, dotJCache, dotKCache, dotLCache, dotMCache, sumNCache, g1b, g1ba1, g1a1, g1ba2, g1a2, tau1, tau2, tau1b, tau2b, w, u, h, g1, A);
    return true;
}

int main()
{
    G1 g1;
    G2 g2;
    G1 g1b;
    G1 g1a1;
    G1 g1a2;
    G1 g1ba1;
    G1 g1ba2;
    G2 tau1;
    G2 tau2;
    G2 tau1b;
    G2 tau2b;
    G1 uG1;
    G2 u;
    G1 wG1;
    G1 hG1;
    G2 w;
    G2 h;
    GT A;
    CharmList pk, sk;
    string m0 = "message0";
    string m1 = "message1";
    ZR tagk;
    G2 S1, S2, S3, S4, S5, SK;
    G1 S6, S7;
    keygen(pk, sk);

    CharmListZR tagklist; 
    CharmListG1 S6list, S7list;
    CharmListG2 S1list, S2list, S3list, S4list, S5list, SKlist; 
    sign(pk, sk, m0, S1list[0], S2list[0], S3list[0], S4list[0], S5list[0], S6list[0], S7list[0], SKlist[0], tagklist[0]);
    sign(pk, sk, m1, S1list[1], S2list[1], S3list[1], S4list[1], S5list[1], S6list[1], S7list[1], SKlist[1], tagklist[1]);
    
    g1 = pk[0].getG1();
    g2 = pk[1].getG2();
    g1b = pk[2].getG1();
    g1a1 = pk[3].getG1();
    g1a2 = pk[4].getG1();
    g1ba1 = pk[5].getG1();
    g1ba2 = pk[6].getG1();
    tau1 = pk[7].getG2();
    tau2 = pk[8].getG2();
    tau1b = pk[9].getG2();
    tau2b = pk[10].getG2();
    uG1 = pk[11].getG1();
    u = pk[12].getG2();
    wG1 = pk[13].getG1();
    hG1 = pk[14].getG1();
    w = pk[15].getG2();
    h = pk[16].getG2();
    A = pk[17].getGT();

    bool status = verify(g1, g2, g1b, g1a1, g1a2, g1ba1, g1ba2, tau1, tau2, tau1b, tau2b, u, w, h, A, S1list[0], S2list[0], S3list[0], S4list[0], S5list[0], S6list[0], S7list[0], SKlist[0], tagklist[0], m0);

    if(status == true)
       cout << "True!" << endl;
    else
       cout << "False!" << endl;
       
    status = verify(g1, g2, g1b, g1a1, g1a2, g1ba1, g1ba2, tau1, tau2, tau1b, tau2b, u, w, h, A, S1list[1], S2list[1], S3list[1], S4list[1], S5list[1], S6list[1], S7list[1], SKlist[1], tagklist[1], m1);
    if(status == true)
       cout << "True!" << endl;
    else
       cout << "False!" << endl;
       
    list<int> incorrectIndices;
    CharmListStr mlist;
    mlist[0] = m0;
    mlist[1] = m1;
    batchverify(A, S1list, S2list, S3list, S4list, S5list, S6list, S7list, SKlist, g1, g1a1, g1a2, g1b, g1ba1, g1ba2, g2, h, mlist, tagklist, tau1, tau1b, tau2, tau2b, u, w, incorrectIndices);

    cout << "Incorrect indices: ";
    for (list<int>::iterator it = incorrectIndices.begin(); it != incorrectIndices.end(); it++)
             cout << *it << " ";
    cout << endl;

    return 0;
}
