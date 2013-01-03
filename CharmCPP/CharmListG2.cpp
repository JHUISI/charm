
#include "CharmListG2.h"

#if ASYMMETRIC == 1
CharmListG2::CharmListG2(void)
{
	// increases as elements are appended
	cur_index = 0;
}

CharmListG2::~CharmListG2()
{
	for(int i = 0; i < (int) list.size(); i++)
		list.erase(i);
}

CharmListG2::CharmListG2(const CharmListG2& cList)
{
	//copy constructor
	cur_index = cList.cur_index;
	list = cList.list;
}

void CharmListG2::insert(int index, G2 g)
{
	list[index] = g;
	cur_index++;
}

void CharmListG2::append(G2 & g)
{
	list[cur_index] = g;
	cur_index++;
}

G2& CharmListG2::operator[](const int index)
{
	if(index == cur_index) { // means we are creating reference.
//		G2 tmp;
//		list[cur_index] = tmp; // this type will disappear and just for creating reference only. caller expected to set result
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

ostream& operator<<(ostream& s, const CharmListG2& cList)
{
	CharmListG2 cList2 = cList;
	for(int i = 0; i < cList2.length(); i++) {
		s << i << ": " << cList2.printAtIndex(i) << endl;
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
