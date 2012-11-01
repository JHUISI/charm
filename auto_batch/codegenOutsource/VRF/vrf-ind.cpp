#include "sdlconfig.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;

int N = 2;
int n = 8;

int secparam = 80;

PairingGroup group(AES_SECURITY);

void setup(int n, CharmList & pk, CharmListG1 & U1, CharmListG2 & U2, CharmList & sk, CharmListZR & u)
{
    G1 g1 = group.init(G1_t);
    G2 g2 = group.init(G2_t);
    G2 h = group.init(G2_t);
    ZR ut = group.init(ZR_t);
    G2 Ut = group.init(G2_t);
    g1 = group.random(G1_t);
    g2 = group.random(G2_t);

    h = group.random(G2_t);
    ut = group.random(ZR_t);
    Ut = group.exp(g2, ut);

    for (int i = 0; i < group.add(n, 1); i++)
    {
        u[i] = group.random(ZR_t);
    }

    for (int i = 0; i < n; i++)  {
        U1[i] = group.exp(g1, u[i]);
        U2[i] = group.exp(g2, u[i]);
    }

    pk.append(Ut);
    pk.append(g1);
    pk.append(g2);
    pk.append(h);
    sk.append(ut);
    sk.append(g1);
    sk.append(h);
    return;
}

void polyF(CharmList & sk, CharmListZR & u, int x[], GT & result0)
{
    ZR ut;
    G1 g1;
    G2 h;
    ZR dotProd = group.init(ZR_t, 1);
    
    ut = sk[0].getZR();
    g1 = sk[1].getG1();
    h = sk[2].getG2();
    group.init(dotProd, 1);
    for (int i = 0; i < n; i++)
    {
        dotProd = group.mul(dotProd, group.exp(u[i], x[i]));
    }
    result0 = group.pair(group.exp(g1, group.mul(group.mul(ut, u[0]), dotProd)), h);
    return;
}

void prove(CharmList & sk, CharmListZR & u, int x[], GT & y0, CharmListG1 & pi, G1 & pi0)
{
    ZR ut;
    G1 g1;
    G2 h;
    ZR dotProd0 = group.init(ZR_t, 1);
    ZR dotProd1 = group.init(ZR_t, 1);
    
    ut = sk[0].getZR();
    g1 = sk[1].getG1();
    h = sk[2].getG2();
    for (int i = 0; i < n; i++)
    {
        group.init(dotProd0, 1);
        for (int j = 0; j < group.add(i, 1); j++)
        {
            dotProd0 = group.mul(dotProd0, group.exp(u[j], x[j]));
        }
        pi[i] = group.exp(g1, group.mul(ut, dotProd0));
    }

    group.init(dotProd1, 1);
    for (int i = 0; i < n; i++)
    {
        dotProd1 = group.mul(dotProd1, group.exp(u[i], x[i]));
    }
    pi0 = group.exp(g1, group.mul(ut, group.mul(u[0], dotProd1)));
    polyF(sk, u, x, y0);
    return;
}

bool verify(CharmListG1 & U1, CharmListG2 & U2, G2 & Ut, G1 & g1, G2 & g2, G2 & h, GT & y0, CharmListG1 & pi, G1 & pi0, int x[])
{
    GT proof0 = group.init(GT_t);
    GT proof1 = group.init(GT_t);
    proof0 = group.pair(pi[0], g2);
    if ( ( (( (x[0]) == (0) )) && (( (proof0) != (group.pair(g1, Ut)) )) ) )
    {
        return false;
    }
    if ( ( (( (x[0]) == (1) )) && (( (proof0) != (group.pair(U1[0], Ut)) )) ) )
    {
        return false;
    }
    if ( ( (( (x[0]) != (0) )) && (( (x[0]) != (1) )) ) )
    {
        return false;
    }
    for (int i = 1; i < n; i++)
    {
        proof1 = group.pair(pi[i], g2);
        if ( ( (( (x[i]) == (0) )) && (( (proof1) != (group.pair(pi[i-1], g2)) )) ) )
        {
            return false;
        }
        if ( ( (( (x[i]) == (1) )) && (( (proof1) != (group.pair(pi[i-1], U2[i])) )) ) )
        {
            return false;
        }
        if ( ( (( (x[i]) != (0) )) && (( (x[i]) != (1) )) ) )
        {
            return false;
        }
    }
    if ( ( (group.pair(pi0, group.mul(g2, h))) != (group.mul(group.pair(pi[n-1], U2[0]), y0)) ) )
    {
        return false;
    }
    return true;
}

int main()
{
	CharmList pk, sk;
	CharmListG1 U1;
	CharmListG1 pi;
	CharmListG2 U2;
	CharmListZR u;

	G1 pi0;
	GT y0;
	setup(n, pk, U1, U2, sk, u);

    int x[n];
    x[0] = 1;
    x[1] = 0;
    x[2] = 1;
    x[3] = 0;
    x[4] = 1;
    x[5] = 0;
    x[6] = 1;
    x[7] = 0;

    G2 Ut = pk[0].getG2();
    G1 g1 = pk[1].getG1();
    G2 g2 = pk[2].getG2();
    G2 h = pk[3].getG2();

	prove(sk, u, x, y0, pi, pi0);

	bool status = verify(U1, U2, Ut, g1, g2, h, y0, pi, pi0, x);

	if(status == true)
		cout << "True!" << endl;
	else
		cout << "False!" << endl;

    return 0;
}
