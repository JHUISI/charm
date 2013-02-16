
#include "CharmList.h"
#include "MiraclAPI.h"
#include "CryptoLib.h"

CharmListZR stringToInt(PairingGroup & group, string strID, int z, int l)
{
    /* 1. hash string. */
    CharmListZR zrlist; // = new CharmListZR;
    ZR intval;
    Big mask( pow(Big(2), l) - 1 );
    ZR id = group.hashListToZR(strID);

    /* 2. cut up result into zz pieces of ll size */
    for(int i = 0; i < z; i++) {
        intval = land(id, mask);
        zrlist.append(intval);
        id = id >> l; // shift to the right by ll bits
    }
    return zrlist;
}

ZR ceillog(int base, int value)
{
   // logb(x) ==> log(x) / log(b)
   big x = mirvar((int) ceil(log10(value) / log10(base)));
   ZR zr(x);
   mr_free(x);
   return zr;
}


ZR SmallExp(int bits) {
	big t = mirvar(0);
	bigbits(bits, t);
    ZR zr(t);
    mr_free(t);
	return zr;
}

PairingGroup::PairingGroup()
{
	pfcObject = NULL;
}

PairingGroup::PairingGroup(int sec_level)
{
	this->setCurve(sec_level);
}

void PairingGroup::setCurve(int sec_level)
{
	cout << "Initializing PairingGroup: MIRACL" << endl;
	pfcObject = new PFC(sec_level);
	miracl *mip=get_mip();  // get handle on mip (Miracl Instance Pointer)
	mip->IOBASE = 10;

	time_t seed;
	time(&seed);
    irand((long)seed);

    G1 g1;
    pfcObject->random(g1);
#if ASYMMETRIC == 1
    G2 g2;
    pfcObject->random(g2);

    gt = new GT(pfcObject->pairing(g2, g1));
#else
    gt = new GT(pfcObject->pairing(g1, g1));
#endif

	gt_id = new GT(pfcObject->power(*gt, ZR(0)));
}

PairingGroup::~PairingGroup()
{
	delete pfcObject;
	delete gt;
	delete gt_id;
}

void PairingGroup::init(ZR & r, char *value)
{
	big x = mirvar(0);
	cinstr(x, value);
	r = ZR(x); //should copy this
	mr_free(x);
}

ZR PairingGroup::init(ZR_type t, int value)
{
	big x = mirvar(value);
	ZR zr(x); // = new ZR(x);
    mr_free(x);
	return zr;
}

void PairingGroup::init(ZR & r, int value)
{
	big x = mirvar(value);
	r = ZR(x); //should copy this
	mr_free(x);
	return;
}

ZR PairingGroup::init(ZR_type t)
{
	ZR zr; // = new ZR();
	return zr;
}

G1 PairingGroup::init(G1_type t)
{
	G1 g1;// = new G1();
	return g1;
}

void PairingGroup::init(G1 & t, int value)
{
	G1 g1;
	t = g1; // set to the identity element
	return;
}

G1 PairingGroup::init(G1_type t, int value)
{
	G1 g1; // = new G1();
	return g1;
}

#if ASYMMETRIC == 1
G2 PairingGroup::init(G2_type t)
{
	G2 g2; // = new G2();
	return g2;
}

G2 PairingGroup::init(G2_type t, int value)
{
	G2 g2; // = new G2();
	return g2;
}

void PairingGroup::init(G2 & t, int value)
{
	G2 g2;
	t = g2;
	return;
}
#endif

GT PairingGroup::init(GT_type t)
{
	GT g(*gt_id); // = new GT(*gt_id);
	return g;
}

GT PairingGroup::init(GT_type t, int value)
{
	GT g(*gt_id); // = new GT(*gt_id);
	return g;
}

void PairingGroup::init(GT & t, int value)
{
	GT g(*gt_id);
	t = g;
	return;
}

ZR PairingGroup::random(ZR_type t)
{
	ZR zr; // = new ZR();
	pfcObject->random(zr);
	return zr;
}

