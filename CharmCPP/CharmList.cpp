
#include "CharmList.h"

CharmList::CharmList(void)
{
	// increases as elements are appended
	cur_index = 0;
}

CharmList::~CharmList()
{
	list.clear();
	strList.clear();
}

CharmList::CharmList(const CharmList& cList)
{
	//copy constructor
	cur_index = cList.cur_index;
	strList = cList.strList;
	list = cList.list;
}

void CharmList::insert(int index, int value)
{
	Element elem(value);
	list[index] = elem;
	cur_index++;
}

void CharmList::insert(int index, const char *s)
{
	Element elem(s);
	list[index] = elem;
	cur_index++;
}

void CharmList::append(const char *s)
{
	Element elem(s);
	list[cur_index] = elem;
	cur_index++;
}

void CharmList::insert(int index, string strs)
{
	Element elem(strs);
	list[index] = elem;
	cur_index++;
}


void CharmList::append(string strs)
{
	Element elem(strs);
	list[cur_index] = elem;
	cur_index++;
}

void CharmList::insert(int index, CharmListStr & lStr)
{
	Element elem(lStr);
	list[index] = elem;
	cur_index++;
}

void CharmList::insert(int index, CharmListInt & lInt)
{
	Element elem(lInt);
	list[index] = elem;
	cur_index++;
}


void CharmList::insert(int index, ZR & zr)
{
	Element elem(zr);
	list[index] = elem;
	cur_index++;
}

void CharmList::append(ZR & zr)
{
	Element elem(zr);
	list[cur_index] = elem;
	cur_index++;
}

void CharmList::insert(int index, const ZR & zr)
{
	ZR zr_1 = zr;
	Element elem(zr_1);
	list[index] = elem;
	cur_index++;
}

void CharmList::append(const ZR & zr)
{
	ZR zr_1 = zr;
	Element elem(zr_1);
	list[cur_index] = elem;
	cur_index++;
}

void CharmList::insert(int index, G1 & g1)
{
	Element elem(g1);
	list[index] = elem;
	cur_index++;
}

void CharmList::append(G1 & g1)
{
	Element elem(g1);
	list[cur_index] = elem;
	cur_index++;
}

void CharmList::insert(int index, const G1 & g1)
{
	G1 g1_1 = g1;
	Element elem(g1_1);
	list[index] = elem;
	cur_index++;
}

void CharmList::append(const G1 & g1)
{
	G1 g1_1 = g1;
	Element elem(g1_1);
	list[cur_index] = elem;
	cur_index++;
}


#if ASYMMETRIC == 1
void CharmList::insert(int index, G2 & g2)
{
	Element elem(g2);
	list[index] = elem;
	cur_index++;
}

void CharmList::append(G2 & g2)
{
	Element elem(g2);
	list[cur_index] = elem;
	cur_index++;
}

void CharmList::insert(int index, const G2 & g2)
{
	G2 g2_1 = g2;
	Element elem(g2_1);
	list[index] = elem;
	cur_index++;
}

void CharmList::append(const G2 & g2)
{
	G2 g2_1 = g2;
	Element elem(g2_1);
	list[cur_index] = elem;
	cur_index++;
}

#endif

void CharmList::insert(int index, GT & gt)
{
	Element elem(gt);
	list[index] = elem;
	cur_index++;
}

void CharmList::append(GT & gt)
{
	Element elem(gt);
	list[cur_index] = elem;
	cur_index++;
}

void CharmList::insert(int index, const GT & gt)
{
	GT gt_1 = gt;
	Element elem(gt_1);
	list[index] = elem;
	cur_index++;
}

void CharmList::append(const GT & gt)
{
	GT gt_1 = gt;
	Element elem(gt_1);
	list[cur_index] = elem;
	cur_index++;
}


void CharmList::insert(int index, Element & e)
{
	list[index] = e;
	cur_index++;
}

void CharmList::append(Element & e)
{
	list[cur_index] = e;
	cur_index++;
}

