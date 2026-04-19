/*
 * Charm-Crypto: Lattice module over NTL
 *
 * Provides polynomial ring arithmetic in R_q = Z_q[X]/(X^n + 1)
 * backed by the NTL library.
 *
 * @author jakinye3@jhu.edu
 */

#include "latticemodule.h"

NTL_CLIENT

/*
 * Python 3.13+ made Py_IsFinalizing() public.
 */
#if PY_VERSION_HEX >= 0x030D0000
  #define CHARM_PY_IS_FINALIZING() Py_IsFinalizing()
#else
  #define CHARM_PY_IS_FINALIZING() _Py_IsFinalizing()
#endif

/* Module state for multi-phase init */
struct module_state {
    PyObject *error;
};

#define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))

/* =========================================================
 * LatticeContext: construction and deallocation
 * ========================================================= */

static PyObject *LatticeContext_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    LatticeContext *self = (LatticeContext *)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->n = 0;
        self->q = NULL;
        self->modulus = NULL;
        self->group_init = 0;
    }
    return (PyObject *)self;
}

static int LatticeContext_init(LatticeContext *self, PyObject *args, PyObject *kwds) {
    long n;
    PyObject *q_obj = NULL;
    static const char *kwlist[] = {"n", "q", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "lO", (char**)kwlist, &n, &q_obj))
        return -1;

    /* Validate n is a power of 2 */
    if (n < 4 || (n & (n - 1)) != 0) {
        PyErr_SetString(PyExc_ValueError, "n must be a power of 2 and >= 4");
        return -1;
    }

    /* Parse q as a Python integer */
    if (!PyLong_Check(q_obj)) {
        PyErr_SetString(PyExc_TypeError, "q must be a Python integer");
        return -1;
    }

    /* Convert Python int to NTL ZZ */
    PyObject *q_str = PyObject_Str(q_obj);
    if (!q_str) return -1;
    const char *q_cstr = PyUnicode_AsUTF8(q_str);
    if (!q_cstr) { Py_DECREF(q_str); return -1; }

    self->q = new ZZ();
    conv(*self->q, q_cstr);
    Py_DECREF(q_str);

    if (*self->q < ZZ(2)) {
        PyErr_SetString(PyExc_ValueError, "q must be >= 2");
        delete self->q; self->q = NULL;
        return -1;
    }

    self->n = n;

    /* Initialize NTL context and build cyclotomic modulus */
    ZZ_p::init(*self->q);
    self->modulus = new ZZ_pX(make_cyclotomic(n));
    self->group_init = 1;

    return 0;
}

static void LatticeContext_dealloc(LatticeContext *self) {
    if (self->modulus) { delete self->modulus; self->modulus = NULL; }
    if (self->q) { delete self->q; self->q = NULL; }
    self->group_init = 0;
    Py_TYPE(self)->tp_free((PyObject *)self);
}

/* =========================================================
 * LatticeElement: construction and deallocation
 * ========================================================= */

static PyObject *LatticeElement_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    LatticeElement *self = (LatticeElement *)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->ctx = NULL;
        self->elem_type = ZQ;
        self->elem_initialized = 0;
        self->zq = NULL;
        self->poly = NULL;
        self->vec = NULL;
        self->mat_rows = 0;
        self->mat_cols = 0;
    }
    return (PyObject *)self;
}

static void LatticeElement_dealloc(LatticeElement *self) {
    if (self->elem_initialized) {
        switch (self->elem_type) {
            case ZQ:  if (self->zq)   { delete self->zq;   self->zq = NULL;   } break;
            case POLY: if (self->poly) { delete self->poly; self->poly = NULL; } break;
            case VEC:
            case MAT:  if (self->vec)  { delete self->vec;  self->vec = NULL;  } break;
        }
    }
    Py_XDECREF(self->ctx);
    self->ctx = NULL;
    Py_TYPE(self)->tp_free((PyObject *)self);
}

/* =========================================================
 * Helper: create an element with proper context
 * ========================================================= */

static LatticeElement *createElement(LatticeContext *ctx, LatticeType type) {
    LatticeElement *elem = (LatticeElement *)LatticeElementType.tp_alloc(&LatticeElementType, 0);
    if (elem == NULL) return NULL;
    Py_INCREF(ctx);
    elem->ctx = ctx;
    elem->elem_type = type;
    elem->elem_initialized = 0;
    elem->zq = NULL;
    elem->poly = NULL;
    elem->vec = NULL;
    elem->mat_rows = 0;
    elem->mat_cols = 0;
    return elem;
}

/* =========================================================
 * Arithmetic helpers
 * ========================================================= */

/* Poly * Poly mod (X^n + 1) */
static ZZ_pX poly_mul_mod(const ZZ_pX &a, const ZZ_pX &b, const ZZ_pX &mod) {
    ZZ_pX result;
    MulMod(result, a, b, mod);
    return result;
}

/* Poly + Poly mod (X^n + 1) — addition doesn't increase degree, but reduce anyway */
static ZZ_pX poly_add_mod(const ZZ_pX &a, const ZZ_pX &b, const ZZ_pX &mod) {
    ZZ_pX result = a + b;
    rem(result, result, mod);
    return result;
}

static ZZ_pX poly_sub_mod(const ZZ_pX &a, const ZZ_pX &b, const ZZ_pX &mod) {
    ZZ_pX result = a - b;
    rem(result, result, mod);
    return result;
}

static ZZ_pX poly_neg_mod(const ZZ_pX &a, const ZZ_pX &mod) {
    ZZ_pX result = -a;
    rem(result, result, mod);
    return result;
}

/* =========================================================
 * Python number protocol: nb_add
 * ========================================================= */
static PyObject *Element_add(PyObject *o1, PyObject *o2) {
    if (!PyLatticeElement_Check(o1) || !PyLatticeElement_Check(o2)) {
        PyErr_SetString(PyExc_TypeError, "Both operands must be LatticeElement");
        return NULL;
    }
    LatticeElement *lhs = (LatticeElement *)o1;
    LatticeElement *rhs = (LatticeElement *)o2;

    if (!lhs->elem_initialized || !rhs->elem_initialized) {
        PyErr_SetString(PyExc_ValueError, "Element not initialized");
        return NULL;
    }
    if (lhs->ctx != rhs->ctx && *lhs->ctx->q != *rhs->ctx->q) {
        PyErr_SetString(PyExc_ValueError, "Elements from different rings");
        return NULL;
    }

    NTLContextGuard guard(*lhs->ctx->q);
    LatticeElement *result = NULL;

    if (lhs->elem_type == ZQ && rhs->elem_type == ZQ) {
        result = createElement(lhs->ctx, ZQ);
        if (!result) return NULL;
        result->zq = new ZZ_p(*lhs->zq + *rhs->zq);
        result->elem_initialized = 1;
    }
    else if (lhs->elem_type == POLY && rhs->elem_type == POLY) {
        result = createElement(lhs->ctx, POLY);
        if (!result) return NULL;
        result->poly = new ZZ_pX(poly_add_mod(*lhs->poly, *rhs->poly, *lhs->ctx->modulus));
        result->elem_initialized = 1;
    }
    else if ((lhs->elem_type == VEC && rhs->elem_type == VEC) ||
             (lhs->elem_type == MAT && rhs->elem_type == MAT)) {
        if (lhs->vec->length() != rhs->vec->length()) {
            PyErr_SetString(PyExc_ValueError, "Vector/matrix dimension mismatch");
            return NULL;
        }
        LatticeType rtype = lhs->elem_type;
        result = createElement(lhs->ctx, rtype);
        if (!result) return NULL;
        long len = lhs->vec->length();
        result->vec = new vec_ZZ_pX();
        result->vec->SetLength(len);
        for (long i = 0; i < len; i++) {
            (*result->vec)[i] = poly_add_mod((*lhs->vec)[i], (*rhs->vec)[i], *lhs->ctx->modulus);
        }
        result->mat_rows = lhs->mat_rows;
        result->mat_cols = lhs->mat_cols;
        result->elem_initialized = 1;
    }
    else {
        PyErr_SetString(PyExc_TypeError, "Incompatible element types for addition");
        return NULL;
    }

    return (PyObject *)result;
}

