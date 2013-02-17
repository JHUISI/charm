#include "CharmListG1.h"

CharmListG1::CharmListG1(void)
{
	// increases as elements are appended
	cur_index = 0;
}

CharmListG1::~CharmListG1()
{
	list.clear();
	strList.clear();
}

CharmListG1::CharmListG1(const CharmListG1& cList)
{
	//copy constructor
	cur_index = cList.cur_index;
	strList = cList.strList;
	list = cList.list;
}

void CharmListG1::insert(int index, G1 g)
{
	list[index] = g;
	cur_index++;
}

void CharmListG1::insert(string index, G1 g)
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

CharmListInt CharmListG1::keys()
{
	CharmListInt j;
	int count = 0;
	G1 tmp;
	for(int i = 0; i < (int) list.size(); i++)
	{
		if(list[i] != tmp) {
			j[count] = i;
			count++;
		}
	}

	return j;
}

CharmListStr CharmListG1::strkeys()
{
	CharmListStr s;
	map<string, int, g_cmp_str>::iterator it;
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

G1& CharmListG1::operator[](const int index)
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

G1& CharmListG1::operator[](const string index)
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
	list.clear();
	if(strList.size() > 0) {
		strList.clear();
	}
	// copy over
	cur_index = cList.cur_index;
	strList = cList.strList;
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

string CharmListG1::printStrKeyIndex(int index)
{
	map<string, int, g_cmp_str>::iterator it;
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


ostream& operator<<(ostream& s, const CharmListG1& cList)
{
	CharmListG1 cList2 = cList;
	for(int i = 0; i < cList2.length(); i++) {
		s << i << ": " << cList2.printAtIndex(i) << cList2.printStrKeyIndex(i) << endl;
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
	list.clear();
	strList.clear();
}

CharmMetaListG1::CharmMetaListG1(const CharmMetaListG1& cList)
{
	//copy constructor
	cur_index = cList.cur_index;
	strList = cList.strList;
	list = cList.list;
}

void CharmMetaListG1::insert(int index, CharmListG1 m)
{
	list[index] = m;
	cur_index++;
}

void CharmMetaListG1::insert(string index, CharmListG1 m)
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


void CharmMetaListG1::append(CharmListG1 & zr)
{
	list[cur_index] = zr;
	cur_index++;
}

CharmListG1& CharmMetaListG1::operator[](const int index)
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

CharmListG1& CharmMetaListG1::operator[](const string index)
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

string CharmMetaListG1::printStrKeyIndex(int index)
{
	map<string, int, g_cmp_str>::iterator it;
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

ostream& operator<<(ostream& s, const CharmMetaListG1& cList)
{
	CharmMetaListG1 cList2 = cList;
	for(int i = 0; i < cList2.length(); i++) {
		s << "list " << i << " " << cList2.printStrKeyIndex(i) << "\n";
		s << cList2.printAtIndex(i) << endl;
	}

	return s;
}

CharmMetaListG1& CharmMetaListG1::operator=(const CharmMetaListG1& cList)
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
