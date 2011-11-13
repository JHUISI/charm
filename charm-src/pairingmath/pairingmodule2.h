/* Disclaimer: this version of the pairing module uses the MIRACL library (www.shamus.ie).
 * At the moment, only useful for academic purposes and should be treated as such.
 * To build into Charm, you'll need to acquire the MIRACL source and compile with
 * build script located in the miracl dir.
 */

#ifndef PAIRINGMODULE2_H
#define PAIRINGMODULE2_H

#include <Python.h>
#include <structmember.h>
#include <longintrepr.h>
#include <stdlib.h>
#include "miraclwrapper.h"
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include "sha1.h"
#include "benchmarkmodule.h"
#include "base64.h"

//#define DEBUG	1
//#define TRUE	1
//#define FALSE	0
#define BUF_MAX_LEN 2048
#define HASH_LEN 20
#define MAX_BENCH_OBJECTS	2

/* Index numbers for different hash functions.  These are all implemented as SHA1(index || message).	*/
#define HASH_FUNCTION_STR_TO_Zr_CRH		0
#define HASH_FUNCTION_Zr_TO_G1_ROM		1
#define HASH_FUNCTION_ELEMENTS			2
#define HASH_FUNCTION_STRINGS			3

#ifdef DEBUG
#define debug_e(...)	element_printf("DEBUG: "__VA_ARGS__)
#else
#define debug_e(...)
#endif

PyTypeObject ElementType;
PyTypeObject PairingType;
static PyObject *ElementError;
static Benchmark *dBench;
#define PyElement_Check(obj) PyObject_TypeCheck(obj, &ElementType)
#define PyPairing_Check(obj) PyObject_TypeCheck(obj, &PairingType)
// static Benchmark *dObjects[MAX_BENCH_OBJECTS], *activeObject = NULL;

PyMethodDef Element_methods[];
PyMethodDef pairing_methods[];
PyMemberDef Element_members[];
PyNumberMethods element_number;

typedef struct {
	PyObject_HEAD
	pairing_t *pair_obj;
	element_t *order;
	int curve;
	int safe;
} Pairing;

typedef struct {
    PyObject_HEAD
	Pairing *pairing;
	element_t *e;
	Group_t element_type;
    int elem_initialized;
	int safe_pairing_clear;
} Element;

/* miracl macros to simplify interface */
#define print(msg, type, e)  \
	printf("%s", msg); 		 \
	element_printf(type, e); \
	printf("\n");

#define element_is(a, b) element_is_value(a->element_type, a->e, b)
#define element_add(c, a, b) _element_add(a->element_type, c->e, a->e, b->e)
#define element_sub(c, a, b) _element_sub(a->element_type, c->e, a->e, b->e)
#define element_mul(c, a, b) _element_mul(a->element_type, c->e, a->e, b->e, a->pairing->order)
#define element_mul_si(c, a, b) \
	_element_mul_si(a->element_type, a->pairing->pair_obj, c->e, a->e, b, a->pairing->order)
#define element_mul_zn(c, a, b) \
	_element_mul_zn(a->element_type, a->pairing->pair_obj, c->e, a->e, b->e, a->pairing->order)
#define element_div(c, a, b) \
	_element_div(a->element_type, c->e, a->e, b->e) // TODO: fix for 1 / ZR
#define element_set(a, b) \
	_element_set(a->pairing->curve, a->element_type, a->e, b->e);

#define element_set_si(a, b) \
	if(a->element_type == ZR_t) { _element_set_si(a->element_type, a->e, b); }

#define element_neg(a, b) \
	a->e = _element_neg(a->element_type, b->e, b->pairing->order);

#define element_invert(a, b) \
	_element_inv(b->element_type, b->e, a->e, b->pairing->order)

#define element_pow_zr(a, b) \
	_element_pow_zr(a->element_type, a->pairing->pair_obj, a->e, b->e)

#define pairing_apply(c, a, b) \
	if(a->pairing->curve == MNT) { \
		c->e = _element_pairing_type3(a->pairing->pair_obj, a->e, b->e); \
		c->element_type = GT_t;   \
	} else { /* do other stuff for SS-curves */ }

#define element_from_hash(a, d, l) \
		a->e = _element_from_hash(a->element_type, a->pairing->pair_obj, d, l);

#define element_after_hash(a, d, l) \
		a->e = hash_then_map(a->element_type, a->pairing->pair_obj, d, l);

#define element_length_in_bytes(a)  \
	_element_length_in_bytes(a->pairing->curve, a->element_type, a->e);

#define element_to_bytes(d, a)	\
	_element_to_bytes(d, a->pairing->curve, a->element_type, a->e);

#define element_from_bytes(o, b)   \
	o->e = _element_from_bytes(o->pairing->curve, o->element_type, b);

#define element_cmp(a, b) \
	_element_cmp(a->element_type, a->e, b->e);

#define Check_Elements(o1, o2)  PyElement_Check(o1) && PyElement_Check(o2)

#define Check_Types2(o1, o2, lhs_o1, rhs_o2, longLHS_o1, longRHS_o2)  \
	if(PyElement_Check(o1)) { \
		lhs_o1 = (Element *) o1; \
		debug("found a lhs element.\n"); \
    } \
	else if(PyLong_Check(o1)) { \
		longLHS_o1 = TRUE;  } \
							  \
	if(PyElement_Check(o2)) {  \
		rhs_o2 = (Element *) o2; \
		debug("found a rhs element.\n"); \
    } \
	else if(PyLong_Check(o2)) {  \
		longRHS_o2 = TRUE; }	\

PyObject *Element_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
int Element_init(Element *self, PyObject *args, PyObject *kwds);
PyObject *Element_print(Element* self);
PyObject *Element_call(Element *elem, PyObject *args, PyObject *kwds);
void	Element_dealloc(Element* self);

PyObject *Apply_pairing(Element *self, PyObject *args);
PyObject *sha1_hash(Element *self, PyObject *args);

int exp_rule(Group_t lhs, Group_t rhs);
int mul_rule(Group_t lhs, Group_t rhs);
int add_rule(Group_t lhs, Group_t rhs);
int sub_rule(Group_t lhs, Group_t rhs);
int div_rule(Group_t lhs, Group_t rhs);
int pair_rule(Group_t lhs, Group_t rhs);
#endif