/* nb_subtract */
static PyObject *Element_sub(PyObject *o1, PyObject *o2) {
    if (!PyLatticeElement_Check(o1) || !PyLatticeElement_Check(o2)) {
        PyErr_SetString(PyExc_TypeError, "Both operands must be LatticeElement");
        return NULL;
    }
    LatticeElement *lhs = (LatticeElement *)o1;
    LatticeElement *rhs = (LatticeElement *)o2;

    if (!lhs->elem_initialized || !rhs->elem_initialized) {
        PyErr_SetString(PyExc_ValueError, "Element not initialized");
        return NULL;
    }

    NTLContextGuard guard(*lhs->ctx->q);
    LatticeElement *result = NULL;

    if (lhs->elem_type == ZQ && rhs->elem_type == ZQ) {
        result = createElement(lhs->ctx, ZQ);
        if (!result) return NULL;
        result->zq = new ZZ_p(*lhs->zq - *rhs->zq);
        result->elem_initialized = 1;
    }
    else if (lhs->elem_type == POLY && rhs->elem_type == POLY) {
        result = createElement(lhs->ctx, POLY);
        if (!result) return NULL;
        result->poly = new ZZ_pX(poly_sub_mod(*lhs->poly, *rhs->poly, *lhs->ctx->modulus));
        result->elem_initialized = 1;
    }
    else if ((lhs->elem_type == VEC && rhs->elem_type == VEC) ||
             (lhs->elem_type == MAT && rhs->elem_type == MAT)) {
        if (lhs->vec->length() != rhs->vec->length()) {
            PyErr_SetString(PyExc_ValueError, "Vector/matrix dimension mismatch");
            return NULL;
        }
        LatticeType rtype = lhs->elem_type;
        result = createElement(lhs->ctx, rtype);
        if (!result) return NULL;
        long len = lhs->vec->length();
        result->vec = new vec_ZZ_pX();
        result->vec->SetLength(len);
        for (long i = 0; i < len; i++) {
            (*result->vec)[i] = poly_sub_mod((*lhs->vec)[i], (*rhs->vec)[i], *lhs->ctx->modulus);
        }
        result->mat_rows = lhs->mat_rows;
        result->mat_cols = lhs->mat_cols;
        result->elem_initialized = 1;
    }
    else {
        PyErr_SetString(PyExc_TypeError, "Incompatible element types for subtraction");
        return NULL;
    }

    return (PyObject *)result;
}

/* nb_multiply — supports cross-type: POLY*ZQ, MAT*VEC, etc. */
static PyObject *Element_mul(PyObject *o1, PyObject *o2) {
    /* Handle Python int * Element */
    if (PyLong_Check(o1) && PyLatticeElement_Check(o2)) {
        PyObject *tmp = o1; o1 = o2; o2 = tmp;
    }
    if (!PyLatticeElement_Check(o1)) {
        PyErr_SetString(PyExc_TypeError, "Operand must be LatticeElement");
        return NULL;
    }
    LatticeElement *lhs = (LatticeElement *)o1;
    if (!lhs->elem_initialized) {
        PyErr_SetString(PyExc_ValueError, "Element not initialized");
        return NULL;
    }

    NTLContextGuard guard(*lhs->ctx->q);

    /* Scalar multiply by Python int */
    if (PyLong_Check(o2)) {
        long scalar = PyLong_AsLong(o2);
        if (scalar == -1 && PyErr_Occurred()) return NULL;
        ZZ_p s = to_ZZ_p(to_ZZ(scalar));

        if (lhs->elem_type == POLY) {
            LatticeElement *result = createElement(lhs->ctx, POLY);
            if (!result) return NULL;
            result->poly = new ZZ_pX(*lhs->poly * s);
            rem(*result->poly, *result->poly, *lhs->ctx->modulus);
            result->elem_initialized = 1;
            return (PyObject *)result;
        }
        else if (lhs->elem_type == ZQ) {
            LatticeElement *result = createElement(lhs->ctx, ZQ);
            if (!result) return NULL;
            result->zq = new ZZ_p(*lhs->zq * s);
            result->elem_initialized = 1;
            return (PyObject *)result;
        }
    }

    if (!PyLatticeElement_Check(o2)) {
        PyErr_SetString(PyExc_TypeError, "Operand must be LatticeElement or int");
        return NULL;
    }
    LatticeElement *rhs = (LatticeElement *)o2;
    if (!rhs->elem_initialized) {
        PyErr_SetString(PyExc_ValueError, "Element not initialized");
        return NULL;
    }

    /* POLY * POLY */
    if (lhs->elem_type == POLY && rhs->elem_type == POLY) {
        LatticeElement *result = createElement(lhs->ctx, POLY);
        if (!result) return NULL;
        result->poly = new ZZ_pX(poly_mul_mod(*lhs->poly, *rhs->poly, *lhs->ctx->modulus));
        result->elem_initialized = 1;
        return (PyObject *)result;
    }
    /* ZQ * ZQ */
    if (lhs->elem_type == ZQ && rhs->elem_type == ZQ) {
        LatticeElement *result = createElement(lhs->ctx, ZQ);
        if (!result) return NULL;
        result->zq = new ZZ_p(*lhs->zq * *rhs->zq);
        result->elem_initialized = 1;
        return (PyObject *)result;
    }
    /* POLY * ZQ or ZQ * POLY — scalar multiply */
    if ((lhs->elem_type == POLY && rhs->elem_type == ZQ) ||
        (lhs->elem_type == ZQ && rhs->elem_type == POLY)) {
        LatticeElement *p = (lhs->elem_type == POLY) ? lhs : rhs;
        LatticeElement *s = (lhs->elem_type == ZQ) ? lhs : rhs;
        LatticeElement *result = createElement(lhs->ctx, POLY);
        if (!result) return NULL;
        result->poly = new ZZ_pX(*p->poly * *s->zq);
        rem(*result->poly, *result->poly, *lhs->ctx->modulus);
        result->elem_initialized = 1;
        return (PyObject *)result;
    }
    /* MAT * VEC — matrix-vector multiply */
    if (lhs->elem_type == MAT && rhs->elem_type == VEC) {
        if (lhs->mat_cols != rhs->vec->length()) {
            PyErr_SetString(PyExc_ValueError, "Matrix cols != vector length");
            return NULL;
        }
        LatticeElement *result = createElement(lhs->ctx, VEC);
        if (!result) return NULL;
        long rows = lhs->mat_rows, cols = lhs->mat_cols;
        result->vec = new vec_ZZ_pX();
        result->vec->SetLength(rows);
        for (long i = 0; i < rows; i++) {
            ZZ_pX acc;
            for (long j = 0; j < cols; j++) {
                ZZ_pX tmp = poly_mul_mod((*lhs->vec)[i * cols + j], (*rhs->vec)[j], *lhs->ctx->modulus);
                acc += tmp;
            }
            rem(acc, acc, *lhs->ctx->modulus);
            (*result->vec)[i] = acc;
        }
        result->elem_initialized = 1;
        return (PyObject *)result;
    }
    /* VEC inner product (component-wise multiply for same-length vectors) */
    if (lhs->elem_type == VEC && rhs->elem_type == VEC) {
        if (lhs->vec->length() != rhs->vec->length()) {
            PyErr_SetString(PyExc_ValueError, "Vector dimension mismatch");
            return NULL;
        }
        /* Inner product: result is a POLY */
        LatticeElement *result = createElement(lhs->ctx, POLY);
        if (!result) return NULL;
        ZZ_pX acc;
        for (long i = 0; i < lhs->vec->length(); i++) {
            ZZ_pX tmp = poly_mul_mod((*lhs->vec)[i], (*rhs->vec)[i], *lhs->ctx->modulus);
            acc += tmp;
        }
        rem(acc, acc, *lhs->ctx->modulus);
        result->poly = new ZZ_pX(acc);
        result->elem_initialized = 1;
        return (PyObject *)result;
    }

    /* VEC * POLY or POLY * VEC — componentwise scalar multiply */
    if ((lhs->elem_type == VEC && rhs->elem_type == POLY) ||
        (lhs->elem_type == POLY && rhs->elem_type == VEC)) {
        LatticeElement *v = (lhs->elem_type == VEC) ? lhs : rhs;
        LatticeElement *p = (lhs->elem_type == POLY) ? lhs : rhs;
        LatticeElement *result = createElement(lhs->ctx, VEC);
        if (!result) return NULL;
        long len = v->vec->length();
        result->vec = new vec_ZZ_pX();
        result->vec->SetLength(len);
        for (long i = 0; i < len; i++) {
            (*result->vec)[i] = poly_mul_mod((*v->vec)[i], *p->poly, *lhs->ctx->modulus);
        }
        result->elem_initialized = 1;
        return (PyObject *)result;
    }

    PyErr_SetString(PyExc_TypeError, "Incompatible element types for multiplication");
    return NULL;
}

