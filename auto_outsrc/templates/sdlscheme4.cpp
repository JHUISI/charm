#include "sdlconfig.h"
#include <iostream>
#include <sstream>
#include <string>
using namespace std;

#define NB 4

int main()
{
    int i;
    char key[32];
    char iv[16];
    for (i=0;i<32;i++) key[i]=0;
//    key[0]=1;
    for (i=0;i<16;i++) iv[i]=i;

	string s =  SymmetricEnc::pad(string("balls on fire 1234567890ABC"));
	int s_len = (int) s.size();

    SymmetricEnc symenc;
    cout << s << endl;
    char *block2 = (char *) s.c_str();

    printf("Plain=   ");
    for (i=0;i< 4*NB;i++) printf("%02x",block2[i]);
    printf("\n");

//    char *cipher = (char *) symenc.encrypt(key, block2, s_len).c_str();

    string cipher_text = symenc.encrypt(key, block2, s_len);
    char *cipher = (char *) cipher_text.c_str();
    int c_len = (int) cipher_text.size();
    cout << "Encrypt := " << cipher_text << endl;

//    printf("Encrypt= ");
//    for (i=0;i<4*NB;i++) printf("%02x", (unsigned char) cipher[i]);
    cout << endl << endl;

    printf("Decrypt= ");
    char *msg = (char *) symenc.decrypt(key, cipher, c_len).c_str();
    for (i=0;i<4*NB;i++) printf("%02x", (unsigned char) msg[i]);
    cout << "\n" << msg << endl;
    cout << endl;

    return 0;
}
