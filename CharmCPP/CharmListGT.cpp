
#include "CharmListGT.h"

CharmListGT::CharmListGT(void)
{
	// increases as elements are appended
	cur_index = 0;
}

CharmListGT::~CharmListGT()
{
	list.clear();
	strList.clear();
}

CharmListGT::CharmListGT(const CharmListGT& cList)
{
	//copy constructor
	cur_index = cList.cur_index;
	strList = cList.strList;
	list = cList.list;
}

void CharmListGT::insert(int index, GT g)
{
	list[index] = g;
	cur_index++;
}

void CharmListGT::insert(string index, GT g)
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

void CharmListGT::append(GT & g)
{
	list[cur_index] = g;
	cur_index++;
}

GT& CharmListGT::operator[](const int index)
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

GT& CharmListGT::operator[](const string index)
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

CharmListGT& CharmListGT::operator=(const CharmListGT& cList)
{
	if(this == &cList)
		return *this;

	// delete current list contents first
	list.clear();
	if(strList.size() > 0) {
		strList.clear();
	}

	cur_index = cList.cur_index;
	strList = cList.strList;
	list = cList.list;
	return *this;
}

int CharmListGT::length()
{
	return (int) list.size();
}

string CharmListGT::printAtIndex(int index)
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

string CharmListGT::printStrKeyIndex(int index)
{
	map<string, int, gt_cmp_str>::iterator it;
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

ostream& operator<<(ostream& s, const CharmListGT& cList)
{
	CharmListGT cList2 = cList;
	for(int i = 0; i < cList2.length(); i++) {
		s << i << ": " << cList2.printAtIndex(i) << cList2.printStrKeyIndex(i) << endl;
	}

	return s;
}


CharmMetaListGT::CharmMetaListGT(void)
{
	// increases as elements are appended
	cur_index = 0;
}

CharmMetaListGT::~CharmMetaListGT()
{
	for(int i = 0; i < (int) list.size(); i++)
		list.erase(i);
}

CharmMetaListGT::CharmMetaListGT(const CharmMetaListGT& cList)
{
	//copy constructor
	cur_index = cList.cur_index;
	list = cList.list;
}

void CharmMetaListGT::append(CharmListGT & gt)
{
	list[cur_index] = gt;
	cur_index++;
}

CharmListGT& CharmMetaListGT::operator[](const int index)
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

int CharmMetaListGT::length()
{
	return (int) list.size();
}

string CharmMetaListGT::printAtIndex(int index)
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

ostream& operator<<(ostream& s, const CharmMetaListGT& cList)
{
	CharmMetaListGT cList2 = cList;
	for(int i = 0; i < cList2.length(); i++) {
		s << "list " << i << "\n";
		s << cList2.printAtIndex(i) << endl;
	}

	return s;
}

CharmMetaListGT& CharmMetaListGT::operator=(const CharmMetaListGT& cList)
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