G1 PairingGroup::random(G1_type t)
{
	G1  g1; // = new G1();
	pfcObject->random(g1);
	return g1;
}

GT PairingGroup::random(GT_type t)
{
	// choose random ZR
	ZR zr;
	GT gts; // = new GT();
	pfcObject->random(zr);

	gts = pfcObject->power(*gt, zr);
    return gts;
}

ZR PairingGroup::neg(ZR r)
{
     ZR zr = r;
     zr.negate();
     return zr;
}

ZR PairingGroup::inv(ZR r)
{
     ZR zr = inverse(r, pfcObject->order());
     return zr;
}

G1 PairingGroup::inv(G1 g)
{
	return -g;
}

bool PairingGroup::ismember(CharmMetaListZR & g)
{
	return true;
}

bool PairingGroup::ismember(CharmMetaListG1 & g)
{
	return true;
}

bool PairingGroup::ismember(CharmMetaListGT & g)
{
	return true;
}

bool PairingGroup::ismember(CharmList & g)
{
	return true;
}

bool PairingGroup::ismember(CharmListZR & g)
{
	return true;
}

bool PairingGroup::ismember(CharmListG1 & g)
{
	return true;
}

bool PairingGroup::ismember(CharmListGT & g)
{
	return true;
}

bool PairingGroup::ismember(ZR & g)
{
	return true;
}

bool PairingGroup::ismember(G1 & g)
{
	return true;
}

#if ASYMMETRIC == 1

G2 PairingGroup::random(G2_type t)
{
	G2 g2; // = new G2();
	pfcObject->random(g2);
	return g2;
}

bool PairingGroup::ismember(G2 & g)
{
	return true; // add code to check
}

bool PairingGroup::ismember(CharmListG2 & g)
{
	return true;
}

bool PairingGroup::ismember(CharmMetaListG2 & g)
{
	return true;
}

G2 PairingGroup::mul(G2 g, G2 h)
{
	G2 l(g + h);
	return l;
}

G2 PairingGroup::div(G2 g, G2 h)
{
	G2 l(g + -h);
	return l;
}

G2 PairingGroup::exp(G2 g, ZR r)
{
	// g ^ r == g * r OR scalar multiplication
	G2 l = pfcObject->mult(g, r);
	return l;
}

G2 PairingGroup::exp(G2 g, int r)
{
	// g ^ r == g * r OR scalar multiplication
	G2 l = pfcObject->mult(g, ZR(r));
	return l;
}

G2 PairingGroup::inv(G2 g)
{
	return -g;
}

GT PairingGroup::pair(G1 g, G2 h)
{
	GT gt = pfcObject->pairing(h, g);
	return gt;
}

#else
GT PairingGroup::pair(G1 g, G1 h)
{
	GT gt = pfcObject->pairing(g, h);
	return gt;
}
#endif

bool PairingGroup::ismember(GT & g)
{
	return true; // add code to check
}

ZR PairingGroup::order()
{
	return ZR(pfcObject->order());
}

int PairingGroup::add(int g, int h)
{
	return g + h;
}

ZR PairingGroup::add(ZR g, ZR h)
{
	ZR o = pfcObject->order();

	return (g + h) % o;
}

int PairingGroup::sub(int g, int h)
{
	return g - h;
}

ZR PairingGroup::sub(ZR g, ZR h)
{
	ZR o = pfcObject->order();
	ZR r = (g - h) % o;
	if(r < 0) {
		return (r + o) % o;
	}
	return r;
}


int PairingGroup::mul(int g, int h)
{
	return g * h;
}


ZR PairingGroup::mul(ZR g, ZR h)
{
	ZR o = pfcObject->order();
	ZR r = modmult(g, h, o);

	if(r < 0) {
		return (r + o) % o;
	}
	return r;
}

// mul for G1 & GT
G1 PairingGroup::mul(G1 g, G1 h)
{
	G1 l(g + h);
	return l;
}

