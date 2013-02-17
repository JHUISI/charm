#ifndef BENCHMARK_H
#define BENCHMARK_H

#include <sys/time.h>
#include <string>
#include <sstream>
using namespace std;

typedef struct timeval timeval_t;

class Benchmark
{
public:
	Benchmark() { initBench = false; sum = 0.0; iterationCount = 0; };
	~Benchmark() { };
	void start();
	void stop();
	double computeTimeInMilliseconds();
	int getTimeInMicroseconds();
	string getRawResultString();
	double getAverage();
private:
	timeval_t startT, endT;
	double sum;
	int iterationCount;
	stringstream ss;
	bool initBench;
};

#endif
