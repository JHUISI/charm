#include "sdlconfig.h"
#include <iostream>
#include <sstream>
#include <string>
using namespace std;

void keygen(PairingGroup & group, CharmDict & pk, CharmDict & sk) {
    G2 *g = new G2(), *gx;
    ZR *x = new ZR();
    
    group.random(*g);
    group.random(*x);
    gx = group.exp(*g, *x); // make sure group operations return dynamic memory
  
    setDict(pk, g);
    setDict(pk, gx);
    setDict(sk, x);
    return;
}

void sign(PairingGroup & group, CharmDict & sk, string M, G1 & sig) 
{
    G1 h = group.hashToG1(M);
    sig = group.exp(h, sk["x"].getZR()); 

    return;
}

void verify(PairingGroup & group, CharmDict & pk, G1 & sig, string M, bool & output) {
   G1 h = group.hashToG1(M);
   if(group.pair(sig, pk["g"].getG2()) == group.pair(h, pk["gx"].getG2())) {
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

    CharmDict pk, sk;
    string M = "hello, world! this is the message.";
    G1 sig; // should be *sig since group.exp() will return newlly allocated memory 
    bool output = false;

    keygen(group, pk, sk);
  
    cout << "pk :=> " << pk << endl; 
    cout << "sk :=> " << sk << endl;

    cout << "Signing: " << M << endl;

    sign(group, sk, M, sig);

    cout << convert_str(sig) << endl;

    verify(group, pk, sig, M, output);
   
    // how we cleanup dict items for now: looking for a more elegant solution 
    //delete &(sk["x"].getRefZR()); 
    deleteDictKey(pk, "g");
    deleteDictKey(pk, "gx");
    deleteDictKey(sk, "x");
    return 0;
}
