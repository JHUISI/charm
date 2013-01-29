
#include "CharmListInt.h"

CharmListInt::CharmListInt(void)
{
	// increases as elements are appended
	cur_index = 0;
}

CharmListInt::~CharmListInt()
{
	intList.clear();
}

CharmListInt::CharmListInt(const CharmListInt & cList)
{
	cur_index = cList.cur_index;
	intList = cList.intList;
}

int CharmListInt::length()
{
	return (int) intList.size();
}

void CharmListInt::init(int list[], int length)
{
	int i;
	cur_index = 0;
	for(i = 0; i < length; i++) {
		intList[i] = list[i];
		cur_index++;
	}
}

string CharmListInt::printAtIndex(int index)
{
	stringstream ss;
	int i;

	if(index >= 0 && index < (int) intList.size()) {
		i = index;
		ss << intList[i];
	}

	string s = ss.str();
	return s;
}


CharmListInt& CharmListInt::operator=(const CharmListInt& cList)
{
	if(this == &cList)
		return *this;

	// delete current list contents first
	intList.clear();
	cur_index = 0;

	cur_index = cList.cur_index;
	intList = cList.intList;
	return *this;
}

int& CharmListInt::operator[](const int index)
{
	if(index == cur_index) { // means we are creating reference.
		cur_index++;
		return intList[index];
	}
	else if(index < MAX_LIST) {
		return intList[index];
	}

	int len = (int) intList.size();
	if(index >= 0 && index < len) {
		return intList[index];
	}
	else {
		throw new string("Invalid access.\n");
	}
}

ostream& operator<<(ostream& s, const CharmListInt& cList)
{
	CharmListInt cList2 = cList;

	for(int i = 0; i < cList2.length(); i++) {
		s << i << ": " << cList2.printAtIndex(i) << endl;
	}

	return s;
}

