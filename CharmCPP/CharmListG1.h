#ifndef CHARMLISTG1_H
#define CHARMLISTG1_H

#include "CryptoLib.h"

class CharmListG1
{
public:
	CharmListG1(void); // static list
	~CharmListG1();
    CharmListG1(const CharmListG1&);
	void insert(int, G1);
	void append(G1&);
	void set(int index, G1);
//	G1& get(const int index);
	int length(); // return length of lists
	string printAtIndex(int index);

	// retrieve a particular index
	G1& operator[](const int index);
	CharmListG1& operator=(const CharmListG1&);
    friend ostream& operator<<(ostream&, const CharmListG1&);
private:
	int cur_index;
	map<int, G1> list;
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
