#include "userFuncs_BSW.h"

def decout(sk, ct, transformOutputList, blindingFactord0Blinded, blindingFactord1Blinded, blindingFactord2Blinded, blindingFactor0Blinded, blindingFactor1Blinded):
    input = [sk, ct, transformOutputList, blindingFactord0Blinded, blindingFactord1Blinded, blindingFactord2Blinded, blindingFactor0Blinded, blindingFactor0Blinded, blindingFactor1Blinded, blindingFactor1Blinded]
    id, d0, d1, d2, d3, d4 = sk
    c0, c1, c2, c3, c4, cpr = ct
    result = ((transformOutputList[0] ** blindingFactord0Blinded) * ((transformOutputList[1] ** blindingFactord1Blinded) * ((transformOutputList[2] ** blindingFactord2Blinded) * ((transformOutputList[3] ** blindingFactor0Blinded) * (transformOutputList[4] ** blindingFactor1Blinded)))))
    M = (cpr * result)
    output = M
    return output

int main(int argc, char* argv[])
{
    PairingGroup group(MNT160);

    CharmDict dict;
    ZR zz;
    GT pk;

    Element T0, T1, T2;
    dict.set("T0", T0);
    dict.set("T1", T1);
    dict.set("T2", T2);

    parsePartCT("transformOutputList_BSW_.txt", dict);
    parseKeys("keys_BSW_.txt", zz, pk);

    GT M = decout(group, dict, zz, pk);

    cout << M << endl;

    return 0;
}
