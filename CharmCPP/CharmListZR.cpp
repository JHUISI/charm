
#include "CharmListZR.h"

// start CharmListZR implementation

CharmListZR::CharmListZR(void)
{
	// increases as elements are appended
	cur_index = 0;
}

CharmListZR::~CharmListZR()
{
	for(int i = 0; i < (int) list.size(); i++)
		list.erase(i);
}

CharmListZR::CharmListZR(const CharmListZR& cList)
{
	//copy constructor
	cur_index = cList.cur_index;
	list = cList.list;
}

void CharmListZR::insert(int index, ZR zr)
{
	list[index] = zr;
	cur_index++;
}

void CharmListZR::append(ZR & zr)
{
	list[cur_index] = zr;
	cur_index++;
}

void CharmListZR::set(int index, ZR zr)
{
	ZR *zr2 = new ZR(zr);
	list[index] = *zr2;
}

ZR& CharmListZR::operator[](const int index)
{
	if(index == cur_index) { // means we are creating reference.
//		list[cur_index] = NULL;
		cur_index++;
		return list[index];
	}
	else if(index < MAX_LIST) {
		return list[index];
	}

	int len = (int) list.size();
	if(index >= 0 && index < len) {
		return list[index];
	}
	else {
		throw new string("Invalid access.\n");
	}
}

ZR& CharmListZR::get(const int index)
{
	int len = (int) list.size();
	if(index >= 0 && index < len) {
		return list[index];
	}
	else {
		throw new string("Invalid access.\n");
	}
}

int CharmListZR::length()
{
	return (int) list.size();
}

string CharmListZR::printAtIndex(int index)
{
	stringstream ss;
	int i;

	if(index >= 0 && index < (int) list.size()) {
		i = index;
		ss << list[i];
	}

	string s = ss.str();
	return s;
}

ostream& operator<<(ostream& s, const CharmListZR& cList)
{
	CharmListZR cList2 = cList;

	for(int i = 0; i < cList2.length(); i++) {
		s << i << ": " << cList2.printAtIndex(i) << endl;
	}

	return s;
}

CharmListZR& CharmListZR::operator=(const CharmListZR& cList)
{
	if(this == &cList)
		return *this;

	// delete current list contents first
	int i;
	for(i = 0; i < (int) list.size(); i++)
		list.erase(i);
	cur_index = 0;

	cur_index = cList.cur_index;
	list = cList.list;
	return *this;
}