/* nb_negative */
static PyObject *Element_neg(PyObject *o1) {
    if (!PyLatticeElement_Check(o1)) {
        PyErr_SetString(PyExc_TypeError, "Operand must be LatticeElement");
        return NULL;
    }
    LatticeElement *self = (LatticeElement *)o1;
    if (!self->elem_initialized) {
        PyErr_SetString(PyExc_ValueError, "Element not initialized");
        return NULL;
    }

    NTLContextGuard guard(*self->ctx->q);
    LatticeElement *result = NULL;

    if (self->elem_type == ZQ) {
        result = createElement(self->ctx, ZQ);
        if (!result) return NULL;
        result->zq = new ZZ_p(-(*self->zq));
        result->elem_initialized = 1;
    }
    else if (self->elem_type == POLY) {
        result = createElement(self->ctx, POLY);
        if (!result) return NULL;
        result->poly = new ZZ_pX(poly_neg_mod(*self->poly, *self->ctx->modulus));
        result->elem_initialized = 1;
    }
    else if (self->elem_type == VEC || self->elem_type == MAT) {
        result = createElement(self->ctx, self->elem_type);
        if (!result) return NULL;
        long len = self->vec->length();
        result->vec = new vec_ZZ_pX();
        result->vec->SetLength(len);
        for (long i = 0; i < len; i++) {
            (*result->vec)[i] = poly_neg_mod((*self->vec)[i], *self->ctx->modulus);
        }
        result->mat_rows = self->mat_rows;
        result->mat_cols = self->mat_cols;
        result->elem_initialized = 1;
    }
    return (PyObject *)result;
}

/* Element equality */
static PyObject *Element_equals(PyObject *o1, PyObject *o2, int op) {
    if (op != Py_EQ && op != Py_NE) {
        Py_RETURN_NOTIMPLEMENTED;
    }
    if (!PyLatticeElement_Check(o1) || !PyLatticeElement_Check(o2)) {
        Py_RETURN_NOTIMPLEMENTED;
    }
    LatticeElement *lhs = (LatticeElement *)o1;
    LatticeElement *rhs = (LatticeElement *)o2;
    if (!lhs->elem_initialized || !rhs->elem_initialized) {
        if (op == Py_EQ) Py_RETURN_FALSE;
        Py_RETURN_TRUE;
    }
    if (lhs->elem_type != rhs->elem_type) {
        if (op == Py_EQ) Py_RETURN_FALSE;
        Py_RETURN_TRUE;
    }

    NTLContextGuard guard(*lhs->ctx->q);
    int equal = 0;
    switch (lhs->elem_type) {
        case ZQ:  equal = (*lhs->zq == *rhs->zq); break;
        case POLY: equal = (*lhs->poly == *rhs->poly); break;
        case VEC:
        case MAT:
            if (lhs->vec->length() != rhs->vec->length()) { equal = 0; break; }
            equal = 1;
            for (long i = 0; i < lhs->vec->length(); i++) {
                if ((*lhs->vec)[i] != (*rhs->vec)[i]) { equal = 0; break; }
            }
            break;
    }
    if (op == Py_EQ) { if (equal) Py_RETURN_TRUE; else Py_RETURN_FALSE; }
    else             { if (!equal) Py_RETURN_TRUE; else Py_RETURN_FALSE; }
}

/* Element repr */
static PyObject *Element_repr(PyObject *o) {
    LatticeElement *self = (LatticeElement *)o;
    if (!self->elem_initialized) {
        return PyUnicode_FromString("<LatticeElement: uninitialized>");
    }
    NTLContextGuard guard(*self->ctx->q);
    std::ostringstream oss;
    switch (self->elem_type) {
        case ZQ:
            oss << "ZQ(" << *self->zq << ")";
            break;
        case POLY: {
            oss << "POLY(";
            long d = deg(*self->poly);
            for (long i = 0; i <= d && i < 8; i++) {
                if (i > 0) oss << ", ";
                oss << coeff(*self->poly, i);
            }
            if (d >= 8) oss << ", ...";
            oss << ")";
            break;
        }
        case VEC:
            oss << "VEC(len=" << self->vec->length() << ")";
            break;
        case MAT:
            oss << "MAT(" << self->mat_rows << "x" << self->mat_cols << ")";
            break;
    }
    return PyUnicode_FromString(oss.str().c_str());
}

/* =========================================================
 * Module-level functions
 * ========================================================= */

