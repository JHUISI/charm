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
 *   @file    pairingmodule2.h
 *
 *   @brief   charm interface over MIRACL's pairing-based operations
 *
 *   @author  ayo.akinyele@charm-crypto.com
 * 	@remark	 this version of the pairing module uses the MIRACL library (www.shamus.ie).
 *   At the moment, only useful for academic purposes and should be treated as such.
 *   To build into Charm, you'll need to acquire the MIRACL source and compile with the
 *   build script located in the miracl dir. See the online documentation at charm-crypto.com
 *   for how to install.
 *
 ************************************************************************/

#ifndef PAIRINGMODULE2_H
#define PAIRINGMODULE2_H

#include <Python.h>
#include <structmember.h>
#include <longintrepr.h>
#include <stdlib.h>
#include "miracl_interface2.h"
#include <gmp.h>
#include <limits.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include "sha1.h"
#include "benchmarkmodule.h"

/* supported pairing curves */
#define MNT160  	80
#define BN256	  	128
#define SS512		80

/* buf sizes */
#define BenchmarkIdentifier 1
#define BUF_MAX_LEN 512
#define HASH_LEN 	20

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

int pairing_init_finished;
PyTypeObject ElementType;
PyTypeObject PairingType;
static PyObject *ElementError;
#ifdef BENCHMARK_ENABLED
static Benchmark *dBench;
#endif

#define PyElement_Check(obj) PyObject_TypeCheck(obj, &ElementType)
#define PyPairing_Check(obj) PyObject_TypeCheck(obj, &PairingType)
#if PY_MAJOR_VERSION >= 3
/* check for both unicode and bytes objects */
#define PyBytes_CharmCheck(obj) PyUnicode_Check(obj) || PyBytes_Check(obj)
#else
/* check for just unicode stuff */
#define PyBytes_CharmCheck(obj)	PyUnicode_Check(obj) || PyString_Check(obj)
#endif

#if PY_MAJOR_VERSION >= 3
/* if unicode then add extra conversion step. two possibilities: unicode or bytes */
#define PyBytes_ToString(a, obj) \
	if(PyUnicode_Check(obj)) { PyObject *_obj = PyUnicode_AsUTF8String(obj); a = PyBytes_AS_STRING(_obj); Py_DECREF(_obj); }	\
	else { a = PyBytes_AS_STRING(obj); }
#else
/* treat everything as string in 2.x */
#define PyBytes_ToString(a, obj) a = PyString_AsString(obj);
#endif

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

#ifdef BENCHMARK_ENABLED
typedef struct {
	int exp_ZR_t, exp_G1_t, exp_G2_t, exp_GT_t;
	int mul_ZR_t, mul_G1_t, mul_G2_t, mul_GT_t;
	int div_ZR_t, div_G1_t, div_G2_t, div_GT_t;
	// optional
	int add_ZR_t, add_G1_t, add_G2_t, add_GT_t;
	int sub_ZR_t, sub_G1_t, sub_G2_t, sub_GT_t;
} Operations;
#endif

#define IS_PAIRING_OBJ_NULL(obj) \
	if(obj->pairing == NULL) {	\
		PyErr_SetString(ElementError, "pairing structure not initialized.");	\
		return NULL;	\
	}

/* miracl macros to simplify interface */
#define print(msg, type, e)  \
	printf("%s", msg); 		 \
	element_printf(type, e); \
	printf("\n");

#define element_init_hash(a) _init_hash(a->pairing->pair_obj)
#define element_add_str_hash(a, b, c) _element_add_str_hash(a->pairing->pair_obj, b, c)
#define element_add_to_hash(a) _element_add_to_hash(a->element_type, a->pairing->pair_obj, a->e)
#define element_finish_hash(a, t) a->e = finish_hash(t, a->pairing->pair_obj)
#define element_hash_to_key(a, b, c) _element_hash_key(a->pairing->pair_obj, a->element_type, a->e, b, c)

