#include "TestWATERS.h"

string createString(int i)
{
	stringstream ss;
	ss << "ATTR" << i;
	return ss.str();
}

void getAttributes(CharmListStr & attrList, int max)
{
	for(int i = 1; i <= max; i++) {
		attrList.append(createString(i));
	}
}

string getPolicy(int max)
{
	string policystr;
	if(max >= 2) {
		policystr = "(" + createString(1) + " and " + createString(2) + ")";
	}
	else if(max == 1) {
		policystr = createString(1);
	}

	for(int i = 3; i <= max; i++)
	{
		policystr = "(" + policystr + " and " + createString(i) + ")";
	}

	return policystr;
}

void benchmarkWATERS(Waters09 & waters, ofstream & outfile0, ofstream & outfile1, ofstream & outfile2, int attributeCount, int iterationCount, CharmListStr & keygenResults, CharmListStr & transformResults, CharmListStr & decoutResults)
{
	Benchmark benchT, benchD, benchK;
    CharmList msk, pk, skBlinded, skBlinded2, ct, transformOutputList;
    CharmListStr S;
    GT M, newM;
    ZR bf0;
    stringstream s0, s1, s2;
    double tf_in_ms, de_in_ms, kg_in_ms;

    waters.setup(msk, pk);
	getAttributes(S, attributeCount);

	// BENCHMARK KEYGEN SETUP
	for(int i = 0; i < iterationCount; i++) {
		benchK.start();
		waters.keygen(pk, msk, S, bf0, skBlinded2);
		benchK.stop();
		kg_in_ms = benchK.computeTimeInMilliseconds();
	}
	cout << "Keygen avg: " << benchK.getAverage() << " ms" << endl;
	s0 << attributeCount << " " << benchK.getAverage() << endl;
	outfile0 << s0.str();
    keygenResults[attributeCount] = benchK.getRawResultString();
	// BENCHMARK KEYGEN SETUP

    waters.keygen(pk, msk, S, bf0, skBlinded);

    M = waters.group.random(GT_t);
    string policy_str =  getPolicy(attributeCount); // get a policy string
    waters.encrypt(pk, M, policy_str, ct);


    //cout << "ct =\n" << ct << endl;
	for(int i = 0; i < iterationCount; i++) {
		benchT.start();
		waters.transform(pk, skBlinded, S, ct, transformOutputList);
		benchT.stop();
		tf_in_ms = benchT.computeTimeInMilliseconds();
		//cout << "transformCT =\n" << transformOutputList << endl;

		benchD.start();
		waters.decout(pk, S, transformOutputList, bf0, newM);
		benchD.stop();
		de_in_ms = benchD.computeTimeInMilliseconds();
	}

	cout << "Transform avg: " << benchT.getAverage() << endl;
	s1 << attributeCount << " " << benchT.getAverage() << endl;
	outfile1 << s1.str();
    transformResults[attributeCount] = benchT.getRawResultString();

	cout << "Decout avg: " << benchD.getAverage() << endl;
	s2 << attributeCount << " " << benchD.getAverage() << endl;
	outfile2 << s2.str();
	decoutResults[attributeCount] = benchD.getRawResultString();

	// measure ciphertext size
	cout << "CT size: " << measureSize(ct) << " bytes" << endl;
	cout << "CTOut size: " << measureSize(transformOutputList) << " bytes" << endl;
//    cout << convert_str(M) << endl;
//    cout << convert_str(newM) << endl;
    if(M == newM) {
      cout << "Successful Decryption!" << endl;
    }
    else {
      cout << "FAILED Decryption." << endl;
    }
    return;
}

int main(int argc, const char *argv[])
{
	string FIXED = "fixed", RANGE = "range";
	if(argc != 4) { cout << "Usage " << argv[0] << ": [ iterationCount => 10 ] [ attributeCount => 100 ] [ 'fixed' or 'range' ]" << endl; return -1; }

	int iterationCount = atoi( argv[1] );
	int attributeCount = atoi( argv[2] );
	string fixOrRange = string(argv[3]);
	cout << "iterationCount: " << iterationCount << endl;
	cout << "attributeCount: " << attributeCount << endl;
	cout << "measurement: " << fixOrRange << endl;

	Waters09 waters;
	string filename = string(argv[0]);
	stringstream s3, s4, s5;
	ofstream outfile0, outfile1, outfile2, outfile3, outfile4, outfile5;
	string f0 = filename + "_keygenout.dat";
	string f1 = filename + "_transform.dat";
	string f2 = filename + "_decout.dat";
	string f3 = filename + "_transform_raw.txt";
	string f4 = filename + "_decout_raw.txt";
	string f5 = filename + "_keygenout_raw.txt";
	outfile0.open(f0.c_str());
	outfile1.open(f1.c_str());
	outfile2.open(f2.c_str());
	outfile3.open(f3.c_str());
	outfile4.open(f4.c_str());
	outfile5.open(f5.c_str());

	CharmListStr keygenResults, transformResults, decoutResults;
	if(isEqual(fixOrRange, RANGE)) {
		for(int i = 2; i <= attributeCount; i++) {
			cout << "Benchmark with " << i << " attributes." << endl;
			benchmarkWATERS(waters, outfile0, outfile1, outfile2, i, iterationCount, keygenResults, transformResults, decoutResults);
		}
		s3 << transformResults << endl;
		s4 << decoutResults << endl;
	}
	else if(isEqual(fixOrRange, FIXED)) {
		cout << "Benchmark with " << attributeCount << " attributes." << endl;
		benchmarkWATERS(waters, outfile0, outfile1, outfile2, attributeCount, iterationCount, keygenResults, transformResults, decoutResults);
		s3 << attributeCount << " " << transformResults[attributeCount] << endl;
		s4 << attributeCount << " " << decoutResults[attributeCount] << endl;
		s5 << attributeCount << " " << keygenResults[attributeCount] << endl;
	}
	else {
		cout << "invalid option." << endl;
		return -1;
	}

	outfile3 << s3.str();
	outfile4 << s4.str();
	outfile5 << s5.str();
	outfile0.close();
	outfile1.close();
	outfile2.close();
	outfile3.close();
	outfile4.close();
	outfile5.close();
//	cout << "<=== Transform benchmarkWATERS breakdown ===>" << endl;
//	cout << transformResults << endl;
//	cout << "<=== Transform benchmarkWATERS breakdown ===>" << endl;
//	cout << "<=== Decout benchmarkWATERS breakdown ===>" << endl;
//	cout << decoutResults << endl;
//	cout << "<=== Decout benchmarkWATERS breakdown ===>" << endl;

	return 0;
}

