#include "TestWATERSOut.h"
//#include "benchmark.h"

int main()
{
    Waters09 waters;
    CharmList msk, pk, skBlinded, ct, transformOutputList;
    CharmListStr S;
    GT M, newM;
    ZR bf0;

    waters.setup(msk, pk);
    S.append("ONE");
    S.append("TWO");

    waters.keygen(pk, msk, S, bf0, skBlinded);

    M = waters.group.random(GT_t);
    string policy_str = "(ONE and TWO)";
    waters.encrypt(pk, M, policy_str, ct);

    cout << "ct =\n" << ct << endl;
    int Y;
    waters.transform(pk, skBlinded, S, ct, transformOutputList, Y);
    cout << "transformCT =\n" << transformOutputList << endl;

    waters.decout(pk, S, transformOutputList, bf0, Y, newM);
    cout << convert_str(M) << endl;
    cout << convert_str(newM) << endl;
    if(M == newM) {
      cout << "Successful Decryption!" << endl;
    }
    else {
      cout << "FAILED Decryption." << endl;
    }
    return 0;
}

