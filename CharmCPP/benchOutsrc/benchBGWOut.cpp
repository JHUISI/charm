
#include "TestBGWOut.h"


void benchmarkBGW()
{
	Bgw05 bgw;
	CharmList pk, msk, Hdr, ct, skCompleteBlinded, transformOutputList;
	CharmMetaListG1 skComplete;
	CharmListInt S;
	int receivers[] = {1, 3, 5, 12, 14};
 	S.init(receivers, 5);
	GT K, KDecrypt;
	ZR bf0;
	int n = 15, i = 1;

	bgw.setup(n, pk, msk);
//	cout << "pk: " << pk << endl;
//	cout << "msk: " << msk << endl;

	bgw.keygen(pk, msk, n, bf0, skCompleteBlinded);
//	cout << "tk: " <<  skCompleteBlinded << endl;
//	cout << "bf: " << bf0 << endl;
	bgw.encrypt(S, pk, n, ct);
	cout << "ct := " << endl;
	Hdr = ct[0].getList();
	K = ct[1].getGT();

	bgw.transform(S, i, n, Hdr, pk, skCompleteBlinded, transformOutputList);

	bgw.decout(S, i, n, Hdr, pk, skCompleteBlinded, transformOutputList, bf0, KDecrypt);
    cout << convert_str(K) << endl;
    cout << convert_str(KDecrypt) << endl;
    if(K == KDecrypt) {
      cout << "Successful Decryption!" << endl;
    }
    else {
      cout << "FAILED Decryption." << endl;
    }
}

int main()
{
	benchmarkBGW();
    return 0;
}
