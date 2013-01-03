#include "Builtin.h"

CharmListZR stringToInt(PairingGroup & group, string strID, int z, int l)
{
    /* 1. hash string. */
    CharmListZR zrlist; // = new CharmListZR;
    ZR intval;
    ZR mask( power(ZR(2), l) - 1 );

    ZR id = group.hashListToZR(strID); 

    /* 2. cut up result into zz pieces of ll size */
    for(int i = 0; i < z; i++) {
        intval = (id & mask);
        zrlist.append(intval);
        id = id >> l; // shift to the right by ll bits ... // add to API
    }

    return zrlist;
}

string Element_ToBytes(Element &e)
{
	int data_len;
	string encoded= "";
	if(e.type == Str_t) {
		return string(e.strPtr);
	}
	else if(e.type == ZR_t) {
		data_len = compute_length(e.type);
		uint8_t data[data_len+1];
		memset(data, 0, data_len);
		bn_write_bin(data, data_len, e.zr.z);
		string t((char *) data, data_len);
		encoded = _base64_encode(reinterpret_cast<const unsigned char*>(t.c_str()), t.size());
		memset(data, 0, data_len);
	}
	else if(e.type == G1_t) {
		data_len = compute_length(e.type);
		uint8_t data[data_len+1];
		memset(data, 0, data_len);
		g1_write_bin(e.g1.g, data, data_len);
		string t((char *) data, data_len);
		encoded = _base64_encode(reinterpret_cast<const unsigned char*>(t.c_str()), t.size());
		memset(data, 0, data_len);
	}
	else if(e.type == G2_t) {
		data_len = compute_length(e.type);
		uint8_t data[data_len+1];
		memset(data, 0, data_len);
		g2_write_bin(e.g2.g, data, data_len);
		string t((char *) data, data_len);
		encoded = _base64_encode(reinterpret_cast<const unsigned char*>(t.c_str()), t.size());
		memset(data, 0, data_len);
	}
	else if(e.type == GT_t) {
		data_len = compute_length(e.type);
		uint8_t data[data_len+1];
		memset(data, 0, data_len);
		gt_write_bin(e.gt.g, data, data_len); // x1-6 && y1-6
		string t((char *) data, data_len);
		encoded = _base64_encode(reinterpret_cast<const unsigned char*>(t.c_str()), t.size());
		memset(data, 0, data_len);
	}
	return encoded;
}

int Element_FromBytes(Element & e, int type, unsigned char *data)
{
	string d = "";
	if(is_base64((unsigned char) data[0])) {
		string b64_encoded((char *) data);
		d = _base64_decode(b64_encoded);
	}
	else {
		return ELEMENT_INVALID_ARG;
	}

	if(type == ZR_t) {
		bn_read_bin(e.zr.z, (unsigned char *) d.c_str(), d.size());
	}
	else if(type == G1_t) {
		return g1_read_bin(e.g1.g, (unsigned char *) d.c_str(), d.size()); // x & y
	}
	else if(type == G2_t) {
		return g2_read_bin(e.g2.g, (unsigned char *) d.c_str(), d.size()); // x1, y1  & x2, y2
	}
	else if(type == GT_t) {
		return gt_read_bin(e.gt.g, (unsigned char *) d.c_str(), d.size()); // x1-6 && y1-6
	}

	return ELEMENT_INVALID_ARG;
}

