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
*   @file    pairingmodule3.h
*
*   @brief   charm interface over RELIC's pairing-based crypto module
*
*   @author  ayo.akinyele@charm-crypto.com
*
************************************************************************/

#ifndef PAIRINGMODULE3_H
#define PAIRINGMODULE3_H

#include <Python.h>
#include <structmember.h>
#include <longintrepr.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include "benchmarkmodule.h"
#include "base64.h"
#include "relic_interface.h"

//#define DEBUG	1
//#define TRUE	1
//#define FALSE	0
#define BenchmarkIdentifier 4
#define MAX_LEN 2048
#define HASH_LEN 20
#define ID_LEN   4
#define MAX_BENCH_OBJECTS	2
// define element_types
//enum Group {ZR, G1, G2, GT, NONE_G};
//typedef enum Group GroupType;

/* Index numbers for different hash functions.  These are all implemented as SHA1(index || message).	*/
#define HASH_FUNCTION_ELEMENTS			0
#define HASH_FUNCTION_STR_TO_Zr_CRH		1
#define HASH_FUNCTION_Zr_TO_G1_ROM		2
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
	if(PyUnicode_Check(obj)) { obj = PyUnicode_AsUTF8String(obj); } \
	a = PyBytes_AS_STRING(obj);
#else
/* treat everything as string in 2.x */
#define PyBytes_ToString(a, obj) a = PyString_AsString(obj);
#endif

// static Benchmark *dObjects[MAX_BENCH_OBJECTS], *activeObject = NULL;

PyMethodDef Element_methods[];
PyMethodDef pairing_methods[];
PyMemberDef Element_members[];
PyNumberMethods element_number;

typedef struct {
	PyObject_HEAD
//	pbc_param_t p;
//	pairing_t pair_obj;
	int safe;
	uint8_t hash_id[ID_LEN+1];
} Pairing;

typedef struct {
    PyObject_HEAD
	char *params;
	char *param_buf;

	Pairing *pairing;
	element_t e;
//	element_ptr e;
	GroupType element_type;
    int elem_initialized;
	int safe_pairing_clear;
} Element;

typedef struct {
	int exp_ZR, exp_G1, exp_G2, exp_GT;
	int mul_ZR, mul_G1, mul_G2, mul_GT;
	int div_ZR, div_G1, div_G2, div_GT;
	// optional
	int add_ZR, add_G1, add_G2, add_GT;
	int sub_ZR, sub_G1, sub_G2, sub_GT;
} Operations;

#define IS_PAIRING_OBJ_NULL(obj)   /* do nothing */
//	if(obj->pairing == NULL) {
//		PyErr_SetString(ElementError, "pairing structure not initialized.");
//		return NULL;
//	}

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

#define set_element_ZR(obj, value)  \
    if(value == 0)		\
       element_set0(obj);   \
	else if(value == 1)		\
	   element_set1(obj);	\
    else {  element_set_si(obj, (signed int) value); }

#define VERIFY_GROUP(g) \
	if(PyElement_Check(g) && g->safe_pairing_clear == FALSE) {	\
		PyErr_SetString(ElementError, "invalid group object specified.");  \
		return NULL;  } 	\
//	if(g->pairing == NULL) {
//		PyErr_SetString(ElementError, "pairing object is NULL.");
//		return NULL;  }

PyObject *Element_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
int Element_init(Element *self, PyObject *args, PyObject *kwds);
PyObject *Element_print(Element* self);
PyObject *Element_call(Element *elem, PyObject *args, PyObject *kwds);
void	Element_dealloc(Element* self);
Element *convertToZR(PyObject *LongObj, PyObject *elemObj);

PyObject *Apply_pairing(Element *self, PyObject *args);
PyObject *sha1_hash(Element *self, PyObject *args);
void Operations_clear(void);

int exp_rule(GroupType lhs, GroupType rhs);
int mul_rule(GroupType lhs, GroupType rhs);
int add_rule(GroupType lhs, GroupType rhs);
int sub_rule(GroupType lhs, GroupType rhs);
int div_rule(GroupType lhs, GroupType rhs);
int pair_rule(GroupType lhs, GroupType rhs);
//void print_int(integer_t x, int base);

#ifdef BENCHMARK_ENABLED
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
	Op_ ##name(op_type, elem_type, ZR, bench_obj)	\
	Op_ ##name(op_type, elem_type, G1, bench_obj)	\
	Op_ ##name(op_type, elem_type, G2, bench_obj)	\
	Op_ ##name(op_type, elem_type, GT, bench_obj)	\

#define UPDATE_BENCH(op_type, elem_type, bench_obj) \
	if(bench_obj->granular_option == TRUE && elem_type >= ZR && elem_type <= GT) {		\
		Update_Op(MUL, op_type, elem_type, bench_obj) \
		Update_Op(DIV, op_type, elem_type, bench_obj) \
		Update_Op(ADD, op_type, elem_type, bench_obj) \
		Update_Op(SUB, op_type, elem_type, bench_obj) \
		Update_Op(EXP, op_type, elem_type, bench_obj) \
	}		\
	UPDATE_BENCHMARK(op_type, bench_obj);

#define CLEAR_ALLDBENCH(bench_obj)  \
	    CLEAR_DBENCH(bench_obj, ZR);	\
	    CLEAR_DBENCH(bench_obj, G1);	\
	    CLEAR_DBENCH(bench_obj, G2);	\
	    CLEAR_DBENCH(bench_obj, GT);	\

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

#define IS_SAME_GROUP(a, b) 	/* doesn't apply */
//#define IS_SAME_GROUP(a, b)
//	if(strncmp((const char *) a->pairing->hash_id, (const char *) b->pairing->hash_id, ID_LEN) != 0) {
//		PyErr_SetString(ElementError, "mixing group elements from different curves.");
//		return NULL;
//	}

#endif
