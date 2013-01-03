#include "CharmListG1.h"

CharmListG1::CharmListG1(void)
{
	// increases as elements are appended
	cur_index = 0;
}

CharmListG1::~CharmListG1()
{
	for(int i = 0; i < (int) list.size(); i++)
		list.erase(i);
}

CharmListG1::CharmListG1(const CharmListG1& cList)
{
	//copy constructor
	cur_index = cList.cur_index;
	list = cList.list;
}

void CharmListG1::insert(int index, G1 g)
{
	list[index] = g;
	cur_index++;
}

void CharmListG1::append(G1 & g)
{
	list[cur_index] = g;
	cur_index++;
}

void CharmListG1::set(int index, G1 g1)
{
	G1 *g = new G1(g1);
	list[index] = *g;
}

//G1& CharmListG1::get(const int index)
//{
//	int len = (int) list.size();
//	if(index >= 0 && index < len) {
//		return list[index];
//	}
//	else {
//		throw new string("Invalid access.\n");
//	}
//}

G1& CharmListG1::operator[](const int index)
{
	if(index == cur_index) { // means we are creating reference.
//		G1 tmp;
//		list[cur_index] = tmp;
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

//CharmListG1& CharmListG1::operator=(const CharmListG1 & newList)
//{
//    list = newList.list;
//    return *this;
//}

CharmListG1& CharmListG1::operator=(const CharmListG1& cList)
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


int CharmListG1::length()
{
	return (int) list.size();
}

string CharmListG1::printAtIndex(int index)
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

ostream& operator<<(ostream& s, const CharmListG1& cList)
{
	CharmListG1 cList2 = cList;
	for(int i = 0; i < cList2.length(); i++) {
		s << i << ": " << cList2.printAtIndex(i) << endl;
	}

	return s;
}


CharmMetaListG1::CharmMetaListG1(void)
{
	// increases as elements are appended
	cur_index = 0;
}

CharmMetaListG1::~CharmMetaListG1()
{
	for(int i = 0; i < (int) list.size(); i++)
		list.erase(i);
}

CharmMetaListG1::CharmMetaListG1(const CharmMetaListG1& cList)
{
	//copy constructor
	cur_index = cList.cur_index;
	list = cList.list;
}

void CharmMetaListG1::append(CharmListG1 & zr)
{
	list[cur_index] = zr;
	cur_index++;
}

CharmListG1& CharmMetaListG1::operator[](const int index)
{
	if(index == cur_index) { // means we are creating reference.
		CharmListG1 tmp;
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

int CharmMetaListG1::length()
{
	return (int) list.size();
}

string CharmMetaListG1::printAtIndex(int index)
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

ostream& operator<<(ostream& s, const CharmMetaListG1& cList)
{
	CharmMetaListG1 cList2 = cList;
	for(int i = 0; i < cList2.length(); i++) {
		s << "list " << i << "\n";
		s << cList2.printAtIndex(i) << endl;
	}

	return s;
}

CharmMetaListG1& CharmMetaListG1::operator=(const CharmMetaListG1& cList)
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
