
#define DEBUG 1
#include "charm_embed_api.h"

int runABETest(Charm_t *pGroup)
{
    Charm_t *pClass = NULL;

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

    PrintObject(pValue);
    PrintObject(pValue1);
    PrintObject(pValue2);
    printf("ct :=> \n");
    PrintObject(pValue3);
    printf("msg :=> \n");
    PrintObject(msg);
    printf("rec msg :=> \n");
    PrintObject(pValue4);

    Free(pValue);
    Free(pValue1);
    Free(pValue2);
    Free(pValue3);
    Free(pValue4);
    Free(skDict);
    Free(pkDict);
    Free(mskDict);
    Free(pKeys);
    Free(pClass);
    return 0;
}

int runHybridABETest(Charm_t *pGroup)
{
    Charm_t *pABEClass = NULL, *pClass = NULL;

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

    printf("g => ");
    PrintObject(pValue);
    printf("beta => ");
    PrintObject(pValue1);
    printf("sk serialized => \n");
    PrintObject(pValue2);
    //	printf("ct :=> \n");
    //	PrintObject(pValue3);
    printf("original msg :=> '%s'\n", msg);
    //	PrintObject(msg);
    printf("rec msg :=> \n");
    PrintObject(rec_msg);

    Free(pValue);
    Free(pValue1);
    Free(pValue2);
    //Free(pValue3);
    Free(rec_msg);
    Free(skDict);
    Free(pkDict);
    Free(mskDict);
    Free(pKeys);
    Free(pClass);
    Free(pABEClass);
    return 0;
}

int main(int argc, char *argv[])
{
    Charm_t *pModule = NULL, *pGroup = NULL;

    InitializeCharm();

    pGroup = InitPairingGroup(pModule, "SS512");
    if(pGroup == NULL) {
        printf("could not import pairing group.\n");
        return -1;
    }

    // runABETest(pGroup);
    runHybridABETest(pGroup);

    Free(pGroup);
    CleanupCharm();
    return 0;
}

