
#include "TestHVEOut.h"
#include <fstream>
#include <time.h>

void getRandomVector(CharmListInt & vector, int numBits)
{
	double val;
	for(int i = 0; i < numBits; i++) {
		val = rand() % 2;
		if(val >= 0.5) vector[i] = 1;
		else {
			vector[i] = 0;
		}
	}
	//cout << "vector:\n" << vector << endl;
	return;
}


void benchmarkHVE(Hve08 & hve, ofstream & outfile1, ofstream & outfile2, int vectorSize, int iterationCount, CharmListStr & transformResults, CharmListStr & decoutResults)
{
	Benchmark benchT, benchD;
	CharmList pk, msk, CT, skBlinded, transformOutputList;
	CharmMetaListG1 skComplete;
	CharmListInt S;
	int receivers[] = {1, 3, 5, 12, 14};
 	S.init(receivers, 5);
	GT M, newM;
	ZR uf1;
	int n = 4;

	CharmListInt xVector, yVector;
	getRandomVector(yVector, vectorSize);
	xVector = yVector;

//	int _vectorX[] = {1, 1, 0, 1};
//	int _vectorY[] = {1, 1, 0, 1};
//	xVector.init(_vectorX, 4); // generate randomly
//	yVector.init(_vectorY, 4);

	hve.setup(n, pk, msk);
//	cout << "pk: " << pk << endl;
//	cout << "msk: " << msk << endl;

	hve.keygen(pk, msk, yVector, uf1, skBlinded);

	M = hve.group.random(GT_t);
	hve.encrypt(M, xVector, pk, CT);
//	cout << "ct :=\n" << CT << endl;

	double tf_in_ms, de_in_ms;
	stringstream s1, s2;

	for(int i = 0; i < iterationCount; i++) {
 		benchT.start();
		hve.transform(CT, skBlinded, transformOutputList);
		benchT.stop();
		tf_in_ms = benchT.computeTimeInMilliseconds();

		benchD.start();
		hve.decout(transformOutputList, uf1, newM);
		benchD.stop();
		de_in_ms = benchD.computeTimeInMilliseconds();
	}
	cout << "Transform avg: " << benchT.getAverage() << " ms" << endl;
	s1 << vectorSize << " " << benchT.getAverage() << endl;
	outfile1 << s1.str();
    transformResults[0] = benchT.getRawResultString();

	cout << "Decout avg: " << benchD.getAverage() << " ms" << endl;
	s2 << vectorSize << " " << benchD.getAverage() << endl;
	outfile2 << s2.str();
	decoutResults[0] = benchD.getRawResultString();

    cout << convert_str(M) << endl;
    cout << convert_str(newM) << endl;
    if(M == newM) {
      cout << "Successful Decryption!" << endl;
    }
    else {
      cout << "FAILED Decryption." << endl;
    }
}

int main(int argc, const char *argv[])
{
	Hve08 hve;
	srand(time(NULL));

	string filename = "test";
	ofstream outfile1, outfile2;
	string f1 = filename + "_tra.dat";
	string f2 = filename + "_dec.dat";
	outfile1.open(f1.c_str());
	outfile2.open(f2.c_str());

	int iterationCount = 10;
	int vectorSize = 128;
	int i = vectorSize;
	CharmListStr transformResults, decoutResults;
	//for(int i = 2; i <= attributeCount; i++) {
		cout << "Benchmark with " << i << "-bit sized vectors." << endl;
		benchmarkHVE(hve, outfile1, outfile2, i, iterationCount, transformResults, decoutResults);
	//}

	outfile1.close();
	outfile2.close();
	cout << "<=== Transform benchmarkBSW breakdown ===>" << endl;
	cout << transformResults << endl;
	cout << "<=== Transform benchmarkBSW breakdown ===>" << endl;

	cout << "<=== Decout benchmarkBSW breakdown ===>" << endl;
	cout << decoutResults << endl;
	cout << "<=== Decout benchmarkBSW breakdown ===>" << endl;

    return 0;
}