GT PairingGroup::mul(GT g, GT h)
{
//	GT l(g * h);
	return g * h;
}

ZR PairingGroup::div(int g, ZR h)
{
	ZR o = pfcObject->order();
	return moddiv(ZR(g), h, o);
}


ZR PairingGroup::div(ZR g, ZR h)
{
	ZR o = pfcObject->order();
	return moddiv(g, h, o);
}

// div for G1 & GT
G1 PairingGroup::div(G1 g, G1 h)
{
	G1 l(g + -h);
	return l;
}

GT PairingGroup::div(GT g, GT h)
{
	GT l(g / h);
	return l;
}

int PairingGroup::div(int g, int h)
{
	return g / h;
}

ZR PairingGroup::exp(ZR x, int y)
{
	ZR z = pfcObject->order();
	if(y == -1) {
	     return inverse(x, z);
	}
	else if(y >= 0) {
		return pow(x, y, z);
	}
	else {
		throw new string("Raising to a negative that isn't -1 is not allowed.\n");
	}
}

ZR PairingGroup::exp(ZR x, ZR y)
{
	ZR z = pfcObject->order();
	ZR result = pow(x, y, z);
	//cout << "exp result: " << result << endl;
	return result;
}

// exp for G1 & GT
G1 PairingGroup::exp(G1 g, ZR r)
{
	// g ^ r == g * r OR scalar multiplication
	G1 l = pfcObject->mult(g, r);
 	return l;
}

G1 PairingGroup::exp(G1 g, int r)
{
	// g ^ r == g * r OR scalar multiplication
	G1 l = pfcObject->mult(g, ZR(r));
 	return l;
}

GT PairingGroup::exp(GT g, ZR r)
{
	// g ^ r == g * r OR scalar multiplication
	GT l = pfcObject->power(g, r);
	return l;
}

GT PairingGroup::exp(GT g, int r)
{
	// g ^ r == g * r OR scalar multiplication
	GT l = pfcObject->power(g, ZR(r));
	return l;
}

ZR PairingGroup::hashListToZR(string str)
{
	ZR r = pfcObject->hash_to_group((char *) str.c_str());
	return r;
}

G1 PairingGroup::hashListToG1(string str)
{
	G1 l;
	pfcObject->hash_and_map(l, (char *) str.c_str());
	return l;
}

#if ASYMMETRIC == 1
G2 PairingGroup::hashListToG2(string str)
{
	G2 l;
	pfcObject->hash_and_map(l, (char *) str.c_str());
	return l;
}
#endif

// serialize helper methods for going from Big to bytes and back
string bigToBytes(Big x)
{
	int len = MAX_LEN;
	char c[len+1];
	memset(c, 0, len);
	int size = to_binary(x, len, c, FALSE);
	string bytes(c, size);
//	printf("bigToBytes before => ");
//	_printf_buffer_as_hex((uint8_t *) bytes.c_str(), size);
	stringstream ss;
	ss << size << ":" << bytes << "\0";
//	printf("bigToBytes after => ");
//	_printf_buffer_as_hex((uint8_t *) ss.str().c_str(), ss.str().size());
	return ss.str();
}

Big bytesToBig(string str, int *counter)
{
	int pos = str.find_first_of(':');
	int max = MAX_LEN;
//	cout << "pos of elem => " << pos << endl;
	int len = atoi( str.substr(0, pos).c_str() );
	int add_zeroes = PAD_SIZE;
	const char *elem = str.substr(pos+1, pos + len).c_str();
	char elem2[max + 1];
	memset(elem2, 0, max);
	// right justify elem2 before call to 'from_binary'
	if(len < BIG_SIZE) {
		// need to prepend additional zero's
		add_zeroes += (BIG_SIZE - len);
	}

	for(int i = add_zeroes; i < BIG_SIZE + add_zeroes; i++)
		elem2[i] = elem[i-add_zeroes];

//	printf("bytesToBig before => ");
//	_printf_buffer_as_hex((uint8_t *) elem, len);
//	cout << "len => " << len << endl;
//	printf("bytesToBig before2 => ");
//	_printf_buffer_as_hex((uint8_t *) elem2, MAX_LEN);
	Big x = from_binary(max, (char *) elem2);
	*counter  = pos + len + 1;
	return x;
}


