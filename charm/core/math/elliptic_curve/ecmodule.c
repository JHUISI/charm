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
 *   @file    ecmodule.c
 *
 *   @brief   charm interface over OpenSSL Ellipic-curve module
 *
 *   @author  ayo.akinyele@charm-crypto.com
 *
 ************************************************************************/

#include "ecmodule.h"

void printf_buffer_as_hex(uint8_t * data, size_t len)
{
#ifdef DEBUG
	size_t i;

	for (i = 0; i < len; i++) {
		printf("%02x ", data[i]);
	}
	printf("\n");
#endif
}

void setBigNum(PyLongObject *obj, BIGNUM **value) {
	// convert Python long object to temporary decimal string
#if PY_MAJOR_VERSION > 3 || (PY_MAJOR_VERSION == 3 && PY_MINOR_VERSION >= 3)
	/* for Python 3.3+ */
	PyObject *strObj = _PyLong_Format((PyObject *)obj, 10);
	const char *tmp_str = (const char *)PyUnicode_DATA(strObj);
#elif PY_MAJOR_VERSION == 3
	/* for Python 3.0-3.2 */
	PyObject *strObj = _PyLong_Format((PyObject *)obj, 10);
	const char *tmp_str = PyUnicode_AS_DATA(strObj);
#else
	/* for Python 2.x */
	PyObject *strObj = _PyLong_Format((PyObject *)obj, 10, 0, 0);
	const char *tmp_str = PyString_AS_STRING(strObj);
#endif
	
	// convert decimal string to OpenSSL bignum
	BN_dec2bn(value, tmp_str);

	// free temporary decimal string
	Py_DECREF(strObj);
}

/*!
 * Hash a null-terminated string to a byte array.
 *
 * @param input_buf		The input buffer.
 * @param input_len		The input buffer length (in bytes).
 * @param output_buf	A pre-allocated output buffer of size hash_len.
 * @param hash_len		Length of the output hash (in bytes). Should be approximately bit size of curve group order.
 * @param hash_prefix	prefix for hash function.
 */
int hash_to_bytes(uint8_t *input_buf, int input_len, uint8_t *output_buf, int hash_len, uint8_t hash_prefix)
{
	SHA256_CTX sha2;
	int i, new_input_len = input_len + 2; // extra byte for prefix
	uint8_t first_block = 0;
	uint8_t new_input[new_input_len+1];

	memset(new_input, 0, new_input_len+1);
	new_input[0] = first_block; // block number (always 0 by default)
	new_input[1] = hash_prefix; // set hash prefix
	memcpy((uint8_t *)(new_input+2), input_buf, input_len); // copy input bytes

	debug("new input => \n");
	printf_buffer_as_hex(new_input, new_input_len);
	// prepare output buf
	memset(output_buf, 0, hash_len);

	if (hash_len <= HASH_LEN) {
		SHA256_Init(&sha2);
		SHA256_Update(&sha2, new_input, new_input_len);
		uint8_t md[HASH_LEN+1];
		SHA256_Final(md, &sha2);
		memcpy(output_buf, md, hash_len);
	}
	else {
		// apply variable-size hash technique to get desired size
		// determine block count.
		int blocks = (int) ceil(((double) hash_len) / HASH_LEN);
		debug("Num blocks needed: %d\n", blocks);
		uint8_t md[HASH_LEN+1];
		uint8_t md2[(blocks * HASH_LEN)+1];
		uint8_t *target_buf = md2;
		for(i = 0; i < blocks; i++) {
			/* compute digest = SHA-2( i || prefix || input_buf ) || ... || SHA-2( n-1 || prefix || input_buf ) */
			target_buf += (i * HASH_LEN);
			new_input[0] = (uint8_t) i;
			SHA256_Init(&sha2);
			debug("input %d => ", i);
			printf_buffer_as_hex(new_input, new_input_len);
			SHA256_Update(&sha2, new_input, new_input_len);
			SHA256_Final(md, &sha2);
			memcpy(target_buf, md, hash_len);
			debug("block %d => ", i);
			printf_buffer_as_hex(md, HASH_LEN);
			memset(md, 0, HASH_LEN);
		}
		// copy back to caller
		memcpy(output_buf, md2, hash_len);
	}

	OPENSSL_cleanse(&sha2,sizeof(sha2));
	return TRUE;
}


/*
 * Create a new point with an existing group object
 */
ECElement *createNewPoint(GroupType type, ECGroup *gobj) {
	if(type != ZR && type != G) return NULL;
	ECElement *newObj = PyObject_New(ECElement, &ECType);
	if(type == ZR) {
		newObj->type = type;
		newObj->elemZ = BN_new();
		newObj->P = NULL;
	}
	else if(type == G) {
		newObj->type = type;
		newObj->P = EC_POINT_new(gobj->ec_group);
		newObj->elemZ = NULL;
	}
	newObj->point_init = TRUE;
	newObj->group = gobj; // gobj->group
	Py_INCREF(newObj->group);
	return newObj;
}

int ECElement_init(ECElement *self, PyObject *args, PyObject *kwds)
{
    return 0;
}


void ECElement_dealloc(ECElement* self) {
	/* clear structure */
	if(self->point_init && self->type == G)  { debug("clearing ec point.\n"); EC_POINT_free(self->P);    }
	if(self->point_init && self->type == ZR) { debug("clearing ec zr element.\n"); BN_free(self->elemZ); }
	Py_XDECREF(self->group);
	Py_TYPE(self)->tp_free((PyObject*)self);
}

PyObject *ECElement_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    ECElement *self;

    self = (ECElement *)type->tp_alloc(type, 0);
    if (self != NULL) {
    	/* initialize fields here */
    	debug("object created...\n");
    	self->type = NONE_G;
    	self->group = NULL;
    	self->P = NULL;
    	self->elemZ = NULL;
    	self->point_init = FALSE;
    }
    return (PyObject *) self;
}

void ECGroup_dealloc(ECGroup *self)
{
	if(self->group_init == TRUE && self->ec_group != NULL) {
		Py_BEGIN_ALLOW_THREADS;
		debug("clearing ec group struct.\n");
		EC_GROUP_clear_free(self->ec_group);
		BN_free(self->order);
		BN_CTX_free(self->ctx);
		self->group_init = FALSE;
		Py_END_ALLOW_THREADS;
	}

#ifdef BENCHMARK_ENABLED
	if(self->dBench != NULL) {
		Py_CLEAR(self->dBench);
		if(self->gBench != NULL) {
			Py_CLEAR(self->gBench);
		}
	}
#endif
	debug("Releasing ECGroup object!\n");
	Py_TYPE(self)->tp_free((PyObject *) self);
}

PyObject *ECGroup_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	ECGroup *self = (ECGroup *) type->tp_alloc(type, 0);
	if(self != NULL) {
		self->group_init = FALSE;
		self->nid        = -1;
		self->ec_group   = NULL;
		self->order		 = BN_new();
    	self->ctx        = BN_CTX_new();
#ifdef BENCHMARK_ENABLED
		memset(self->bench_id, 0, ID_LEN);
		self->dBench = NULL;
		self->gBench = NULL;
#endif
	}

	return (PyObject *) self;
}