#define element_is(a, b) element_is_value(a->element_type, a->e, b)
#define element_add(c, a, b) _element_add(a->element_type, c->e, a->e, b->e, a->pairing->order)
#define element_sub(c, a, b) _element_sub(a->element_type, c->e, a->e, b->e, a->pairing->order)
#define element_mul(c, a, b) _element_mul(a->element_type, c->e, a->e, b->e, a->pairing->order)
#define element_mul_si(c, a, b) _element_mul_si(a->element_type, a->pairing->pair_obj, c->e, a->e, b, a->pairing->order)
#define element_mul_zn(c, a, b) _element_mul_zn(a->element_type, a->pairing->pair_obj, c->e, a->e, b->e, a->pairing->order)
// TODO: fix for -1 / ZR and similar operations
#define element_div(c, a, b) _element_div(a->element_type, c->e, a->e, b->e, a->pairing->order)
#define element_set(a, b) _element_set(a->pairing->curve, a->element_type, a->e, b->e);
#define element_set_raw(g, t, a, b) _element_set(g->pairing->curve, t, a, b);
#define element_setG1(c, a, b) _element_setG1(c->element_type, c->e, a->e, b->e);

#define element_set_si(a, b) \
	if(a->element_type == ZR_t) { _element_set_si(a->element_type, a->e, b); }

#define element_set_mpz(a, b)	_element_set_mpz(a->element_type, a->e, b);
#define element_to_mpz(a, b)	_element_to_mpz(ZR_t, a->e, b);
#define object_to_mpz(a, b)	_element_to_mpz(ZR_t, a, b);

#define element_neg(a, b) \
	a->e = _element_neg(a->element_type, b->e, b->pairing->order);

#define element_invert(a, b) \
	_element_inv(b->element_type, b->pairing->pair_obj, b->e, a->e, b->pairing->order)

#define element_pow_zr(c, a, b) \
	if (a->element_type != NONE_G)  {  \
	c->e = _element_pow_zr(a->element_type, a->pairing->pair_obj, a->e, b->e, a->pairing->order); \
	c->element_type = a->element_type; }

#define element_pow_int(c, a, b) \
	c->e = _element_pow_zr_zr(ZR_t, a->pairing->pair_obj, a->e, b, a->pairing->order);	\
	c->element_type = ZR_t;

#define pairing_apply(c, a, b) \
	if(a->pairing->curve == MNT || a->pairing->curve == BN || a->pairing->curve == SS) { \
		c->e = _element_pairing(a->pairing->pair_obj, a->e, b->e); \
		c->element_type = GT_t;   \
	}

#define element_prod_pairing(c, a, b, l) \
	if(c->pairing->curve == MNT || c->pairing->curve == BN || c->pairing->curve == SS) { \
		c->e = _element_prod_pairing(c->pairing->pair_obj, a, b, l); \
		c->element_type = GT_t;  }

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

#define element_cmp(a, b) _element_cmp(a->element_type, a->e, b->e);
#define element_length_to_str(a) _element_length_to_str(a->element_type, a->e);
#define element_to_str(d, a)  _element_to_str(d, a->element_type, a->e);
#define element_init_G1   _element_init_G1
#define element_init_G2   _element_init_G2
#define element_init_GT(a)   _element_init_GT(a->pair_obj);
#define check_membership(a)  element_is_member(a->pairing->curve, a->element_type, a->pairing->pair_obj, a->e)

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

#define VERIFY_GROUP(g) \
	if(PyElement_Check(g) && g->safe_pairing_clear == FALSE) {	\
		PyErr_SetString(ElementError, "invalid group object specified.");  \
		return NULL;  } 	\
	if(g->pairing == NULL) {	\
		PyErr_SetString(ElementError, "pairing object is NULL.");	\
		return NULL;  }		\

PyObject *Element_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
int Element_init(Element *self, PyObject *args, PyObject *kwds);
PyObject *Element_print(Element* self);
PyObject *Element_call(Element *elem, PyObject *args, PyObject *kwds);
void	Element_dealloc(Element* self);
Element *convertToZR(PyObject *LongObj, PyObject *elemObj);

PyObject *Apply_pairing(Element *self, PyObject *args);
PyObject *sha1_hash(Element *self, PyObject *args);

int exp_rule(Group_t lhs, Group_t rhs);
int mul_rule(Group_t lhs, Group_t rhs);
int add_rule(Group_t lhs, Group_t rhs);
int sub_rule(Group_t lhs, Group_t rhs);
int div_rule(Group_t lhs, Group_t rhs);
int pair_rule(Group_t lhs, Group_t rhs);

#ifdef BENCHMARK_ENABLED
void Operations_clear(void);

