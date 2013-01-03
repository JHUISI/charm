#ifndef BUILTIN_H
#define BUILTIN_H

#include "relic_api.h"
#include "CharmList.h"
#include "CharmListZR.h"
#include "CharmListStr.h"

CharmListZR stringToInt(PairingGroup & group, string strID, int z, int l);

/* other functions */
string Element_ToBytes(Element &e);
void Element_FromBytes(Element &e, unsigned char *s);

#endif
