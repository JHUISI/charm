#include "sdlconfig.h"
#include <iostream>
#include <sstream>
#include <string>
using namespace std;
#define DEBUG  true

groupObjUserFuncs = NULL

void DeriveKey(R)
{
	getUserGlobals();
	return;
}

void SymDec(s_sesskey, T1)
{
	getUserGlobals();
	return;
}

void userErrorFunction(userErrorFunctionArgString)
{
	getUserGlobals();
	return;
}

void getUserGlobals()
{
	if (groupObjUserFuncs == NULL)
	{
		PairingGroup groupObjUserFuncs(AES_SECURITY);
	}
}
