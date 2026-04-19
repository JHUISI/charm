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
 */

/*
 *   @file    latticemodule.h
 *
 *   @brief   charm interface for lattice-based crypto over NTL
 *
 *   @author  jakinye3@jhu.edu
 *
 ************************************************************************/

#ifndef LATTICEMODULE_H
#define LATTICEMODULE_H

#ifndef PY_SSIZE_T_CLEAN
#define PY_SSIZE_T_CLEAN
#endif

#include <Python.h>
#include <structmember.h>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <vector>
#include <string>
#include <sstream>

// NTL headers
#include <NTL/ZZ.h>
#include <NTL/ZZ_p.h>
#include <NTL/ZZ_pX.h>
#include <NTL/ZZ_pXFactoring.h>
#include <NTL/vector.h>
#include <NTL/mat_ZZ.h>
#include <NTL/LLL.h>

/* NTL doesn't have a dedicated vec_ZZ_pX type, use Vec<ZZ_pX> */
typedef NTL::Vec<NTL::ZZ_pX> vec_ZZ_pX;

// OpenSSL for random and hashing
#include <openssl/rand.h>
#include <openssl/sha.h>
#include <openssl/evp.h>

#ifdef DEBUG
#define debug(...)  printf("DEBUG: " __VA_ARGS__)
#else
#define debug(...)
#endif

/* Element types for lattice group */
enum LatticeType { ZQ = 0, POLY = 1, VEC = 2, MAT = 3 };

/*
 * NTL Context Guard - saves and restores ZZ_p modulus context.
 * NTL uses thread-local global modulus, so we must save/restore
 * around every operation to support multiple LatticeContext objects.
 */
class NTLContextGuard {
    NTL::ZZ_pContext saved;
public:
    NTLContextGuard(const NTL::ZZ& q) {
        saved.save();
        NTL::ZZ_p::init(q);
    }
    ~NTLContextGuard() {
        saved.restore();
    }
};

/*
 * LatticeContext - holds ring parameters R_q = Z_q[X]/(X^n + 1)
 */
typedef struct {
    PyObject_HEAD
    long n;                   /* ring dimension (power of 2) */
    NTL::ZZ *q;              /* modulus */
    NTL::ZZ_pX *modulus;     /* cyclotomic polynomial X^n + 1 */
    int group_init;
} LatticeContext;

/*
 * LatticeElement - a ring element (scalar, polynomial, vector, or matrix)
 */
typedef struct {
    PyObject_HEAD
    LatticeContext *ctx;
    LatticeType elem_type;
    int elem_initialized;
    /* Element storage — only one is active based on elem_type */
    NTL::ZZ_p *zq;           /* ZQ: scalar in Z_q */
    NTL::ZZ_pX *poly;        /* POLY: polynomial in R_q */
    NTL::Vec<NTL::ZZ_pX> *vec; /* VEC: vector of polynomials */
    /* MAT: stored as vec_ZZ_pX with rows * cols layout */
    long mat_rows;
    long mat_cols;
} LatticeElement;

/* Forward declarations */
extern PyTypeObject LatticeContextType;
extern PyTypeObject LatticeElementType;
static PyObject *LatticeError;

#define PyLatticeContext_Check(obj) PyObject_TypeCheck(obj, &LatticeContextType)
#define PyLatticeElement_Check(obj) PyObject_TypeCheck(obj, &LatticeElementType)

/* Helper: reduce polynomial mod (X^n + 1) */
static inline void reduce_mod_cyclotomic(NTL::ZZ_pX &f, const NTL::ZZ_pX &mod) {
    NTL::rem(f, f, mod);
}

/* Helper: create the cyclotomic polynomial X^n + 1 */
static inline NTL::ZZ_pX make_cyclotomic(long n) {
    NTL::ZZ_pX f;
    NTL::SetCoeff(f, 0, 1);
    NTL::SetCoeff(f, n, 1);
    return f;
}

#endif /* LATTICEMODULE_H */
