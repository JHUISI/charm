#ifndef CHARMLISTGT_H
#define CHARMLISTGT_H

#include "CryptoLib.h"

class CharmListGT
{
public:
	CharmListGT(void);
	~CharmListGT();
    CharmListGT(const CharmListGT&);
	void insert(int, GT&);
	void append(GT&);
	int length(); // return length of lists
	string printAtIndex(int index);

	// retrieve a particular index
	GT& operator[](const int index);
	CharmListGT& operator=(const CharmListGT&);
    friend ostream& operator<<(ostream&, const CharmListGT&);
private:
	int cur_index;
	map<int, GT> list;
};

class CharmMetaListGT
{
public:
	CharmMetaListGT(void); // static list
	~CharmMetaListGT();
    CharmMetaListGT(const CharmMetaListGT&); // copy constructor
    CharmMetaListGT& operator=(const CharmMetaListGT&);
	// consider adding remove
	void append(CharmListGT&);

	int length(); // return length of lists
	string printAtIndex(int index);

	// retrieve a particular index
	CharmListGT& operator[](const int index);

    friend ostream& operator<<(ostream&, const CharmMetaListGT&);
private:
	int cur_index;
	map<int, CharmListGT> list;
};

#endif
