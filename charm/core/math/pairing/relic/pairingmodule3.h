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
#ifdef BENCHMARK_ENABLED
#define RAND_pseudo_bytes(a, b) /* redefine */
#include "benchmark_util.h"
#endif

//#define DEBUG	1
//#define TRUE	1
//#define FALSE	0
#define MAX_LEN 2048
#define HASH_LEN 20
#define ID_LEN   4
#define MAX_BENCH_OBJECTS	2

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
#define PyElement_Check(obj) PyObject_TypeCheck(obj, &ElementType)
#define PyPairing_Check(obj) PyObject_TypeCheck(obj, &PairingType)

PyMethodDef Element_methods[];
PyMethodDef pairing_methods[];
PyMemberDef Element_members[];
PyNumberMethods element_number;

#ifdef BENCHMARK_ENABLED

typedef struct {
	PyObject_HEAD
	int op_init;
	int exp_ZR, exp_G1, exp_G2, exp_GT;
	int mul_ZR, mul_G1, mul_G2, mul_GT;
	int div_ZR, div_G1, div_G2, div_GT;
	// optional
	int add_ZR, add_G1, add_G2, add_GT;
	int sub_ZR, sub_G1, sub_G2, sub_GT;
} Operations;

#endif


typedef struct {
	PyObject_HEAD
	int group_init;
	uint8_t hash_id[ID_LEN+1];
#ifdef BENCHMARK_ENABLED
	Operations *gBench;
    Benchmark *dBench;
	uint8_t bench_id[ID_LEN+1];
#endif
} Pairing;

typedef struct {
    PyObject_HEAD
	Pairing *pairing;
	element_t e;
	GroupType element_type;
    int elem_initialized;
	element_pp_t e_pp;
	int elem_initPP;
} Element;

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
	else if(_PyLong_Check(o1)) { \
		longLHS_o1 = TRUE;  } \
							  \
	if(PyElement_Check(o2)) {  \
		rhs_o2 = (Element *) o2; \
		debug("found a rhs element.\n"); \
    } \
	else if(_PyLong_Check(o2)) {  \
		longRHS_o2 = TRUE; }	\

#define set_element_ZR(obj, value)  \
    if(value == 0)		\
       element_set0(obj);   \
	else if(value == 1)		\
	   element_set1(obj);	\
    else {  element_set_si(obj, (signed int) value); }

#define VERIFY_GROUP(g) \
	if(PyPairing_Check(g) && g->group_init == FALSE) {	\
		PyErr_SetString(ElementError, "Not a Pairing group object.");  \
		return NULL;  }

PyObject *Element_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
int Element_init(Element *self, PyObject *args, PyObject *kwds);
PyObject *Element_print(Element* self);
PyObject *Element_call(Element *elem, PyObject *args, PyObject *kwds);
void	Element_dealloc(Element* self);
Element *convertToZR(PyObject *LongObj, PyObject *elemObj);

PyObject *Apply_pairing(Element *self, PyObject *args);
PyObject *sha2_hash(Element *self, PyObject *args);

int exp_rule(GroupType lhs, GroupType rhs);
int mul_rule(GroupType lhs, GroupType rhs);
int add_rule(GroupType lhs, GroupType rhs);
int sub_rule(GroupType lhs, GroupType rhs);
int div_rule(GroupType lhs, GroupType rhs);
int pair_rule(GroupType lhs, GroupType rhs);
//void print_int(integer_t x, int base);

#if PY_MAJOR_VERSION < 3
#define ConvertToInt2(x, obj) \
	PyObject *_longObj = PyNumber_Long(obj);	\
	longObjToInt(x, (PyLongObject *) _longObj);		\
	Py_DECREF(_longObj);
#else
#define ConvertToInt2(x, obj) \
	longObjToInt(x, (PyLongObject *) obj);
#endif

#ifdef BENCHMARK_ENABLED

#define IsBenchSet(obj)  obj->dBench != NULL

#define Update_Op(name, op_type, elem_type, bench_obj)	\
	Op_ ##name(op_type, elem_type, ZR, bench_obj)	\
	Op_ ##name(op_type, elem_type, G1, bench_obj)	\
	Op_ ##name(op_type, elem_type, G2, bench_obj)	\
	Op_ ##name(op_type, elem_type, GT, bench_obj)	\

#define CLEAR_ALLDBENCH(bench_obj)  \
	    CLEAR_DBENCH(bench_obj, ZR);	\
	    CLEAR_DBENCH(bench_obj, G1);	\
	    CLEAR_DBENCH(bench_obj, G2);	\
	    CLEAR_DBENCH(bench_obj, GT);	\

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
