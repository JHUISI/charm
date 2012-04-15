#include "sdlconfig.h"
#include <iostream>
#include <sstream>
#include <string>
using namespace std;

#define NB 4
#define TEST_ALL

int main()
{
	PairingGroup group(AES_SECURITY);

	string Rstr = "3:MjA6Z+Jw6hcPR40MRNKKrA4FV8ztPDwyMDpmf6K/0CrHw4UQst1iYq9QFB7woDIwOiunSkccLEXajoQFyGtZGcSjGNVkMjA6gzTplMwMwpbCsDdURVNxWj1UbWUyMDptgzr4zmIPwYDgcRrNg3lqlLLbqzIwOkAsvloI9I6glmnaQScHX0+tCsry";
	string T1str = "w/gRnW9W7Toc7JvIJmqvyw==";
	Element elem;
	Element::deserialize(elem, Rstr);
	GT R = elem.getGT();
	string s_sesskey = DeriveKey(R);

	cout << "Session key := " << s_sesskey << endl;

//	csprng RNG;
//	string raw = "seeding RNG"; // read
//	strong_init(&RNG, (int) raw.size(), (char *) raw.c_str(), 0L);
//	cout << strong_rng(&RNG) << endl;
//	strong_kill(&RNG);

    int i;
    char *key = (char *) s_sesskey.c_str();
    char iv[16];
//    for (i=0;i<32;i++) key[i]=0;
//    key[0]=1;
    for (i=0;i<16;i++) iv[i]=i;

    SymmetricEnc symenc;
#ifdef TEST_ALL
	string s =  "hello world12345"; // SymmetricEnc::pad(string("hello world12345"));
	int s_len = (int) s.size();
    cout << s_len << ": '" << s << "'" << endl;
    char *block2 = (char *) s.c_str();

    printf("Plain=   ");
    for (i=0;i< s_len;i++) printf("%02x",block2[i]);
    printf("\n");

//    char *cipher = (char *) symenc.encrypt(key, block2, s_len).c_str();

    string cipher_text = symenc.encrypt(key, block2, s_len);
    if (strcmp(T1str.c_str(), cipher_text.c_str()) == 0) { cout << "Houston, we have a match. Charm-Python and Charm-C++ in sync." << endl; }
    char *cipher = (char *) cipher_text.c_str();
    int c_len = (int) cipher_text.size();
    cout << "Encrypt := " << cipher_text << endl << endl;

//    printf("Encrypt= ");
//    for (i=0;i<4*NB;i++) printf("%02x", (unsigned char) cipher[i]);

#else
    string c = "Bj0xj6oA74Ot02AAVFUt9DM0NTY3ODkwQUJDICAgICA=";
    char *cipher = (char *) c.c_str();
    int c_len = (int) c.size();
#endif
    printf("Decrypt= ");
    char *msg = (char *) symenc.decrypt(key, cipher, c_len).c_str();
    for (i=0;i< s_len;i++) printf("%02x", (unsigned char) msg[i]);
    cout << "\n" << msg << endl;
    cout << endl;

    return 0;
}
