#ifndef PBC_API_H
#define PBC_API_H

// define classes
extern "C" {
   #include <stdlib.h>
   #include <pbc/pbc.h>
   #include "common.h"
}
#include <map>
#include <vector>
#include <string>
#include <sstream>
#include <iostream>
#include <fstream>
#include <math.h>
using namespace std;

#define convert_str(a)  a /* nothing */
void ro_error(void);

class CharmList;

class ZR
{
public:
	element_t z;
//	element_t order;
	bool isInit;
	ZR() 	 { isInit = true; }
	ZR(int);
	ZR(char*);
	ZR(element_t y) { element_init_same_as(z, y); isInit = true; }
	ZR(const ZR& w) { bn_inits(z); bn_inits(order); bn_copy(z, w.z); bn_copy(order, w.order); isInit = true; }
	~ZR() { bn_free(z); bn_free(order); }
	ZR& operator=(const ZR& w)
	{
		if (isInit == true) { bn_copy(z, w.z); bn_copy(order, w.order); }
		else ro_error();
		return *this;
	}
	bool ismember();
	friend ZR hashToZR(string);
	friend ZR power(const ZR&, int);
	friend ZR power(const ZR&, const ZR&);
	friend ZR operator-(const ZR&);
	friend ZR operator-(const ZR&,const ZR&);
	friend ZR operator+(const ZR&,const ZR&);
	friend ZR operator*(const ZR&,const ZR&);
	friend ZR operator/(const ZR&,const ZR&);
    friend ZR operator&(const ZR&, const ZR&);  // bitwise-AND
//    friend ZR operator|(const ZR&, const ZR&);  // bitwise-OR
//    friend ZR operator^(const ZR&, const ZR&);  // bitwise-XOR
    friend ZR operator<<(const ZR&, int);
    friend ZR operator>>(const ZR&, int);

    friend ostream& operator<<(ostream&, const ZR&);
	friend bool operator==(const ZR& x,const ZR& y)
      {if(bn_cmp(x.z, y.z) == CMP_EQ) return true; else return false; }
	friend bool operator!=(const ZR& x,const ZR& y)
      {if (bn_cmp(x.z, y.z) != CMP_EQ) return true; else return false; }
};
