
#include "relic_api.h"
#include "CharmList.h"

void ro_error(void)
{
	cout << "Writing to read only object." << endl;
	exit(0);
}

// Begin ZR-specific classes
ZR::ZR(int x)
{
	bn_inits(z);
	bn_inits(order);
	g1_get_ord(order);
	isInit = true;
	if(x < 0) {
		bn_set_dig(z, x * -1); // set positive value
		bn_neg(z, z);			// set bn to negative
	}
	else {
		bn_set_dig(z, x);
	}
}

ZR::ZR(char *str)
{
	bn_inits(z);
	bn_inits(order);
	g1_get_ord(order);
	isInit = true;
	bn_read_str(z, (const char *) str, strlen(str), DECIMAL);
	// bn_mod(z, z, order);
}

ZR operator+(const ZR& x, const ZR& y)
{
	ZR zr = x;
	bn_add(zr.z, zr.z, y.z);
	bn_mod(zr.z, zr.z, zr.order);
	return zr;
}

ZR operator-(const ZR& x, const ZR& y)
{
	ZR zr = x;
	bn_sub(zr.z, zr.z, y.z);
	if(bn_sign(zr.z) == BN_NEG) bn_add(zr.z, zr.z, zr.order);
	else {
		bn_mod(zr.z, zr.z, zr.order);
	}
	return zr;
}

ZR operator-(const ZR& x)
{
	ZR zr = x;
	bn_neg(zr.z, zr.z);
	if(bn_sign(zr.z) == BN_NEG) bn_add(zr.z, zr.z, zr.order);
	return zr;
}


ZR operator*(const ZR& x, const ZR& y)
{
	ZR zr = x;
	bn_mul(zr.z, zr.z, y.z);
	if(bn_sign(zr.z) == BN_NEG) bn_add(zr.z, zr.z, zr.order);
	else {
		bn_mod(zr.z, zr.z, zr.order);
	}

	return zr;
}

int bn_is_one(bn_t a)
{
	if(a->used == 0) return 0; // false
	else if((a->used == 1) && (a->dp[0] == 1)) return 1; // true
	else return 0; // false
}

void invertZR(ZR & c, ZR & a, bn_t order)
{
	bn_t s;
	bn_inits(s);
	// compute c = (1 / a) mod n
	bn_gcd_ext(s, c.z, NULL, a.z, order);
	if(bn_sign(c.z) == BN_NEG) bn_add(c.z, c.z, order);
	bn_free(s);
}

ZR operator/(const ZR& x, const ZR& y)
{
	if(bn_is_zero(y.z)) {
		cout << "Divide by zero error!" << endl;
		return 0;
	}
	ZR c, b = y, a = x;
	// c = (1 / y) mod order
	invertZR(c, b, b.order);
	if(bn_is_one(a.z))  return c;
	// remainder of ((a * c) / order)
	bn_t s;
	bn_inits(s);
	// c = (a * c) / order (remainder only)
	bn_mul(s, a.z, c.z);
	bn_div_rem(s, c.z, s, a.order);
	bn_free(s);
	return c;
}

ZR power(const ZR& x, int r)
{
	ZR zr;
	bn_mxp(zr.z, x.z, ZR(r).z, zr.order);
	return zr;
}


ZR power(const ZR& x, const ZR& r)
{
	ZR zr;
	bn_mxp(zr.z, x.z, r.z, zr.order);
	return zr;
}

ZR hashToZR(string str)
{
	ZR zr;
	int digest_len = SHA_LEN;
	unsigned char digest[digest_len + 1];
	memset(digest, 0, digest_len);
	string str2 = string(HASH_FUNCTION_STR_TO_Zr_CRH) + str;
	SHA_FUNC(digest, (unsigned char *) str2.c_str(), (int) str2.size());

	bn_read_bin(zr.z, digest, digest_len);
	if(bn_cmp(zr.z, zr.order) == CMP_GT) bn_mod(zr.z, zr.z, zr.order);
	return zr;
}

bool ZR::ismember(void)
{
	bool result;
	if((bn_cmp(z, order) < CMP_EQ) && (bn_sign(z) == BN_POS))
		result = true;
	else
		result = false;
	return result;
}

ostream& operator<<(ostream& s, const ZR& zr)
{
	int length = (compute_length(ZR_t) * 4);
	char data[length + 1];
	memset(data, 0, length);
	bn_write_str(data, length, zr.z, DECIMAL);
	string s1(data, length);
	s << s1;
	memset(data, 0, length);
	return s;
}