string bigToRawBytes(Big x)
{
	char c[MAX_LEN+1];
	memset(c, 0, MAX_LEN);
	int size = to_binary(x, MAX_LEN, c, FALSE);
	string bytes(c, size);
	stringstream ss;
	ss << bytes << "\0";
	return ss.str();
}

// TODO: fix compile error here
//string PairingGroup::aes_key(GT & g)
//{
//	Big tmp = pfcObject->hash_to_aes_key(g);
//	string tmp_str = bigToRawBytes(tmp);
//	int output_len = strlen(tmp_str.c_str());
//	return string(convert_buffer_to_hex((uint8_t *) tmp_str.c_str(), output_len));
//}

ZR PairingGroup::hashListToZR(CharmList list)
{
	int len = list.length();
	pfcObject->start_hash();
	for(int i = 0; i < len; i++) {
		Element e = list[i];
		if(e.type == Str_t) {
			ZR tmp = pfcObject->hash_to_group( (char *) e.strPtr.c_str());
			pfcObject->add_to_hash(tmp);
		}
		else if(e.type == ZR_t)
			pfcObject->add_to_hash(e.zr);
		else if(e.type == G1_t)
			pfcObject->add_to_hash(e.g1);
#if ASYMMETRIC == 1
		else if(e.type == G2_t)
			pfcObject->add_to_hash(e.g2);
#endif
		else if(e.type == GT_t)
			pfcObject->add_to_hash(e.gt);
	}

	//ZR *result = new ZR(pfcObject->finish_hash_to_group());
	return pfcObject->finish_hash_to_group();
}

G1 PairingGroup::hashListToG1(CharmList list)
{
	int len = list.length();
	pfcObject->start_hash();
	for(int i = 0; i < len; i++) {
		Element e = list[i];
		if(e.type == Str_t) {
			ZR tmp = pfcObject->hash_to_group( (char *) e.strPtr.c_str());
			pfcObject->add_to_hash(tmp);
		}
		else if(e.type == ZR_t)
			pfcObject->add_to_hash(e.zr);
		else if(e.type == G1_t)
			pfcObject->add_to_hash(e.g1);
#if ASYMMETRIC == 1
		else if(e.type == G2_t)
			pfcObject->add_to_hash(e.g2);
#endif
		else if(e.type == GT_t)
			pfcObject->add_to_hash(e.gt);
	}

	ZR tmp1 = pfcObject->finish_hash_to_group();
	G1 g1;
	// convert result to bytes and hash to G1
	pfcObject->hash_and_map(g1, (char *) bigToBytes(tmp1).c_str());
	return g1;
}

#if ASYMMETRIC == 1
G2 PairingGroup::hashListToG2(CharmList list)
{
	int len = list.length();
	pfcObject->start_hash();
	for(int i = 0; i < len; i++) {
		Element e = list[i];
		if(e.type == Str_t) {
			ZR tmp = pfcObject->hash_to_group( (char *) e.strPtr.c_str());
			pfcObject->add_to_hash(tmp);
		}
		else if(e.type == ZR_t)
			pfcObject->add_to_hash(e.zr);
		else if(e.type == G1_t)
			pfcObject->add_to_hash(e.g1);
		else if(e.type == G2_t)
			pfcObject->add_to_hash(e.g2);
		else if(e.type == GT_t)
			pfcObject->add_to_hash(e.gt);
	}

	ZR tmp1 = pfcObject->finish_hash_to_group();
	G2 g2;
	// convert result to bytes and hash to G2
	pfcObject->hash_and_map(g2, (char *) bigToBytes(tmp1).c_str());
	return g2;
}
#endif

