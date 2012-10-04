#include "sdlconfig.h"
#include <iostream>
#include <sstream>
#include <string>
using namespace std;

void keygen(PairingGroup & group, G2 & pk, ZR & sk, G2 & g) {
    ZR *x = new ZR();
    
    group.random(g);
    group.random(*x);
    pk = group.exp(g, *x); // make sure group operations return dynamic memory
    sk = *x;
     
    return;
}

void sign(PairingGroup & group, ZR & sk, string M, G1 & sig) 
{
    G1 h = group.hashToG1(M);
    sig = group.exp(h, sk); 

    return;
}

void verify(PairingGroup & group, G2 & pk, G2 & g, G1 & sig, string M, bool & output) {
   G1 h = group.hashToG1(M);
   if(group.pair(sig, g) == group.pair(h, pk)) {
      cout << "Successful Verification" << endl;
      output = true;
   }
   else {
      output = false;
   }
}

int main()
{
    PairingGroup group(AES_SECURITY);

    G2 pk, g;
    ZR sk;
    string M = "hello, world! this is the message.";
    G1 sig; // should be *sig since group.exp() will return newlly allocated memory 
    bool output = false;

    keygen(group, pk, sk, g);
  
    cout << "pk :=> " << convert_str(pk) << endl; 
    cout << "sk :=> " << sk << endl;

    cout << "Signing: " << M << endl;

    sign(group, sk, M, sig);

    cout << convert_str(sig) << endl;

    verify(group, pk, g, sig, M, output);
   
    return 0;
}