int ECGroup_init(ECGroup *self, PyObject *args, PyObject *kwds)
{
  PyObject *pObj = NULL, *aObj = NULL, *bObj = NULL;
  char *params = NULL, *param_string = NULL;
  int pf_len, ps_len, nid;
  static char *kwlist[] = {"params", "param_string", "p", "a", "b", "nid", NULL};

  if (! PyArg_ParseTupleAndKeywords(args, kwds, "|s#s#OOOi", kwlist,
                                   &params, &pf_len, &param_string, &ps_len,
                                   &pObj, &aObj, &bObj, &nid)) {
    return -1;
  }

  debug("initializing object...\n");
  if(pObj && aObj && bObj && !params && !param_string && !nid) {
    // p, a, and b curve parameters are set...
    if(!PyLong_Check(pObj) || !PyLong_Check(aObj) || !PyLong_Check(bObj))
    {
      return -1;
    }

    BIGNUM *p,*a,*b;
    p = BN_new();
    setBigNum((PyLongObject *) pObj, &p);

    // make sure p is prime then continue loading a and b parameters for EC
    if(BN_is_prime_ex(p, BN_prime_checks, self->ctx, NULL) != 1) {
      debug("p is not prime.\n");
      BN_free(p);
      PyErr_SetString(PyECErrorObject, "p must be a prime integer.");
      return -1;
    }

    a = BN_new();
    b = BN_new();
    setBigNum((PyLongObject *) aObj, &a);
    setBigNum((PyLongObject *) bObj, &b);
    debug("p (bn) is now '%s'\n", BN_bn2dec(p));
    debug("a (bn) is now '%s'\n", BN_bn2dec(a));
    debug("b (bn) is now '%s'\n", BN_bn2dec(b));
    // now we can instantiate the ec_group
    self->ec_group = EC_GROUP_new_curve_GFp(p, a, b, self->ctx);
    if(!self->ec_group) {
      EC_GROUP_free(self->ec_group);
      PyErr_SetString(PyECErrorObject, "could not initialize ec group.");
      BN_free(p);
      BN_free(a);
      BN_free(b);
      return -1;
    }
    BN_free(p);
    BN_free(a);
    BN_free(b);
    debug("Now, we're finished.\n");
  }
  // check if builtin curve specified.
  else if(nid > 0 && !pObj && !aObj && !bObj && !params && !param_string) {
    debug("nid => %d == %s...\n", nid, OBJ_nid2sn(nid));
    self->ec_group = EC_GROUP_new_by_curve_name(nid);
    if(self->ec_group == NULL) {
      EC_GROUP_free(self->ec_group);
      printf("could not find curve: error code = %s.", OBJ_nid2sn(nid));
      PyErr_SetString(PyECErrorObject, "can't find specified curve.");
      return -1;
    }
#ifdef DEBUG
		printf("OK!\n");
#endif
    debug("ec group check...\n");
    if(!EC_GROUP_check(self->ec_group, self->ctx)) {
        EC_GROUP_free(self->ec_group);
        PyErr_SetString(PyECErrorObject, "group check failed, try another curve.");
        return -1;
    }
    self->nid = nid;
#ifdef DEBUG
		printf("OK!\n");
#endif
  }
  else {
    PyErr_SetString(PyECErrorObject, "invalid input. try again.");
    return -1;
  }

  // obtain the order of the elliptic curve and store in group object
  EC_GROUP_get_order(self->ec_group, self->order, self->ctx);
  self->group_init = TRUE;
  return 0;
}

PyObject *ECElement_call(ECElement *intObject, PyObject *args, PyObject *kwds) {

	return NULL;
}

PyObject *ECGroup_print(ECGroup *self) {
	if(!self->group_init)
		return PyUnicode_FromString("");
	BIGNUM *p = BN_new(), *a = BN_new(), *b = BN_new();
	EC_GROUP_get_curve_GFp(self->ec_group, p, a, b, self->ctx);

	const char *id;
	if(self->nid == -1) id = "custom";
	else id = OBJ_nid2sn(self->nid);
	char *pstr = BN_bn2dec(p);
	char *astr = BN_bn2dec(a);
	char *bstr = BN_bn2dec(b);
	PyObject *strObj = PyUnicode_FromFormat("Curve '%s' => y^2 = x^3 + a*x + b  (mod p):\np = %s\na = %s\nb = %s", id, (const char *) pstr,
											(const char *) astr, (const char *) bstr);
	OPENSSL_free(pstr);
	OPENSSL_free(astr);
	OPENSSL_free(bstr);
	BN_free(p);
	BN_free(a);
	BN_free(b);
	return strObj;
}

PyObject *ECElement_print(ECElement *self) {
  if(self->type == ZR) {
    if(!self->point_init)
      return PyUnicode_FromString("");
    char *Zstr = BN_bn2dec(self->elemZ);
    PyObject *strObj = PyUnicode_FromString((const char *) Zstr);
    OPENSSL_free(Zstr);
    return strObj;
  }
  else if(self->type == G) {
    if(!self->point_init)
      return PyUnicode_FromString("");
    VERIFY_GROUP(self->group);

    BIGNUM *x = BN_new(), *y = BN_new();
    EC_POINT_get_affine_coordinates_GFp(self->group->ec_group, self->P, x, y, self->group->ctx);
    char *xstr = BN_bn2dec(x);
    char *ystr = BN_bn2dec(y);
    //debug("P -> x = %s\n", xstr);
    //debug("P -> y = %s\n", ystr);
    PyObject *strObj = PyUnicode_FromFormat("[%s, %s]", (const char *)xstr, (const char *)ystr);
    OPENSSL_free(xstr);
    OPENSSL_free(ystr);
    BN_free(x);
    BN_free(y);
    return strObj;
  }

  return (PyObject *) PyUnicode_FromString("");
}

PyObject *ECE_init(ECElement *self, PyObject *args) {
  GroupType type = NONE_G;
  ECElement *obj;
  ECGroup *gobj = NULL;
  PyObject *long_obj = NULL;

  if(PyArg_ParseTuple(args, "Oi|O", &gobj, &type, &long_obj)) {
    VERIFY_GROUP(gobj);

    if(type == G) {
      debug("init element in group G.\n");
      obj = createNewPoint(G, gobj);
      return (PyObject *) obj;
    }
    else if(type == ZR) {
      debug("init element of ZR.\n");
      obj = createNewPoint(ZR, gobj);
      if(long_obj != NULL) {
        if (_PyLong_Check(long_obj)) {
          setBigNum((PyLongObject *) long_obj, &obj->elemZ);
          BN_mod(obj->elemZ, obj->elemZ, gobj->order, gobj->ctx);
        } else {
          EXIT_IF(TRUE, "expecting a number (int or long)");
        }
      }
      return (PyObject *) obj;
    }
    else {
      EXIT_IF(TRUE, "invalid type selected.");
    }
  }
  EXIT_IF(TRUE, "invalid argument.");
}

PyObject *ECE_random(ECElement *self, PyObject *args)
{
	GroupType type = NONE_G;
	ECGroup *gobj = NULL;

	if(PyArg_ParseTuple(args, "Oi", &gobj, &type)) {
		VERIFY_GROUP(gobj);

		if(type == G) {
			// generate a random element from ec group G.
			// call 'EC_POINT_set_compressed_coordinates_GFp' w/ group, P, x, 1, ctx
			// call 'EC_POINT_set_affine_coordinates_GFp' w/ group, P, x/y, ctx
			// test group membership 'EC_POINT_is_on_curve'
			ECElement *objG = createNewPoint(G, gobj);
			BIGNUM *x = BN_new(), *y = BN_new(); // *order = BN_new();
			//EC_GROUP_get_order(gobj->ec_group, order, gobj->ctx);
			int FindAnotherPoint = TRUE;
			//START_CLOCK(dBench);
			do {
				// generate random point
				BN_rand_range(x, gobj->order);
				EC_POINT_set_compressed_coordinates_GFp(gobj->ec_group, objG->P, x, 1, gobj->ctx);
				EC_POINT_get_affine_coordinates_GFp(gobj->ec_group, objG->P, x, y, gobj->ctx);
				// make sure point is on curve and not zero

				if(BN_is_zero(x) || BN_is_zero(y)) {
					FindAnotherPoint = TRUE;
					continue;
				}

				if(EC_POINT_is_on_curve(gobj->ec_group, objG->P, gobj->ctx)) {
					FindAnotherPoint = FALSE;
				}
//				char *xstr = BN_bn2dec(x);
//				char *ystr = BN_bn2dec(y);
//				debug("P -> x = %s\n", xstr);
//				debug("P -> y = %s\n", ystr);
//				OPENSSL_free(xstr);
//				OPENSSL_free(ystr);
			} while(FindAnotherPoint);

			BN_free(x);
			BN_free(y);
//			BN_free(order);
			return (PyObject *) objG;
		}
		else if(type == ZR) {
			ECElement *objZR = createNewPoint(ZR, gobj);
			BN_rand_range(objZR->elemZ, gobj->order);

			return (PyObject *) objZR;
		}
		else {

			EXIT_IF(TRUE, "invalid object type.");
		}
	}


	EXIT_IF(TRUE, "invalid argument.");
}

static PyObject *ECE_is_infinity(ECElement *self, PyObject *args) {

	Point_Init(self);
	EXIT_IF(self->type != G, "element not of type G.");

	 if(EC_POINT_is_at_infinity(self->group->ec_group, self->P)) {
		 Py_INCREF(Py_True);
		 return Py_True;
	 }

	 Py_INCREF(Py_False);
	 return Py_False;
}