void CharmList::insert(int index, const Element & e)
{
	Element e1 = e;
	list[index] = e1;
	cur_index++;
}

void CharmList::append(const Element & e)
{
	Element e1 = e;
	list[cur_index] = e1;
	cur_index++;
}


void CharmList::append(const CharmList & c)
{
	CharmList c2 = c;
	for(int i = 0; i < (int) c2.length(); i++) {
		list[cur_index] = c2[i];
		cur_index++;
	}
}

void CharmList::insert(int index, CharmList c)
{
	CharmList c2 = c;
	Element elem(c2);
	list[index] = elem;
	cur_index++;
}

void CharmList::insert(string index, CharmList c)
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
	CharmList c2 = c;
	Element elem(c2);
	list[the_index] = elem;
	cur_index++;
}


void CharmList::insert(int index, CharmListZR c)
{
	CharmListZR c2 = c;
	Element elem(c2);
	list[index] = elem;
	cur_index++;
}

void CharmList::insert(int index, CharmListG1 c)
{
	CharmListG1 c2 = c;
	Element elem(c2);
	list[index] = elem;
	cur_index++;
}

#if ASYMMETRIC == 1
void CharmList::insert(int index, CharmListG2 c)
{
	CharmListG2 c2 = c;
	Element elem(c2);
	list[index] = elem;
	cur_index++;
}
#endif

void CharmList::insert(int index, CharmListGT c)
{
	CharmListGT c2 = c;
	Element elem(c2);
	list[index] = elem;
	cur_index++;
}

Element& CharmList::operator[](const int index)
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

Element& CharmList::operator[](const string index)
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

CharmList& CharmList::operator=(const CharmList& cList)
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

int CharmList::length()
{
	return (int) list.size();
}

CharmList CharmList::operator+(const Element& e) const
{
	CharmList result;
	Element e2 = e;
	result.append(*this);
	result.append(e2);
	return result;
}

CharmList CharmList::operator+(const CharmList& r) const
{
	CharmList result;
	result.append(*this);
	result.append(r);

	return result;
}

ostream& operator<<(ostream& s, const CharmList& cList)
{
	CharmList cList2 = cList;
	for(int i = 0; i < cList2.length(); i++) {
		s << "[" << i << "]:" << cList2.printAtIndex(i) << endl;
	}

	return s;
}

string CharmList::printAtIndex(int index)
{
	stringstream ss;
	int i;

	if(index >= 0 && index < (int) list.size()) {
		i = index;
		int t = list[i].type;
		if(t == Str_t) {
			ss << list[i].strPtr;
		}
		else if(t == listStr_t) {
			ss << "Str list\n" << list[i].sList;
		}
		else if(t == listInt_t) {
			ss << "Int list\n" << list[i].iList;
		}
		else if(t == ZR_t) {
			ss << list[i].zr;
		}
		else if(t == listZR_t) {
			ss << "ZR list\n" << list[i].zrList;
		}
		else if(t == G1_t) {
			ss << convert_str(list[i].g1);
		}
		else if(t == listG1_t) {
			ss << "G1 list\n" << list[i].g1List;
		}
#if ASYMMETRIC == 1
		else if(t == G2_t) {
			ss << convert_str(list[i].g2);
		}
		else if(t == listG2_t) {
			ss << "G2 list\n" << list[i].g2List;
		}
#endif
		else if(t == GT_t) {
			ss << convert_str(list[i].gt);
		}
		else if(t == listGT_t) {
			ss << "GT list\n" << list[i].gtList;
		}
		else if(t == list_t) {
			ss << "\nBegin CharmList\n" << list[i].aList << "End CharmList" << endl;
		}
	}

	string s = ss.str();
	return s;
}

string CharmList::printStrKeyIndex(int index)
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

CharmMetaList::CharmMetaList(void)
{
	// increases as elements are appended
	cur_index = 0;
}

CharmMetaList::~CharmMetaList()
{
	list.clear();
	strList.clear();
}

