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
 *   @file    integermodule.h
 *
 *   @brief   charm interface over GMP multi-precision integers
 *
 *   @author  ayo.akinyele@charm-crypto.com
 *
 ************************************************************************/

#ifndef INTEGERMODULE_H
#define INTEGERMODULE_H

#include <Python.h>
#include <stdio.h>
#include <string.h>
#include <structmember.h>
#include <longintrepr.h>				/* for conversions */
#include <math.h>
#include <string.h>
#include <gmp.h>
#include "benchmarkmodule.h"
#include "base64.h"
/* used to initialize the RNG */
#include <openssl/objects.h>
#include <openssl/rand.h>
#include <openssl/bn.h>
#include <openssl/sha.h>

/* integermath */
#define MAX_RUN  	25
#define HASH_LEN 	SHA256_DIGEST_LENGTH
#define MSG_LEN  	128

#define ErrorMsg(msg) \
	PyErr_SetString(IntegerError, msg); \
	return NULL;

#if PY_MAJOR_VERSION >= 3

#define Convert_Types(left, right, lhs, rhs, foundLHS, foundRHS, lhs_mpz, rhs_mpz, errorOccured)  \
	if(PyInteger_Check(left)) { \
		lhs = (Integer *) left; } \
	else if(PyLong_Check(left)) { \
		longObjToMPZ(lhs_mpz, left);	\
		foundLHS = TRUE;  } \
	else { errorOccured = TRUE; } \
						\
	if(PyInteger_Check(right)) {  \
		rhs = (Integer *) right; } \
	else if(PyLong_Check(right)) {  \
		longObjToMPZ(rhs_mpz, right);	\
		foundRHS = TRUE;  } \
	else { errorOccured = TRUE; }

#define Convert_Types2(o1, o2, lhs, rhs, foundLHS, foundRHS)  \
	if(PyInteger_Check(o1)) { \
		lhs = (Integer *) o1; } \
	else if(PyLong_Check(o1)) { \
		foundLHS = TRUE;  } \
	else { ErrorMsg("invalid left operand type."); } \
							\
	if(PyInteger_Check(o2)) {  \
		rhs = (Integer *) o2; } \
	else if(PyLong_Check(o2)) {  \
		foundRHS = TRUE; }  \
	else { ErrorMsg("invalid right operand type."); }

#else
/* python 2.x series */
#define Convert_Types(left, right, lhs, rhs, foundLHS, foundRHS, lhs_mpz, rhs_mpz, errorOccured)  \
	if(PyInteger_Check(left)) { \
		lhs = (Integer *) left; } \
	else if(PyLong_Check(left) || PyInt_Check(left)) { \
		PyObject *_left = PyNumber_Long(left); \
		longObjToMPZ(lhs_mpz, _left);	\
		foundLHS = TRUE;  Py_XDECREF(_left); } \
	else { errorOccured = TRUE; } \
						\
	if(PyInteger_Check(right)) {  \
		rhs = (Integer *) right; } \
	else if(PyLong_Check(right) || PyInt_Check(right)) { \
		PyObject *_right = PyNumber_Long(right); \
		longObjToMPZ(rhs_mpz, _right);	\
		foundRHS = TRUE;  Py_XDECREF(_right); } \
	else { errorOccured = TRUE; }

// TODO: revisit o1 & o2 in 2nd if blocks
#define Convert_Types2(o1, o2, lhs, rhs, foundLHS, foundRHS)  \
	if(PyInteger_Check(o1)) { \
		lhs = (Integer *) o1; } \
	else if(PyLong_Check(o1) || PyInt_Check(o1)) { \
		foundLHS = TRUE;  } \
	else { ErrorMsg("invalid left operand type."); } \
							\
	if(PyInteger_Check(o2)) {  \
		rhs = (Integer *) o2; } \
	else if(PyLong_Check(o2) || PyInt_Check(o2)) {  \
		foundRHS = TRUE; }  \
	else { ErrorMsg("invalid right operand type."); }


#endif

//#ifdef BENCHMARK_ENABLED
//static Benchmark *dBench;
//#endif

/* Index numbers for different hash functions.  These are all implemented as SHA1(index || message).	*/
#define HASH_FUNCTION_STR_TO_Zr_CRH		0
#define HASH_FUNCTION_Zr_TO_G1_ROM		1
#define HASH_FUNCTION_KEM_DERIVE		2
#define RAND_MAX_BYTES					2048

// declare global gmp_randstate_t state object. Initialize based on /dev/random if linux
// then make available to all random functions
PyTypeObject IntegerType;
static PyObject *IntegerError;
#define PyInteger_Check(obj) PyObject_TypeCheck(obj, &IntegerType)
#define PyInteger_Init(obj1, obj2) obj1->initialized && obj2->initialized

typedef struct {
	PyObject_HEAD
	mpz_t m;
	mpz_t e;
	int initialized;
} Integer;

PyMethodDef Integer_methods[];
PyNumberMethods integer_number;

void	Integer_dealloc(Integer* self);
PyObject *Integer_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
int Integer_init(Integer *self, PyObject *args, PyObject *kwds);
PyObject *Integer_print(Integer *self);
Integer *createNewInteger(void);
void print_mpz(mpz_t x, int base);
void print_bn_dec(const BIGNUM *bn);

#define EXIT_IF(check, msg) \
	if(check) { 						\
	PyErr_SetString(IntegerError, msg); \
	return NULL;	}


#endif