static PyObject *ECE_add(PyObject *o1, PyObject *o2) {
	ECElement *lhs = NULL, *rhs = NULL, *ans = NULL;
	int foundLHS = FALSE, foundRHS = FALSE;

	Check_Types2(o1, o2, lhs, rhs, foundLHS, foundRHS);

   if(foundLHS) {
		debug("found lhs.\n");
		// if rhs == ZR, then convert lhs to a bn otherwise fail.
		if(rhs->point_init && rhs->type == ZR) {
			BIGNUM *lhs_val = BN_new();
			setBigNum((PyLongObject *) o1, &lhs_val);
			ans = createNewPoint(ZR, rhs->group);
			BN_mod_add(ans->elemZ, lhs_val, rhs->elemZ, ans->group->order, ans->group->ctx);
			BN_free(lhs_val);
#ifdef BENCHMARK_ENABLED
			UPDATE_BENCH(ADDITION, ans->type, ans->group);
#endif
			return (PyObject *) ans;
		}
	}
	else if(foundRHS) {
		debug("found rhs.\n");
		// if lhs == ZR, then convert rhs to a bn otherwise fail.
		if(lhs->point_init && lhs->type == ZR) {
			BIGNUM *rhs_val = BN_new();
			setBigNum((PyLongObject *) o2, &rhs_val);
			ans = createNewPoint(ZR, lhs->group); // ->group, lhs->ctx);
			BN_mod_add(ans->elemZ, lhs->elemZ, rhs_val, ans->group->order, ans->group->ctx);
			BN_free(rhs_val);
#ifdef BENCHMARK_ENABLED
			UPDATE_BENCH(ADDITION, ans->type, ans->group);
#endif
			return (PyObject *) ans;
		}
	}
	else {
		// check whether we have two Points
		Point_Init(lhs);
		Point_Init(rhs);
		if(ElementZR(lhs, rhs)) {

			IS_SAME_GROUP(lhs, rhs);
			// easy, just call BN_add
			ans = createNewPoint(ZR, lhs->group);
			BN_mod_add(ans->elemZ, lhs->elemZ, rhs->elemZ, ans->group->order, ans->group->ctx);
#ifdef BENCHMARK_ENABLED
			UPDATE_BENCH(ADDITION, ans->type, ans->group);
#endif
			return (PyObject *) ans;
		}
		else { // if(lhs->type == G && rhs->type == ZR) or vice versa operation undefined...

			EXIT_IF(TRUE, "adding the a group element G to ZR is undefined.");
		}
	}

	EXIT_IF(TRUE, "invalid arguments.");
}

/*
 * Point Subtraction of two points A and B is really
 * A + (-B) where -B is the reflection of that point with
 * respect to the x-axis. i.e. (xb,yb) => (xb,-yb)
 */
static PyObject *ECE_sub(PyObject *o1, PyObject *o2) {
	ECElement *lhs = NULL, *rhs = NULL, *ans = NULL;
	int foundLHS = FALSE, foundRHS = FALSE;

	Check_Types2(o1, o2, lhs, rhs, foundLHS, foundRHS);

	if(foundLHS) {
		debug("found lhs.\n");
		// if rhs == ZR, then convert lhs to a bn otherwise fail.
		// only supported for elements of Long (lhs) and ZR (rhs)
		if(rhs->point_init && rhs->type == ZR) {
			BIGNUM *lhs_val = BN_new();
			setBigNum((PyLongObject *) o1, &lhs_val);
			ans = createNewPoint(ZR, rhs->group); // ->group, rhs->ctx);
			BN_mod_sub(ans->elemZ, lhs_val, rhs->elemZ, ans->group->order, ans->group->ctx);
			BN_free(lhs_val);
#ifdef BENCHMARK_ENABLED
			UPDATE_BENCH(SUBTRACTION, ans->type, ans->group);
#endif
			return (PyObject *) ans;
		}
	}
	else if(foundRHS) {
		debug("found rhs.\n");
		// if lhs == ZR, then convert rhs to a bn otherwise fail.
		// only supported for elements of ZR (lhs) and Long (rhs)
		if(lhs->point_init && lhs->type == ZR) {
			BIGNUM *rhs_val = BN_new();
			setBigNum((PyLongObject *) o2, &rhs_val);
			ans = createNewPoint(ZR, lhs->group);
			BN_mod_sub(ans->elemZ, lhs->elemZ, rhs_val, ans->group->order, ans->group->ctx);
			BN_free(rhs_val);
#ifdef BENCHMARK_ENABLED
			UPDATE_BENCH(SUBTRACTION, ans->type, ans->group);
#endif
			return (PyObject *) ans;
		}
	}
	else {
		// check whether we have two Points
		Point_Init(lhs);
		Point_Init(rhs);

		if(ElementZR(lhs, rhs)) {
			IS_SAME_GROUP(lhs, rhs);
			ans = createNewPoint(ZR, lhs->group);
			BN_mod_sub(ans->elemZ, lhs->elemZ, rhs->elemZ, ans->group->order, ans->group->ctx);
#ifdef BENCHMARK_ENABLED
			UPDATE_BENCH(SUBTRACTION, ans->type, ans->group);
#endif
			return (PyObject *) ans;
		}
		else {
			// not defined for other combinations
			EXIT_IF(TRUE, "invalid combination of operands.");
		}
	}


	EXIT_IF(TRUE, "invalid arguments.");
}

static PyObject *ECE_mul(PyObject *o1, PyObject *o2) {
	ECElement *lhs = NULL, *rhs = NULL, *ans = NULL;
	int foundLHS = FALSE, foundRHS = FALSE;

	Check_Types2(o1, o2, lhs, rhs, foundLHS, foundRHS);

	if(foundLHS) {
		debug("found lhs.\n");
		// if rhs == ZR, then convert lhs to a bn otherwise fail.
		// only supported for elements of Long (lhs) and ZR (rhs)
		if(rhs->point_init && rhs->type == ZR) {
			BIGNUM *lhs_val = BN_new();
			setBigNum((PyLongObject *) o1, &lhs_val);
			ans = createNewPoint(ZR, rhs->group);
			BN_mod_mul(ans->elemZ, lhs_val, rhs->elemZ, ans->group->order, ans->group->ctx);
			BN_free(lhs_val);
#ifdef BENCHMARK_ENABLED
			UPDATE_BENCH(MULTIPLICATION, ans->type, ans->group);
#endif
			return (PyObject *) ans;
		}
	}
	else if(foundRHS) {
		debug("found rhs.\n");
		// if lhs == ZR, then convert rhs to a bn otherwise fail.
		// only supported for elements of ZR (lhs) and Long (rhs)
		if(lhs->point_init && lhs->type == ZR) {
			BIGNUM *rhs_val = BN_new();
			setBigNum((PyLongObject *) o2, &rhs_val);
			ans = createNewPoint(ZR, lhs->group); // ->group, lhs->ctx);
			BN_mod_mul(ans->elemZ, lhs->elemZ, rhs_val, ans->group->order, ans->group->ctx);
			BN_free(rhs_val);
#ifdef BENCHMARK_ENABLED
			UPDATE_BENCH(MULTIPLICATION, ans->type, ans->group);
#endif
			return (PyObject *) ans;
		}
	}
	else {
		// check whether we have two Points
		Point_Init(lhs);
		Point_Init(rhs);
		IS_SAME_GROUP(lhs, rhs);

		if(ElementG(lhs, rhs)) {
			ans = createNewPoint(G, lhs->group);
			EC_POINT_add(ans->group->ec_group, ans->P, lhs->P, rhs->P, ans->group->ctx);
		}
		else if(ElementZR(lhs, rhs)) {
			ans = createNewPoint(ZR, lhs->group);
			BN_mod_mul(ans->elemZ, lhs->elemZ, rhs->elemZ, ans->group->order, ans->group->ctx);
		}
		else {

			EXIT_IF(TRUE, "elements are not of the same type.");
		}
#ifdef BENCHMARK_ENABLED
		UPDATE_BENCH(MULTIPLICATION, ans->type, ans->group);
#endif
		return (PyObject *) ans;
	}


	ErrorMsg("invalid argument.");
}

static PyObject *ECE_div(PyObject *o1, PyObject *o2) {
	;
	ECElement *lhs = NULL, *rhs = NULL, *ans = NULL;
	BIGNUM *rm = NULL;
	int foundLHS = FALSE, foundRHS = FALSE;

	Check_Types2(o1, o2, lhs, rhs, foundLHS, foundRHS);

	if(foundLHS) {
		debug("found lhs.\n");
		// if rhs == ZR, then convert lhs to a bn otherwise fail.
		// only supported for elements of Long (lhs) and ZR (rhs)
		if(rhs->point_init && rhs->type == ZR) {
			BIGNUM *lhs_val = BN_new();
			rm = BN_new();
			setBigNum((PyLongObject *) o1, &lhs_val);
			ans = createNewPoint(ZR, rhs->group);
			BN_div(ans->elemZ, rm, lhs_val, rhs->elemZ, ans->group->ctx);
			BN_free(lhs_val);
			BN_free(rm);
#ifdef BENCHMARK_ENABLED
			UPDATE_BENCH(DIVISION, ans->type, ans->group);
#endif
			return (PyObject *) ans;
		}
	}
	else if(foundRHS) {
		debug("found rhs.\n");
		// if lhs == ZR, then convert rhs to a bn otherwise fail.
		// only supported for elements of ZR (lhs) and Long (rhs)
		if(lhs->point_init && lhs->type == ZR) {
			BIGNUM *rhs_val = BN_new();
			rm = BN_new();
			setBigNum((PyLongObject *) o2, &rhs_val);
			ans = createNewPoint(ZR, lhs->group); // ->group, lhs->ctx);
			BN_div(ans->elemZ, rm, lhs->elemZ, rhs_val, ans->group->ctx);
			BN_free(rhs_val);
			BN_free(rm);
#ifdef BENCHMARK_ENABLED
			UPDATE_BENCH(DIVISION, ans->type, ans->group);
#endif
			return (PyObject *) ans;
		}
	}
	else {
		// check whether we have two Points
		Point_Init(lhs);
		Point_Init(rhs);
		IS_SAME_GROUP(lhs, rhs);

		if(ElementG(lhs, rhs)) {
			ECElement *rhs_neg = negatePoint(rhs);
			if(rhs_neg != NULL) {
				ans = createNewPoint(G, lhs->group);
				EC_POINT_add(ans->group->ec_group, ans->P, lhs->P, rhs_neg->P, ans->group->ctx);
			}
			Py_DECREF(rhs_neg);
		}
		else if(ElementZR(lhs, rhs)) {
			ans = createNewPoint(ZR, lhs->group);
			rm = BN_new();
			BN_div(ans->elemZ, rm, lhs->elemZ, rhs->elemZ, ans->group->ctx);
			BN_free(rm);
		}
		else {

			EXIT_IF(TRUE, "elements not the same type.");
		}
#ifdef BENCHMARK_ENABLED
		UPDATE_BENCH(DIVISION, ans->type, ans->group);
#endif
		return (PyObject *) ans;
	}

	EXIT_IF(TRUE, "invalid argument.");
}