/* random(ctx, type) -> LatticeElement */
static PyObject *Lattice_random(PyObject *self, PyObject *args) {
    LatticeContext *ctx;
    int type;
    if (!PyArg_ParseTuple(args, "Oi", &ctx, &type))
        return NULL;
    if (!PyLatticeContext_Check((PyObject*)ctx) || !ctx->group_init) {
        PyErr_SetString(PyExc_TypeError, "First arg must be an initialized LatticeContext");
        return NULL;
    }

    NTLContextGuard guard(*ctx->q);

    if (type == ZQ) {
        LatticeElement *elem = createElement(ctx, ZQ);
        if (!elem) return NULL;
        elem->zq = new ZZ_p(random_ZZ_p());
        elem->elem_initialized = 1;
        return (PyObject *)elem;
    }
    else if (type == POLY) {
        LatticeElement *elem = createElement(ctx, POLY);
        if (!elem) return NULL;
        elem->poly = new ZZ_pX();
        random(*elem->poly, ctx->n);
        elem->elem_initialized = 1;
        return (PyObject *)elem;
    }
    PyErr_SetString(PyExc_ValueError, "Type must be ZQ (0) or POLY (1)");
    return NULL;
}

/* random_vec(ctx, k) -> VEC of k random polynomials */
static PyObject *Lattice_random_vec(PyObject *self, PyObject *args) {
    LatticeContext *ctx;
    long k;
    if (!PyArg_ParseTuple(args, "Ol", &ctx, &k))
        return NULL;
    if (!PyLatticeContext_Check((PyObject*)ctx) || !ctx->group_init) {
        PyErr_SetString(PyExc_TypeError, "First arg must be an initialized LatticeContext");
        return NULL;
    }
    if (k < 1) {
        PyErr_SetString(PyExc_ValueError, "k must be >= 1");
        return NULL;
    }

    NTLContextGuard guard(*ctx->q);
    LatticeElement *elem = createElement(ctx, VEC);
    if (!elem) return NULL;
    elem->vec = new vec_ZZ_pX();
    elem->vec->SetLength(k);
    for (long i = 0; i < k; i++) {
        ZZ_pX p;
        random(p, ctx->n);
        (*elem->vec)[i] = p;
    }
    elem->elem_initialized = 1;
    return (PyObject *)elem;
}

/* random_mat(ctx, rows, cols) -> MAT of random polynomials */
static PyObject *Lattice_random_mat(PyObject *self, PyObject *args) {
    LatticeContext *ctx;
    long rows, cols;
    if (!PyArg_ParseTuple(args, "Oll", &ctx, &rows, &cols))
        return NULL;
    if (!PyLatticeContext_Check((PyObject*)ctx) || !ctx->group_init) {
        PyErr_SetString(PyExc_TypeError, "First arg must be an initialized LatticeContext");
        return NULL;
    }

    NTLContextGuard guard(*ctx->q);
    LatticeElement *elem = createElement(ctx, MAT);
    if (!elem) return NULL;
    elem->vec = new vec_ZZ_pX();
    elem->vec->SetLength(rows * cols);
    for (long i = 0; i < rows * cols; i++) {
        ZZ_pX p;
        random(p, ctx->n);
        (*elem->vec)[i] = p;
    }
    elem->mat_rows = rows;
    elem->mat_cols = cols;
    elem->elem_initialized = 1;
    return (PyObject *)elem;
}

/* gaussian(ctx, type, sigma) -> element with discrete Gaussian coefficients */
static PyObject *Lattice_gaussian(PyObject *self, PyObject *args) {
    LatticeContext *ctx;
    int type;
    double sigma;
    if (!PyArg_ParseTuple(args, "Oid", &ctx, &type, &sigma))
        return NULL;
    if (!PyLatticeContext_Check((PyObject*)ctx) || !ctx->group_init) {
        PyErr_SetString(PyExc_TypeError, "First arg must be an initialized LatticeContext");
        return NULL;
    }
    if (sigma <= 0.0) {
        PyErr_SetString(PyExc_ValueError, "sigma must be positive");
        return NULL;
    }

    NTLContextGuard guard(*ctx->q);

    /* CDT (Cumulative Distribution Table) discrete Gaussian sampling.
     * Precompute CDF once, then binary search for each sample. */
    long bound = (long)(6.0 * sigma + 1.0);
    long table_size = 2 * bound + 1;
    std::vector<double> cdt(table_size);
    double norm = 0.0;
    double two_sigma_sq = 2.0 * sigma * sigma;
    for (long i = 0; i < table_size; i++) {
        long x = i - bound;
        double w = exp(-(double)(x * x) / two_sigma_sq);
        norm += w;
        cdt[i] = norm;
    }
    /* Normalize to [0, 1] */
    for (long i = 0; i < table_size; i++) cdt[i] /= norm;

    auto sample_gaussian = [&]() -> long {
        unsigned char rand_bytes[8];
        RAND_bytes(rand_bytes, 8);
        unsigned long r = 0;
        for (int i = 0; i < 8; i++) r = (r << 8) | rand_bytes[i];
        double u = (double)r / (double)ULONG_MAX;
        /* Binary search in CDF table */
        long lo = 0, hi = table_size - 1;
        while (lo < hi) {
            long mid = (lo + hi) / 2;
            if (cdt[mid] < u) lo = mid + 1;
            else hi = mid;
        }
        return lo - bound;
    };

    if (type == POLY) {
        LatticeElement *elem = createElement(ctx, POLY);
        if (!elem) return NULL;
        elem->poly = new ZZ_pX();
        for (long i = 0; i < ctx->n; i++) {
            long coef = sample_gaussian();
            SetCoeff(*elem->poly, i, to_ZZ_p(to_ZZ(coef)));
        }
        elem->elem_initialized = 1;
        return (PyObject *)elem;
    }
    PyErr_SetString(PyExc_ValueError, "Gaussian sampling only supported for POLY type");
    return NULL;
}

/* gaussian_vec(ctx, k, sigma) -> VEC of k Gaussian polynomials */
static PyObject *Lattice_gaussian_vec(PyObject *self, PyObject *args) {
    LatticeContext *ctx;
    long k;
    double sigma;
    if (!PyArg_ParseTuple(args, "Old", &ctx, &k, &sigma))
        return NULL;
    if (!PyLatticeContext_Check((PyObject*)ctx) || !ctx->group_init) {
        PyErr_SetString(PyExc_TypeError, "First arg must be an initialized LatticeContext");
        return NULL;
    }
    if (k < 1 || sigma <= 0.0) {
        PyErr_SetString(PyExc_ValueError, "k must be >= 1 and sigma must be positive");
        return NULL;
    }

    /* Create k Gaussian polynomials */
    PyObject *vec_args = Py_BuildValue("(Oid)", ctx, (int)POLY, sigma);
    if (!vec_args) return NULL;

    NTLContextGuard guard(*ctx->q);
    LatticeElement *result = createElement(ctx, VEC);
    if (!result) { Py_DECREF(vec_args); return NULL; }
    result->vec = new vec_ZZ_pX();
    result->vec->SetLength(k);

    for (long i = 0; i < k; i++) {
        PyObject *p = Lattice_gaussian(self, vec_args);
        if (!p) { Py_DECREF(vec_args); Py_DECREF(result); return NULL; }
        (*result->vec)[i] = *((LatticeElement *)p)->poly;
        Py_DECREF(p);
    }
    Py_DECREF(vec_args);
    result->elem_initialized = 1;
    return (PyObject *)result;
}

