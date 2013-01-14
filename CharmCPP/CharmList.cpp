
#include "CharmList.h"

CharmList::CharmList(void)
{
	// increases as elements are appended
	cur_index = 0;
}

CharmList::~CharmList()
{
	for(int i = 0; i < (int) list.size(); i++)
		list.erase(i);
}

CharmList::CharmList(const CharmList& cList)
{
	//copy constructor
	cur_index = cList.cur_index;
	list = cList.list;
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
	int len = (int) list.size();
	if(index >= 0 && index < len) {
		return list[index];
	}
	else {
		throw new string("Invalid access.\n");
	}
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