static PyObject *ECE_rem(PyObject *o1, PyObject *o2) {
	;
	ECElement *lhs = NULL, *rhs = NULL, *ans = NULL;
	int foundLHS = FALSE, foundRHS = FALSE;

	Check_Types2(o1, o2, lhs, rhs, foundLHS, foundRHS);

	if(foundLHS) {
		debug("found lhs.\n");
		// if rhs == ZR, then convert lhs to a bn otherwise fail.
		// only supported for elements of Long (lhs) and ZR (rhs)
		if(rhs->point_init && rhs->type == ZR) {
			BIGNUM *lhs_val = BN_new();
			setBigNum((PyLongObject *) o1, &lhs_val);
			ans = createNewPoint(ZR, rhs->group);
			BN_mod(ans->elemZ, lhs_val, rhs->elemZ, ans->group->ctx);
			BN_free(lhs_val);

			return (PyObject *) ans;
		}
	}
	else if(foundRHS) {
		debug("found rhs.\n");
		// if lhs == ZR, then convert rhs to a bn otherwise fail.
		// only supported for elements of ZR (lhs) and Long (rhs)
		if(lhs->point_init && lhs->type == ZR) {
			BIGNUM *rhs_val = BN_new();
			setBigNum((PyLongObject *) o2, &rhs_val);
			ans = createNewPoint(ZR, lhs->group);
			BN_mod(ans->elemZ, lhs->elemZ, rhs_val, ans->group->ctx);
			BN_free(rhs_val);
			return (PyObject *) ans;
		}
	}
	else {
		Point_Init(lhs);
		Point_Init(rhs);

		if(ElementZR(lhs, rhs)) {
			ans = createNewPoint(ZR, lhs->group);
			// reall calls BN_div with the dv se to NULL.
			BN_mod(ans->elemZ, lhs->elemZ, rhs->elemZ, ans->group->ctx);
			return (PyObject *) ans;
		}
		else {

			EXIT_IF(TRUE, "invalid combination of element types");
		}
	}


	EXIT_IF(TRUE, "invalid argument type.");
}

static PyObject *ECE_pow(PyObject *o1, PyObject *o2, PyObject *o3) {
	ECElement *lhs = NULL, *rhs = NULL, *ans = NULL;
	int foundLHS = FALSE, foundRHS = FALSE;

	Check_Types2(o1, o2, lhs, rhs, foundLHS, foundRHS);

	if(foundLHS) {
		// TODO: implement for elements of Long ** ZR
		if(rhs->point_init && rhs->type == ZR) {
			BIGNUM *lhs_val = BN_new();
			setBigNum((PyLongObject *) o1, &lhs_val);
			ans = createNewPoint(ZR, rhs->group);
			BN_mod_exp(ans->elemZ, lhs_val, rhs->elemZ, ans->group->order, ans->group->ctx);
			BN_free(lhs_val);
#ifdef BENCHMARK_ENABLED
			UPDATE_BENCH(EXPONENTIATION, ans->type, ans->group);
#endif
			return (PyObject *) ans;
		}
		EXIT_IF(TRUE, "element type combination not supported.");
	}
	else if(foundRHS) {
		// TODO: implement for elements of G ** Long or ZR ** Long
		long rhs = PyLong_AsLong(o2);
		if(lhs->type == ZR) {
			if(PyErr_Occurred() || rhs >= 0) {
				// clear error and continue
//					PyErr_Print(); // for debug purposes
					PyErr_Clear();
					BIGNUM *rhs_val = BN_new();
					setBigNum((PyLongObject *) o2, &rhs_val);

					ans = createNewPoint(ZR, lhs->group);
					BN_mod_exp(ans->elemZ, lhs->elemZ, rhs_val, ans->group->order, ans->group->ctx);
					BN_free(rhs_val);
			}
			else if(rhs == -1) {
				debug("finding modular inverse.\n");
				ans = invertECElement(lhs);
			}
			else {
				EXIT_IF(TRUE, "unsupported operation.");
			}
		}
		else if(lhs->type == G) {
			if(PyErr_Occurred() || rhs >= 0) {
				// clear error and continue
//					PyErr_Print(); // for debug purposes
					PyErr_Clear();
					BIGNUM *rhs_val = BN_new();
					setBigNum((PyLongObject *) o2, &rhs_val);
					ans = createNewPoint(G, lhs->group); // ->group, lhs->ctx);
					EC_POINT_mul(ans->group->ec_group, ans->P, NULL, lhs->P, rhs_val, ans->group->ctx);
					BN_free(rhs_val);
			}
			else if(rhs == -1) {
				debug("finding modular inverse.\n");
				ans = invertECElement(lhs);
			}
			else {
				EXIT_IF(TRUE, "unsupported operation.");
			}
		}
		else {
			EXIT_IF(TRUE, "element type combination not supported.");
		}
#ifdef BENCHMARK_ENABLED
		UPDATE_BENCH(EXPONENTIATION, ans->type, ans->group);
#endif
		return (PyObject *) ans;
	}
	else {
		// check whether we have two Points
		Point_Init(lhs);
		Point_Init(rhs);
		IS_SAME_GROUP(lhs, rhs);

		if(lhs->type == G && rhs->type == ZR) {
			ans = createNewPoint(G, lhs->group);
			EC_POINT_mul(ans->group->ec_group, ans->P, NULL, lhs->P, rhs->elemZ, ans->group->ctx);
		}
		else if(ElementZR(lhs, rhs)) {
			ans = createNewPoint(ZR, lhs->group);
			BN_mod_exp(ans->elemZ, lhs->elemZ, rhs->elemZ, ans->group->order, ans->group->ctx);
		}
		else {

			EXIT_IF(TRUE, "cannot exponentiate two points.");
		}
#if BENCHMARK_ENABLED
		UPDATE_BENCH(EXPONENTIATION, ans->type, ans->group);
#endif
		return (PyObject *) ans;
	}

	EXIT_IF(TRUE, "invalid arguments.");
}

/* assume 'self' is a valid ECElement instance */
ECElement *invertECElement(ECElement *self) {
	ECElement *newObj = NULL;
	if(self->type == G) {
		newObj = createNewPoint(G, self->group); // ->group, self->ctx);
		EC_POINT_copy(newObj->P, self->P);
		if(EC_POINT_invert(newObj->group->ec_group, newObj->P, newObj->group->ctx)) {
			return newObj;
		}
		Py_XDECREF(newObj);
	}
	else if(self->type == ZR) {
		// get modulus and compute mod_inverse
		BIGNUM *x = BN_mod_inverse(NULL, self->elemZ, self->group->order, self->group->ctx);
		if(x != NULL) {
			newObj = createNewPoint(ZR, self->group);
			BN_copy(newObj->elemZ, x);
			BN_free(x);
			return newObj;
		}
		Py_XDECREF(newObj);
	}
	/* error */
	return NULL;
}

static PyObject *ECE_invert(PyObject *o1) {

	if(PyEC_Check(o1)) {
		ECElement *obj1 = (ECElement *) o1;
		Point_Init(obj1);

		ECElement *obj2 = invertECElement(obj1);

		if(obj2 != NULL) {

			return (PyObject *) obj2;
		}

		EXIT_IF(TRUE, "could not find inverse of element.");
	}

	EXIT_IF(TRUE, "invalid argument type.");
}