/* hash(ctx, data, type) -> LatticeElement from hash of bytes */
static PyObject *Lattice_hash(PyObject *self, PyObject *args) {
    LatticeContext *ctx;
    const char *data;
    Py_ssize_t data_len;
    int type;
    if (!PyArg_ParseTuple(args, "Os#i", &ctx, &data, &data_len, &type))
        return NULL;
    if (!PyLatticeContext_Check((PyObject*)ctx) || !ctx->group_init) {
        PyErr_SetString(PyExc_TypeError, "First arg must be an initialized LatticeContext");
        return NULL;
    }

    NTLContextGuard guard(*ctx->q);

    /* Helper: compute SHA-256(data || counter) */
    auto sha256_with_counter = [](const char *data, Py_ssize_t len, uint32_t counter, unsigned char out[32]) {
        SHA256_CTX sha_ctx;
        SHA256_Init(&sha_ctx);
        SHA256_Update(&sha_ctx, data, len);
        unsigned char ctr[4] = {(unsigned char)(counter & 0xFF), (unsigned char)((counter >> 8) & 0xFF),
                                 (unsigned char)((counter >> 16) & 0xFF), (unsigned char)((counter >> 24) & 0xFF)};
        SHA256_Update(&sha_ctx, ctr, 4);
        SHA256_Final(out, &sha_ctx);
    };

    if (type == POLY) {
        LatticeElement *elem = createElement(ctx, POLY);
        if (!elem) return NULL;
        elem->poly = new ZZ_pX();
        for (long i = 0; i < ctx->n; i++) {
            unsigned char hbuf[32];
            sha256_with_counter(data, data_len, (uint32_t)i, hbuf);
            ZZ val = ZZFromBytes(hbuf, 32);
            val %= *ctx->q;
            SetCoeff(*elem->poly, i, to_ZZ_p(val));
        }
        elem->elem_initialized = 1;
        return (PyObject *)elem;
    }
    else if (type == ZQ) {
        LatticeElement *elem = createElement(ctx, ZQ);
        if (!elem) return NULL;
        unsigned char hbuf[32];
        sha256_with_counter(data, data_len, 0, hbuf);
        ZZ val = ZZFromBytes(hbuf, 32);
        val %= *ctx->q;
        elem->zq = new ZZ_p(to_ZZ_p(val));
        elem->elem_initialized = 1;
        return (PyObject *)elem;
    }
    PyErr_SetString(PyExc_ValueError, "hash type must be ZQ or POLY");
    return NULL;
}

/* serialize(ctx, element) -> bytes */
static PyObject *Lattice_serialize(PyObject *self, PyObject *args) {
    LatticeContext *ctx;
    LatticeElement *elem;
    if (!PyArg_ParseTuple(args, "OO", &ctx, &elem))
        return NULL;
    if (!PyLatticeElement_Check((PyObject*)elem) || !elem->elem_initialized) {
        PyErr_SetString(PyExc_TypeError, "Second arg must be an initialized LatticeElement");
        return NULL;
    }

    NTLContextGuard guard(*elem->ctx->q);
    std::ostringstream oss;
    oss << (int)elem->elem_type << "|";

    switch (elem->elem_type) {
        case ZQ:
            oss << *elem->zq;
            break;
        case POLY:
            oss << *elem->poly;
            break;
        case VEC:
            oss << elem->vec->length() << "|";
            for (long i = 0; i < elem->vec->length(); i++) {
                oss << (*elem->vec)[i];
                if (i < elem->vec->length() - 1) oss << "|";
            }
            break;
        case MAT:
            oss << elem->mat_rows << "|" << elem->mat_cols << "|";
            for (long i = 0; i < elem->vec->length(); i++) {
                oss << (*elem->vec)[i];
                if (i < elem->vec->length() - 1) oss << "|";
            }
            break;
    }
    std::string s = oss.str();
    return PyBytes_FromStringAndSize(s.c_str(), s.size());
}

/* deserialize(ctx, bytes) -> element */
static PyObject *Lattice_deserialize(PyObject *self, PyObject *args) {
    LatticeContext *ctx;
    const char *data;
    Py_ssize_t data_len;
    if (!PyArg_ParseTuple(args, "Os#", &ctx, &data, &data_len))
        return NULL;
    if (!PyLatticeContext_Check((PyObject*)ctx) || !ctx->group_init) {
        PyErr_SetString(PyExc_TypeError, "First arg must be an initialized LatticeContext");
        return NULL;
    }

    NTLContextGuard guard(*ctx->q);
    std::string s(data, data_len);
    std::istringstream iss(s);

    int type;
    char sep;
    iss >> type >> sep;
    if (sep != '|') {
        PyErr_SetString(PyExc_ValueError, "Invalid serialized format");
        return NULL;
    }

    if (type == ZQ) {
        LatticeElement *elem = createElement(ctx, ZQ);
        if (!elem) return NULL;
        elem->zq = new ZZ_p();
        iss >> *elem->zq;
        elem->elem_initialized = 1;
        return (PyObject *)elem;
    }
    else if (type == POLY) {
        LatticeElement *elem = createElement(ctx, POLY);
        if (!elem) return NULL;
        elem->poly = new ZZ_pX();
        iss >> *elem->poly;
        elem->elem_initialized = 1;
        return (PyObject *)elem;
    }
    else if (type == VEC) {
        long len;
        iss >> len >> sep;
        LatticeElement *elem = createElement(ctx, VEC);
        if (!elem) return NULL;
        elem->vec = new vec_ZZ_pX();
        elem->vec->SetLength(len);
        for (long i = 0; i < len; i++) {
            iss >> (*elem->vec)[i];
            if (i < len - 1) iss >> sep;
        }
        elem->elem_initialized = 1;
        return (PyObject *)elem;
    }
    else if (type == MAT) {
        long rows, cols;
        iss >> rows >> sep >> cols >> sep;
        LatticeElement *elem = createElement(ctx, MAT);
        if (!elem) return NULL;
        elem->mat_rows = rows;
        elem->mat_cols = cols;
        elem->vec = new vec_ZZ_pX();
        elem->vec->SetLength(rows * cols);
        for (long i = 0; i < rows * cols; i++) {
            iss >> (*elem->vec)[i];
            if (i < rows * cols - 1) iss >> sep;
        }
        elem->elem_initialized = 1;
        return (PyObject *)elem;
    }

    PyErr_SetString(PyExc_ValueError, "Unknown element type in serialized data");
    return NULL;
}

/* ismember(ctx, element) -> bool */
static PyObject *Lattice_ismember(PyObject *self, PyObject *args) {
    LatticeContext *ctx;
    LatticeElement *elem;
    if (!PyArg_ParseTuple(args, "OO", &ctx, &elem))
        return NULL;
    if (!PyLatticeElement_Check((PyObject*)elem)) {
        Py_RETURN_FALSE;
    }
    if (!elem->elem_initialized) {
        Py_RETURN_FALSE;
    }
    /* Check context matches */
    if (elem->ctx != ctx && *elem->ctx->q != *ctx->q) {
        Py_RETURN_FALSE;
    }
    /* Check polynomial degree < n */
    NTLContextGuard guard(*ctx->q);
    if (elem->elem_type == POLY) {
        if (deg(*elem->poly) >= ctx->n) {
            Py_RETURN_FALSE;
        }
    }
    else if (elem->elem_type == VEC || elem->elem_type == MAT) {
        for (long i = 0; i < elem->vec->length(); i++) {
            if (deg((*elem->vec)[i]) >= ctx->n) {
                Py_RETURN_FALSE;
            }
        }
    }
    Py_RETURN_TRUE;
}

