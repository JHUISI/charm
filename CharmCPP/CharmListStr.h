#ifndef CHARMLISTSTR_H
#define CHARMLISTSTR_H

#include "CryptoLib.h"

class CharmListStr
{
public:
	CharmListStr(void); // static list
	~CharmListStr();
    CharmListStr(const CharmListStr&); // copy constructor
	void append(string&);
	void append(string);
	void insert(int, string&);
	void insert(int, string);
	int length(); // return length of lists
	string printAtIndex(int index);

	// retrieve a particular index
	string& operator[](const int index);
    CharmListStr& operator=(const CharmListStr&);
    friend ostream& operator<<(ostream&, const CharmListStr&);
private:
	int cur_index;
	map<int, string> list;
};

bool isEqual(string value1, string value2);
bool isNotEqual(string value1, string value2);
string concat(CharmListStr & list);
string GetString(string & list);

#endif