/* assume 'self' is a valid ECElement instance */
ECElement *negatePoint(ECElement *self) {
	ECElement *newObj = NULL;

	BIGNUM *x = BN_new(), *y = BN_new();
	EC_POINT_get_affine_coordinates_GFp(self->group->ec_group, self->P, x, y, self->group->ctx);
	BN_set_negative(y, TRUE);

	newObj = createNewPoint(G, self->group);
	EC_POINT_set_affine_coordinates_GFp(newObj->group->ec_group, newObj->P, x, y, newObj->group->ctx);
	BN_free(x);
	BN_free(y);
	if(EC_POINT_is_on_curve(newObj->group->ec_group, newObj->P, newObj->group->ctx)) {
		return newObj;
	}
	/* error */
	Py_DECREF(newObj);
	return NULL;
}

static PyObject *ECE_neg(PyObject *o1) {
	ECElement *obj1 = NULL, *obj2 = NULL;

	if(PyEC_Check(o1)) {
		obj1 = (ECElement *) o1;
		Point_Init(obj1);

		if(obj1->type == G) {
			if((obj2 = negatePoint(obj1)) != NULL) {
				return (PyObject *) obj2;
			}
		}
		else if(obj1->type == ZR) {
			// consider supporting this type.
			obj2 = createNewPoint(ZR, obj1->group);
			if(BN_copy(obj2->elemZ, obj1->elemZ) != NULL) {
				int negate;
				if(!BN_is_negative(obj2->elemZ)) negate = -1;
				else negate = 0;
				BN_set_negative(obj2->elemZ, negate);

				return (PyObject *) obj2;
			}
			Py_XDECREF(obj2);
		}

	}


	EXIT_IF(TRUE, "invalid argument.");
}

static PyObject *ECE_long(PyObject *o1) {
	ECElement *obj1 = NULL;
	if(PyEC_Check(o1)) {
		obj1 = (ECElement *) o1;
		if(obj1->type == ZR) {
			/* borrowed from mixminion 0.0.7.1 */
			// now convert to python integer
	        char *hex = BN_bn2hex(obj1->elemZ);
	        PyObject *output = PyLong_FromString(hex, NULL, BASE_HEX);
	        OPENSSL_free(hex);
	        return output; /* pass along errors */
		}
	}
	EXIT_IF(TRUE, "cannot convert this type of object to an integer.");
}

static PyObject *ECE_convertToZR(ECElement *self, PyObject *args) {
	ECElement *obj = NULL;
	ECGroup *gobj = NULL;
	PyObject *retXY = NULL;

	/* gobj - initialized ec group object */
	/* obj - ecc point object on an elliptic curve */
	/* retXY => whether to return just x (Py_True) or x and y (Py_False) */
	if(PyArg_ParseTuple(args, "OOO", &gobj, &obj, &retXY)) {
		VERIFY_GROUP(gobj);

		if(PyEC_Check(obj)) {
			// convert to
			Point_Init(obj);
			if(obj->type == G) {
				BIGNUM *x = BN_new(), *y = BN_new();
				EC_POINT_get_affine_coordinates_GFp(gobj->ec_group, obj->P, x, y, gobj->ctx);
				if(PyBool_Check(retXY)) {
					// see if retXY is Py_True or Py_False
					if(retXY == Py_True) {
						debug("Py_True detected.\n");
						ECElement *X = createNewPoint(ZR, gobj);
						ECElement *Y = createNewPoint(ZR, gobj);
						BN_copy(X->elemZ, x);
						BN_copy(Y->elemZ, y);
						BN_free(x); BN_free(y);
						return (PyObject *) PyTuple_Pack(2, (PyObject *) X, (PyObject *) Y);
					}
					else {
						BN_free(y);
						ECElement *newObj = createNewPoint(ZR, gobj);
						BN_copy(newObj->elemZ, x);
						BN_free(x);
						return (PyObject *) newObj;
					}
				}
			}
		}

		EXIT_IF(TRUE, "invalid type.");
	}
	EXIT_IF(TRUE, "invalid argument.");
}

static PyObject *ECE_getOrder(ECElement *self, PyObject *arg) {
	if(PyECGroup_Check(arg)) {
		ECGroup *gobj = (ECGroup*) arg;
		VERIFY_GROUP(gobj);

		ECElement *order = createNewPoint(ZR, gobj);
		BN_copy(order->elemZ, gobj->order);
		// return the order of the group
		return (PyObject *) order;
	}
	EXIT_IF(TRUE, "invalid argument.");
}

static PyObject *ECE_bitsize(ECElement *self, PyObject *arg) {
	if(PyECGroup_Check(arg)) {
		ECGroup *gobj = (ECGroup *) arg;
		VERIFY_GROUP(gobj);

		size_t max_len = BN_num_bytes(gobj->order) - RESERVED_ENCODING_BYTES;
		debug("order len in bytes => '%zd'\n", max_len);

		// maximum bitsize for messages encoded for the selected group
		return Py_BuildValue("i", max_len);
	}
	EXIT_IF(TRUE, "invalid argument.");
}


static PyObject *ECE_equals(PyObject *o1, PyObject *o2, int opid) {
	EXIT_IF(opid != Py_EQ && opid != Py_NE, "'==' and '!=' only comparisons supported.");

	int foundLongLHS = FALSE, foundLongRHS = FALSE, result = FALSE;
	ECElement *lhs = NULL, *rhs = NULL;
	Check_Types2(o1, o2, lhs, rhs, foundLongLHS, foundLongRHS);

	if(foundLongLHS) {
		if(rhs->type == ZR) {
			BIGNUM *lhs_val = BN_new();
			BN_set_word(lhs_val, PyLong_ToUnsignedLong(o1));
			if(BN_cmp(lhs_val, rhs->elemZ) == 0) {
				if(opid == Py_EQ) result = TRUE;
			}
			else if(opid == Py_NE) result = TRUE;
			BN_free(lhs_val);
		}
		else {
			EXIT_IF(TRUE, "comparison types not supported."); }
	}
	else if(foundLongRHS) {
		if(lhs->type == ZR) {
			BIGNUM *rhs_val = BN_new();
			BN_set_word(rhs_val, PyLong_ToUnsignedLong(o2));
			if(BN_cmp(lhs->elemZ, rhs_val) == 0) {
				if(opid == Py_EQ) result = TRUE;
			}
			else if(opid == Py_NE) result = TRUE;
			BN_free(rhs_val);
		}
		else {

			EXIT_IF(TRUE, "comparison types not supported."); }
	}
	else {
//		Point_Init(lhs)
//		Point_Init(rhs)

		if(ElementG(lhs, rhs)) {
			if(EC_POINT_cmp(lhs->group->ec_group, lhs->P, rhs->P, lhs->group->ctx) == 0) {
				if(opid == Py_EQ) result = TRUE;
			}
			else if(opid == Py_NE) result = TRUE;
		}
		else if(ElementZR(lhs, rhs)) {
			if(BN_cmp(lhs->elemZ, rhs->elemZ) == 0) {
				if(opid == Py_EQ) result = TRUE;
			}
			else if(opid == Py_NE) result = TRUE;
		}
		else {

			EXIT_IF(TRUE, "cannot compare point to an integer.\n"); }
	}

	/* return the result here */
	if(result) {
		Py_INCREF(Py_True);
		return Py_True;
	}

	Py_INCREF(Py_False);
	return Py_False;
}

static PyObject *ECE_getGen(ECElement *self, PyObject *arg) {
	if(PyECGroup_Check(arg)) {
		ECGroup *gobj = (ECGroup *) arg;
		VERIFY_GROUP(gobj);

		ECElement *genObj = createNewPoint(G, gobj);
		const EC_POINT *gen = EC_GROUP_get0_generator(gobj->ec_group);
		EC_POINT_copy(genObj->P, gen);

		return (PyObject *) genObj;
	}
	EXIT_IF(TRUE, "invalid argument.");
}

/*
 * Takes an arbitrary string and returns a group element
 */
void set_element_from_hash(ECElement *self, uint8_t *input, int input_len)
{
	if (self->type != G) {
	    PyErr_SetString(PyECErrorObject, "element not of type G.");
	}

	BIGNUM *x = BN_new(), *y = BN_new();
	int TryNextX = TRUE;
	BN_CTX *ctx = BN_CTX_new();
	ECGroup *gobj = self->group;
	// assume input string is a binary string, then set x to (x mod q)
	BN_bin2bn((const uint8_t *) input, input_len, x);
	BN_mod(x, x, gobj->order, ctx);
	do {
		// set x coordinate and then test whether it's on curve
#ifdef DEBUG
		char *xstr = BN_bn2dec(x);
		debug("Generating another x => %s\n", xstr);
		OPENSSL_free(xstr);
#endif
		EC_POINT_set_compressed_coordinates_GFp(gobj->ec_group, self->P, x, 1, ctx);
		EC_POINT_get_affine_coordinates_GFp(gobj->ec_group, self->P, x, y, ctx);

		if(BN_is_zero(x) || BN_is_zero(y)) {
			BN_add(x, x, BN_value_one());
			continue;
		}

		if(EC_POINT_is_on_curve(gobj->ec_group, self->P, ctx)) {
			TryNextX = FALSE;
		}
		else {
			BN_add(x, x, BN_value_one());
		}
	}while(TryNextX);

	BN_free(x);
	BN_free(y);
	BN_CTX_free(ctx);
}

