#include "TestHVE.h"

void Hve08::setup(int n, CharmList & pk, CharmList & msk)
{
    G1 g1 = group.init(G1_t);
    G2 g2 = group.init(G2_t);
    GT egg = group.init(GT_t);
    ZR y = group.init(ZR_t);
    GT Y = group.init(GT_t);
    CharmListZR t;
    CharmListZR v;
    CharmListZR r;
    CharmListZR m;
    CharmListG1 T;
    CharmListG1 V;
    CharmListG1 R;
    CharmListG1 M;
    g1 = group.random(G1_t);
    g2 = group.random(G2_t);
    egg = group.pair(g1, g2);
    y = group.random(ZR_t);
    Y = group.exp(egg, y);
    for (int i = 0; i < n; i++)
    {
        t.insert(i, group.random(ZR_t));
        v.insert(i, group.random(ZR_t));
        r.insert(i, group.random(ZR_t));
        m.insert(i, group.random(ZR_t));
        T.insert(i, group.exp(g1, t[i]));
        V.insert(i, group.exp(g1, v[i]));
        R.insert(i, group.exp(g1, r[i]));
        M.insert(i, group.exp(g1, m[i]));
    }
    pk.insert(0, g1);
    pk.insert(1, g2);
    pk.insert(2, Y);
    pk.insert(3, T);
    pk.insert(4, V);
    pk.insert(5, R);
    pk.insert(6, M);
    msk.insert(0, y);
    msk.insert(1, t);
    msk.insert(2, v);
    msk.insert(3, r);
    msk.insert(4, m);
    return;
}

void Hve08::keygen(CharmList & pk, CharmList & msk, CharmListInt & yVector, CharmList & sk)
{
    G1 g1;
    G2 g2;
    GT Y;
    CharmListG1 T;
    CharmListG1 V;
    CharmListG1 R;
    CharmListG1 M;
    ZR y;
    CharmListZR t;
    CharmListZR v;
    CharmListZR r;
    CharmListZR m;
    int numNonDontCares = 0;
    ZR sumUSaisUSsoFar = group.init(ZR_t, 0);
    int endForLoop = 0;
    CharmListZR a;
    int currentUSaUSindex = 0;
    CharmListG2 YVector;
    CharmListG2 LVector;
    
    g1 = pk[0].getG1();
    g2 = pk[1].getG2();
    Y = pk[2].getGT();
    T = pk[3].getListG1();
    V = pk[4].getListG1();
    R = pk[5].getListG1();
    M = pk[6].getListG1();
    
    y = msk[0].getZR();
    t = msk[1].getListZR();
    v = msk[2].getListZR();
    r = msk[3].getListZR();
    m = msk[4].getListZR();
    //;
    for (int i = 0; i < n; i++)
    {
        if ( ( (yVector[i]) != (2) ) )
        {
            numNonDontCares = (numNonDontCares + 1);
        }
    }
    group.init(sumUSaisUSsoFar, 0);
    endForLoop = (numNonDontCares - 1);
    for (int i = 0; i < endForLoop; i++)
    {
        a.insert(i, group.random(ZR_t));
        sumUSaisUSsoFar = group.add(sumUSaisUSsoFar, a[i]);
    }
    a.insert(numNonDontCares-1, group.sub(y, sumUSaisUSsoFar));
    //;
    for (int i = 0; i < n; i++)
    {
        if ( ( (yVector[i]) == (2) ) )
        {
            YVector.insert(i, group.init(G2_t));
            LVector.insert(i, group.init(G2_t));
        }
        if ( ( (yVector[i]) == (0) ) )
        {
            YVector.insert(i, group.exp(g2, group.div(a[currentUSaUSindex], r[i])));
            LVector.insert(i, group.exp(g2, group.div(a[currentUSaUSindex], m[i])));
            currentUSaUSindex = (currentUSaUSindex + 1);
        }
        if ( ( (yVector[i]) == (1) ) )
        {
            YVector.insert(i, group.exp(g2, group.div(a[currentUSaUSindex], t[i])));
            LVector.insert(i, group.exp(g2, group.div(a[currentUSaUSindex], v[i])));
            currentUSaUSindex = (currentUSaUSindex + 1);
        }
    }
    sk.insert(0, YVector);
    sk.insert(1, LVector);
    return;
}

void Hve08::encrypt(GT & Message, CharmListInt & xVector, CharmList & pk, CharmList & CT)
{
    G1 g1;
    G2 g2;
    GT Y;
    CharmListG1 T;
    CharmListG1 V;
    CharmListG1 R;
    CharmListG1 M;
    ZR s = group.init(ZR_t);
    CharmListZR sUSi;
    GT omega = group.init(GT_t);
    G1 C0 = group.init(G1_t);
    CharmListG1 XVector;
    CharmListG1 WVector;
    
    g1 = pk[0].getG1();
    g2 = pk[1].getG2();
    Y = pk[2].getGT();
    T = pk[3].getListG1();
    V = pk[4].getListG1();
    R = pk[5].getListG1();
    M = pk[6].getListG1();
    s = group.random(ZR_t);
    for (int i = 0; i < n; i++)
    {
        sUSi.insert(i, group.random(ZR_t));
    }
    omega = group.mul(Message, group.exp(Y, group.neg(s)));
    C0 = group.exp(g1, s);
    for (int i = 0; i < n; i++)
    {
        if ( ( (xVector[i]) == (0) ) )
        {
            XVector.insert(i, group.exp(R[i], group.sub(s, sUSi[i])));
            WVector.insert(i, group.exp(M[i], sUSi[i]));
        }
        if ( ( (xVector[i]) == (1) ) )
        {
            XVector.insert(i, group.exp(T[i], group.sub(s, sUSi[i])));
            WVector.insert(i, group.exp(V[i], sUSi[i]));
        }
    }
    CT.insert(0, omega);
    CT.insert(1, C0);
    CT.insert(2, XVector);
    CT.insert(3, WVector);
    return;
}

void Hve08::decrypt(CharmList & CT, CharmList & sk, GT & Message2)
{
    GT omega;
    G1 C0;
    CharmListG1 XVector;
    CharmListG1 WVector;
    CharmListG2 YVector;
    CharmListG2 LVector;
    GT dotProd = group.init(GT_t, 1);
    G2 g2Id = group.init(G2_t);
    int nn = 0;
    GT intermediateResults = group.init(GT_t);
    
    omega = CT[0].getGT();
    C0 = CT[1].getG1();
    XVector = CT[2].getListG1();
    WVector = CT[3].getListG1();
    
    YVector = sk[0].getListG2();
    LVector = sk[1].getListG2();
    group.init(dotProd, 1);
    //;
    nn = YVector.length();
    for (int i = 0; i < nn; i++)
    {
        if ( ( (( (YVector[i]) != (g2Id) )) && (( (LVector[i]) != (g2Id) )) ) )
        {
            intermediateResults = group.mul(group.pair(XVector[i], YVector[i]), group.pair(WVector[i], LVector[i]));
            dotProd = group.mul(dotProd, intermediateResults);
        }
    }
    Message2 = group.mul(omega, dotProd);
    return;
}

