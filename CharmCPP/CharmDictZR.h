#ifndef CHARMDICTZR_H
#define CHARMDICTZR_H

#include "CryptoLib.h"
#include "CharmListStr.h"

struct cmp_str
{
	bool operator()(const string a, const string b) {
		return strcmp(a.c_str(), b.c_str()) < 0;
	}
};

class CharmDictZR
{
public:
	CharmDictZR(void); // static list
	~CharmDictZR();
    CharmDictZR(const CharmDictZR&); // copy constructor

	int length(); // return length of lists
	CharmListStr keys(); // vector<string>
	string printAll();
	void set(string key, ZR& value);

	// retrieve a particular index
	ZR& operator[](const string key);
    CharmDictZR& operator=(const CharmDictZR&);
    friend ostream& operator<<(ostream&, const CharmDictZR&);
private:
	map<string, ZR, cmp_str> emap;
};

/*
class CharmDict
{
public:
	CharmDict(void); // static list
	~CharmDict();
	// consider adding remove
	void set(string key, Element& value);
	int length(); // return length of lists
	CharmList keys(); // vector<string>
	string printAll();

	// retrieve a particular index
	Element& operator[](const string key);
    friend ostream& operator<<(ostream&, const CharmDict&);

private:
	map<string, Element, cmp_str> emap;
};
*/

#endif
