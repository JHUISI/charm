#ifndef PAIRINGMODULE_H
#define PAIRINGMODULE_H

#include <Python.h>
#include <structmember.h>
#include <longintrepr.h>
#include <stdlib.h>
#include <gmp.h>
#include <pbc/pbc.h>
#include "sha1.h"
#include "benchmarkmodule.h"
#include "base64.h"

//#define DEBUG	1
//#define TRUE	1
//#define FALSE	0
#define MAX_LEN 2048
#define HASH_LEN 20
#define MAX_BENCH_OBJECTS	2
// define element_types
enum Group {ZR, G1, G2, GT, NONE_G};
typedef enum Group GroupType;

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
	pairing_t pair_obj;
	int safe;
} Pairing;

typedef struct {
    PyObject_HEAD
	char *params;
	char *param_buf;
//	pairing_ptr pairing;
	Pairing *pairing;
	element_t e;
	GroupType element_type;
    int elem_initialized;
	int safe_pairing_clear;
} Element;

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
		longRHS_o2 = TRUE; }


PyObject *Element_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
int Element_init(Element *self, PyObject *args, PyObject *kwds);
PyObject *Element_print(Element* self);
PyObject *Element_call(Element *elem, PyObject *args, PyObject *kwds);
void	Element_dealloc(Element* self);

PyObject *Apply_pairing(Element *self, PyObject *args);
PyObject *sha1_hash(Element *self, PyObject *args);

#endif