string Element_ToBytes(Element &e)
{
	int type = e.type;
	char c[MAX_LEN+1];
	memset(c, 0, MAX_LEN);
	string t;

	if(type == ZR_t) {
		Big s = e.zr;
		t.append(bigToBytes(s));
		string encoded = _base64_encode(reinterpret_cast<const unsigned char*>(t.c_str()), t.size());
		return encoded;
	}
	else if(type == G1_t) {
		G1 p = e.g1;
		Big x, y;
		p.g.get(x, y);
		t.append(bigToBytes(x));
		t.append(bigToBytes(y));
		string encoded = _base64_encode(reinterpret_cast<const unsigned char*>(t.c_str()), t.size());
		return encoded;
	}
#if ASYMMETRIC == 1
	else if(type == G2_t) {
		G2 P = e.g2; // embeds an ECn3 element (for MNT curves)

#if BUILD_MNT_CURVE == 1
		ZZn3 x, y;

		ZZn *a = new ZZn[6];
		P.g.get(x, y); // get ZZn3's
		x.get(a[0], a[1], a[2]); // get coordinates for each ZZn
		y.get(a[3], a[4], a[5]);

		for(int i = 0; i < 6; i++) {
			t.append( bigToBytes(Big(a[i])) );
		}

		delete [] a;
#elif BUILD_BN_CURVE == 1
		ZZn2 x1, y1; // each zzn2 has a (x, y) coordinate of type Big
		P.g.get(x1, y1);

		Big *a = new Big[4];
		x1.get(a[0], a[1]);
		y1.get(a[2], a[3]);

		for(int i = 0; i < 4; i++) {
			string tmp = bigToBytes(a[i]);
			t.append( tmp );
		}
		delete [] a;
#endif
		// base64 encode t and return
		string encoded = _base64_encode(reinterpret_cast<const unsigned char*>(t.c_str()), t.size());
		return encoded;
	}
#endif
	else if(type == GT_t) {
#if BUILD_MNT_CURVE == 1
		GT P = e.gt; // embeds an ZZn6 element (for MNT curves) is equivalent to
		// control this w/ a flag
		ZZn2 x, y, z; // each zzn2 has a (x,y) coordinates of type Big
		Big *a = new Big[6];
		P.g.get(x, y, z); // get ZZn2's

		x.get(a[0], a[1]); // get coordinates for each ZZn2
		y.get(a[2], a[3]);
		z.get(a[4], a[5]);
//	    cout << "Point => (" << x << ", " << y << ", " << z << ")" << endl;
		for(int i = 0; i < 6; i++) {
			t.append( bigToBytes(a[i]) );
		}
		delete [] a;
#elif BUILD_BN_CURVE == 1
		GT P = e.gt;
		ZZn4 x, y, z;
		ZZn2 x0, x1, y0, y1, z0, z1;
		P.g.get(x, y, z);

		Big *a = new Big[12];
		x.get(x0, x1);
		y.get(y0, y1);
		z.get(z0, z1);

		x0.get(a[0], a[1]);
		x1.get(a[2], a[3]);
		y0.get(a[4], a[5]);
		y1.get(a[6], a[7]);
		z0.get(a[8], a[9]);
		z1.get(a[10], a[11]);

		for(int i = 0; i < 12; i++) {
			t.append( bigToBytes(a[i]) );
		}

		delete [] a;
#elif BUILD_SS_CURVE == 1
		GT P = e.gt;
		Big *a = new Big[2];
		P.g.get(a[0], a[1]);

		for(int i = 0; i < 2; i++) {
			t.append( bigToBytes(a[i]) );
		}

		delete [] a;
#endif
		string encoded = _base64_encode(reinterpret_cast<const unsigned char*>(t.c_str()), t.size());
		return encoded;
	}

	return 0;
}