ZR operator<<(const ZR& a, int b)
{
	// left shift
	ZR zr;
	bn_lsh(zr.z, a.z, b);
	return zr;
}

ZR operator>>(const ZR& a, int b)
{
	// right shift
	ZR zr;
	bn_rsh(zr.z, a.z, b);
	return zr;
}

ZR operator&(const ZR& a, const ZR& b)
{
	int i, d = (a.z->used > b.z->used) ? b.z->used : a.z->used;
	bn_t c;
	bn_inits(c);

	for(i = 0; i < d; i++)
		c->dp[i] = (a.z->dp[i] & b.z->dp[i]);

	c->used = d;
	ZR zr(c);
	bn_free(c);
	return zr;
}

//ZR operator|(const ZR& a, const ZR& b)
//{
//	int i, d = (a.z->used > b.z->used) ? b.z->used : a.z->used;
//	bn_t c;
//	bn_inits(c);
//
//	for(i = 0; i < d; i++)
//		c->dp[i] = a.z->dp[i] | b.z->dp[i];
//
//	c->used = d;
//	ZR zr(c);
//	bn_free(c);
//	return zr;
//}

//ZR operator^(const ZR& a, const ZR& b)
//{
//	int i, d = (a.z->used > b.z->used) ? a.z->used : b.z->used;
//	bn_t c;
//	bn_inits(c);
//
//	for(i = 0; i < d; i++)
//		c->dp[i] = a.z->dp[i] ^ b.z->dp[i];
//
//	c->used = d;
//	ZR zr(c);
//	bn_free(c);
//	return zr;
//}


// End ZR-specific classes

// Begin G1-specific classes

G1 operator+(const G1& x,const G1& y)
{
	G1 z = x;
	g1_add(z.g, z.g, y.g);
	return z;
}

G1 operator-(const G1& x,const G1& y)
{
	G1 z = x;
	g1_sub(z.g, z.g, y.g);
	return z;
}

G1 operator-(const G1& x)
{
	G1 z = x;
	g1_neg(z.g, z.g);
	return z;
}

G1 power(const G1& g, const ZR& zr)
{
	G1 g1;
	g1_mul(g1.g, g.g, zr.z);
	return g1;
}

G1 hashToG1(string str)
{
	G1 g1;
	int digest_len = SHA_LEN;
	unsigned char digest[digest_len + 1];
	memset(digest, 0, digest_len);
	string str2 = string(HASH_FUNCTION_Zr_TO_G1_ROM) + str;
	SHA_FUNC(digest, (unsigned char *) str2.c_str(), (int) str2.size());

	g1_map(g1.g, digest, digest_len);
	return g1;
}

bool G1::ismember(bn_t order)
{
	bool result;
	g1_t r;
	g1_inits(r);

	g1_mul(r, g, order);
	if(g1_is_infty(r) == 1)
		result = true;
	else
		result = false;
	g1_free(r);
	return result;
}

ostream& operator<<(ostream& s, const G1& g1)
{
	// base field
	int length = (compute_length(G1_t) * 2)+1;
	char data[length + 1];
	char data2[length + 1];
	memset(data, 0, length+1);
	memset(data2, 0, length+1);
	g1_write_str(g1.g, (uint8_t *) data, length);
	int dist_y = FP_STR;
	snprintf(data2, length, "[%s, %s]", data, &(data[dist_y]));

	string s1(data2, length);
	s << s1;
	memset(data, 0, length);
	memset(data2, 0, length);
	return s;
}

// End G1-specific classes

// Begin G2-specific classes

G2 operator+(const G2& x,const G2& y)
{
	G2 z = x;
	g2_add(z.g, z.g, y.g);
	return z;
}

G2 operator-(const G2& x,const G2& y)
{
	G2 z = x;
	g2_sub(z.g, z.g, y.g);
	return z;
}

G2 operator-(const G2& x)
{
	G2 z = x;
	g2_neg(z.g, z.g);
	return z;
}

G2 power(const G2& g, const ZR& zr)
{
	G2 g2;
	g2_mul(g2.g, g.g, zr.z);
	return g2;
}

G2 hashToG2(string str)
{
	G2 g2;
	int digest_len = SHA_LEN;
	unsigned char digest[digest_len + 1];
	memset(digest, 0, digest_len);
	string str2 = string(HASH_FUNCTION_Zr_TO_G2_ROM) + str;
	SHA_FUNC(digest, (unsigned char *) str2.c_str(), (int) str2.size());

	g2_map(g2.g, digest, digest_len);
	return g2;
}