// for multiplicative notation
#define Op_MUL(op_var_type, op_group_type, group, bench_obj)  \
	if(op_var_type == MULTIPLICATION && op_group_type == group)      \
		((Operations *) bench_obj->data_ptr)->mul_ ##group += 1;

#define Op_DIV(op_var_type, op_group_type, group, bench_obj)  \
	if(op_var_type == DIVISION && op_group_type == group)      \
		((Operations *) bench_obj->data_ptr)->div_ ##group += 1;

// for additive notation
#define Op_ADD(op_var_type, op_group_type, group, bench_obj)  \
	if(op_var_type == ADDITION && op_group_type == group)      \
		((Operations *) bench_obj->data_ptr)->add_ ##group += 1;

#define Op_SUB(op_var_type, op_group_type, group, bench_obj)  \
	if(op_var_type == SUBTRACTION && op_group_type == group)      \
		((Operations *) bench_obj->data_ptr)->sub_ ##group += 1;

// exponentiation
#define Op_EXP(op_var_type, op_group_type, group, bench_obj)  \
	if(op_var_type == EXPONENTIATION && op_group_type == group)      \
		((Operations *) bench_obj->data_ptr)->exp_ ##group += 1;

#define Update_Op(name, op_type, elem_type, bench_obj)	\
	Op_ ##name(op_type, elem_type, ZR_t, bench_obj)	\
	Op_ ##name(op_type, elem_type, G1_t, bench_obj)	\
	Op_ ##name(op_type, elem_type, G2_t, bench_obj)	\
	Op_ ##name(op_type, elem_type, GT_t, bench_obj)	\

#define UPDATE_BENCH(op_type, elem_type, bench_obj) \
	if(bench_obj->granular_option == TRUE && elem_type >= ZR_t && elem_type <= GT_t) {		\
		Update_Op(MUL, op_type, elem_type, bench_obj) \
		Update_Op(DIV, op_type, elem_type, bench_obj) \
		Update_Op(ADD, op_type, elem_type, bench_obj) \
		Update_Op(SUB, op_type, elem_type, bench_obj) \
		Update_Op(EXP, op_type, elem_type, bench_obj) \
	}		\
	UPDATE_BENCHMARK(op_type, bench_obj);

#define CLEAR_ALLDBENCH(bench_obj)  \
	    CLEAR_DBENCH(bench_obj, ZR_t);	\
	    CLEAR_DBENCH(bench_obj, G1_t);	\
	    CLEAR_DBENCH(bench_obj, G2_t);	\
	    CLEAR_DBENCH(bench_obj, GT_t);	\

#define CLEAR_DBENCH(bench_obj, group)   \
	((Operations *) bench_obj->data_ptr)->mul_ ##group = 0;	\
	((Operations *) bench_obj->data_ptr)->exp_ ##group = 0;	\
	((Operations *) bench_obj->data_ptr)->div_ ##group = 0;	\
	((Operations *) bench_obj->data_ptr)->add_ ##group = 0;	\
	((Operations *) bench_obj->data_ptr)->sub_ ##group = 0;	\

#define GetField(count, type, group, bench_obj)  \
	if(type == MULTIPLICATION) count = (((Operations *) bench_obj->data_ptr)->mul_ ##group ); \
	else if(type == DIVISION) count = (((Operations *) bench_obj->data_ptr)->div_ ##group );	\
	else if(type == ADDITION) count = (((Operations *) bench_obj->data_ptr)->add_ ##group ); \
	else if(type == SUBTRACTION) count = (((Operations *) bench_obj->data_ptr)->sub_ ##group ); \
	else if(type == EXPONENTIATION) count = (((Operations *) bench_obj->data_ptr)->exp_ ##group );

#else

#define UPDATE_BENCH(op_type, elem_type, bench_obj)  /* ... */
// #define UPDATE_BENCHMARK(op_type, bench_obj)  /* ... */
#define CLEAR_ALLDBENCH(bench_obj) /* ... */
#define GetField(count, type, group, bench_obj)  /* ... */
#endif


#define EXIT_IF(check, msg) \
	if(check) { 						\
	PyErr_SetString(ElementError, msg); \
	return NULL;	}

#define EXITCODE_IF(check, msg, code) \
	if(check) {						     \
	PyErr_SetString(ElementError, msg);	 \
	return Py_BuildValue("i", code);	}

#endif
