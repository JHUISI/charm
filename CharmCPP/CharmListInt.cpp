
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

bool CharmListInt::contains(int value)
{
	int i;
	for(i = 0; i < (int) intList.size(); i++) {
		if(intList[i] == value)
			return true;
	}
	return false;
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

CharmMetaListInt::CharmMetaListInt(void)
{
	// increases as elements are appended
	cur_index = 0;
}

CharmMetaListInt::~CharmMetaListInt()
{
	list.clear();
	strList.clear();
}

CharmMetaListInt::CharmMetaListInt(const CharmMetaListInt& cList)
{
	//copy constructor
	cur_index = cList.cur_index;
	strList = cList.strList;
	list = cList.list;
}

void CharmMetaListInt::insert(int index, CharmListInt m)
{
	list[index] = m;
	cur_index++;
}

void CharmMetaListInt::insert(string index, CharmListInt m)
{
	int the_index;
	// see if index exists in strList. If so, use that index
	if(strList.find(index) == strList.end()) {
		the_index = cur_index; // select current index
		strList.insert(pair<string, int>(index, the_index));
	}
	else {
		// retrieve the index
		the_index = strList[index];
	}

	list[the_index] = m;
	cur_index++;
}


void CharmMetaListInt::append(CharmListInt & zr)
{
	list[cur_index] = zr;
	cur_index++;
}

CharmListInt& CharmMetaListInt::operator[](const int index)
{
	if(index == cur_index) { // means we are creating reference.
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

CharmListInt& CharmMetaListInt::operator[](const string index)
{
	int the_index;
	if(strList.find(index) == strList.end()) {
		the_index = cur_index; // select current index
		strList[index] = the_index;
		cur_index++;
	}
	else {
		// retrieve the index
		the_index = strList[index];
	}

	return list[the_index];
}

int CharmMetaListInt::length()
{
	return (int) list.size();
}

string CharmMetaListInt::printAtIndex(int index)
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

string CharmMetaListInt::printStrKeyIndex(int index)
{
	map<string, int, i_cmp_str>::iterator it;
	if(((int) strList.size()) > 0) {
		//cout << "iterate over length: " << strList.size() << endl;
		for(it = strList.begin(); it != strList.end(); ++it) {
			//cout << "Compare: " << it->second << " == " << index << endl;
			if(it->second == index) {
				return ": " + it->first;
			}
		}
	}
	return "";
}

ostream& operator<<(ostream& s, const CharmMetaListInt& cList)
{
	CharmMetaListInt cList2 = cList;
	for(int i = 0; i < cList2.length(); i++) {
		s << "list " << i << " " << cList2.printStrKeyIndex(i) << "\n";
		s << cList2.printAtIndex(i) << endl;
	}

	return s;
}

CharmMetaListInt& CharmMetaListInt::operator=(const CharmMetaListInt& cList)
{
	if(this == &cList)
		return *this;

	// delete current list contents first
	list.clear();
	if(strList.size() > 0) strList.clear();

	cur_index = cList.cur_index;
	strList = cList.strList;
	list = cList.list;
	return *this;
}
