#ifndef COMMON_H
#define COMMON_H

enum ZR_type { ZR_t = 0, listZR_t = 1 };
enum G1_type { G1_t = 2, listG1_t = 3 };
#if ASYMMETRIC == 1
enum G2_type { G2_t = 4, listG2_t = 5 };
#endif
enum GT_type { GT_t = 6, listGT_t = 7 };
enum Other_type { Str_t = 8, listStr_t = 9, int_t = 10, listInt_t = 11, list_t = 12, None_t = 13 };
//enum Basic_type { None_t = 10 };
//int compute_length(int type);

#endif