bool G2::ismember(bn_t order)
{
	bool result;
	g2_t r;
	g2_inits(r);

	g2_mul(r, g, order);
	if(g2_is_infty(r) == 1)
		result = true;
	else
		result = false;
	g2_free(r);
	return result;
}

ostream& operator<<(ostream& s, const G2& g2)
{
	// designed for BN curves at the moment
	int length = (compute_length(G2_t) * 2)+1;
	char data[length + 1];
	char data2[length + 1];
	memset(data, 0, length+1);
	memset(data2, 0, length+1);
	g2_write_str(g2.g, (uint8_t *) data, length);

	int len2 = FP_STR;
	int dist_x1 = len2, dist_y0 = len2 * 2, dist_y1 = len2 * 3;
	snprintf(data2, length, "[%s, %s,\n%s, %s]", data, &(data[dist_x1]), &(data[dist_y0]), &(data[dist_y1]));

	string s1(data2, length);
	s << s1;
	memset(data, 0, length);
	memset(data2, 0, length);
	return s;
}

// End G2-specific classes

// Begin GT-specific classes

GT operator*(const GT& x,const GT& y)
{
	GT z = x, y1 = y;
	gt_mul(z.g, z.g, y1.g);
	return z;
}

GT operator/(const GT& x,const GT& y)
{
	GT z=x, y1 = y;
	// z = x * y^-1
	gt_t t;
	gt_inits(t);
	gt_inv(t, y1.g);
	gt_mul(z.g, z.g, t);
	gt_free(t);
	return z;
}

GT power(const GT& g, const ZR& zr)
{
	GT gt;
	if(zr.z == ZR(-1)) { // find efficient way for comparing bn_t to ints
		// compute inverse
		return -g;
	}
	else {
		gt_exp(gt.g, const_cast<GT&>(g).g, zr.z);
	}
	return gt;
}

GT operator-(const GT& g)
{
	GT gt;
	gt_inv(gt.g, const_cast<GT&>(g).g);
	return gt;
}

GT pairing(const G1& g1, const G2& g2)
{
	GT gt;
	/* compute optimal ate pairing */
	pp_map_oatep(gt.g, g1.g, g2.g);
	return gt;
}

GT pairing(const G1& g10, const G1& g11)
{
	GT gt;
	/* compute optimal ate pairing */
//	pp_map_oatep(gt.g, g1.g, g2.g);
	return gt;
}

bool GT::ismember(bn_t order)
{
	bool result;
	gt_t r;
	gt_inits(r);

	gt_exp(r, g, order);
	if(gt_is_unity(r) == 1)
		result = true;
	else
		result = false;
	gt_free(r);
	return result;
}

ostream& operator<<(ostream& s, const GT& gt)
{
	// designed for BN curves at the moment
	int length = (compute_length(GT_t) * 2)+2;
	char data[length + 1];
	char data2[length + 1];
	memset(data, 0, length+1);
	memset(data2, 0, length+1);
	gt_write_str(const_cast<GT&>(gt).g, (uint8_t *) data, length);

	int len2 = FP_STR;
	int dist_x01 = len2, dist_x10 = len2 * 2, dist_x11 = len2 * 3,
		dist_x20 = len2 * 4, dist_x21 = len2 * 5, dist_y00 = len2 * 6,
		dist_y01 = len2 * 7, dist_y10 = len2 * 8, dist_y11 = len2 * 9,
		dist_y20 = len2 * 10, dist_y21 = len2 * 11;
	 snprintf(data2, length, "[%s, %s, %s, %s, %s, %s],\n[%s, %s, %s, %s, %s, %s]",
	 			  data, &(data[dist_x01]), &(data[dist_x10]), &(data[dist_x11]),
				  &(data[dist_x20]), &(data[dist_x21]),
				  &(data[dist_y00]), &(data[dist_y01]), &(data[dist_y10]), &(data[dist_y11]),
				  &(data[dist_y20]), &(data[dist_y21]));

	string s1(data2, length);
	s << s1;
	memset(data, 0, length);
	memset(data2, 0, length);
	return s;
}


PairingGroup::PairingGroup()
{
	isInit = false; // user needs to call setCurve after construction
}

PairingGroup::PairingGroup(int sec_level)
{
	this->setCurve(sec_level);
}

