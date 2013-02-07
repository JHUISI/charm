#ifndef CHARMLISTINT_H
#define CHARMLISTINT_H

#include "CryptoLib.h"

struct i_cmp_str
{
	bool operator()(const string a, const string b) {
		return strcmp(a.c_str(), b.c_str()) < 0;
	}
};


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

class CharmMetaListInt
{
public:
	CharmMetaListInt(void); // static list
	~CharmMetaListInt();
    CharmMetaListInt(const CharmMetaListInt&); // copy constructor
    CharmMetaListInt& operator=(const CharmMetaListInt&);

	// consider adding remove
	void insert(int, CharmListInt);
	void insert(string, CharmListInt);
	void append(CharmListInt&);

	int length(); // return length of lists
	string printAtIndex(int index);
	string printStrKeyIndex(int index);
	// retrieve a particular index
	CharmListInt& operator[](const int index);
	CharmListInt& operator[](const string index);

    friend ostream& operator<<(ostream&, const CharmMetaListInt&);
private:
	int cur_index;
	map<int, CharmListInt> list;
	map<string, int, i_cmp_str> strList;
};



#endif
