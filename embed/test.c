
#define DEBUG 1
#include "charm_embed_api.h"

int runABETest(Charm_t *pGroup)
{
	Charm_t *pClass = NULL;
    int pRes = 0;

    pClass = InitScheme("abenc_bsw07", "CPabe_BSW07", pGroup);
    if(pClass == NULL) return -1;

    Charm_t *pKeys = CallMethod(pClass, "setup", "");
    debug("setup ok.\n");

	Charm_t *pkDict = GetIndex(pKeys, 0);
	Charm_t *mskDict = GetIndex(pKeys, 1);

	Charm_t *pValue = GetDict(pkDict, "g");
	Charm_t *pValue1 = GetDict(mskDict, "beta");

	char *attrList = "[ONE, TWO]";

	debug("calling keygen...\n");
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

    return 0;
}

int runHybridABETest(Charm_t *pGroup)
{
	Charm_t *pABEClass = NULL, *pClass = NULL;
    int pRes = 0;

    pABEClass = InitScheme("charm.schemes.abenc.abenc_bsw07", "CPabe_BSW07", pGroup);
    if(pABEClass == NULL) return -1;

    debug("cpabe initialized.\n");

    pClass = InitAdapter("charm.adapters.abenc_adapt_hybrid", "HybridABEnc", pABEClass, pGroup);
    if(pClass == NULL) return -1;

    debug("hyb_abe initialized.\n");

    Charm_t *pKeys = CallMethod(pClass, "setup", "");
    debug("setup ok.\n");

	Charm_t *pkDict = GetIndex(pKeys, 0);
	Charm_t *mskDict = GetIndex(pKeys, 1);

	Charm_t *pValue = GetDict(pkDict, "g");
	Charm_t *pValue1 = GetDict(mskDict, "beta");

	char *attrList = "[ONE, TWO]";

	debug("calling keygen...\n");
	char *policy = "((THREE or ONE) and (THREE or TWO))";
	printf("attribute: '%s'\n", attrList);
	printf("enc policy: '%s'\n", policy);
	Charm_t *skDict = CallMethod(pClass, "keygen", "%O%O%A", pkDict, mskDict, attrList);

	Charm_t *pValue2 = objectToBytes(skDict, pGroup);
    debug("keygen ok.\n");

	//Charm_t *pValue2 = GetDict(skDict, "D");

	char *msg = "this is a test message.";
	Charm_t *ctDict = CallMethod(pClass, "encrypt", "%O%b%s", pkDict, msg, policy);
    debug("encrypt ok.\n");

	Charm_t *rec_msg = CallMethod(pClass, "decrypt", "%O%O%O", pkDict, skDict, ctDict);
    debug("decrypt ok.\n");

	RunCommands(pValue, pRes);
	RunCommands(pValue1, pRes);
	printf("sk serialized => \n");
	RunCommands(pValue2, pRes);
	//	printf("ct :=> \n");
	//	RunCommands(pValue3, pRes);
	printf("original msg :=> '%s'\n", msg);
	//	RunCommands(msg, pRes);
	printf("rec msg :=> \n");
	RunCommands(rec_msg, pRes);

	Free(pValue);
	Free(pValue1);
	Free(pValue2);
//	Free(pValue3);
	Free(rec_msg);
	Free(skDict);
	Free(pkDict);
	Free(mskDict);
	Free(pKeys);

	return 0;
}



int main(int argc, char *argv[])
{
	Charm_t *pModule = NULL, *pGroup;

	InitializeCharm();

    pGroup = InitPairingGroup(pModule, "SS512");
    if(pGroup == NULL) return -1;

    // runABETest(pGroup);
    runHybridABETest(pGroup);

    CleanupCharm();
    return 0;
}

