#ifndef CHARMLISTINT_H
#define CHARMLISTINT_H

#include "CryptoLib.h"

class CharmListInt
{
public:
	CharmListInt(void);
	~CharmListInt();
    CharmListInt(const CharmListInt&); // copy constructor
    CharmListInt& operator=(const CharmListInt&);
	int length(); // return length of lists
	string printAtIndex(int index);
	void init(int list[], int length);

	int& operator[](const int index);
    friend ostream& operator<<(ostream&, const CharmListInt&);
private:
    int cur_index;
    map<int, int> intList;
};


#endif
