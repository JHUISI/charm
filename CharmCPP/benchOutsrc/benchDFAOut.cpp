
#include "TestDFAOut.h"

string getRandomHexString(int len)
{
	string hex = "0x";
	if(len == 2) return hex;
	else if(len > 2) {
		string alpha = "ABCDEFabcdef0123456789";
		int val, alpha_len = alpha.size();
		for(int i = 0; i < len-2; i++)
		{
			val = (int) (rand() % alpha_len);
			hex +=  alpha[val];
		}
		cout << "Hex Value: '" << hex << "'" << endl;
	}
	else {
		cout << "getRandomHexString: invalid len => " << len << endl;
		return "";
	}
	return hex;

}

void benchmarkDFA(Dfa12 & dfa12, ofstream & outfile1, ofstream & outfile2, int wStringCount, int iterationCount, CharmListStr & transformResults, CharmListStr & decoutResults)
{
	Benchmark benchT, benchD;
	string letters = "xABCDEFabcdef0123456789";
	dfa12.dfaUtil.constructDFA("0x(0|1|2|3|4|5|6|7|8|9|a|b|c|d|e|f|A|B|C|D|E|F)*", letters);
	CharmList mpk, skBlinded, ct, transformOutputList, transformOutputListForLoop;
	CharmListStr alphabet = dfa12.dfaUtil.getAlphabet();
	CharmListStr w;
	CharmListInt Q = dfa12.dfaUtil.getStates(), F = dfa12.dfaUtil.getAcceptStates(); // get all states, and all accept states
	CharmMetaListInt T = dfa12.dfaUtil.getTransitions(); // get all transitions in DFA
	ZR bf0;
	G1 msk;
	GT M, newM, Cm;

	//cout << "Q:\n" << Q << endl;
	//cout << "F:\n" << F << endl;
	//cout << "T:\n" << T << endl;

	dfa12.setup(alphabet, mpk, msk);

	//cout << "MPK:\n" << mpk << endl;
	//cout << "MSK:\n" << convert_str(msk) << endl;
	dfa12.keygen(mpk, msk, Q, T, F, bf0, skBlinded);

	//cout << "SK:\n" << skBlinded << endl;

	w = dfa12.dfaUtil.getSymbols(getRandomHexString(wStringCount)); // "aba"
	M = dfa12.group.random(GT_t);
	dfa12.encrypt(mpk, w, M, ct);
	double tf_in_ms, de_in_ms;

	if(dfa12.dfaUtil.accept(w)) {
		cout << "isAccept: true" << endl;
		CharmMetaListInt Ti = dfa12.dfaUtil.getTransitions(w); // 1
		cout << "transitions to decrypt: " << Ti.length() << endl;
		int x = dfa12.dfaUtil.getAcceptState(Ti); // 2
		int l = 0;
		stringstream s1, s2;
		for(int i = 0; i < iterationCount; i++) {
			benchT.start();
			dfa12.transform(skBlinded, ct, transformOutputList, l, Ti, x, transformOutputListForLoop);
			benchT.stop();
			tf_in_ms = benchT.computeTimeInMilliseconds();

			benchD.start();
			dfa12.decout(transformOutputList, bf0, l, Ti, transformOutputListForLoop, newM);
			benchD.stop();
			de_in_ms = benchD.computeTimeInMilliseconds();
		}
		cout << "Transform avg: " << benchT.getAverage() << " ms" << endl;
		s1 << wStringCount << " " << benchT.getAverage() << endl;
		outfile1 << s1.str();
                outfile1.flush();
	    transformResults[wStringCount] = benchT.getRawResultString();

		cout << "Decout avg: " << benchD.getAverage() << " ms" << endl;
		s2 << wStringCount << " " << benchD.getAverage() << endl;
		outfile2 << s2.str();
                outfile2.flush();
		decoutResults[wStringCount] = benchD.getRawResultString();
//		cout << convert_str(M) << endl;
//		cout << convert_str(newM) << endl;
		if(M == newM) {
		  cout << "Successful Decryption!" << endl << endl;
		}
		else {
		  cout << "FAILED Decryption." << endl << endl;
		}
	}
	else {
		cout << "isAccept: false" << endl;
	}
    return;
}

int main(int argc, const char *argv[])
{
	string FIXED = "fixed", RANGE = "range";
	if(argc != 5) { cout << "Usage " << argv[0] << ": [ iterationCount => 10 ] [ wStringCount => 1000 ] [ incrementCount => 25 ] [ 'fixed' or 'range' ]" << endl; return -1; }

	int iterationCount = atoi( argv[1] );
	int wStringCount = atoi( argv[2] );
	int incrementCount = atoi( argv[3] );
	string fixOrRange = string( argv[4] );
	cout << "iterationCount: " << iterationCount << endl;
	cout << "wStringCount: " << wStringCount << endl;
	cout << "incrementCount: " << incrementCount << endl;
	cout << "measurement: " << fixOrRange << endl;

	Dfa12 dfa12;
	string filename = string(argv[0]);
	stringstream s3, s4;
	ofstream outfile1, outfile2, outfile3, outfile4;
	string f1 = filename + "_transform.dat";
	string f2 = filename + "_decout.dat";
	string f3 = filename + "_transform_raw.txt";
	string f4 = filename + "_decout_raw.txt";
	outfile1.open(f1.c_str());
	outfile2.open(f2.c_str());
	outfile3.open(f3.c_str());
	outfile4.open(f4.c_str());

	CharmListStr transformResults, decoutResults;
	if(isEqual(fixOrRange, RANGE)) {
		for(int i = 2; i <= wStringCount; i += incrementCount) {
			cout << "Benchmark with " << i << " wStringCount." << endl;
			benchmarkDFA(dfa12, outfile1, outfile2, i, iterationCount, transformResults, decoutResults);
		}
		s3 << transformResults << endl;
		s4 << decoutResults << endl;
	}
	else if(isEqual(fixOrRange, FIXED)) {
		cout << "Benchmark with " << wStringCount << " wStringCount." << endl;
		benchmarkDFA(dfa12, outfile1, outfile2, wStringCount, iterationCount, transformResults, decoutResults);
		s3 << wStringCount << " " << transformResults[wStringCount] << endl;
		s4 << wStringCount << " " << decoutResults[wStringCount] << endl;
	}
	else {
		cout << "invalid option." << endl;
		return -1;
	}

	outfile3 << s3.str();
	outfile4 << s4.str();
	outfile1.close();
	outfile2.close();
	outfile3.close();
	outfile4.close();
//	cout << "<=== Transform benchmarkWATERS breakdown ===>" << endl;
//	cout << transformResults << endl;
//	cout << "<=== Transform benchmarkWATERS breakdown ===>" << endl;
//	cout << "<=== Decout benchmarkWATERS breakdown ===>" << endl;
//	cout << decoutResults << endl;
//	cout << "<=== Decout benchmarkWATERS breakdown ===>" << endl;

	return 0;
}

//	Dfa12 dfa12;
//	dfa12.dfaUtil.constructDFA("ab*a", "ab");
//	CharmListStr w = dfa12.dfaUtil.getSymbols("aba");
//	CharmMetaListInt Ti = dfa12.dfaUtil.getTransitions(w); // 1
//	int x = dfa12.dfaUtil.getAcceptState(Ti); // 2

//	dfa12.dfaUtil.constructDFA("(0|1|2|3|4|5|6|7|8|9)*-(a|b|c)*-(0|1|2|3|4|5|6|7|8|9)*", "abc0123456789-"); // "abcdefghijklmnopqrstuvwxyz0123456789"
