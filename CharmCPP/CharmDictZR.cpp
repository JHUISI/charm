
#include "CharmDictZR.h"

// start CharmDictZR implementation

CharmDictZR::CharmDictZR(void)
{
	// increases as elements are appended
}

CharmDictZR::~CharmDictZR()
{
	emap.clear();
}

CharmDictZR::CharmDictZR(const CharmDictZR& cDict)
{
	//copy constructor
	emap = cDict.emap;
}

int CharmDictZR::length()
{
	return (int) emap.size();
}

CharmListStr CharmDictZR::keys()
{
	CharmListStr s;
	map<string, ZR>::iterator iter;
	for(iter = emap.begin(); iter != emap.end(); iter++) {
		// s.push_back(iter->first);
		const char *ptr = iter->first.c_str();
		s.append( ptr );
	}

	return s;
}

string CharmDictZR::printAll()
{
	stringstream ss;
	map<string, ZR, cmp_str>::iterator iter;
	for(iter = emap.begin(); iter != emap.end(); iter++) {
		ss << "key = " << iter->first << ", value = " << iter->second << endl;
	}

	string s = ss.str();
	return s;
}

void CharmDictZR::set(string key, ZR& value)
{
	emap.insert(pair<string, ZR>(key, value));
}

ZR& CharmDictZR::operator[](const string key)
{
//	map<string, ZR, cmp_str>::iterator iter;
//	for(iter = emap.begin(); iter != emap.end(); iter++) {
//		if (strcmp(key.c_str(), iter->first.c_str()) == 0) {
//			return iter->second;
//		}
//	}

	// means it's a new index so set it here
	ZR tmpValue = 0;
	pair<map<string, ZR>::iterator, bool> retValue;
	retValue = emap.insert(pair<string, ZR>(key, tmpValue));
/* retValue.second is true if new element was inserted
 *	  or false if an equivalent key already existed.
 * Either case: we want to return the first->second element which is
 * a pointer to the ZR field.
 */
	return retValue.first->second;

}

ostream& operator<<(ostream& s, const CharmDictZR& e)
{
	CharmDictZR e2 = e;
	s << e2.printAll();
	return s;
}

CharmDictZR& CharmDictZR::operator=(const CharmDictZR& cDict)
{
	if(this == &cDict)
		return *this;

	// delete current list contents first
	emap.clear();
	emap = cDict.emap;
	return *this;
}
