/*
 * Charm-Crypto is a framework for rapidly prototyping cryptosystems.
 *
 * Charm-Crypto is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * Charm-Crypto is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with Charm-Crypto. If not, see <http://www.gnu.org/licenses/>.
 *
 * Please contact the charm-crypto dev team at support@charm-crypto.com
 * for any questions.
 */

/*
*   @file    miracl_interface.cc
*
*   @brief   charm interface over MIRACL's pairing-based crypto C++ classes
*
*   @author  ayo.akinyele@charm-crypto.com
*
************************************************************************/

#include "miracl_interface.h"
#define MR_PAIRING_MNT
#define AES_SECURITY 80
#include "pairing_3.h"
#include "miracl.h"
#include <sstream>

extern "C" {

string _base64_encode(unsigned char const* bytes_to_encode, unsigned int in_len);
string _base64_decode(string const& encoded_string);
static inline bool is_base64(unsigned char c);

void _printf_buffer_as_hex(uint8_t * data, size_t len)
{
//#ifdef DEBUG
	size_t i;

	for (i = 0; i < len; i++) {
		printf("%02x ", data[i]);
	}
	printf("\n");
//#endif
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


string bigToBytes(Big x)
{
	char c[MAX_LEN+1];
	memset(c, 0, MAX_LEN);
	int size = to_binary(x, MAX_LEN, c, FALSE);
	string bytes(c, size);
//	printf("bigToBytes before => ");
//	_printf_buffer_as_hex((uint8_t *) bytes.c_str(), size);
	stringstream ss;
	ss << size << ":" << bytes << "\0";
//	printf("bigToBytes after => ");
//	_printf_buffer_as_hex((uint8_t *) ss.str().c_str(), ss.str().size());
	return ss.str();
}

Big *bytesToBig(string str, int *counter)
{
	int pos = str.find_first_of(':');
	int len = atoi( str.substr(0, pos).c_str() );
	const char *elem = str.substr(pos+1, pos + len).c_str();
//		cout << "pos of elem => " << pos << endl;
//		cout << "elem => " << elem << endl;
//	printf("bytesToBig before => ");
//	_printf_buffer_as_hex((uint8_t *) elem, len);
	Big x = from_binary(len, (char *) elem);
//	cout << "Big => " << x << endl;
	Big *X  = new Big(x);
	*counter  = pos + len + 1;
	return X;
}

pairing_t *pairing_init(int securitylevel) {

	PFC *pfc = new PFC(securitylevel);
	miracl *mip=get_mip();  // get handle on mip (Miracl Instance Pointer)
	mip->IOBASE = 10;

	//cout << "Initialized: " << pfc << endl;
    //cout << "Order = " << pfc->order() << endl;
    time_t seed;

    time(&seed);
    irand((long)seed); // weak RNG for now

	// TODO: need to initialize RNG here as well (Testing w/o for now)
    return (pairing_t *) pfc;
}

element_t *order(pairing_t *pairing) {
	PFC *pfc = (PFC *) pairing;
	Big *x = new Big(pfc->order());
	return (element_t *) x;
}


element_t *element_init_ZR(int value = 0)
{
	Big *b = new Big(value);
	return (element_t *) b;
}

element_t *_element_init_G1()
{
	G1 *g = new G1(); // infinity by default
	return (element_t *) g;
}

element_t *_element_init_G2()
{
	G2 *g = new G2();
	return (element_t *) g;
}

element_t *_element_init_GT(const pairing_t *pairing)
{
	PFC *pfc = (PFC *) pairing;
	GT *g = new GT();
	*g = pfc->power(*g, Big(0)); // gt ^ 0 = identity element?
	return (element_t *) g;
}

int element_is_member(Curve_t ctype, Group_t type, const pairing_t *pairing, element_t *e)
{
	PFC *pfc = (PFC *) pairing;
	// test whether e is in type
	if(type == ZR_t) {
		Big *x = (Big *) e;
		if(*x > 0 && *x < pfc->order()) return TRUE;
		return FALSE;
	}
	else if(type == G1_t) {
		G1 *point = (G1 *) e;
		if(ctype == MNT) {
			if ((*(pfc->cof) * point->g).iszero() == TRUE) { return FALSE; }
			else { return TRUE; }
		}
		else {
			// (order * point->g).iszero
		}
	}
	else if(type == G2_t) {
		G2 *point = (G2 *) e;
		if(ctype == MNT) {
			if ((*(pfc->cof) * point->g).iszero() == TRUE) { return FALSE; }
			else { return TRUE; }
		}
	}
	else if(type == GT_t) {
		GT *point = (GT *) e;
//		BOOL result = pfc->member(*point);
		if(ctype == MNT) {
			if ((pow(point->g, pfc->order())).iszero() == TRUE) { return FALSE; }
			else { return TRUE; }
		}
	}
	return -1;
}


void element_random(Group_t type, const pairing_t *pairing, element_t *e) {
	PFC *pfc = (PFC *) pairing;

	if(type == ZR_t) {
		Big *x = (Big *) e;
		pfc->random(*x);
		// cout << "1st: generated a random value x = " << *x << endl;
	}
	else if(type == G1_t) {
		G1 *g = (G1 *) e;
		pfc->random(*g);
	}
	else if(type == G2_t) {
		G2 *g = (G2 *) e;
		pfc->random(*g);
	}
	else if(type == GT_t) {
		cout << "Error: can't generate random GT elements directly!" << endl;
	}
	else {
		cout << "Error: unrecognized type." << endl;
	}
}

void element_printf(Group_t type, const element_t *e)
{
	if(type == ZR_t) {
		Big *y = (Big *) e;
		cout << *y;
	}
	else if(type == G1_t) {
		G1 *point = (G1 *) e;
		cout << point->g;
	}
	else if(type == G2_t) {
		G2 *point = (G2 *) e;
		cout << point->g;
	}
	else if(type == GT_t) {
		GT *point = (GT *) e;
		cout << point->g;
	}
	else {
		cout << "Unrecognized type" << endl;
	}
}

// assume data_str is a NULL ptr
int _element_length_to_str(Group_t type, const element_t *e)
{
	stringstream ss;
	string s;
	if(type == ZR_t) {
		Big *y = (Big *) e;
		ss << *y;
// 		cout << "ZR origin => " << *y << endl;
	}
	else if(type == G1_t) {
		G1 *point = (G1 *) e;
		ss << point->g;
//		cout << "G1 origin => " << point->g << endl;
	}
	else if(type == G2_t) {
		G2 *point = (G2 *) e;
		ss << point->g;
//		cout << "G2 origin => " << point->g << endl;
	}
	else if(type == GT_t) {
		GT *point = (GT *) e;
		ss << point->g;
//		cout << "GT origin => " << point->g << endl;
	}
	else {
		cout << "Unrecognized type" << endl;
		return FALSE;
	}
	s = ss.str();
	return s.size();
}

int _element_to_str(unsigned char **data_str, Group_t type, const element_t *e)
{
	stringstream ss;
	string s;
	if(type == ZR_t) {
		Big *y = (Big *) e;
		ss << *y;
	}
	else if(type == G1_t) {
		G1 *point = (G1 *) e;
		ss << point->g;
	}
	else if(type == G2_t) {
		G2 *point = (G2 *) e;
		ss << point->g;
//		cout << "G2 origin => " << point->g << endl;
	}
	else if(type == GT_t) {
		GT *point = (GT *) e;
		ss << point->g;
//		cout << "GT origin => " << point->g << endl;
	}
	else {
		cout << "Unrecognized type" << endl;
		return FALSE;
	}
	s = ss.str();
	memcpy(*data_str, s.c_str(), s.size());
	return TRUE;
}

void _element_add(Group_t type, element_t *c, const element_t *a, const element_t *b, const element_t *o)
{
	if(type == ZR_t) {
		Big *x = (Big *) a;
		Big *y = (Big *) b;
		Big *z = (Big *) c;
		Big *o1 = (Big *) o;
		*z = ((*x + *y) % *o1);
//		cout << "Result => " << *z << endl;
	}
	else if(type == G1_t) {
		G1 *x = (G1 *) a;  G1 *y = (G1 *) b; G1 *z = (G1 *) c;
		*z = *x + *y;
	}
	else if(type == G2_t) {
		G2 *x = (G2 *) a;  G2 *y = (G2 *) b; G2 *z = (G2 *) c;
		*z = *x + *y;
	}
	else {
		/* Error */
	}

}

void _element_sub(Group_t type, element_t *c, const element_t *a, const element_t *b, const element_t *o)
{
	if(type == ZR_t) {
		Big *x = (Big *) a;
		Big *y = (Big *) b;
		Big *z = (Big *) c;
		Big *o1 = (Big *) o;
		*z = ((*x - *y) % *o1);
	}
	else if(type == G1_t) {
		G1 *x = (G1 *) a;  G1 *y = (G1 *) b; G1 *z = (G1 *) c;
		*z = *x + (-*y);
	}
	else if(type == G2_t) {
		G2 *x = (G2 *) a;  G2 *y = (G2 *) b; G2 *z = (G2 *) c;
		*z = *x + (-*y);
	}

}

void _element_mul(Group_t type, element_t *c, const element_t *a, const element_t *b, const element_t *o)
{
	if(type == ZR_t) {
		Big *x = (Big *) a;
		Big *y = (Big *) b;
		Big *z = (Big *) c;
//		*z = *x * *y;
		Big *o1 = (Big *) o;
		*z = modmult(*x, *y, *o1);
//		cout << "Result => " << *z << endl;
	}
	else if(type == G1_t) {
		G1 *x = (G1 *) a;  G1 *y = (G1 *) b; G1 *z = (G1 *) c;
		 *z = *x + *y;
	}
	else if(type == G2_t) {
		G2 *x = (G2 *) a;  G2 *y = (G2 *) b; G2 *z = (G2 *) c;
		*z = *x + *y;
//		z->g = x->g * y->g;
	}
	else if(type == GT_t) {
		GT *x = (GT *) a;  GT *y = (GT *) b; GT *z = (GT *) c;
		*z = *x * *y;
	}
	else {
		/* Error */
	}

}

void _element_mul_si(Group_t type, const pairing_t *pairing, element_t *c, const element_t *a, const signed long int b, const element_t *o)
{
	PFC *pfc = (PFC *) pairing;
	if(type == ZR_t) {
		Big *z  = (Big *) c;
		Big *x  = (Big *) a;
		Big *o1 = (Big *) o;

		*z = modmult(*x, Big(b), *o1);
	}
	else if(type == G1_t) {
		G1 *z = (G1 *) c;
		G1 *x = (G1 *) a;
		*z = pfc->mult(*x, Big(b));
	}
	else if(type == G2_t) {
		G2 *z = (G2 *) c;
		G2 *x = (G2 *) a;
		*z = pfc->mult(*x, Big(b));
	}
	else if(type == GT_t) {
		GT *z = (GT *) c;
		GT *x = (GT *) a;
		*z = pfc->power(*x, Big(b));
	}
}

void _element_mul_zn(Group_t type, const pairing_t *pairing, element_t *c, const element_t *a, const element_t *b, const element_t *o)
{
	PFC *pfc = (PFC *) pairing;
	Big *b1 = (Big *) b;
	if(type == ZR_t) {
		Big *z = (Big *) c;
		Big *x = (Big *) a;
		Big *o1 = (Big *) o;

		*z = modmult(*x, *b1, *o1);
	}
	else if(type == G1_t) {
		G1 *z = (G1 *) c;
		G1 *x = (G1 *) a;
		*z = pfc->mult(*x, *b1);
	}
	else if(type == G2_t) {
		G2 *z = (G2 *) c;
		G2 *x = (G2 *) a;
		*z = pfc->mult(*x, *b1);
	}
	else if(type == GT_t) {
		GT *z = (GT *) c;
		GT *x = (GT *) a;
		*z = pfc->power(*x, *b1);
	}
}

void _element_div(Group_t type, element_t *c, const element_t *a, const element_t *b, const element_t *o)
{
	if(type == ZR_t) {
		Big *x = (Big *) a;
		Big *y = (Big *) b;
		Big *z = (Big *) c;
		Big *o1 = (Big *) o;

		if(!y->iszero()) *z = moddiv(*x, *y, *o1);
//		cout << "y => " << *y << endl;
//		cout << "Result => " << *z << endl;
	}
	else if(type == G1_t) {
		G1 *x = (G1 *) a;  G1 *y = (G1 *) b; G1 *z = (G1 *) c;
		*z = *x + (-*y);
	}
	else if(type == G2_t) {
		G2 *x = (G2 *) a;  G2 *y = (G2 *) b; G2 *z = (G2 *) c;
		*z = *x + (-*y);
	}
	else if(type == GT_t) {
		GT *x = (GT *) a;  GT *y = (GT *) b; GT *z = (GT *) c;
		*z = *x / *y;
	}
//	else if(type == )

}

element_t *_element_pow_zr_zr(Group_t type, const pairing_t *pairing, const element_t *a, const int b, const element_t *o)
{
	Big *o1 = (Big *) o;

	if(type == ZR_t) {
		Big *x = (Big *) a;
		return (element_t *) new Big(pow(*x, b, *o1));
	}

	return NULL;
}

element_t *_element_pow_zr(Group_t type, const pairing_t *pairing, element_t *a, element_t *b, element_t *o)
{
	Big *y = (Big *) b; // note: must be ZR
	PFC *pfc = (PFC *) pairing;

	if(type == ZR_t) {
		Big *x = (Big *) a;
		Big *z = (Big *) o;
		Big w = pow(*x, *y, *z);
		return (element_t *) new Big(w);
	}
	else if(type == G1_t) {
		G1 *x  = (G1 *)  a;
		G1 *z = new G1();
		// (x->point)^y
//		z->g = *y * x->g;
		// TODO: overflow error occurs if "y" is too big w/in miracl. Need to investigate
		*z = pfc->mult(*x, *y);
		return (element_t *) z;
	}
	else if(type == G2_t) {
		G2 *x  = (G2 *)  a;
		G2 *z = new G2();
		// (x->point)^y
		*z = pfc->mult(*x, *y);
		return (element_t *) z;
	}
	else if(type == GT_t) {
//		PFC *pfc = (PFC *) pairing;
		GT *x  = (GT *)  a;
		GT *z = new GT();
		// point ^ int
//		z->g = powu(x->g, *y);
		*z = pfc->power(*x, *y);
		return (element_t *) z;
	}
	return NULL;

}

element_t *_element_neg(Group_t type, const element_t *e, const element_t *o)
{
	if(type == ZR_t) {
		Big *x = (Big *) e;
		Big *y = new Big(*x);
		// Big *o1 = (Big *) o;
		y->negate();
		// *y %= *o1;
		return (element_t *) y;
	}
	else if(type == G1_t) {
		G1 *x = (G1 *) e;
		G1 *y = new G1();
		y->g = -x->g;
		return (element_t *) y;
	}
	else if(type == G2_t) {
		G2 *x = (G2 *) e;
		G2 *y = new G2();
		y->g = -x->g;
		return (element_t *) y;
	}
	else if(type == GT_t) {
		// TODO: see element_inv comment
	}
	return NULL;
}

// a => element, o => order of group
//element_t *_element_inv(Group_t type, const element_t *a, element_t *o) {
//
//}

void _element_inv(Group_t type, const pairing_t *pairing, const element_t *a, element_t *b, element_t *o)
{
	PFC *pfc = (PFC *) pairing;
	// TODO: not working as expected for ZR_t * ~ZR_t = seg fault?
	if(type == ZR_t) {
		Big *x = (Big *) a;
		Big *order = (Big *) o;
//		Big *y = new Big();
		Big *y = (Big *) b;
		*y = inverse(*x, *order);
//		cout << "inv res => " << *y << endl;
	}
	else if(type == G1_t) {
		G1 *g = (G1 *) a;
		G1 *h = (G1 *) b;
		// set it to the inverse
		h->g = -g->g;
	}
	else if(type == G2_t) {
		G2 *g = (G2 *) a;
		G2 *h = (G2 *) b;
		h->g = -g->g;
	}
	else if(type == GT_t) {
		GT *g = (GT *) a;
		GT *h = (GT *) b;
		h->g     = pfc->power(*g, Big(-1)).g;
	}
}

Big *charToBig (char *c, int len)
{
    Big *A;
    big a = mirvar(0);
    bytes_to_big(len, c, a);
    A = new Big(a);
	mr_free(a);
    return A;
}

Big getx(Big y)
{
    Big p=get_modulus();
    Big t=modmult(y+1,y-1,p);   // avoids overflow
    return pow(t,(2*p-1)/3,p);
}

G1 *charToG1(char *c, int len)
{
	G1 *point = new G1();
	Big *x0 = charToBig(c, len); // convert to a char
	while(!point->g.set(*x0, *x0)) *x0 += 1;

	// cout << "Point in G1 => " << point->g << endl;
	return point;
}

element_t *hash_then_map(Group_t type, const pairing_t *pairing, char *data, int len)
{
	PFC *pfc = (PFC *) pairing;
	if(type == ZR_t) {
		Big x = pfc->hash_to_group(data);
		Big *X = new Big(x);
		return (element_t *) X;
	}
	else if(type == G1_t) {
		G1 *w = new G1();
		pfc->hash_and_map(*w, data);
		return (element_t *) w;
	}
	else if(type == G2_t) {
		G2 *w = new G2();
		pfc->hash_and_map(*w, data);
		return (element_t *) w;
	}
	else {
		cout << "Error: unrecognized type." << endl;
		return NULL;
	}

}

void _init_hash(const pairing_t *pairing)
{
	PFC *pfc = (PFC *) pairing;
	pfc->start_hash();
}

void _element_add_str_hash(const pairing_t *pairing, void *data, int len)
{
	PFC *pfc = (PFC *) pairing;
	string s((char *) data);
	if(s.size() == (size_t) len) {
		Big b = pfc->hash_to_group((char *) s.c_str());
		pfc->add_to_hash(b);
	}
}

void _element_add_to_hash(Group_t type, const pairing_t *pairing, const element_t *e)
{
	PFC *pfc = (PFC *) pairing;
	if(type == ZR_t) {
		Big *b = (Big *) e;
		pfc->add_to_hash(*b);
	}
	else if(type == G1_t) {
		G1 *g1 = (G1 *) e;
		pfc->add_to_hash(*g1);
	}
	else if(type == G2_t) {
		G2 *g2 = (G2 *) e;
		pfc->add_to_hash(*g2);
	}
	else if(type == GT_t) {
		GT *gt = (GT *) e;
		pfc->add_to_hash(*gt);
	}
}

element_t *finish_hash(Group_t type, const pairing_t *pairing)
{
	PFC *pfc = (PFC *) pairing;
	Big *b = new Big(pfc->finish_hash_to_group());

	if(type == ZR_t) {
		return (element_t *) b;
	}
	else if(type == G1_t) {
		G1 *g1 = new G1();
		pfc->hash_and_map(*g1, (char *) bigToBytes(*b).c_str());
		return (element_t *) g1;
	}
	else if(type == G2_t) {
		G2 *g2 = new G2();
		pfc->hash_and_map(*g2, (char *) bigToBytes(*b).c_str());
		return (element_t *) g2;
	}
	else {
		cout << "Hashing to an invalid type: " << type << endl;
		delete b;
		return NULL;
	}
}

element_t *_element_from_hash(Group_t type, const pairing_t *pairing, void *data, int len)
{
	if(type == ZR_t) {
		return (element_t *) charToBig((char *) data, len);
	}
	else if(type == G1_t) {
		return (element_t *) charToG1((char *) data, len);
	}
	/* G2_t not so straigthforward to do by hand - just use hash then map */
	else if(type == G2_t) {
		return hash_then_map(type, pairing, (char *) data, len);
	}
	return NULL;
}


int element_is_value(Group_t type, element_t *n, int value) {
	if(type == ZR_t) {
		Big *x = (Big *) n;
		if(*x == Big(value)) {
			return TRUE;
		}
		else {
			return FALSE;
		}
	}
	return FALSE;
}

int _element_cmp(Group_t type, element_t *a, element_t *b) {

	BOOL result = -1;
	if(type == ZR_t) {
		Big *lhs = (Big *) a;
		Big *rhs = (Big *) b;
		result = *lhs == *rhs ? TRUE : FALSE;
		// cout << "Equal ? " << result << endl;
	}
	else if(type == G1_t) {
		G1 *lhs = (G1 *) a;
		G1 *rhs = (G1 *) b;
		result = *lhs == *rhs ? TRUE : FALSE;
	}
	else if(type == G2_t) {
		G2 *lhs = (G2 *) a;
		G2 *rhs = (G2 *) b;
		result = *lhs == *rhs ? TRUE  : FALSE;
	}
	else if(type == GT_t) {
		GT *lhs = (GT *) a;
		GT *rhs = (GT *) b;
		result = *lhs == *rhs ? TRUE  : FALSE;
	}

	return (int) result;
}

void _element_set_si(Group_t type, element_t *dst, const signed long int src)
{
	if(type == ZR_t) {
		Big *d = (Big *) dst;
		*d = Big(src);
//		cout << "Final value => " << *d << endl;
	}
}

int _element_setG1(Group_t type, element_t *c, const element_t *a, const element_t *b)
{
	if(type == G1_t) {
		G1 *p = (G1 *) c;
		Big *x = (Big *) a;
		Big *y = (Big *) b;

		if(p->g.set(*x, *y)) return TRUE;
	}
	return FALSE;
}

void _element_set(Curve_t ctype, Group_t type, element_t *dst, const element_t *src)
{
	if(type == ZR_t) {
		Big *e1 = (Big *) dst;
		Big *a1 = (Big *) src;
		*e1 = *a1;
	}
	else if(type == G1_t) {
		G1 *g = (G1 *) dst;
		G1 *h = (G1 *) src;

		Big x, y;
		h->g.get(x, y);
		g->g.set(x, y);
	}
	else if(type == G2_t) {
		G2 *g = (G2 *) dst;
		G2 *h = (G2 *) src;

		if(ctype == MNT) {
			ZZn3 x, y;			// assume it's an MNT curve
			h->g.get(x, y);
			g->g.set(x, y);
			//cout << "output => " << h->g << endl;
		}
	}
	else if(type == GT_t) {
		GT *g = (GT *) dst;
		GT *h = (GT *) src;
		if(ctype == MNT) {
			ZZn2 x, y, z;  		// assume it's an MNT curve
			h->g.get(x, y, z);
			g->g.set(x, y, z);
		}
	}
}


char *print_mpz(mpz_t x, int base) {
	if(base <= 2 || base > 64) return NULL;
	size_t x_size = mpz_sizeinbase(x, base) + 2;
	char *x_str = (char *) malloc(x_size + 1);
	memset(x_str, 0, x_size);
	x_str = mpz_get_str(x_str, base, x);
//	printf("Element => '%s'\n", x_str);
//	printf("Order of Element => '%zd'\n", x_size);
	// free(x_str);
	return x_str;
}


void _element_set_mpz(Group_t type, element_t *dst, mpz_t src)
{
	// convert an mpz to a Big (for ZR_t)
	if(type == ZR_t) {
		char *x_string = print_mpz(src, 10);
		big y;
		y = mirvar(0);

		// TODO: not the best solution and susceptible to overflow - number too big error. look into converting piece by piece.
		cinstr(y, x_string);
		Big *b = new Big(y);
//		cout << "Converted => " << *b << endl;
		free(x_string);
		Big *d = (Big *) dst;
		*d = *b;
	}
}

void _element_to_mpz(Group_t type, element_t *src, mpz_t dst)
{
	if(type == ZR_t) {
		Big *x = (Big *) src;

		// This is a hack: find a better way of convert big to mpz
		char c[MAX_LEN+1];
		memset(c, 0, MAX_LEN);
		int size = to_binary(*x, MAX_LEN, c, FALSE);
		string bytes(c, size);
		const char *b = bytes.c_str();
		mpz_import(dst, size, 1, sizeof(b[0]), 0, 0, b);
//		char *result = print_mpz(dst, 10);
//		printf("Result in dec '%s'\n", result);
	}
}

/*
 * pointer to data should be to allocated memory of size len
 */
void _element_hash_key(const pairing_t *pairing, Group_t type, element_t *e, void *data, int len)
{
	if(type == GT_t) {
		PFC *pfc = (PFC *) pairing;
		GT *gt = (GT *) e;
		Big tmp = pfc->hash_to_aes_key(*gt);

		// convert tmp to a string, right?
		string tmp_str = bigToRawBytes(tmp);
		memcpy((char *) data, tmp_str.c_str(), (size_t) strlen(tmp_str.c_str()));
	}
}
/* Note the following type definition from MIRACL pairing_3.h
 * G1 is a point over the base field, and G2 is a point over an extension field.
 * GT is a finite field point over the k-th extension, where k is the embedding degree.
 */
element_t *_element_pairing_type3(const pairing_t *pairing, const element_t *in1, const element_t *in2) {
	// we assume that in1 is G1 and in2 is G2 otherwise bad things happen
	PFC *pfc = (PFC *) pairing;
	G1 *g1 = (G1 *) in1;
	G2 *g2 = (G2 *) in2;
	G1 g_id = pfc->mult(*g1, Big(0)); // get identity elements
	G2 g2_id = pfc->mult(*g2, Big(0));
	GT *gt = new GT();
	// check whetehr g1 and g2 != identity element
	if(*g1 == g_id || *g2 == g2_id) {
		*gt = pfc->power(*gt, Big(0)); // gt ^ 0 = identity element?
//		cout << "One of the above is the identity element!" << endl;
	}
	else {
		pfc->precomp_for_pairing(*g2);
		gt = new GT(pfc->pairing(*g2, *g1)); // assumes type-3 pairings for now
	}
//	GT *gt_res = new GT(gt);
//	cout << "Result of pairing => " << gt->g << endl;
//	cout << "Result of pairing2 => " << gt_res->g << endl;
	return (element_t *) gt;
}

/* Does NOT perform any error checking */
element_t *_element_prod_pairing_type3(const pairing_t *pairing, const element_t **in1, const element_t **in2, int length)
{
	if(length <= 0) { return NULL; }

	PFC *pfc = (PFC *) pairing;
	G1 *g1_list[length];
	G2 *g2_list[length];

	for(int i = 0; i < length; i++) {
		g1_list[i] = (G1 *) in1[i];
		g2_list[i] = (G2 *) in2[i];
	}

	GT *gt = new GT(pfc->multi_pairing(length, g2_list, g1_list));
	return (element_t *) gt;
}

int _element_length_in_bytes(Curve_t ctype, Group_t type, element_t *e) {
	char c[MAX_LEN+1];
	memset(c, 0, MAX_LEN);
	if(type == ZR_t) {
		Big *s = (Big *) e;
		string t;
		t.append(bigToBytes(*s));
//		int size = to_binary(*s, MAX_LEN, c, FALSE);
//		stringstream o;
//		o << size << ":" << c << "\0";
		// purely for estimating length
		string encoded = _base64_encode(reinterpret_cast<const unsigned char*>(t.c_str()), t.size());
		return encoded.size();
	}
	else if(type == G1_t) {
		G1 *p = (G1 *) e;
		Big x, y;
		p->g.get(x, y);
		string t;
		t.append(bigToBytes(x));
		t.append(bigToBytes(y));

		// purely for estimating length
		string encoded = _base64_encode(reinterpret_cast<const unsigned char*>(t.c_str()), t.size());
		return encoded.size();
	}
	else if(type == G2_t) {
		G2 *P = (G2 *) e; // embeds an ECn3 element (for MNT curves)
		ZZn3 x, y;
		ZZn *a = new ZZn[6];
		P->g.get(x, y); // get ZZn3's
		x.get(a[0], a[1], a[2]); // get coordinates for each ZZn
		y.get(a[3], a[4], a[5]);

		string t;
		for(int i = 0; i < 6; i++) {
			t.append( bigToBytes(Big(a[i])) );
		}
		// base64 encode t and return
		string encoded = _base64_encode(reinterpret_cast<const unsigned char*>(t.c_str()), t.size());
		return encoded.size();
	}
	else if(type == GT_t) {
		GT *P = (GT *) e; // embeds an ZZn6 element (for MNT curves) is equivalent to
		// control this w/ a flag
		ZZn2 x, y, z; // each zzn2 has a (x,y) coordinates of type Big
		Big *a = new Big[6];
		P->g.get(x, y, z); // get ZZn2's

		x.get(a[0], a[1]); // get coordinates for each ZZn2
		y.get(a[2], a[3]);
	    z.get(a[4], a[5]);
//	    cout << "x => " << x << endl;
//	    cout << "y => " << y << endl;
//	    cout << "z => " << z << endl;
	    string t;
	    for(int i = 0; i < 6; i++) {
	    	string tmp = bigToBytes(a[i]);
	    	t.append( tmp );
	    }
		// base64 encode t and return
		string encoded = _base64_encode(reinterpret_cast<const unsigned char*>(t.c_str()), t.size());
		return encoded.size();
	}

	return 0;
}

int _element_to_bytes(unsigned char *data, Curve_t ctype, Group_t type, element_t *e) {
	char c[MAX_LEN+1];
	memset(c, 0, MAX_LEN);
	int enc_len;
	string t;

	if(type == ZR_t) {
		Big *s = (Big *) e;
		t.append(bigToBytes(*s));
		string encoded = _base64_encode(reinterpret_cast<const unsigned char*>(t.c_str()), t.size());
		enc_len = encoded.size();
		memcpy(data, encoded.c_str(), enc_len);
		data[enc_len] = '\0';
//		printf("Result => ");
//		_printf_buffer_as_hex((uint8_t *) data, enc_len);
//		printf("\n");
		return enc_len;
	}
	else if(type == G1_t) {
		G1 *p = (G1 *) e;
		Big x, y;
		p->g.get(x, y);
		string t;
		t.append(bigToBytes(x));
		t.append(bigToBytes(y));

		string encoded = _base64_encode(reinterpret_cast<const unsigned char*>(t.c_str()), t.size());
		enc_len = encoded.size();
		memcpy(data, encoded.c_str(), enc_len);
		data[enc_len] = '\0';
		return enc_len;
	}
	else if(type == G2_t) {
		G2 *P = (G2 *) e; // embeds an ECn3 element (for MNT curves)
		if(ctype == MNT) { // handling only MNT curves at the moment
		ZZn3 x, y;
		// ZZn a,b,c;
		ZZn *a = new ZZn[6];
		P->g.get(x, y); // get ZZn3's
		x.get(a[0], a[1], a[2]); // get coordinates for each ZZn
		y.get(a[3], a[4], a[5]);

		string t;
		for(int i = 0; i < 6; i++) {
			t.append( bigToBytes(Big(a[i])) );
		}
		// base64 encode t and return
		string encoded = _base64_encode(reinterpret_cast<const unsigned char*>(t.c_str()), t.size());
		enc_len = encoded.size();
		memcpy(data, encoded.c_str(), enc_len);
		data[enc_len] = '\0';
		return enc_len;
		}
	}
	else if(type == GT_t) {
		if(ctype == MNT) {
			GT *P = (GT *) e; // embeds an ZZn6 element (for MNT curves) is equivalent to
			// control this w/ a flag
			ZZn2 x, y, z; // each zzn2 has a (x,y) coordinates of type Big
			Big *a = new Big[6];
			P->g.get(x, y, z); // get ZZn2's

			x.get(a[0], a[1]); // get coordinates for each ZZn2
			y.get(a[2], a[3]);
		    z.get(a[4], a[5]);
	//	    cout << "Point => (" << x << ", " << y << ", " << z << ")" << endl;
		    string t;
		    for(int i = 0; i < 6; i++) {
		    	t.append( bigToBytes(a[i]) );
		    }
//		    cout << "Pre-encoding => ";
//		    _printf_buffer_as_hex((uint8_t *) t.c_str(), t.size());
			// base64 encode t and return
			string encoded = _base64_encode(reinterpret_cast<const unsigned char*>(t.c_str()), t.size());
			enc_len = encoded.size();
			memcpy(data, encoded.c_str(), enc_len);
			data[enc_len] = '\0';
			return enc_len;
		}
	}

	return 0;
}
element_t *_element_from_bytes(Curve_t ctype, Group_t type, unsigned char *data) {
	if(type == ZR_t) {
		if(is_base64((unsigned char) data[0])) {
			string b64_encoded((char *) data);
			string s = _base64_decode(b64_encoded);
			int cnt = 0;
			Big *X = bytesToBig(s, &cnt);
			return (element_t *) X;
		}
	}
	else if(type == G1_t) {
		if(is_base64((unsigned char) data[0])) {
		string b64_encoded((char *) data);
		string s = _base64_decode(b64_encoded);

		int cnt = 0;
		Big x,y;
		x = *bytesToBig(s, &cnt);
		s = s.substr(cnt);
		y = *bytesToBig(s, &cnt);
//		cout << "point => (" << x << ", " << y << ")" << endl;
		G1 *p = new G1();
		p->g.set(x,y);
		return (element_t *) p;
		}
	}
	else if(type == G2_t) {
		if(ctype == MNT && is_base64((unsigned char) data[0])) {
			string b64_encoded((char *) data);
			string s = _base64_decode(b64_encoded);
	//		cout << "original => " << s << endl;
			int cnt = 0;
			ZZn *a = new ZZn[6];
			for(int i = 0; i < 6; i++) {
				a[i] = ZZn(*bytesToBig(s, &cnt) ); // retrieve all six coordinates
				s = s.substr(cnt);
			}
			ZZn3 x (a[0], a[1], a[2]);
			ZZn3 y (a[3], a[4], a[5]);

			G2 *point = new G2();
			point->g.set(x, y);
			// cout << "Recovered pt => " << point->g << endl;
			return (element_t *) point;
		}
	}
	else if(type == GT_t) {
		if(ctype == MNT && is_base64((unsigned char) data[0])) {
			string b64_encoded((char *) data);
			string s = _base64_decode(b64_encoded);
	//		cout << "original => " << s << endl;
			int cnt = 0;
			Big *a = new Big[6];
			for(int i = 0; i < 6; i++) {
				// cout << "buffer => ";
			    // printf_buffer_as_hex((uint8_t *) s.c_str(), s.size());
				a[i] = *bytesToBig(s, &cnt); // retrieve all six coordinates
				s = s.substr(cnt);
				// cout << "i => " << a[i] << endl;
			}
			ZZn2 x, y, z;
			x.set(a[0], a[1]);
			y.set(a[2], a[3]);
			z.set(a[4], a[5]);

			GT *point = new GT();
			point->g.set(x, y, z);
			return (element_t *) point;
		}
	}

	return NULL;
}

void element_delete(Group_t type, element_t *e) {

	if(type == ZR_t) {
		Big *y = (Big *) e;
		delete y;
	}
	else if(type == G1_t) {
		G1 *point = (G1 *) e;
		delete point;
	}
	else if(type == G2_t) {
		G2 *point = (G2 *) e;
		delete point;
	}
	else if(type == GT_t) {
		GT *point = (GT *) e;
		delete point;
	}
	else {
		cout << "Unrecognized type" << endl;
	}
}


void pairing_clear(pairing_t *pairing) {
        PFC *pfc = (PFC *)pairing;
        delete pfc;
}

void miracl_clean() {
	// cout << "mirexit() call to clean-up." << endl;
	mirexit();
}

static const string base64_chars =
             "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
             "abcdefghijklmnopqrstuvwxyz"
             "0123456789+/";


/* Note that the following was borrowed from Copyright (C) 2004-2008 RenŽ Nyffenegger (*/

static inline bool is_base64(unsigned char c) {
  return (isalnum(c) || (c == '+') || (c == '/'));
}

string _base64_encode(unsigned char const* bytes_to_encode, unsigned int in_len) {
  string ret;
  int i = 0;
  int j = 0;
  unsigned char char_array_3[3];
  unsigned char char_array_4[4];

  while (in_len--) {
    char_array_3[i++] = *(bytes_to_encode++);
    if (i == 3) {
      char_array_4[0] = (char_array_3[0] & 0xfc) >> 2;
      char_array_4[1] = ((char_array_3[0] & 0x03) << 4) + ((char_array_3[1] & 0xf0) >> 4);
      char_array_4[2] = ((char_array_3[1] & 0x0f) << 2) + ((char_array_3[2] & 0xc0) >> 6);
      char_array_4[3] = char_array_3[2] & 0x3f;

      for(i = 0; (i <4) ; i++)
        ret += base64_chars[char_array_4[i]];
      i = 0;
    }
  }

  if (i)
  {
    for(j = i; j < 3; j++)
      char_array_3[j] = '\0';

    char_array_4[0] = (char_array_3[0] & 0xfc) >> 2;
    char_array_4[1] = ((char_array_3[0] & 0x03) << 4) + ((char_array_3[1] & 0xf0) >> 4);
    char_array_4[2] = ((char_array_3[1] & 0x0f) << 2) + ((char_array_3[2] & 0xc0) >> 6);
    char_array_4[3] = char_array_3[2] & 0x3f;

    for (j = 0; (j < i + 1); j++)
      ret += base64_chars[char_array_4[j]];

    while((i++ < 3))
      ret += '=';

  }

  return ret;

}

string _base64_decode(string const& encoded_string) {
  int in_len = encoded_string.size();
  int i = 0;
  int j = 0;
  int in_ = 0;
  unsigned char char_array_4[4], char_array_3[3];
  std::string ret;

  while (in_len-- && ( encoded_string[in_] != '=') && is_base64(encoded_string[in_])) {
    char_array_4[i++] = encoded_string[in_]; in_++;
    if (i ==4) {
      for (i = 0; i <4; i++)
        char_array_4[i] = base64_chars.find(char_array_4[i]);

      char_array_3[0] = (char_array_4[0] << 2) + ((char_array_4[1] & 0x30) >> 4);
      char_array_3[1] = ((char_array_4[1] & 0xf) << 4) + ((char_array_4[2] & 0x3c) >> 2);
      char_array_3[2] = ((char_array_4[2] & 0x3) << 6) + char_array_4[3];

      for (i = 0; (i < 3); i++)
        ret += char_array_3[i];
      i = 0;
    }
  }

  if (i) {
    for (j = i; j <4; j++)
      char_array_4[j] = 0;

    for (j = 0; j <4; j++)
      char_array_4[j] = base64_chars.find(char_array_4[j]);

    char_array_3[0] = (char_array_4[0] << 2) + ((char_array_4[1] & 0x30) >> 4);
    char_array_3[1] = ((char_array_4[1] & 0xf) << 4) + ((char_array_4[2] & 0x3c) >> 2);
    char_array_3[2] = ((char_array_4[2] & 0x3) << 6) + char_array_4[3];

    for (j = 0; (j < i - 1); j++) ret += char_array_3[j];
  }

  return ret;
}

int aes_encrypt(char *key, char *message, int len, char **out)
{
	aes a;
	int keysize = aes_block_size;
	csprng RNG;
	unsigned long ran;
	time((time_t *) &ran);
	string raw = "seeding RNGs"; // read from /dev/random
	strong_init(&RNG, (int) raw.size(), (char *) raw.c_str(), ran);

	int i;
	char iv[aes_block_size];
	// select random IV here
    for (i=0;i<16;i++) iv[i]=i;
//	for (i=0;i<16;i++) iv[i]=strong_rng(&RNG);
    if (!aes_init(&a, MR_CBC, keysize, key, iv))
	{
		printf("Failed to Initialize\n");
		return -1;
	}

    char message_buf[len + 1];
	memset(message_buf, 0, len);
	memcpy(message_buf, message, len);
    aes_encrypt(&a, message_buf);
//    for (i=0;i<aes_block_size;i++) printf("%02x",(unsigned char) message_buf[i]);
//    aes_end(&a);

	strong_kill(&RNG);
    string t = string(message_buf, len);
	aes_end(&a);
	string s = _base64_encode(reinterpret_cast<const unsigned char*>(t.c_str()), t.size());
	int len2 = (int) s.size();
	*out = (char *) malloc(len2 + 1);
	memset(*out, 0, len2);
	memcpy(*out, (char *) s.c_str(), len2);
	return len2;
}

int aes_decrypt(char *key, char *ciphertext, int len, char **out)
{
	aes a;
	int keysize = aes_block_size;
	int i;
	char iv[aes_block_size];
	for (i=0;i<16;i++) iv[i]=i; // TODO: retrieve IV from ciphertext

	// assumes we're dealing with 16-block aligned buffers
	if (!aes_init(&a, MR_CBC, keysize, key, iv))
	{
		printf("Failed to Initialize\n");
		return -1;
	}

	char *ciphertext2;
	int len2;
	if(is_base64((unsigned char) ciphertext[0])) {
		string b64_encoded((char *) ciphertext, len);
		string t = _base64_decode(b64_encoded);
		ciphertext2 = (char *) t.c_str();
		len2 = (int) t.size();
	}
	else {
		ciphertext2 = ciphertext;
		len2 = len;
	}

	char message_buf[len2 + 1];
	memset(message_buf, 0, len2);
	memcpy(message_buf, ciphertext2, len2);

	aes_decrypt(&a, message_buf);
//	for (i=0;i<aes_block_size;i++) printf("%02x",(unsigned char) ciphertext_buf[i]);
	aes_end(&a);
//	return string(message_buf, len2);
	*out = (char *) malloc(len2 + 1);
	memset(*out, 0, len2);
	memcpy(*out, (char *) message_buf, len2);

	return len2;
}


} // end of extern
