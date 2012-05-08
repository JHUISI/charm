#include "sdlconfig.h"
#include <iostream>
#include <ctime>
using namespace std;

typedef unsigned int bench_t;
// double nsec_per_sec = 1000000000; 
int ms_per_sec = 1000;
int i, trials = 100;
bench_t start, stop;

#define setup_bench(o) \
   o = 0;  \
   for(i = 0; i < trials; i++) { \
      start = clock();  
      
#define bench_time(o) \
   stop = clock(); \
   o += (((double)(stop - start) / CLOCKS_PER_SEC)); \
   }

#define bench_print(m, o) cout << m << ((o / trials ) * ms_per_sec) << " ms." << endl; 

int main(int argc, char *argv)
{
    PairingGroup group(AES_SECURITY);
    ZR z, c;
    G1 g1, g1_tmp; 
    G2 g2, g2_tmp;
    GT gt, gt_tmp;
    double res;

    // pairing test
    setup_bench(res); 
       group.random(g1);
       group.random(g2);
       gt_tmp = group.pair(g1, g2);
    bench_time(res);
    
    bench_print("Pairing time :=> ", res);

    setup_bench(res); 
       group.random(gt);
       group.random(c);
       gt_tmp = group.exp(gt, c);
    bench_time(res); 
    bench_print("GT exp time :=> ", res);

    setup_bench(res);
       group.random(g2);
       group.random(c);        
       g2_tmp = group.exp(g2, c);
    bench_time(res);
    bench_print("G2 exp time :=> ", res);

    setup_bench(res);
       group.random(g1);
       group.random(c);        
       g1_tmp = group.exp(g1, c);
    bench_time(res);
    bench_print("G1 exp time :=> ", res);

    setup_bench(res); 
       group.random(gt);
       group.random(gt_tmp);        
       gt_tmp = group.mul(gt, gt_tmp);
    bench_time(res);
    bench_print("GT mul time :=> ", res);

    setup_bench(res)
       group.random(g2);
       group.random(g2_tmp);        
       g2_tmp = group.mul(g2, g2_tmp);
    bench_time(res);
    bench_print("G2 mul time :=> ", res);

    setup_bench(res)
       group.random(g1);
       group.random(g1_tmp);        
       g1_tmp = group.mul(g1, g1_tmp);
    bench_time(res);
    bench_print("G1 mul time :=> ", res);

    return 0;
}
