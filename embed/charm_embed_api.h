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
 *   @file    charm_embed_api.h
 *
 *   @brief   charm interface for C/C++ applications
 *
 *   @author  ayo.akinyele@charm-crypto.com
 *
 ************************************************************************/

#ifndef CHARM_EMBED_API_H
#define CHARM_EMBED_API_H

#ifndef PY_SSIZE_T_CLEAN
#define PY_SSIZE_T_CLEAN
#endif

#include <gmp.h>
#ifdef __cplusplus
extern "C" {
#endif
#include <Python.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>

#define DEBUG	1

#if defined(BUILD_PAIR) && defined(BUILD_PBC)

//#ifdef __cplusplus
//extern "C" {
//#endif
#include <pbc/pbc.h>
//#ifdef __cplusplus
//}
//#endif

#elif defined(BUILD_EC)

#include "openssl/ec.h"
#include "openssl/err.h"
#include "openssl/obj_mac.h"
#include "openssl/objects.h"
#include "openssl/rand.h"
#include "openssl/bn.h"

#elif defined(BUILD_INT)

#include <gmp.h>

#endif

typedef enum _result_type {
	INTEGER_T = 1,
	EC_T,
	PAIRING_T,
	PYDICT_T,
	PYTUPLE_T,
	PYBYTES_T,
	PYINT_T,
	PYSTR_T,
	NONE_T
} result_t;

#define INTEGER_TYPE  "integer.Element"
#define EC_TYPE		  "elliptic_curve.Element"
#define PAIRING_TYPE  "pairing.Element"
#define PYDICT_TYPE	  "dict"
#define PYTUPLE_TYPE  "tuple"
#define PYBYTES_TYPE  "bytes"
#define PYINT_TYPE	  "int"
#define PYSTR_TYPE	  "str"
#define PYNONE_TYPE   "NoneType"
#define ZR		"0"
#define G1		"1" /* bilinear map specific */
#define G2		"2"
#define GT		"3"
#define G		"1" /* ec specific */

typedef PyObject Charm_t; // user facing abstraction for Python

#ifdef DEBUG
#define debug(...)	printf("DEBUG: "__VA_ARGS__)
#else
#define debug(...)
#endif


/* wrappers to initialize/tear down Python environment & paths */
int InitializeCharm(void);
void CleanupCharm(void);

Charm_t *InitPairingGroup(Charm_t *pModule, const char *param_id);
Charm_t *InitECGroup(Charm_t *pModule, int param_id);
Charm_t *InitIntegerGroup(Charm_t *pModule, int param_id);

Charm_t *InitScheme(const char *class_file, const char *class_name, Charm_t *pObject);
Charm_t *InitAdapter(const char *class_file, const char *class_name, Charm_t *pObject1, Charm_t *pObject2);
Charm_t *CallMethod(Charm_t *pObject, const char *func_name, char *types, ...);

/* retrieve objects inside a Python tuple or list by index number: must decref result */
Charm_t *GetIndex(Charm_t *pObject, int index);
/* retrieve objects inside a Python dictionary by key string: must decref result */
Charm_t *GetDict(Charm_t *pObject, char *key);
result_t getType(PyObject *o);

Charm_t *objectToBytes(Charm_t *object, Charm_t *group);
Charm_t *bytesToObject(Charm_t *object, Charm_t *group);

#define Free Py_XDECREF

// for debug purposes
#define PrintObject(obj) 		\
			{	uint8_t *b;				\
            	result_t r = getType(obj);	\
            	if(obj == NULL) { printf("NULL object.\n"); r = NONE_T; } \
				switch (r)						\
				{								\
					case PYDICT_T:				\
					case PYTUPLE_T:						\
					case PAIRING_T:						\
 						 PyObject_Print(obj, stdout, Py_PRINT_RAW);	\
 						 printf("\n");					\
						break;							\
					case PYSTR_T:						\
					case PYBYTES_T:						\
						b = (uint8_t *) PyBytes_AsString(obj);	\
						printf("bytes :=> '%s'\n", b);			\
						break;									\
					default:									\
						printf("unsupported for argument.\n");	\
						break;									\
				}	}


#ifdef __cplusplus
}
#endif

#endif