/* order(ctx) -> q as Python int */
static PyObject *Lattice_order(PyObject *self, PyObject *args) {
    LatticeContext *ctx;
    if (!PyArg_ParseTuple(args, "O", &ctx))
        return NULL;
    if (!PyLatticeContext_Check((PyObject*)ctx) || !ctx->group_init) {
        PyErr_SetString(PyExc_TypeError, "Arg must be an initialized LatticeContext");
        return NULL;
    }
    std::ostringstream oss;
    oss << *ctx->q;
    return PyLong_FromString(oss.str().c_str(), NULL, 10);
}

/* degree(ctx) -> n as Python int */
static PyObject *Lattice_degree(PyObject *self, PyObject *args) {
    LatticeContext *ctx;
    if (!PyArg_ParseTuple(args, "O", &ctx))
        return NULL;
    if (!PyLatticeContext_Check((PyObject*)ctx) || !ctx->group_init) {
        PyErr_SetString(PyExc_TypeError, "Arg must be an initialized LatticeContext");
        return NULL;
    }
    return PyLong_FromLong(ctx->n);
}

/* encode(ctx, bytes) -> POLY with bits embedded as floor(q/2)-scaled coefficients */
static PyObject *Lattice_encode(PyObject *self, PyObject *args) {
    LatticeContext *ctx;
    const char *data;
    Py_ssize_t data_len;
    if (!PyArg_ParseTuple(args, "Os#", &ctx, &data, &data_len))
        return NULL;
    if (!PyLatticeContext_Check((PyObject*)ctx) || !ctx->group_init) {
        PyErr_SetString(PyExc_TypeError, "First arg must be an initialized LatticeContext");
        return NULL;
    }
    /* Maximum n bits can be encoded */
    long max_bits = ctx->n;
    long total_bits = data_len * 8;
    if (total_bits > max_bits) {
        PyErr_Format(PyExc_ValueError, "Message too long: %ld bits > %ld max", total_bits, max_bits);
        return NULL;
    }

    NTLContextGuard guard(*ctx->q);
    ZZ half_q = *ctx->q / 2;
    LatticeElement *elem = createElement(ctx, POLY);
    if (!elem) return NULL;
    elem->poly = new ZZ_pX();

    for (long i = 0; i < total_bits; i++) {
        int bit = (data[i / 8] >> (i % 8)) & 1;
        if (bit) {
            SetCoeff(*elem->poly, i, to_ZZ_p(half_q));
        }
        /* else coefficient stays 0 */
    }
    elem->elem_initialized = 1;
    return (PyObject *)elem;
}

/* decode(ctx, element) -> bytes by thresholding each coefficient */
static PyObject *Lattice_decode(PyObject *self, PyObject *args) {
    LatticeContext *ctx;
    LatticeElement *elem;
    long num_bits = -1;
    if (!PyArg_ParseTuple(args, "OO|l", &ctx, &elem, &num_bits))
        return NULL;
    if (!PyLatticeElement_Check((PyObject*)elem) || !elem->elem_initialized || elem->elem_type != POLY) {
        PyErr_SetString(PyExc_TypeError, "Second arg must be an initialized POLY element");
        return NULL;
    }

    NTLContextGuard guard(*ctx->q);
    ZZ q = *ctx->q;
    ZZ quarter_q = q / 4;
    ZZ three_quarter_q = q - quarter_q;

    if (num_bits < 0) num_bits = ctx->n;
    long num_bytes = (num_bits + 7) / 8;
    std::vector<unsigned char> result(num_bytes, 0);

    for (long i = 0; i < num_bits; i++) {
        ZZ coef = rep(coeff(*elem->poly, i));
        /* Threshold: if coef is closer to q/2 than to 0, it's a 1
         * i.e., if quarter_q <= coef <= three_quarter_q, bit = 1 */
        if (coef >= quarter_q && coef <= three_quarter_q) {
            result[i / 8] |= (1 << (i % 8));
        }
    }
    return PyBytes_FromStringAndSize((const char *)result.data(), num_bytes);
}

/* get_coeff(ctx, element, i) -> coefficient i as Python int */
static PyObject *Lattice_get_coeff(PyObject *self, PyObject *args) {
    LatticeContext *ctx;
    LatticeElement *elem;
    long idx;
    if (!PyArg_ParseTuple(args, "OOl", &ctx, &elem, &idx))
        return NULL;
    if (!PyLatticeElement_Check((PyObject*)elem) || !elem->elem_initialized) {
        PyErr_SetString(PyExc_TypeError, "Element must be initialized");
        return NULL;
    }
    if (elem->elem_type != POLY && elem->elem_type != ZQ) {
        PyErr_SetString(PyExc_TypeError, "get_coeff only works on POLY and ZQ elements");
        return NULL;
    }
    NTLContextGuard guard(*ctx->q);
    ZZ val;
    if (elem->elem_type == ZQ) {
        val = rep(*elem->zq);
    } else {
        if (idx < 0 || idx >= ctx->n) {
            PyErr_Format(PyExc_IndexError, "Index %ld out of range [0, %ld)", idx, ctx->n);
            return NULL;
        }
        val = rep(coeff(*elem->poly, idx));
    }
    std::ostringstream oss;
    oss << val;
    return PyLong_FromString(oss.str().c_str(), NULL, 10);
}

/* set_coeff(ctx, element, i, val) */
static PyObject *Lattice_set_coeff(PyObject *self, PyObject *args) {
    LatticeContext *ctx;
    LatticeElement *elem;
    long idx, val;
    if (!PyArg_ParseTuple(args, "OOll", &ctx, &elem, &idx, &val))
        return NULL;
    if (!PyLatticeElement_Check((PyObject*)elem) || !elem->elem_initialized || elem->elem_type != POLY) {
        PyErr_SetString(PyExc_TypeError, "Must be an initialized POLY element");
        return NULL;
    }
    NTLContextGuard guard(*ctx->q);
    SetCoeff(*elem->poly, idx, to_ZZ_p(to_ZZ(val)));
    Py_RETURN_NONE;
}

/* cbd_sample(ctx, eta) -> POLY with coefficients from CBD(eta) */
static PyObject *Lattice_cbd_sample(PyObject *self, PyObject *args) {
    LatticeContext *ctx;
    int eta;
    if (!PyArg_ParseTuple(args, "Oi", &ctx, &eta))
        return NULL;
    if (!PyLatticeContext_Check((PyObject*)ctx) || !ctx->group_init) {
        PyErr_SetString(PyExc_TypeError, "First arg must be an initialized LatticeContext");
        return NULL;
    }
    if (eta < 1 || eta > 8) {
        PyErr_SetString(PyExc_ValueError, "eta must be in [1, 8]");
        return NULL;
    }

    NTLContextGuard guard(*ctx->q);
    LatticeElement *elem = createElement(ctx, POLY);
    if (!elem) return NULL;
    elem->poly = new ZZ_pX();

    /* CBD(eta): sample 2*eta random bits, count ones in each half */
    int bytes_needed = (2 * eta * ctx->n + 7) / 8;
    std::vector<unsigned char> rand_buf(bytes_needed);
    RAND_bytes(rand_buf.data(), bytes_needed);

    int bit_pos = 0;
    for (long i = 0; i < ctx->n; i++) {
        int a_sum = 0, b_sum = 0;
        for (int j = 0; j < eta; j++) {
            int byte_idx = bit_pos / 8;
            int bit_idx = bit_pos % 8;
            a_sum += (rand_buf[byte_idx] >> bit_idx) & 1;
            bit_pos++;
        }
        for (int j = 0; j < eta; j++) {
            int byte_idx = bit_pos / 8;
            int bit_idx = bit_pos % 8;
            b_sum += (rand_buf[byte_idx] >> bit_idx) & 1;
            bit_pos++;
        }
        long coef = a_sum - b_sum;
        /* to_ZZ_p handles negative values correctly via mod q */
        SetCoeff(*elem->poly, i, to_ZZ_p(to_ZZ(coef)));
    }
    elem->elem_initialized = 1;
    return (PyObject *)elem;
}

