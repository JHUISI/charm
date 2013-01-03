#ifndef CHARMLISTZR_H
#define CHARMLISTZR_H

#include "CryptoLib.h"

class CharmListZR
{
public:
	CharmListZR(void); // static list
	~CharmListZR();
    CharmListZR(const CharmListZR&); // copy constructor
    CharmListZR& operator=(const CharmListZR&);
	void insert(int, ZR);
	void append(ZR&);
	void set(int index, ZR);
	ZR& get(const int index);
	int length(); // return length of lists
	string printAtIndex(int index);

	// retrieve a particular index
	ZR& operator[](const int index);
    friend ostream& operator<<(ostream&, const CharmListZR&);
private:
	int cur_index;
	map<int, ZR> list;
};

#endif
