
#include "CharmListG2.h"

#if ASYMMETRIC == 1
CharmListG2::CharmListG2(void)
{
	// increases as elements are appended
	cur_index = 0;
}

CharmListG2::~CharmListG2()
{
	list.clear();
	strList.clear();
}

CharmListG2::CharmListG2(const CharmListG2& cList)
{
	//copy constructor
	cur_index = cList.cur_index;
	strList = cList.strList;
	list = cList.list;
}

void CharmListG2::insert(int index, G2 g)
{
	list[index] = g;
	cur_index++;
}

void CharmListG2::insert(string index, G2 g)
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
	list[the_index] = g;
	cur_index++;
}

void CharmListG2::append(G2 & g)
{
	list[cur_index] = g;
	cur_index++;
}

CharmListStr CharmListG2::strkeys()
{
	CharmListStr s;
	map<string, int, g2_cmp_str>::iterator it;
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

G2& CharmListG2::operator[](const int index)
{
	if(index == cur_index) { // means we are creating reference.
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

G2& CharmListG2::operator[](const string index)
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

CharmListG2& CharmListG2::operator=(const CharmListG2& cList)
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

int CharmListG2::length()
{
	return (int) list.size();
}

string CharmListG2::printAtIndex(int index)
{
	stringstream ss;
	int i;

	if(index >= 0 && index < (int) list.size()) {
		i = index;
		ss << list[i].g;
	}

	string s = ss.str();
	return s;
}

string CharmListG2::printStrKeyIndex(int index)
{
	map<string, int, g2_cmp_str>::iterator it;
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

ostream& operator<<(ostream& s, const CharmListG2& cList)
{
	CharmListG2 cList2 = cList;
	for(int i = 0; i < cList2.length(); i++) {
		s << i << ": " << cList2.printAtIndex(i) << cList2.printStrKeyIndex(i) << endl;
	}

	return s;
}


CharmMetaListG2::CharmMetaListG2(void)
{
	// increases as elements are appended
	cur_index = 0;
}

CharmMetaListG2::~CharmMetaListG2()
{
	for(int i = 0; i < (int) list.size(); i++)
		list.erase(i);
}

CharmMetaListG2::CharmMetaListG2(const CharmMetaListG2& cList)
{
	//copy constructor
	cur_index = cList.cur_index;
	list = cList.list;
}

void CharmMetaListG2::append(CharmListG2 & g2)
{
	list[cur_index] = g2;
	cur_index++;
}

CharmListG2& CharmMetaListG2::operator[](const int index)
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

int CharmMetaListG2::length()
{
	return (int) list.size();
}

string CharmMetaListG2::printAtIndex(int index)
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

ostream& operator<<(ostream& s, const CharmMetaListG2& cList)
{
	CharmMetaListG2 cList2 = cList;
	for(int i = 0; i < cList2.length(); i++) {
		s << "list " << i << "\n";
		s << cList2.printAtIndex(i) << endl;
	}

	return s;
}

CharmMetaListG2& CharmMetaListG2::operator=(const CharmMetaListG2& cList)
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
#endif