/* compress(ctx, elem, d) -> POLY with coefficients compressed to d bits */
static PyObject *Lattice_compress(PyObject *self, PyObject *args) {
    LatticeContext *ctx;
    LatticeElement *elem;
    int d;
    if (!PyArg_ParseTuple(args, "OOi", &ctx, &elem, &d))
        return NULL;
    if (!PyLatticeElement_Check((PyObject*)elem) || !elem->elem_initialized || elem->elem_type != POLY) {
        PyErr_SetString(PyExc_TypeError, "Must be an initialized POLY element");
        return NULL;
    }

    NTLContextGuard guard(*ctx->q);
    LatticeElement *result = createElement(ctx, POLY);
    if (!result) return NULL;
    result->poly = new ZZ_pX();

    ZZ two_d_zz = ZZ(1) << d;
    ZZ q = *ctx->q;
    for (long i = 0; i < ctx->n; i++) {
        ZZ x = rep(coeff(*elem->poly, i));
        /* compress_d(x) = round(2^d / q * x) mod 2^d */
        ZZ val = (x * two_d_zz + q / 2) / q;
        val %= two_d_zz;
        SetCoeff(*result->poly, i, to_ZZ_p(val));
    }
    result->elem_initialized = 1;
    return (PyObject *)result;
}

/* decompress(ctx, elem, d) -> POLY with coefficients decompressed from d bits */
static PyObject *Lattice_decompress(PyObject *self, PyObject *args) {
    LatticeContext *ctx;
    LatticeElement *elem;
    int d;
    if (!PyArg_ParseTuple(args, "OOi", &ctx, &elem, &d))
        return NULL;
    if (!PyLatticeElement_Check((PyObject*)elem) || !elem->elem_initialized || elem->elem_type != POLY) {
        PyErr_SetString(PyExc_TypeError, "Must be an initialized POLY element");
        return NULL;
    }

    NTLContextGuard guard(*ctx->q);
    LatticeElement *result = createElement(ctx, POLY);
    if (!result) return NULL;
    result->poly = new ZZ_pX();

    ZZ two_d_zz = ZZ(1) << d;
    ZZ q = *ctx->q;
    for (long i = 0; i < ctx->n; i++) {
        ZZ x = rep(coeff(*elem->poly, i));
        /* decompress_d(x) = round(q / 2^d * x) */
        ZZ val = (q * x + two_d_zz / 2) / two_d_zz;
        SetCoeff(*result->poly, i, to_ZZ_p(val));
    }
    result->elem_initialized = 1;
    return (PyObject *)result;
}

/* poly_from_coeffs(ctx, list) -> POLY from a Python list of ints */
static PyObject *Lattice_poly_from_coeffs(PyObject *self, PyObject *args) {
    LatticeContext *ctx;
    PyObject *coeffs;
    if (!PyArg_ParseTuple(args, "OO", &ctx, &coeffs))
        return NULL;
    if (!PyLatticeContext_Check((PyObject*)ctx) || !ctx->group_init) {
        PyErr_SetString(PyExc_TypeError, "First arg must be an initialized LatticeContext");
        return NULL;
    }
    if (!PyList_Check(coeffs)) {
        PyErr_SetString(PyExc_TypeError, "Second arg must be a list of integers");
        return NULL;
    }

    NTLContextGuard guard(*ctx->q);
    LatticeElement *elem = createElement(ctx, POLY);
    if (!elem) return NULL;
    elem->poly = new ZZ_pX();

    Py_ssize_t n = PyList_Size(coeffs);
    for (Py_ssize_t i = 0; i < n; i++) {
        PyObject *item = PyList_GetItem(coeffs, i);
        long val = PyLong_AsLong(item);
        if (val == -1 && PyErr_Occurred()) { Py_DECREF(elem); return NULL; }
        SetCoeff(*elem->poly, i, to_ZZ_p(to_ZZ(val)));
    }
    elem->elem_initialized = 1;
    return (PyObject *)elem;
}

/* mat_transpose(ctx, mat) -> transposed MAT */
static PyObject *Lattice_mat_transpose(PyObject *self, PyObject *args) {
    LatticeContext *ctx;
    LatticeElement *mat;
    if (!PyArg_ParseTuple(args, "OO", &ctx, &mat))
        return NULL;
    if (!PyLatticeElement_Check((PyObject*)mat) || !mat->elem_initialized || mat->elem_type != MAT) {
        PyErr_SetString(PyExc_TypeError, "Second arg must be an initialized MAT element");
        return NULL;
    }
    NTLContextGuard guard(*ctx->q);
    long rows = mat->mat_rows, cols = mat->mat_cols;
    LatticeElement *result = createElement(ctx, MAT);
    if (!result) return NULL;
    result->vec = new vec_ZZ_pX();
    result->vec->SetLength(cols * rows);
    result->mat_rows = cols;
    result->mat_cols = rows;
    for (long i = 0; i < rows; i++) {
        for (long j = 0; j < cols; j++) {
            (*result->vec)[j * rows + i] = (*mat->vec)[i * cols + j];
        }
    }
    result->elem_initialized = 1;
    return (PyObject *)result;
}

/* =========================================================
 * Number protocol
 * ========================================================= */
static PyNumberMethods Element_num_meths = {
    Element_add,       /* nb_add */
    Element_sub,       /* nb_subtract */
    Element_mul,       /* nb_multiply */
    0,                 /* nb_remainder */
    0,                 /* nb_divmod */
    0,                 /* nb_power */
    Element_neg,       /* nb_negative */
    0,                 /* nb_positive */
    0,                 /* nb_absolute */
    0,                 /* nb_bool */
};

/* =========================================================
 * Method tables
 * ========================================================= */
static PyMethodDef LatticeContext_methods[] = {
    {NULL}
};