void PairingGroup::setCurve(int sec_level)
{
	cout << "Initializing PairingGroup: RELIC" << endl;
	int err_code = core_init();
	if(err_code != STS_OK) isInit = false;
//	conf_print();
	pc_param_set_any(); // see if we can open this up?
	isInit = true;
	bn_inits(grp_order);
	g1_get_ord(grp_order);
}

PairingGroup::~PairingGroup()
{
	if(isInit) {
		core_clean();
		bn_free(grp_order);
	}
}

void PairingGroup::init(ZR & r, char *value)
{
	r = ZR(value);
}

ZR PairingGroup::init(ZR_type t, int value)
{
	ZR zr(value);
	return zr;
}

void PairingGroup::init(ZR & r, int value)
{
	r = ZR(value); //should copy this
	return;
}

ZR PairingGroup::init(ZR_type t)
{
	ZR zr;
	return zr;
}

G1 PairingGroup::init(G1_type t)
{
	G1 g1;
	return g1;
}

void PairingGroup::init(G1 & t, int value)
{
	G1 g1;
	if(value == 1) t = g1; // set to the identity element
	return;
}

G1 PairingGroup::init(G1_type t, int value)
{
	G1 g1; // = new G1();
	return g1;
}

//#ifdef ASYMMETRIC
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
//#endif

GT PairingGroup::init(GT_type t)
{
	GT g;
	return g;
}

GT PairingGroup::init(GT_type t, int value)
{
	GT g;
	return g;
}

void PairingGroup::init(GT & t, int value)
{
	GT g;
	t = g;
	return;
}

ZR PairingGroup::random(ZR_type t)
{
	ZR zr;
	bn_rand(zr.z, BN_POS, bn_bits(grp_order));
	bn_mod(zr.z,  zr.z, grp_order);
	return zr;
}

G1 PairingGroup::random(G1_type t)
{
	G1  g1;
	g1_rand(g1.g);
	return g1;
}

G2 PairingGroup::random(G2_type t)
{
	G2  g2;
	g2_rand(g2.g);
	return g2;
}

GT PairingGroup::random(GT_type t)
{
	GT gts;
	gt_rand(gts.g);
    return gts;
}

ZR PairingGroup::neg(ZR r)
{
    ZR zr = r;
	bn_neg(zr.z, zr.z);
  	if(bn_sign(zr.z) == BN_NEG) bn_add(zr.z, zr.z, zr.order);
    return zr;
}

ZR PairingGroup::inv(ZR r)
{
     ZR zr = r;
     invertZR(zr, zr, r.order);
     return zr;
}

GT PairingGroup::inv(GT g)
{
	GT gt;
	return -gt;
}

//bool PairingGroup::ismember(CharmMetaListZR & g)
//{
//	return true;
//}
//
//bool PairingGroup::ismember(CharmMetaListG1 & g)
//{
//	return true;
//}
//
//bool PairingGroup::ismember(CharmMetaListG2 & g)
//{
//	return true;
//}
//
//bool PairingGroup::ismember(CharmMetaListGT & g)
//{
//	return true;
//}

bool PairingGroup::ismember(CharmList & g)
{
	return true;
}

//bool PairingGroup::ismember(CharmListZR & g)
//{
//	return true;
//}
//
//bool PairingGroup::ismember(CharmListG1 & g)
//{
//	return true;
//}
//
//bool PairingGroup::ismember(CharmListGT & g)
//{
//	return true;
//}
//
bool PairingGroup::ismember(ZR & zr)
{
	return zr.ismember();
}

bool PairingGroup::ismember(G1 & g)
{
	return g.ismember(grp_order);
}

bool PairingGroup::ismember(G2 & g)
{
	return g.ismember(grp_order); // add code to check
}

//bool PairingGroup::ismember(CharmListG2 & g)
//{
//	return true;
//}

G2 PairingGroup::mul(G2 g, G2 h)
{
	return g + h;
}

G2 PairingGroup::div(G2 g, G2 h)
{
	return g + -h;
}

G2 PairingGroup::exp(G2 g, ZR r)
{
	// g ^ r == g * r OR scalar multiplication
	return power(g, r);
}

G2 PairingGroup::exp(G2 g, int r)
{
	// g ^ r == g * r OR scalar multiplication
	return power(g, ZR(r));
}

GT PairingGroup::pair(G1 g, G2 h)
{
	return pairing(g, h);
}

