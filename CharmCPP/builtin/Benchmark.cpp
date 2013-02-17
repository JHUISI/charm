
#include "Benchmark.h"

int sec_in_microsecond = 1000000;
int ms_in_microsecond = 1000;

void Benchmark::start()
{
	initBench = true;
	gettimeofday(&startT, NULL);
}

void Benchmark::stop()
{
	gettimeofday(&endT, NULL);
}

int Benchmark::getTimeInMicroseconds()
{
	if(initBench) {
		return ((endT.tv_sec - startT.tv_sec) * sec_in_microsecond) + (endT.tv_usec - startT.tv_usec);
	}
	return -1.0;
}

double Benchmark::computeTimeInMilliseconds()
{
	if (initBench) {
		double microsec_result = (double) this->getTimeInMicroseconds();
		double rawResult = microsec_result / ms_in_microsecond;
		ss << rawResult << ", ";
		sum += rawResult;
		iterationCount++;
		return rawResult;
	}
	return -1.0; // didn't call start
}

string Benchmark::getRawResultString()
{
	return ss.str();
}

double Benchmark::getAverage()
{
	return sum / iterationCount;
}

