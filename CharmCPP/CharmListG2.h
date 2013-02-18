#ifndef CHARMLISTG2_H
#define CHARMLISTG2_H

#include "CryptoLib.h"
#include "CharmListInt.h"
#include "CharmListStr.h"

#if ASYMMETRIC == 1

struct g2_cmp_str
{
	bool operator()(const string a, const string b) {
		return strcmp(a.c_str(), b.c_str()) < 0;
	}
};


class CharmListG2
{
public:
	CharmListG2(void); // static list
	~CharmListG2();
    CharmListG2(const CharmListG2&);
	void insert(int, G2);
	void insert(string, G2);
	void append(G2&);
	CharmListInt keys();
	CharmListStr strkeys();
	int length(); // return length of lists
	string printAtIndex(int index);
	string printStrKeyIndex(int index);
	// retrieve a particular index
	G2& operator[](const string index);
	G2& operator[](const int index);
	CharmListG2& operator=(const CharmListG2&);
    friend ostream& operator<<(ostream&, const CharmListG2&);
private:
	int cur_index;
	map<int, G2> list;
	map<string, int, g2_cmp_str> strList;
};

class CharmMetaListG2
{
public:
	CharmMetaListG2(void); // static list
	~CharmMetaListG2();
    CharmMetaListG2(const CharmMetaListG2&); // copy constructor
    CharmMetaListG2& operator=(const CharmMetaListG2&);

	// consider adding remove
	void append(CharmListG2&);

	int length(); // return length of lists
	string printAtIndex(int index);

	// retrieve a particular index
	CharmListG2& operator[](const int index);

    friend ostream& operator<<(ostream&, const CharmMetaListG2&);
private:
	int cur_index;
	map<int, CharmListG2> list;
};

#endif

#endif
