#include <iostream>
#include <ctime>
#include <map>
#include <sstream>
#define MR_PAIRING_MNT
#define AES_SECURITY 80
#include "pairing_3.h"
#include <map>
#include <sstream>
#define Group PFC

#ifndef VERCPP_H
#define VERCPP_H

extern void verifySigsRecursive(map<int, map<string, G2> > pk, map<int, G1> sig, map<int, string> message, Group group, int startSigNum, int endSigNum, Big delta[], G1 dotA[], G1 dotB[]);

#endif