GT PairingGroup::pair(G1 g, G1 h)
{
	return pairing(g, h);
}

bool PairingGroup::ismember(GT & g)
{
	return g.ismember(grp_order); // add code to check
}

ZR PairingGroup::order()
{
	return ZR(grp_order);
}

int PairingGroup::add(int g, int h)
{
	return g + h;
}

ZR PairingGroup::add(ZR g, ZR h)
{
	return g + h;
}

int PairingGroup::sub(int g, int h)
{
	return g - h;
}

ZR PairingGroup::sub(ZR g, ZR h)
{
	return g - h;
}

int PairingGroup::mul(int g, int h)
{
	return g * h;
}


ZR PairingGroup::mul(ZR g, ZR h)
{
	return g * h;
}

// mul for G1 & GT
G1 PairingGroup::mul(G1 g, G1 h)
{
	return g + h;
}

GT PairingGroup::mul(GT g, GT h)
{
	return g * h;
}

ZR PairingGroup::div(int g, ZR h)
{
	return ZR(g) / h;
}

ZR PairingGroup::div(ZR g, ZR h)
{
	return g / h;
}

// div for G1 & GT
G1 PairingGroup::div(G1 g, G1 h)
{
	return g + -h;
}

GT PairingGroup::div(GT g, GT h)
{
	return g / h;
}

int PairingGroup::div(int g, int h)
{
	return g / h;
}

ZR PairingGroup::exp(ZR x, int y)
{
	return power(x, y);
}

ZR PairingGroup::exp(ZR x, ZR y)
{
	return power(x, y);
}

//// exp for G1 & GT
G1 PairingGroup::exp(G1 g, ZR r)
{
	// g ^ r == g * r OR scalar multiplication
 	return power(g, r);
}

G1 PairingGroup::exp(G1 g, int r)
{
	// g ^ r == g * r OR scalar multiplication
 	return power(g, ZR(r));
}

GT PairingGroup::exp(GT g, ZR r)
{
	// g ^ r == g * r OR scalar multiplication
	return power(g, r);
}

GT PairingGroup::exp(GT g, int r)
{
	// g ^ r == g * r OR scalar multiplication
	return power(g, ZR(r));
}

ZR PairingGroup::hashListToZR(string str)
{
	ZR r = hashToZR(str);
	return r;
}

G1 PairingGroup::hashListToG1(string str)
{
	G1 l = hashToG1(str);
	return l;
}

G2 PairingGroup::hashListToG2(string str)
{
	G2 l = hashToG2(str);
	return l;
}

string getBytesOverList(CharmList s)
{
	int i, type, data_len, len = s.length();
	string str = "";
	for(i = 0; i < len; i++) {
		type = s[i].type;
		if(type == Str_t) {
			str = str + s[i].strPtr;
		}
		else if(type == ZR_t) {
			data_len = compute_length(type);
			uint8_t data[data_len + 1];
			memset(data, 0, data_len);
			bn_write_bin(data, data_len, s[i].zr.z);
			string tmp((char *) data, data_len);
			str = str + tmp;
		}
		else if(type == G1_t) {
			data_len = compute_length(type);
			uint8_t data[data_len + 1];
			memset(data, 0, data_len);
			g1_write_bin(s[i].g1.g, data, data_len); // x & y
			string tmp((char *) data, data_len);
			str = str + tmp;
		}
		else if(type == G2_t) {
			data_len = compute_length(type);
			uint8_t data[data_len + 1];
			memset(data, 0, data_len);
			g2_write_bin(s[i].g2.g, data, data_len); // x1, y1  & x2, y2
			string tmp((char *) data, data_len);
			str = str + tmp;
		}
		else if(type == GT_t) {
			data_len = compute_length(type);
			uint8_t data[data_len + 1];
			memset(data, 0, data_len);
			gt_write_bin(s[i].gt.g, data, data_len); // x1-6 && y1-6
			string tmp((char *) data, data_len);
			str = str + tmp;
		}
	}
	return str;
}

ZR PairingGroup::hashListToZR(CharmList s)
{
	string s2 = getBytesOverList(s);
	ZR r = hashToZR(s2);
	return r;
}

G1 PairingGroup::hashListToG1(CharmList s)
{
	string s2 = getBytesOverList(s);
	return hashToG1(s2);
}

G2 PairingGroup::hashListToG2(CharmList s)
{
	string s2 = getBytesOverList(s);
	return hashToG2(s2);
}
