
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
	strList = cList.strList;
	list = cList.list;
}

void CharmListZR::insert(int index, ZR zr)
{
	list[index] = zr;
	cur_index++;
}

void CharmListZR::insert(int index, ZR zr, string zs)
{
	list[index] = zr;
	strList.insert(pair<string, int>(zs, index));
	cur_index++;
}

void CharmListZR::insert(string index, ZR zr)
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
	list[the_index] = zr;
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

ZR& CharmListZR::operator[](const string index)
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

CharmListStr CharmListZR::strkeys()
{
	CharmListStr s;
	map<string, int, zr_cmp_str>::iterator it;
	if(((int) strList.size()) > 0) {
		//cout << "iterate over length: " << strList.size() << endl;
		for(it = strList.begin(); it != strList.end(); ++it) {
			// cout << "Compare: " << it->second << " == " << it->second << " => " << it->first << endl;
			s.insert((int) it->second, it->first);
			// index++;
		}
	}
	return s;
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

string CharmListZR::printStrKeyIndex(int index)
{
	map<string, int, zr_cmp_str>::iterator it;
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

ostream& operator<<(ostream& s, const CharmListZR& cList)
{
	CharmListZR cList2 = cList;

	for(int i = 0; i < cList2.length(); i++) {
		s << i << ": " << cList2.printAtIndex(i) << cList2.printStrKeyIndex(i) << endl;
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
	strList = cList.strList;
	list = cList.list;
	return *this;
}

CharmMetaListZR::CharmMetaListZR(void)
{
	// increases as elements are appended
	cur_index = 0;
}

CharmMetaListZR::~CharmMetaListZR()
{
	list.clear();
	strList.clear();
}

CharmMetaListZR::CharmMetaListZR(const CharmMetaListZR& cList)
{
	//copy constructor
	cur_index = cList.cur_index;
	strList = cList.strList;
	list = cList.list;
}

void CharmMetaListZR::insert(int index, CharmListZR m)
{
	list[index] = m;
	cur_index++;
}

void CharmMetaListZR::insert(string index, CharmListZR m)
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


void CharmMetaListZR::append(CharmListZR & zr)
{
	list[cur_index] = zr;
	cur_index++;
}

CharmListZR& CharmMetaListZR::operator[](const int index)
{
	if(index == cur_index) { // means we are creating reference.
		CharmListZR tmp;
		list[cur_index] = tmp;
		cur_index++;
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

CharmListZR& CharmMetaListZR::operator[](const string index)
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

int CharmMetaListZR::length()
{
	return (int) list.size();
}

string CharmMetaListZR::printAtIndex(int index)
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

string CharmMetaListZR::printStrKeyIndex(int index)
{
	map<string, int, zr_cmp_str>::iterator it;
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

ostream& operator<<(ostream& s, const CharmMetaListZR& cList)
{
	CharmMetaListZR cList2 = cList;
	for(int i = 0; i < cList2.length(); i++) {
		s << "list " << i << " " << cList2.printStrKeyIndex(i) << "\n";
		s << cList2.printAtIndex(i) << endl;
	}

	return s;
}

CharmMetaListZR& CharmMetaListZR::operator=(const CharmMetaListZR& cList)
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

