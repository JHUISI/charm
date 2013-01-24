#ifndef CHARMLISTG1_H
#define CHARMLISTG1_H

#include "CryptoLib.h"

struct g_cmp_str
{
	bool operator()(const string a, const string b) {
		return strcmp(a.c_str(), b.c_str()) < 0;
	}
};

class CharmListG1
{
public:
	CharmListG1(void); // static list
	~CharmListG1();
    CharmListG1(const CharmListG1&);
	void insert(int, G1);
	void insert(string, G1);
	void append(G1&);
	void set(int index, G1);
//	G1& get(const int index);
	int length(); // return length of lists
	string printAtIndex(int index);
	string printStrKeyIndex(int index);
	// retrieve a particular index
	G1& operator[](const string index);
	G1& operator[](const int index);
	CharmListG1& operator=(const CharmListG1&);
    friend ostream& operator<<(ostream&, const CharmListG1&);
private:
	int cur_index;
	map<int, G1> list;
	map<string, int, g_cmp_str> strList;
};

class CharmMetaListG1
{
public:
	CharmMetaListG1(void); // static list
	~CharmMetaListG1();
    CharmMetaListG1(const CharmMetaListG1&); // copy constructor
    CharmMetaListG1& operator=(const CharmMetaListG1&);

	// consider adding remove
	void append(CharmListG1&);

	int length(); // return length of lists
	string printAtIndex(int index);

	// retrieve a particular index
	CharmListG1& operator[](const int index);

    friend ostream& operator<<(ostream&, const CharmMetaListG1&);
private:
	int cur_index;
	map<int, CharmListG1> list;
};

#endif
