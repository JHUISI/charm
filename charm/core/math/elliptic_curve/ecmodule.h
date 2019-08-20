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
 *   @file    ecmodule.h
 *
 *   @brief   charm interface over OpenSSL Ellipic-curve module
 *
 *   @author  ayo.akinyele@charm-crypto.com
 *
 ************************************************************************/

#ifndef ECMODULE_H
#define ECMODULE_H

#include <Python.h>
#include <structmember.h>
#include <longintrepr.h>
#include <math.h>
#include "benchmarkmodule.h"
#include "base64.h"

/* Openssl header files */
#include <openssl/ec.h>
#include <openssl/err.h>
#include <openssl/obj_mac.h>
#include <openssl/objects.h>
#include <openssl/rand.h>
#include <openssl/bn.h>
#include <openssl/sha.h>
#ifdef BENCHMARK_ENABLED
#include "benchmark_util.h"
#endif


//#define DEBUG	1
#define TRUE	1
#define FALSE	0
#define BYTE	8
#define ID_LEN  BYTE
#define BASE_DEC 10
#define BASE_HEX 16
#define MAX_BUF  256
#define RAND_MAX_BYTES	2048
/* Index numbers for different hash functions.  These are all implemented as SHA1(index || message).	*/
#define HASH_FUNCTION_STR_TO_ZR_CRH		10
#define HASH_FUNCTION_STR_TO_G_CRH		11
#define HASH_FUNCTION_KEM_DERIVE		12
#define HASH_LEN						SHA256_DIGEST_LENGTH
#define RESERVED_ENCODING_BYTES			4

PyTypeObject ECType;
PyTypeObject ECGroupType;
PyTypeObject OperationType;
static PyObject *PyECErrorObject;
#define PyEC_Check(obj) PyObject_TypeCheck(obj, &ECType)
#define PyECGroup_Check(obj) PyObject_TypeCheck(obj, &ECGroupType)
enum Group {ZR = 0, G, NONE_G};
typedef enum Group GroupType;

PyMethodDef ECElement_methods[];
PyNumberMethods ecc_number;

#ifdef BENCHMARK_ENABLED
typedef struct {
	PyObject_HEAD
	int op_init;
	int exp_ZR, exp_G;
	int mul_ZR, mul_G;
	int div_ZR, div_G;

	int add_ZR, add_G;
	int sub_ZR, sub_G;
} Operations;
#endif

typedef struct {
	PyObject_HEAD
	EC_GROUP *ec_group;
	int group_init;
	int nid;
	BN_CTX *ctx;
	BIGNUM *order;
#ifdef BENCHMARK_ENABLED
    Benchmark *dBench;
    Operations *gBench;
	uint8_t bench_id[ID_LEN+1];
#endif
} ECGroup;

typedef struct {
	PyObject_HEAD
	GroupType type;
	ECGroup *group;
	EC_POINT *P;
	BIGNUM *elemZ;
	int point_init;
} ECElement;

#if PY_MAJOR_VERSION >= 3
#define PyLong_ToUnsignedLong(o) PyLong_AsUnsignedLong(o)
#define PyLongCheck(o) PyLong_Check(o)
#else
#define PyLong_ToUnsignedLong(o) PyInt_AsUnsignedLongMask(o)
#define PyLongCheck(o) PyInt_Check(o) || PyLong_Check(o)
#endif

#define ErrorMsg(msg) \
	PyErr_SetString(PyECErrorObject, msg); \
	debug("%s: %d error occured here!", __FUNCTION__, __LINE__); \
	return NULL;

#define Check_Types2(o1, o2, lhs, rhs, foundLHS, foundRHS)  \
	if(PyEC_Check(o1)) { \
		lhs = (ECElement *) o1; \
		debug("found a lhs object.\n"); \
    } \
	else if(PyLongCheck(o1)) { \
		foundLHS = TRUE;  }		\
	else  {  ErrorMsg("invalid type specified.");    \
		}				\
	if(PyEC_Check(o2)) {  \
		rhs = (ECElement *) o2; \
		debug("found a rhs object.\n"); \
    } \
	else if(PyLongCheck(o2)) {  \
		foundRHS = TRUE; }		\
	else  {  ErrorMsg("invalid type specified.");   \
		}

#define Group_NULL(obj) if(obj->ec_group == NULL) {  \
	PyErr_SetString(PyECErrorObject, "group object not allocated."); \
	return NULL;    }

#define VERIFY_GROUP(obj) \
	if(!PyECGroup_Check(obj))  {  \
		PyErr_SetString(PyECErrorObject, "not an ecc object."); return NULL; } \
	if(obj->group_init == FALSE || obj->ec_group == NULL) { \
		PyErr_SetString(PyECErrorObject, "group object not initialized.");   \
	return NULL;	}

#define Point_Init(obj) if(!obj->point_init) {  	\
	printf("ERROR: element not initialized.\n");		\
	return NULL;  }

#define isPoint(a) a->type == G
#define ElementG(a, b) a->type == G && b->type == G
#define ElementZR(a, b) a->type == ZR && b->type == ZR

void setBigNum(PyLongObject *obj, BIGNUM **value);
PyObject *ECElement_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
int ECElement_init(ECElement *self, PyObject *args, PyObject *kwds);
PyObject *ECElement_call(ECElement *intObject, PyObject *args, PyObject *kwds);
PyObject *ECElement_print(ECElement *self);
void	ECElement_dealloc(ECElement* self);

ECElement *negatePoint(ECElement *self);
ECElement *invertECElement(ECElement *self);
int hash_to_bytes(uint8_t *input_buf, int input_len, uint8_t *output_buf, int hash_len, uint8_t hash_prefix);
void set_element_from_hash(ECElement *self, uint8_t *input, int input_len);

#define EXIT_IF(check, msg) \
	if(check) { 						\
	PyErr_SetString(PyECErrorObject, msg); \
	return NULL;	}


#ifdef BENCHMARK_ENABLED

#define IS_SAME_GROUP(a, b) \
	if(a->group->nid != b->group->nid) {	\
		PyErr_SetString(PyECErrorObject, "mixing group elements from different curves.");	\
		return NULL;	\
	} 	\
	if(strncmp((const char *) a->group->bench_id, (const char *) b->group->bench_id, ID_LEN) != 0) { \
		PyErr_SetString(PyECErrorObject, "mixing benchmark objects not allowed.");	\
		return NULL;	\
	}

#define IsBenchSet(obj)  obj->dBench != NULL

#define Update_Op(name, op_type, elem_type, bench_obj)	\
	Op_ ##name(op_type, elem_type, ZR, bench_obj)	\
	Op_ ##name(op_type, elem_type, G, bench_obj)	\

#define CLEAR_ALLDBENCH(bench_obj)  \
	    CLEAR_DBENCH(bench_obj, ZR);	\
	    CLEAR_DBENCH(bench_obj, G);

#else

#define IS_SAME_GROUP(a, b) \
	if(a->group->nid != b->group->nid) {	\
		PyErr_SetString(PyECErrorObject, "mixing group elements from different curves.");	\
		return NULL;	\
	}

#define UPDATE_BENCH(op_type, elem_type, bench_obj)  /* ... */
// #define UPDATE_BENCHMARK(op_type, bench_obj)  /* ... */
#define CLEAR_ALLDBENCH(bench_obj) /* ... */
#define GetField(count, type, group, bench_obj)  /* ... */

#endif



#endif
