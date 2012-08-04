
#include "charm_embed_api.h"

int main(int argc, char *argv[])
{
    PyObject *pName, *pModule = NULL, *pGroup = NULL, *pFunc, *pClass;
    int pRes = 0;

    InitializeCharm();

    pGroup = InitPairingGroup(pModule, "SS512");
    if(pGroup == NULL) return -1;

    pClass = InitClass("abenc_bsw07", "CPabe_BSW07", pGroup);
    if(pClass == NULL) return -1;

    Charm_t *pKeys = CallMethod(pClass, "setup", "");
    debug("setup ok.\n");

	Charm_t *pkDict = GetIndex(pKeys, 0);
	Charm_t *mskDict = GetIndex(pKeys, 1);

	Charm_t *pValue = GetDict(pkDict, "g");
	Charm_t *pValue1 = GetDict(mskDict, "beta");

	char *attrList = "[ONE, TWO, THREE]";

	printf("calling keygen...\n");
	int i;
	char *policy = "((THREE or ONE) and (THREE or TWO))";
	printf("attribute: '%s'\n", attrList);
	printf("enc policy: '%s'\n", policy);
	Charm_t *skDict = CallMethod(pClass, "keygen", "%O%O%A", pkDict, mskDict, attrList);

	Charm_t *pValue2 = GetDict(skDict, "D");

	Charm_t *msg = CallMethod(pGroup, "random", "%I", GT);
	Charm_t *ctDict = CallMethod(pClass, "encrypt", "%O%O%s", pkDict, msg, policy);
	Charm_t *pValue3 = GetDict(ctDict, "C_tilde");

	Charm_t *pValue4 = CallMethod(pClass, "decrypt", "%O%O%O", pkDict, skDict, ctDict);

	RunCommands(pValue, pRes);
	RunCommands(pValue1, pRes);
	RunCommands(pValue2, pRes);
	printf("ct :=> \n");
	RunCommands(pValue3, pRes);
	printf("msg :=> \n");
	RunCommands(msg, pRes);
	printf("rec msg :=> \n");
	RunCommands(pValue4, pRes);

	Free(pValue);
	Free(pValue1);
	Free(pValue2);
	Free(pValue3);
	Free(pValue4);
	Free(skDict);
	Free(pkDict);
	Free(mskDict);
	Free(pKeys);

    CleanupCharm();
    return 0;
}
