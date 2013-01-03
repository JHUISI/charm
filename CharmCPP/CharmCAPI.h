#ifndef CHARMAPI_H
#define CHARMAPI_H

#if BUILD_RELIC == 1
#include "relic_api.h"
#include "CharmList.h"
#include "Builtin.h"

#elif BUILD_MIRACL == 1

//#define ASYMMETRIC
#include <string>
#include <sstream>
#include "MiraclAPI.h"

#endif

#endif
