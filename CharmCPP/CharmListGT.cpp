
#include "CharmListGT.h"

CharmListGT::CharmListGT(void)
{
	// increases as elements are appended
	cur_index = 0;
}

CharmListGT::~CharmListGT()
{
	for(int i = 0; i < (int) list.size(); i++)
		list.erase(i);
}

CharmListGT::CharmListGT(const CharmListGT& cList)
{
	//copy constructor
	cur_index = cList.cur_index;
	list = cList.list;
}

void CharmListGT::append(GT & g)
{
	list[cur_index] = g;
	cur_index++;
}

GT& CharmListGT::operator[](const int index)
{
	if(index == cur_index) { // means we are creating reference.
		//GT tmp;
		//list[cur_index] = tmp; // this type will disappear and just for creating reference only. caller expected to set result
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

CharmListGT& CharmListGT::operator=(const CharmListGT& cList)
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

ostream& operator<<(ostream& s, const CharmListGT& cList)
{
	CharmListGT cList2 = cList;
	for(int i = 0; i < cList2.length(); i++) {
		s << i << ": " << cList2.printAtIndex(i) << endl;
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