CharmMetaList::CharmMetaList(const CharmMetaList& cList)
{
	//copy constructor
	cur_index = cList.cur_index;
	strList = cList.strList;
	list = cList.list;
}

void CharmMetaList::insert(int index, CharmList zr)
{
	list[index] = zr;
	cur_index++;
}

void CharmMetaList::insert(string index, CharmList zr)
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


void CharmMetaList::append(CharmList & zr)
{
	list[cur_index] = zr;
	cur_index++;
}

CharmList& CharmMetaList::operator[](const int index)
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

CharmList& CharmMetaList::operator[](const string index)
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

int CharmMetaList::length()
{
	return (int) list.size();
}

string CharmMetaList::printAtIndex(int index)
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

string CharmMetaList::printStrKeyIndex(int index)
{
	map<string, int, e_cmp_str>::iterator it;
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


ostream& operator<<(ostream& s, const CharmMetaList& cList)
{
	CharmMetaList cList2 = cList;
	for(int i = 0; i < cList2.length(); i++) {
		s << "list " << i << " " << cList2.printStrKeyIndex(i) << "\n";
		s << cList2.printAtIndex(i) << endl;
	}

	return s;
}

CharmMetaList& CharmMetaList::operator=(const CharmMetaList& cList)
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


int measureSize(CharmList & c)
{
	int len = c.length();
	int byteCount = 0;
	for(int i = 0; i < len; i++) {
		if(c[i].type == ZR_t || c[i].type == G1_t || c[i].type == GT_t) {
			string tmp = serialize(c[i]);
			byteCount += tmp.size();
		}
#if ASYMMETRIC == 1
		else if(c[i].type == G2_t) {
			string tmp = serialize(c[i]);
			byteCount += tmp.size();
		}
#endif
		else if(c[i].type == Str_t) {
			byteCount += c[i].strPtr.size();
		}
		else if(c[i].type == int_t) {
			continue;
		}
		else {
			byteCount += measureSize(c[i]);
		}
	}

	return byteCount;
}

int measureSize(Element & e)
{
	if(e.type == list_t)
		return measureSize(e.aList);
	else if(e.type == listZR_t)
		return measureSize(e.zrList);
	else if(e.type == listG1_t)
		return measureSize(e.g1List);
#if ASYMMETRIC == 1
	else if(e.type == listG2_t)
		return measureSize(e.g2List);
#endif
	else if(e.type == listGT_t)
		return measureSize(e.gtList);
	else if(e.type == listStr_t)
		return measureSize(e.sList);
	else if(e.type == listInt_t)
		return 0; // not focusing on integers
//	else
//		cout << "Invalid type: " << e.type << endl;
	return 0;
}

int measureSize(CharmListZR & c)
{
	int len = c.length();
	int byteCount = 0;
	for(int i = 0; i < len; i++) {
		Element e(c[i]);
		string tmp = serialize(e);
		byteCount += tmp.size();
	}
	return byteCount;
}

int measureSize(CharmListG1 & c)
{
	int len = c.length();
	int byteCount = 0;
	for(int i = 0; i < len; i++) {
		Element e(c[i]);
		string tmp = serialize(e);
		byteCount += tmp.size();
	}
	return byteCount;
}

#if ASYMMETRIC == 1
int measureSize(CharmListG2 & c)
{
	int len = c.length();
	int byteCount = 0;
	for(int i = 0; i < len; i++) {
		Element e(c[i]);
		string tmp = serialize(e);
		byteCount += tmp.size();
	}
	return byteCount;
}
#endif

int measureSize(CharmListGT & c)
{
	int len = c.length();
	int byteCount = 0;
	for(int i = 0; i < len; i++) {
		Element e(c[i]);
		string tmp = serialize(e);
		byteCount += tmp.size();
	}
	return byteCount;
}

int measureSize(CharmListStr & c)
{
	int len = c.length();
	int byteCount = 0;
	for(int i = 0; i < len; i++) {
		byteCount += c[i].size();
	}
	return byteCount;
}