static PyObject *ECE_hash(ECElement *self, PyObject *args) {

	char *msg = NULL;
	int msg_len;
	GroupType type;
	ECElement *hashObj = NULL;
	ECGroup *gobj = NULL;

	if(PyArg_ParseTuple(args, "Os#i", &gobj, &msg, &msg_len, &type)) {
		VERIFY_GROUP(gobj);
		// compute bit size of group
		int hash_len = BN_num_bytes(gobj->order);
		debug("hash_len => %d\n", hash_len);
		uint8_t hash_buf[hash_len+1];
		if(type == G) {
			// hash input bytes
			hash_to_bytes((uint8_t *) msg, msg_len, hash_buf, hash_len, HASH_FUNCTION_STR_TO_G_CRH);
			debug("Message => '%s'\n", msg);
			debug("Digest  => ");
			printf_buffer_as_hex(hash_buf, hash_len);
			// generate an EC element from message digest
			hashObj = createNewPoint(G, gobj);
			set_element_from_hash(hashObj, (uint8_t *) hash_buf, hash_len);
			return (PyObject *) hashObj;
		}
		else if(type == ZR) {
			hash_to_bytes((uint8_t *) msg, msg_len, hash_buf, hash_len, HASH_FUNCTION_STR_TO_ZR_CRH);
			debug("Message => '%s'\n", msg);
			debug("Digest  => ");
			printf_buffer_as_hex(hash_buf, hash_len);

			hashObj = createNewPoint(ZR, gobj);
			BN_bin2bn((const uint8_t *) hash_buf, hash_len, hashObj->elemZ);
			return (PyObject *) hashObj;
		}
		else {

			EXIT_IF(TRUE, "invalid argument type");
		}
	}


	EXIT_IF(TRUE, "invalid arguments");
}

/*
 * Encode a message as a group element
 */
static PyObject *ECE_encode(ECElement *self, PyObject *args) {
	PyObject *old_m;
	uint8_t *old_msg;
	int include_ctr = FALSE;
	uint32_t msg_len, ctr = 1, ERROR_SET = FALSE; // always have a ctr start from 1
	BIGNUM *x = NULL, *y = NULL;
	ECGroup *gobj = NULL;

	if(PyArg_ParseTuple(args, "OO|i", &gobj, &old_m, &include_ctr)) {
		VERIFY_GROUP(gobj);

		if(PyBytes_Check(old_m)) {
			old_msg = (uint8_t *) PyBytes_AS_STRING(old_m);
			msg_len = PyBytes_Size(old_m);
			debug("Encoding hex msg => ");
			// check if msg len is big enough to fit into length
			printf_buffer_as_hex((uint8_t *) old_msg, msg_len);
			debug("len => '%d'\n", msg_len);
		}
		else {
			/* return error */
			EXIT_IF(TRUE, "message not a bytes object");
		}

		// make sure msg will fit into group (get order num bits / 8)
		int max_len = BN_num_bytes(gobj->order);  //  (BN_num_bits(gobj->order) / BYTE);
		debug("max msg len => '%d'\n", max_len);

		debug("msg_len accepted => '%d'\n", msg_len);
		int len = msg_len;
		if (include_ctr == FALSE) {
            len += RESERVED_ENCODING_BYTES;
		}

        // use default of 32-bits (4 bytes) to represent ctr
        // concatenate 'ctr' to buffer and set x coordinate and test for y coordiate on curve
		// if point not on curve, increment ctr by 1
        if(len == max_len) {
            // concatenate msg
            char *input = (char *) malloc(len + 1);
            memset(input, 0, len);
            memcpy(input, old_msg, msg_len);
            int TryNextCTR = TRUE;
            ECElement *encObj = NULL;
            y=BN_new();
            x=BN_new();
            do {

                if(encObj!=NULL)
                    Py_DECREF(encObj);

                if (include_ctr == FALSE) {
                    /* 		       == msg_len       ctr
                     * encoding [    message    |  \x01 \x00 \x00 \x00 ]
                     */
                    *((uint32_t*)(input + msg_len)) = (uint32_t) ctr;
                }

                debug("input hex msg => ");
                // check if msg len is big enough to fit into length
                printf_buffer_as_hex((uint8_t *) input, len);
                encObj = createNewPoint(G, gobj);
                BN_bin2bn((const uint8_t *) input, len, x);
                BN_free(y);
                y = BN_new();
                // Uncomment for debugging purposes
                //char *xstr = BN_bn2dec(x);
                //debug("gen x => %s\n", xstr);
                //OPENSSL_free(xstr);
                EC_POINT_set_compressed_coordinates_GFp(gobj->ec_group, encObj->P, x, 1, gobj->ctx);
                EC_POINT_get_affine_coordinates_GFp(gobj->ec_group, encObj->P, x, y, gobj->ctx);

                if(BN_is_zero(x) || BN_is_zero(y)) {
                    ctr++;
                    continue;
                }

                if(EC_POINT_is_on_curve(gobj->ec_group, encObj->P, gobj->ctx)) {
                    debug("point is on curve!\n");
                    debug("final hex msg => ");
                    // check if msg len is big enough to fit into length
                    printf_buffer_as_hex((uint8_t *) input, len);
                    free(input);
                    TryNextCTR = FALSE;
                }
                else {
                    ctr++;
                }
            }while(TryNextCTR);

            BN_free(x);
            BN_free(y);

            return (PyObject *) encObj;
        }
        else {
            printf("expected message len: %lu, you provided: %d\n", (max_len - sizeof(uint32_t)), msg_len);
            EXIT_IF(TRUE, "message length does not match the selected group size.");
        }
	}

	EXIT_IF(ERROR_SET, "Ran out of counters. So, could not be encode message at given length. make it smaller.");
	Py_INCREF(Py_False);

	return Py_False;
}


/*
 * Decode a group element to a message (PyUnicode_String)
 */
static PyObject *ECE_decode(ECElement *self, PyObject *args) {
	ECElement *obj = NULL;
	ECGroup *gobj = NULL;
	int include_ctr = FALSE;

	if(PyArg_ParseTuple(args, "OO|i", &gobj, &obj, &include_ctr)) {
		VERIFY_GROUP(gobj);

		// make sure it is a point and not a scalar
		if(PyEC_Check(obj) && isPoint(obj)) {
			BIGNUM *x = BN_new(), *y = BN_new();
			// verifies that element is on the curve then gets coordinates
			EC_POINT_get_affine_coordinates_GFp(gobj->ec_group, obj->P, x, y, gobj->ctx);
			int max_byte_len = BN_num_bytes(gobj->order);
			int prepend_zeros = max_byte_len;
			// by default we will strip out the counter part (unless specified otherwise by user)
			if (include_ctr == FALSE) {
				max_byte_len -= RESERVED_ENCODING_BYTES;
			}
			debug("Size of order => '%d'\n", max_byte_len);
			int x_len = BN_num_bytes(x);
			prepend_zeros -= x_len;
			if (prepend_zeros > 0) {
                		x_len += prepend_zeros;
			}
			uint8_t *xstr = (uint8_t*) malloc(x_len + 1);
			memset(xstr, 0, x_len);
			debug("Size of xstr => '%d'\n", x_len);
			// BN_bn2bin does not include leading null bytes that might've been included in original message
			// so doing that here by counting length and then pre-pending zeroes
			BN_bn2bin(x, (uint8_t*)(xstr + prepend_zeros));
			debug("Decoded x => ");
			printf_buffer_as_hex((uint8_t *) (xstr), x_len);
			BN_free(x);
			BN_free(y);

            		int size_msg = max_byte_len;
			PyObject *decObj = PyBytes_FromStringAndSize((const char *)xstr, size_msg);
			OPENSSL_free(xstr);
			return decObj;
		}
	}

	EXIT_IF(TRUE, "invalid argument");
}