int Element_FromBytes(Element &e, int type, unsigned char *data)
{
	if(type == ZR_t) {
		if(is_base64((unsigned char) data[0])) {
			string b64_encoded((char *) data);
			string s = _base64_decode(b64_encoded);
			int cnt = 0;
			Big b = Big(bytesToBig(s, &cnt));
			e = Element(b);
//			cout << "Element_FromBytes: " << e << endl;
			return TRUE;
		}
	}
	else if(type == G1_t) {
		if(is_base64((unsigned char) data[0])) {
			string b64_encoded((char *) data);
			string s = _base64_decode(b64_encoded);

			int cnt = 0;
			Big x, y;
			x = bytesToBig(s, &cnt);
			s = s.substr(cnt);
			y = bytesToBig(s, &cnt);
	//		cout << "point => (" << x << ", " << y << ")" << endl;
			G1 p;
			p.g.set(x, y);
			e = Element(p);
			//cout << "Element_FromBytes: " << e << endl;
			return TRUE;
		}
	}
#if ASYMMETRIC == 1
	else if(type == G2_t) {
		if(is_base64((unsigned char) data[0])) {
			string b64_encoded((char *) data);
			string s = _base64_decode(b64_encoded);
	//		cout << "original => " << s << endl;
			int cnt = 0;
			G2 p;
#if BUILD_MNT_CURVE == 1
			ZZn a[MNT_G2_SIZE];
			for(int i = 0; i < MNT_G2_SIZE; i++) {
				Big b = bytesToBig(s, &cnt);
				a[i] = ZZn( b ); // retrieve all six coordinates
				s = s.substr(cnt);
			}
			ZZn3 x (a[0], a[1], a[2]);
			ZZn3 y (a[3], a[4], a[5]);

			p.g.set(x, y);
#elif BUILD_BN_CURVE == 1
			Big a[BN_G2_SIZE];
			for(int i = 0; i < BN_G2_SIZE; i++) {
				a[i] = bytesToBig(s, &cnt);
				s = s.substr(cnt); // advance s ptr
			}

			ZZn2 x1(a[0], a[1]); // each zzn2 has a (x, y) coordinate of type Big
			ZZn2 y1(a[2], a[3]);
			p.g.set(x1, y1);
#endif
			e = Element(p);
			//cout << "Element_FromBytes: " << e << endl;
			return TRUE;
		}
	}
#endif
	else if(type == GT_t) {
		if(is_base64((unsigned char) data[0])) {
			string b64_encoded((char *) data);
			string s = _base64_decode(b64_encoded);
	//		cout << "original => " << s << endl;
			int cnt = 0;
			GT p;
#if BUILD_MNT_CURVE == 1
			Big a[MNT_GT_SIZE];
			for(int i = 0; i < MNT_GT_SIZE; i++) {
				a[i] = bytesToBig(s, &cnt);
				s = s.substr(cnt); // advance s ptr
			}

			ZZn2 x, y, z;
			x.set(a[0], a[1]);
			y.set(a[2], a[3]);
			z.set(a[4], a[5]);
			p.g.set(x, y, z);
#elif BUILD_BN_CURVE == 1
			Big a[BN_GT_SIZE];
			for(int i = 0; i < BN_GT_SIZE; i++) {
				a[i] = bytesToBig(s, &cnt);
				s = s.substr(cnt); // advance s ptr
			}
			ZZn2 x0, x1, y0, y1, z0, z1;
			x0.set(a[0], a[1]);
			x1.set(a[2], a[3]);
			y0.set(a[4], a[5]);
			y1.set(a[6], a[7]);
			z0.set(a[8], a[9]);
			z1.set(a[10], a[11]);

			ZZn4 x(x0, x1);
			ZZn4 y(y0, y1);
			ZZn4 z(z0, z1);
			p.g.set(x, y, z);
#elif BUILD_SS_CURVE == 1
			// must be symmetric
			Big a[SS_GT_SIZE];
			for(int i = 0; i < SS_GT_SIZE; i++) {
				a[i] = bytesToBig(s, &cnt);
				s = s.substr(cnt); // advance s ptr
			}
			p.g.set(a[0], a[1]);
#endif
			e = Element(p);
			//cout << "Element_FromBytes: " << e << endl;
			return TRUE;
		}
	}
	return 0;
}
