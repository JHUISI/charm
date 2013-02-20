
#include "CharmListStr.h"

/* test inequality for two strings */
bool isEqual(string value1, string value2)
{
    string s1 = value1;
    string s2 = value2;
    if (strcmp(s1.c_str(), s2.c_str()) == 0)
    	return true;
    else
    	return false;
}

/* test inequality for two strings */
bool isNotEqual(string value1, string value2)
{
    string s1 = value1;
    string s2 = value2;
    if (strcmp(s1.c_str(), s2.c_str()) != 0)
	return true;
    else
	return false;
}

string concat(CharmListStr & list)
{
    int l = 0;
    string L = "";
    l = list.length();
    for (int y = 0; y < l; y++)
    {
        L = (L + list[y]);
    }
    return L;
}

string GetString(string & str)
{
	return str;
}


CharmListStr::CharmListStr(void)
{
	// increases as elements are appended
	cur_index = 0;
}

CharmListStr::~CharmListStr()
{
	for(int i = 0; i < (int) list.size(); i++)
		list.erase(i);
}

CharmListStr::CharmListStr(const CharmListStr& cList)
{
	//copy constructor
	cur_index = cList.cur_index;
	list = cList.list;
}

//void CharmListStr::append(char *s)
//{
//	string s2(s);
//	list[cur_index] = s2;
//	cur_index++;
//}

void CharmListStr::append(string & s)
{
	list[cur_index] = s;
	cur_index++;
}

void CharmListStr::append(string s)
{
	list[cur_index] = s;
	cur_index++;
}

void CharmListStr::insert(int index, string s)
{
	list[index] = s;
	cur_index++;
}

void CharmListStr::insert(int index, string & s)
{
	list[index] = s;
	cur_index++;
}

int CharmListStr::searchKey(string index)
{
	for(int i = 0; i < (int) list.size(); i++) {
		if(isEqual(index, list[i])) { return i; }
	}
	return -1;
}

string& CharmListStr::operator[](const int index)
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

CharmListStr& CharmListStr::operator=(const CharmListStr& cList)
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

int CharmListStr::length()
{
	return (int) list.size();
}

string CharmListStr::printAtIndex(int index)
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

ostream& operator<<(ostream& s, const CharmListStr& cList)
{
	CharmListStr cList2 = cList;
	for(int i = 0; i < cList2.length(); i++) {
		s << i << ": " << cList2.printAtIndex(i) << endl;
	}

	return s;
}