static PyObject *Serialize(ECElement *self, PyObject *args) {

	ECElement *obj = NULL;
	if(!PyArg_ParseTuple(args, "O", &obj)) {
		ErrorMsg("invalid argument.");
		return NULL;
	}

	if(obj != NULL && PyEC_Check(obj)) {
		// allows export a compressed string
		if(obj->point_init && obj->type == G) {
			uint8_t p_buf[MAX_BUF+1];
			memset(p_buf, 0, MAX_BUF);
			size_t len = EC_POINT_point2oct(obj->group->ec_group, obj->P, POINT_CONVERSION_COMPRESSED,  p_buf, MAX_BUF, obj->group->ctx);
			EXIT_IF(len == 0, "could not serialize point.");

			debug("Serialized point => ");
			printf_buffer_as_hex(p_buf, len);
			size_t length = 0;
			char *base64_buf = NewBase64Encode(p_buf, len, FALSE, &length);

			PyObject *result = PyBytes_FromString((const char *) base64_buf);
			PyObject *obj2 = PyBytes_FromFormat("%d:", obj->type);
			PyBytes_ConcatAndDel(&obj2, result);
			free(base64_buf);
			return obj2;
		}
		else if(obj->point_init && obj->type == ZR) {
			size_t len = BN_num_bytes(obj->elemZ);
			uint8_t z_buf[len+1];
			memset(z_buf, 0, len);
			if((size_t)BN_bn2bin(obj->elemZ, z_buf) == len) {
				// we're okay
				// convert z_buf to base64 and the rest is history.
				size_t length = 0;
				char *base64_buf = NewBase64Encode(z_buf, len, FALSE, &length);

				PyObject *result = PyBytes_FromString((const char *) base64_buf);
				PyObject *obj2 = PyBytes_FromFormat("%d:", obj->type);
				PyBytes_ConcatAndDel(&obj2, result);
				free(base64_buf);
				return obj2;
			}
		}
	}


	return NULL;
}

static PyObject *Deserialize(ECElement *self, PyObject *args)
{
	PyObject *obj = NULL;
	ECGroup *gobj = NULL;

	if(PyArg_ParseTuple(args, "OO", &gobj, &obj)) {
		VERIFY_GROUP(gobj);
		if(PyBytes_Check(obj)) {
			unsigned char *serial_buf = (unsigned char *) PyBytes_AsString(obj);
			GroupType type = atoi((const char *) &(serial_buf[0]));
			uint8_t *base64_buf = (uint8_t *)(serial_buf + 2);

			size_t deserialized_len = 0;
			uint8_t *buf = NewBase64Decode((const char *) base64_buf, strlen((char *) base64_buf), &deserialized_len);
			size_t len = deserialized_len;
			debug("Deserialize this => ");
			printf_buffer_as_hex(buf, len);
			if(type == G) {
				ECElement *newObj = createNewPoint(type, gobj); // ->group, gobj->ctx);
				EC_POINT_oct2point(gobj->ec_group, newObj->P, (const uint8_t *) buf, len, gobj->ctx);

				if(EC_POINT_is_on_curve(gobj->ec_group, newObj->P, gobj->ctx)) {
					obj=(PyObject *) newObj;
				}
			}
			else if(type == ZR) {
				ECElement *newObj = createNewPoint(type, gobj);
				BN_bin2bn((const uint8_t *) buf, len, newObj->elemZ);
                obj = (PyObject *) newObj;
			}else{
                Py_INCREF(Py_False);
                obj = Py_False;
            }
            free(buf);
			return obj;
		}
		else {
			EXIT_IF(TRUE, "invalid object type");
		}
	}
	EXIT_IF(TRUE, "invalid argument");
}

#ifdef BENCHMARK_ENABLED

#define BenchmarkIdentifier 2
#define GET_RESULTS_FUNC	GetResults
#define GROUP_OBJECT		ECGroup
#define BENCH_ERROR			PyECErrorObject

PyObject *PyCreateList(Operations *gBench, MeasureType type)
{
	int countZR = -1, countG = -1;
	GetField(countZR, type, ZR, gBench);
	GetField(countG,  type,  G, gBench);

	PyObject *objList = Py_BuildValue("[ii]", countZR, countG);
	return objList;
}

#include "benchmark_util.c"

#endif

PyMemberDef ECElement_members[] = {
	{"type", T_INT, offsetof(ECElement, type), 0,
		"group type"},
    {"initialized", T_INT, offsetof(ECElement, point_init), 0,
		"determine initialization status"},
    {NULL}  /* Sentinel */
};

PyMethodDef ECElement_methods[] = {
		{"isInf", (PyCFunction)ECE_is_infinity, METH_NOARGS, "Checks whether a point is at infinity."},
		{NULL}
};

#if PY_MAJOR_VERSION >= 3
PyNumberMethods ec_number = {
		(binaryfunc) ECE_add,            /* nb_add */
	    (binaryfunc) ECE_sub,            /* nb_subtract */
	    (binaryfunc) ECE_mul,            /* nb_multiply */
	    (binaryfunc) ECE_rem,      		    /* nb_remainder */
	    0,					/* nb_divmod */
	    (ternaryfunc) ECE_pow,			/* nb_power */
	    (unaryfunc) ECE_neg,            /* nb_negative */
	    0,            /* nb_positive */
	    0,            /* nb_absolute */
	    0,          	/* nb_bool */
	    (unaryfunc)ECE_invert,  /* nb_invert */
	    0,                    /* nb_lshift */
	    0,                    /* nb_rshift */
	    0,                       /* nb_and */
	    0,                       /* nb_xor */
	    0,                        /* nb_or */
	    (unaryfunc)ECE_long,           /* nb_int */
	    0,						/* nb_reserved */
	    0,          			/* nb_float */
	    (binaryfunc) ECE_add,            /* nb_inplace_add */
	    (binaryfunc) ECE_sub,            /* nb_inplace_subtract */
	    (binaryfunc) ECE_mul,            /* nb_inplace_multiply */
	    (binaryfunc) ECE_rem,      			/* nb_inplace_remainder */
	    (ternaryfunc) ECE_pow,		    /* nb_inplace_power */
	    0,                   /* nb_inplace_lshift */
	    0,                   /* nb_inplace_rshift */
	    0,                      /* nb_inplace_and */
	    0,                      /* nb_inplace_xor */
	    0,                       /* nb_inplace_or */
	    0,                  /* nb_floor_divide */
	    ECE_div,                   /* nb_true_divide */
	    0,                 /* nb_inplace_floor_divide */
	    ECE_div,                  /* nb_inplace_true_divide */
	    0,          /* nb_index */
};

PyTypeObject ECType = {
	PyVarObject_HEAD_INIT(NULL, 0)
	"elliptic_curve.Element",             /*tp_name*/
	sizeof(ECElement),         /*tp_basicsize*/
	0,                         /*tp_itemsize*/
	(destructor)ECElement_dealloc, /*tp_dealloc*/
	0,                         /*tp_print*/
	0,                         /*tp_getattr*/
	0,                         /*tp_setattr*/
	0,			   				/*tp_reserved*/
	(reprfunc)ECElement_print, /*tp_repr*/
	&ec_number,               /*tp_as_number*/
	0,                         /*tp_as_sequence*/
	0,                         /*tp_as_mapping*/
	0,                         /*tp_hash */
	0,                         /*tp_call*/
	(reprfunc)ECElement_print, /*tp_str*/
	0,                         /*tp_getattro*/
	0,                         /*tp_setattro*/
	0,                         /*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
	"Elliptic Curve objects",           /* tp_doc */
	0,		               /* tp_traverse */
	0,		               /* tp_clear */
	ECE_equals,		       /* tp_richcompare */
	0,		               /* tp_weaklistoffset */
	0,		               /* tp_iter */
	0,		               /* tp_iternext */
	ECElement_methods,             /* tp_methods */
	ECElement_members,             /* tp_members */
	0,                         /* tp_getset */
	0,                         /* tp_base */
	0,                         /* tp_dict */
	0,                         /* tp_descr_get */
	0,                         /* tp_descr_set */
	0,                         /* tp_dictoffset */
	(initproc)ECElement_init,      /* tp_init */
	0,                         /* tp_alloc */
	ECElement_new,                 /* tp_new */
};
#else
/* python 2.x series */
PyNumberMethods ec_number = {
    ECE_add,                       /* nb_add */
    ECE_sub,                       /* nb_subtract */
    ECE_mul,                        /* nb_multiply */
    ECE_div,                       /* nb_divide */
    ECE_rem,                      /* nb_remainder */
    0,						/* nb_divmod */
    ECE_pow,						/* nb_power */
    ECE_neg,            		/* nb_negative */
    0,            /* nb_positive */
    0,            /* nb_absolute */
    0,          	/* nb_nonzero */
    (unaryfunc)ECE_invert,         /* nb_invert */
    0,                    /* nb_lshift */
    0,                    /* nb_rshift */
    0,                       /* nb_and */
    0,                       /* nb_xor */
    0,                        /* nb_or */
    0,                    				/* nb_coerce */
    0,            /* nb_int */
    (unaryfunc)ECE_long,           /* nb_long */
    0,          /* nb_float */
    0,            /* nb_oct */
    0,            /* nb_hex */
    ECE_add,                      /* nb_inplace_add */
    ECE_sub,                      /* nb_inplace_subtract */
    ECE_mul,                      /* nb_inplace_multiply */
    ECE_div,                      /* nb_inplace_divide */
    0,                      /* nb_inplace_remainder */
    0,								/* nb_inplace_power */
    0,                   /* nb_inplace_lshift */
    0,                   /* nb_inplace_rshift */
    0,                      /* nb_inplace_and */
    0,                      /* nb_inplace_xor */
    0,                       /* nb_inplace_or */
    0,                  /* nb_floor_divide */
    0,                   /* nb_true_divide */
    0,                 /* nb_inplace_floor_divide */
    0,                  /* nb_inplace_true_divide */
    0,          /* nb_index */
};