static PyMethodDef lattice_module_methods[] = {
    {"random",         Lattice_random,       METH_VARARGS, "random(ctx, type) -> random element"},
    {"random_vec",     Lattice_random_vec,   METH_VARARGS, "random_vec(ctx, k) -> random VEC"},
    {"random_mat",     Lattice_random_mat,   METH_VARARGS, "random_mat(ctx, rows, cols) -> random MAT"},
    {"gaussian",       Lattice_gaussian,     METH_VARARGS, "gaussian(ctx, type, sigma) -> Gaussian element"},
    {"gaussian_vec",   Lattice_gaussian_vec, METH_VARARGS, "gaussian_vec(ctx, k, sigma) -> Gaussian VEC"},
    {"hash",           Lattice_hash,         METH_VARARGS, "hash(ctx, data, type) -> hashed element"},
    {"serialize",      Lattice_serialize,    METH_VARARGS, "serialize(ctx, element) -> bytes"},
    {"deserialize",    Lattice_deserialize,  METH_VARARGS, "deserialize(ctx, bytes) -> element"},
    {"ismember",       Lattice_ismember,     METH_VARARGS, "ismember(ctx, element) -> bool"},
    {"order",          Lattice_order,        METH_VARARGS, "order(ctx) -> q"},
    {"degree",         Lattice_degree,       METH_VARARGS, "degree(ctx) -> n"},
    {"encode",         Lattice_encode,       METH_VARARGS, "encode(ctx, bytes) -> POLY with bits as q/2-scaled coefficients"},
    {"decode",         Lattice_decode,       METH_VARARGS, "decode(ctx, element) -> bytes from thresholded coefficients"},
    {"get_coeff",      Lattice_get_coeff,    METH_VARARGS, "get_coeff(ctx, element, i) -> coefficient i as Python int"},
    {"set_coeff",      Lattice_set_coeff,    METH_VARARGS, "set_coeff(ctx, element, i, val) -> set coefficient i"},
    {"cbd_sample",     Lattice_cbd_sample,   METH_VARARGS, "cbd_sample(ctx, eta) -> POLY with CBD(eta) coefficients"},
    {"compress",       Lattice_compress,     METH_VARARGS, "compress(ctx, elem, d) -> compressed element"},
    {"decompress",     Lattice_decompress,   METH_VARARGS, "decompress(ctx, elem, d) -> decompressed element"},
    {"poly_from_coeffs", Lattice_poly_from_coeffs, METH_VARARGS, "poly_from_coeffs(ctx, list) -> POLY"},
    {"mat_transpose", Lattice_mat_transpose, METH_VARARGS, "mat_transpose(ctx, mat) -> transposed MAT"},
    {NULL}
};

/* =========================================================
 * Type definitions
 * ========================================================= */
PyTypeObject LatticeContextType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "lattice.LatticeContext",           /* tp_name */
    sizeof(LatticeContext),             /* tp_basicsize */
    0,                                  /* tp_itemsize */
    (destructor)LatticeContext_dealloc, /* tp_dealloc */
    0,                                  /* tp_print / tp_vectorcall_offset */
    0,                                  /* tp_getattr */
    0,                                  /* tp_setattr */
    0,                                  /* tp_reserved */
    0,                                  /* tp_repr */
    0,                                  /* tp_as_number */
    0,                                  /* tp_as_sequence */
    0,                                  /* tp_as_mapping */
    0,                                  /* tp_hash */
    0,                                  /* tp_call */
    0,                                  /* tp_str */
    0,                                  /* tp_getattro */
    0,                                  /* tp_setattro */
    0,                                  /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
    "Lattice ring context R_q = Z_q[X]/(X^n+1)", /* tp_doc */
    0,                                  /* tp_traverse */
    0,                                  /* tp_clear */
    0,                                  /* tp_richcompare */
    0,                                  /* tp_weaklistoffset */
    0,                                  /* tp_iter */
    0,                                  /* tp_iternext */
    LatticeContext_methods,             /* tp_methods */
    0,                                  /* tp_members */
    0,                                  /* tp_getset */
    0,                                  /* tp_base */
    0,                                  /* tp_dict */
    0,                                  /* tp_descr_get */
    0,                                  /* tp_descr_set */
    0,                                  /* tp_dictoffset */
    (initproc)LatticeContext_init,      /* tp_init */
    0,                                  /* tp_alloc */
    LatticeContext_new,                 /* tp_new */
};

PyTypeObject LatticeElementType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "lattice.LatticeElement",           /* tp_name */
    sizeof(LatticeElement),             /* tp_basicsize */
    0,                                  /* tp_itemsize */
    (destructor)LatticeElement_dealloc, /* tp_dealloc */
    0,                                  /* tp_print / tp_vectorcall_offset */
    0,                                  /* tp_getattr */
    0,                                  /* tp_setattr */
    0,                                  /* tp_reserved */
    Element_repr,                       /* tp_repr */
    &Element_num_meths,                 /* tp_as_number */
    0,                                  /* tp_as_sequence */
    0,                                  /* tp_as_mapping */
    0,                                  /* tp_hash */
    0,                                  /* tp_call */
    Element_repr,                       /* tp_str */
    0,                                  /* tp_getattro */
    0,                                  /* tp_setattro */
    0,                                  /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
    "Lattice ring element",             /* tp_doc */
    0,                                  /* tp_traverse */
    0,                                  /* tp_clear */
    Element_equals,                     /* tp_richcompare */
    0,                                  /* tp_weaklistoffset */
    0,                                  /* tp_iter */
    0,                                  /* tp_iternext */
    0,                                  /* tp_methods */
    0,                                  /* tp_members */
    0,                                  /* tp_getset */
    0,                                  /* tp_base */
    0,                                  /* tp_dict */
    0,                                  /* tp_descr_get */
    0,                                  /* tp_descr_set */
    0,                                  /* tp_dictoffset */
    0,                                  /* tp_init */
    0,                                  /* tp_alloc */
    LatticeElement_new,                 /* tp_new */
};

/* =========================================================
 * Module definition and init
 * ========================================================= */

static int lattice_traverse(PyObject *m, visitproc visit, void *arg) {
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}

static int lattice_clear(PyObject *m) {
    Py_CLEAR(GETSTATE(m)->error);
    if (LatticeError) { Py_XDECREF(LatticeError); LatticeError = NULL; }
    return 0;
}

static struct PyModuleDef lattice_module_def = {
    PyModuleDef_HEAD_INIT,
    "lattice",
    "Lattice-based cryptography module over NTL.\n"
    "Provides polynomial ring arithmetic in R_q = Z_q[X]/(X^n+1).",
    sizeof(struct module_state),
    lattice_module_methods,
    NULL,
    lattice_traverse,
    lattice_clear,
    NULL
};

#define INITERROR return NULL

extern "C" PyObject *PyInit_lattice(void) {
    PyObject *m;

    if (PyType_Ready(&LatticeContextType) < 0)
        INITERROR;
    if (PyType_Ready(&LatticeElementType) < 0)
        INITERROR;

    m = PyModule_Create(&lattice_module_def);
    if (m == NULL)
        INITERROR;

    struct module_state *st = GETSTATE(m);
    st->error = PyErr_NewException((char*)"lattice.LatticeError", NULL, NULL);
    if (st->error == NULL) {
        Py_DECREF(m);
        INITERROR;
    }
    LatticeError = st->error;
    Py_INCREF(LatticeError);
    PyModule_AddObject(m, "LatticeError", LatticeError);

    Py_INCREF(&LatticeContextType);
    PyModule_AddObject(m, "LatticeContext", (PyObject *)&LatticeContextType);

    Py_INCREF(&LatticeElementType);
    PyModule_AddObject(m, "LatticeElement", (PyObject *)&LatticeElementType);

    /* Export type constants */
    PyModule_AddIntConstant(m, "ZQ", ZQ);
    PyModule_AddIntConstant(m, "POLY", POLY);
    PyModule_AddIntConstant(m, "VEC", VEC);
    PyModule_AddIntConstant(m, "MAT", MAT);

    return m;
}