PyTypeObject ECType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "elliptic_curve.Element",             /*tp_name*/
    sizeof(ECElement),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)ECElement_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    (reprfunc)ECElement_print,  /*tp_repr*/
    &ec_number,       /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0, 						/*tp_call*/
    (reprfunc)ECElement_print,   /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_CHECKTYPES, /*tp_flags*/
    "Elliptic Curve objects",           /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    ECE_equals,		   /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    ECElement_methods,           /* tp_methods */
    ECElement_members,           /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc) ECElement_init,      /* tp_init */
    0,                         /* tp_alloc */
    ECElement_new,                 /* tp_new */
};

#endif

#if PY_MAJOR_VERSION >= 3

PyTypeObject ECGroupType = {
	PyVarObject_HEAD_INIT(NULL, 0)
	"elliptic_curve.ECGroup",  /*tp_name*/
	sizeof(ECGroup),         /*tp_basicsize*/
	0,                         /*tp_itemsize*/
	(destructor)ECGroup_dealloc, /*tp_dealloc*/
	0,                         /*tp_print*/
	0,                         /*tp_getattr*/
	0,                         /*tp_setattr*/
	0,			   				/*tp_reserved*/
    (reprfunc)ECGroup_print,   /*tp_str*/
	0,               /*tp_as_number*/
	0,                         /*tp_as_sequence*/
	0,                         /*tp_as_mapping*/
	0,                         /*tp_hash */
	0,                         /*tp_call*/
	0,                         /*tp_str*/
	0,                         /*tp_getattro*/
	0,                         /*tp_setattro*/
	0,                         /*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
	"ECGroup parameters",           /* tp_doc */
	0,		               /* tp_traverse */
	0,		               /* tp_clear */
	0,		       /* tp_richcompare */
	0,		               /* tp_weaklistoffset */
	0,		               /* tp_iter */
	0,		               /* tp_iternext */
	0,             		  /* tp_methods */
	0,             	      /* tp_members */
	0,                         /* tp_getset */
	0,                         /* tp_base */
	0,                         /* tp_dict */
	0,                         /* tp_descr_get */
	0,                         /* tp_descr_set */
	0,                         /* tp_dictoffset */
	(initproc)ECGroup_init,      /* tp_init */
	0,                         /* tp_alloc */
	ECGroup_new,                 /* tp_new */
};
#else
/* python 2.x series */
PyTypeObject ECGroupType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "elliptic_curve.ECGroup",    /*tp_name*/
    sizeof(ECGroup),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)ECGroup_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,       /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0, 						/*tp_call*/
    (reprfunc)ECGroup_print,   /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "ECGroup parameters",           /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		   /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    0,           /* tp_methods */
    0,           /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc) ECGroup_init,      /* tp_init */
    0,                         /* tp_alloc */
    ECGroup_new,                 /* tp_new */
};

#endif


struct module_state {
	PyObject *error;
//#ifdef BENCHMARK_ENABLED
//	Benchmark *dBench;
//#endif
};

#if PY_MAJOR_VERSION >= 3
#define GETSTATE(m) ((struct module_state *) PyModule_GetState(m))
#else
#define GETSTATE(m) (&_state)
static struct module_state _state;
#endif

static PyMethodDef ec_methods[] = {
		{"init", (PyCFunction)ECE_init, METH_VARARGS, "Create an element in a specific group G or ZR."},
		{"random", (PyCFunction)ECE_random, METH_VARARGS, "Return a random element in a specific group G or ZR."},
		{"order", (PyCFunction)ECE_getOrder, METH_O, "Return the order of a group."},
		{"getGenerator", (PyCFunction)ECE_getGen, METH_O, "Get the generator of the group."},
		{"bitsize", (PyCFunction)ECE_bitsize, METH_O, "Returns number of bytes to represent a message."},
		{"serialize", (PyCFunction)Serialize, METH_VARARGS, "Serialize an element to a string"},
		{"deserialize", (PyCFunction)Deserialize, METH_VARARGS, "Deserialize an element to G or ZR"},
		{"hashEC", (PyCFunction)ECE_hash, METH_VARARGS, "Perform a hash of a string to a group element of G."},
		{"encode", (PyCFunction)ECE_encode, METH_VARARGS, "Encode string as a group element of G"},
		{"decode", (PyCFunction)ECE_decode, METH_VARARGS, "Decode group element to a string."},
		{"getXY", (PyCFunction)ECE_convertToZR, METH_VARARGS, "Returns the x and/or y coordinates of point on an elliptic curve."},
#ifdef BENCHMARK_ENABLED
		{"InitBenchmark", (PyCFunction)InitBenchmark, METH_VARARGS, "Initialize a benchmark object"},
		{"StartBenchmark", (PyCFunction)StartBenchmark, METH_VARARGS, "Start a new benchmark with some options"},
		{"EndBenchmark", (PyCFunction)EndBenchmark, METH_VARARGS, "End a given benchmark"},
		{"GetBenchmark", (PyCFunction)GetBenchmark, METH_VARARGS, "Returns contents of a benchmark object"},
		{"GetGeneralBenchmarks", (PyCFunction)GetAllBenchmarks, METH_VARARGS, "Retrieve general benchmark info as a dictionary"},
		{"GetGranularBenchmarks", (PyCFunction) GranularBenchmark, METH_VARARGS, "Retrieve granular benchmarks as a dictionary"},
#endif
		{NULL, NULL}
};


#if PY_MAJOR_VERSION >= 3
static int ec_traverse(PyObject *m, visitproc visit, void *arg) {
	Py_VISIT(GETSTATE(m)->error);
	return 0;
}

static int ec_clear(PyObject *m) {
  Py_CLEAR(GETSTATE(m)->error);
  Py_XDECREF(PyECErrorObject);
	return 0;
}

static struct PyModuleDef moduledef = {
		PyModuleDef_HEAD_INIT,
		"elliptic_curve",
		NULL,
		sizeof(struct module_state),
		ec_methods,
		NULL,
		ec_traverse,
		ec_clear,
		NULL
};

#define CLEAN_EXIT goto LEAVE;
#define INITERROR return NULL
PyMODINIT_FUNC
PyInit_elliptic_curve(void) 		{
#else
#define CLEAN_EXIT goto LEAVE;
#define INITERROR return
void initelliptic_curve(void) 		{
#endif
	PyObject *m;
	if(PyType_Ready(&ECGroupType) < 0)
		CLEAN_EXIT;
    if(PyType_Ready(&ECType) < 0)
    	CLEAN_EXIT;
#ifdef BENCHMARK_ENABLED
    if(import_benchmark() < 0)
        CLEAN_EXIT;
    if(PyType_Ready(&BenchmarkType) < 0)
        CLEAN_EXIT;
    if(PyType_Ready(&OperationsType) < 0)
    	CLEAN_EXIT;
#endif

#if PY_MAJOR_VERSION >= 3
	m = PyModule_Create(&moduledef);
#else
	m = Py_InitModule("elliptic_curve", ec_methods);
#endif

	struct module_state *st = GETSTATE(m);
	st->error = PyErr_NewException("elliptic_curve.Error", NULL, NULL);
	if (st->error == NULL)
        CLEAN_EXIT;
	PyECErrorObject = st->error;
    Py_INCREF(PyECErrorObject);

	Py_INCREF(&ECType);
	if(PyModule_AddObject(m, "ec_element", (PyObject *)&ECType) != 0)
		CLEAN_EXIT;
    Py_INCREF(&ECGroupType);
    if(PyModule_AddObject(m, "elliptic_curve", (PyObject *)&ECGroupType) != 0)
    	CLEAN_EXIT;

	PyModule_AddIntConstant(m, "G", G);
	PyModule_AddIntConstant(m, "ZR", ZR);
#ifdef BENCHMARK_ENABLED
	ADD_BENCHMARK_OPTIONS(m);
	PyModule_AddStringConstant(m, "Granular", _GRAN_OPT);
#endif
	// initialize PRNG
	// replace with read from some source of randomness
#ifndef MS_WINDOWS
	debug("Linux: seeding openssl prng.\n");
	char *rand_file = "/dev/urandom";
	RAND_load_file(rand_file, RAND_MAX_BYTES);
#else
	debug("Windows: seeding openssl prng.\n");
	RAND_screen();
#endif

LEAVE:
	if (PyErr_Occurred()) {
    PyErr_Clear();
    Py_XDECREF(m);
    INITERROR;
	}

#if PY_MAJOR_VERSION >= 3
	return m;
#endif
}
