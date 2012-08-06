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

void longObjToMPZ (mpz_t m, PyLongObject * p)
{
	int size, i, tmp = Py_SIZE(p);
	mpz_t temp, temp2;
	mpz_init (temp);
	mpz_init (temp2);
	if (tmp > 0)
		size = tmp;
	else
		size = -tmp;
	mpz_set_ui (m, 0);
	for (i = 0; i < size; i++)
	{
		mpz_set_ui (temp, p->ob_digit[i]);
		mpz_mul_2exp (temp2, temp, PyLong_SHIFT * i);
		mpz_add (m, m, temp2);
	}
	mpz_clear (temp);
	mpz_clear (temp2);
}

// TODO: implement a longObjToBN(PyLongObject *a, BIGNUM **b)

void setBigNum(PyLongObject *obj, BIGNUM **value) {
	mpz_t tmp;
	mpz_init(tmp);
	// convert long object into an mpz_t type
	longObjToMPZ(tmp, obj);
	// now convert tmp into a decimal string
	size_t tmp_len = mpz_sizeinbase(tmp, 10) + 2;
	char *tmp_str = (char *) malloc(tmp_len);
	tmp_str = mpz_get_str(tmp_str, 10, tmp);
	debug("Element => '%s'\n", tmp_str);
	//debug("Order of Element => '%zd'\n", tmp_len);

	// use BN_* to set decimal to BIGNUM
	BN_dec2bn(value, (const char *) tmp_str);
	free(tmp_str);
	mpz_clear(tmp);
}

/* START: module function definitions */
/*!
 * Hash a null-terminated string to a byte array.
 *
 * @param input_buf		The input buffer.
 * @param input_len		The input buffer length (in bytes).
 * @param hash_len		Length of the output hash (in bytes).
 * @param output_buf	A pre-allocated output buffer.
 * @param hash_num		Index number of the hash function to use (changes the output).
 * @return				FENC_ERROR_NONE or an error code.
 */
int hash_to_bytes(uint8_t *input_buf, int input_len, int hash_size, uint8_t *output_buf, uint32_t hash_num)
{
	SHA1Context sha_context;
	// int output_size = 0;
	uint32_t block_hdr[2];

	/* Compute an arbitrary number of SHA1 hashes of the form:
	 * output_buf[0...19] = SHA1(hash_num || 0 || input_buf)
	 * output_buf[20..39] = SHA1(hash_num || 1 || output_buf[0...19])
	 * ...
	 */
	block_hdr[0] = hash_num;
	for (block_hdr[1] = 0; hash_size > 0; (block_hdr[1])++) {
		/* Initialize the SHA1 function.	*/
		SHA1Reset(&sha_context);

		SHA1Input(&sha_context, (uint8_t *)&(block_hdr[0]), sizeof(block_hdr));
		SHA1Input(&sha_context, (uint8_t *)input_buf, input_len);

		SHA1Result(&sha_context);
		if (hash_size <= HASH_LEN) {
			memcpy(output_buf, sha_context.Message_Digest, hash_size);
			hash_size = 0;
		} else {
			memcpy(output_buf, sha_context.Message_Digest, HASH_LEN);
			input_buf = (uint8_t *) output_buf;
			hash_size -= HASH_LEN;
			output_buf += HASH_LEN;
		}
	}

	return TRUE;
}

/*
 * Create a new point with an existing group object
 */
ECElement *createNewPoint(GroupType type, ECElement *gobj) { // EC_GROUP *group, BN_CTX *ctx) {
	if(type != ZR && type != G) return NULL;
	ECElement *newObj = PyObject_New(ECElement, &ECType);
	if(type == ZR) {
		newObj->type = type;
		newObj->elemZ = BN_new();
		newObj->P = NULL;
	}
	else if(type == G) {
		newObj->type = type;
		newObj->P = EC_POINT_new(gobj->group);
		newObj->elemZ = NULL;
	}
	newObj->point_init = TRUE;
	newObj->nid = gobj->nid;
	newObj->group = gobj->group;
	newObj->group_init = FALSE;
	newObj->ctx = gobj->ctx;
	return newObj;
}

void ECElement_dealloc(ECElement* self) {
	/* clear structure */
	if(self->group_init && self->group && self->ctx) {
		debug("clearing ec group struct.\n");
		EC_GROUP_free(self->group);
		BN_CTX_free(self->ctx);
	}
	if(self->point_init && self->type == G) { debug("clearing ec point.\n"); EC_POINT_free(self->P); }
	if(self->point_init && self->type == ZR) { debug("clearing ec zr element.\n"); BN_free(self->elemZ); }
	Py_TYPE(self)->tp_free((PyObject*)self);
}

PyObject *ECElement_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    ECElement *self;

    self = (ECElement *)type->tp_alloc(type, 0);
    if (self != NULL) {
    	/* initialize fields here */
    	debug("object created...\n");
    	self->type = NONE_G;
    	self->nid = -1;
    	self->group = NULL;
    	self->P = NULL;
    	self->elemZ = NULL;
    	self->ctx = BN_CTX_new();
    	self->point_init = FALSE;
    	self->group_init = FALSE;
    }
    return (PyObject *) self;
}

int ECElement_init(ECElement *self, PyObject *args, PyObject *kwds)
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
    	if(!PyLong_Check(pObj) || !PyLong_Check(aObj) || !PyLong_Check(bObj)) { return -1; }

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
    	self->group = EC_GROUP_new_curve_GFp(p, a, b, self->ctx);
    	if(!self->group) {
    		EC_GROUP_free(self->group);
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
    	debug("nid => %d == %s...", nid, OBJ_nid2sn(nid));
    	if((self->group = EC_GROUP_new_by_curve_name(nid)) == NULL) {
    		EC_GROUP_free(self->group);
    		printf("could not find curve: error code = %s.", OBJ_nid2sn(nid));
    		PyErr_SetString(PyECErrorObject, "can't find specified curve.");
    		return -1;
    	}
#ifdef DEBUG
		printf("OK!\n");
#endif
    	debug("ec group check...");
		if(!EC_GROUP_check(self->group, self->ctx)) {
    		EC_GROUP_free(self->group);
    		PyErr_SetString(PyECErrorObject, "group check failed, try another curve.");
    		return -1;
		}
		self->nid = nid;
#ifdef DEBUG
		printf("OK!\n");
#endif
    }
    // check if file was provided
    // check if param_string provided
	self->group_init = TRUE;
    return 0;
}

PyObject *ECElement_call(ECElement *intObject, PyObject *args, PyObject *kwds) {

	return NULL;
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
		BIGNUM *x = BN_new(), *y = BN_new();
		EC_POINT_get_affine_coordinates_GFp(self->group, self->P, x, y, self->ctx);
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
	else {
		/* must be group object */
		if(!self->group_init)
			return PyUnicode_FromString("");
		BIGNUM *p = BN_new(), *a = BN_new(), *b = BN_new();
		EC_GROUP_get_curve_GFp(self->group, p, a, b, self->ctx);

		const char *id;
		if(self->nid == -1) id = "custom";
		else id = OBJ_nid2sn(self->nid);
		char *pstr = BN_bn2dec(p);
		char *astr = BN_bn2dec(a);
		char *bstr = BN_bn2dec(b);
		PyObject *strObj = PyUnicode_FromFormat("Curve '%s' => y^2 = x^3 + a*x + b  (mod p):\np = %s\na = %s\nb = %s", id, (const char *) pstr,
												(const char *) astr, (const char *) bstr);
		OPENSSL_free(pstr); OPENSSL_free(astr); OPENSSL_free(bstr);
		BN_free(p); BN_free(a); BN_free(b);
		return strObj;
	}

	return (PyObject *) PyUnicode_FromString("");
}

PyObject *ECE_init(ECElement *self, PyObject *args) {
	GroupType type = NONE_G;
	ECElement *obj, *gobj = NULL;

	if(PyArg_ParseTuple(args, "Oi", &gobj, &type)) {
		Group_Init(gobj);

		if(type == G) {
			debug("init element in group G.\n");
			obj = createNewPoint(G, gobj); // ->group, gobj->ctx);
			return (PyObject *) obj;
		}
		else if(type == ZR) {
			debug("init element of ZR.\n");
			obj = createNewPoint(ZR, gobj); // ->group, gobj->ctx);
			return (PyObject *) obj;
		}
		else {
			EXIT_IF(TRUE, "invalid type selected.");
		}
	}
	EXIT_IF(TRUE, "invalid argument.");
}

PyObject *ECE_random(ECElement *self, PyObject *args) {

	GroupType type = NONE_G;
	ECElement *gobj = NULL;

	if(PyArg_ParseTuple(args, "Oi", &gobj, &type)) {
		Group_Init(gobj);

		if(type == G) {
			// generate a random element from ec group G.
			// call 'EC_POINT_set_compressed_coordinates_GFp' w/ group, P, x, 1, ctx
			// call 'EC_POINT_set_affine_coordinates_GFp' w/ group, P, x/y, ctx
			// test group membership 'EC_POINT_is_on_curve'
			ECElement *objG = createNewPoint(G, gobj); // ->group, gobj->ctx);
			BIGNUM *x = BN_new(), *y = BN_new(), *order = BN_new();
			EC_GROUP_get_order(gobj->group, order, gobj->ctx);
			int FindAnotherPoint = TRUE;
			START_CLOCK(dBench);
			do {
				// generate random point
				BN_rand_range(x, order);
				EC_POINT_set_compressed_coordinates_GFp(gobj->group, objG->P, x, 1, objG->ctx);
				EC_POINT_get_affine_coordinates_GFp(gobj->group, objG->P, x, y, objG->ctx);
				// make sure point is on curve and not zero

				if(BN_is_zero(x) || BN_is_zero(y)) {
					FindAnotherPoint = TRUE;
					continue;
				}

				if(EC_POINT_is_on_curve(gobj->group, objG->P, objG->ctx)) {
					FindAnotherPoint = FALSE;
				}
//				char *xstr = BN_bn2dec(x);
//				char *ystr = BN_bn2dec(y);
//				debug("P -> x = %s\n", xstr);
//				debug("P -> y = %s\n", ystr);
//				OPENSSL_free(xstr);
//				OPENSSL_free(ystr);
			} while(FindAnotherPoint);

			STOP_CLOCK(dBench);
			BN_free(x);
			BN_free(y);
			BN_free(order);
			return (PyObject *) objG;
		}
		else if(type == ZR) {
			ECElement *objZR = createNewPoint(ZR, gobj); // ->group, gobj->ctx);
			BIGNUM *order = BN_new();
			EC_GROUP_get_order(gobj->group, order, gobj->ctx);
			objZR->elemZ = BN_new();
			START_CLOCK(dBench);
			BN_rand_range(objZR->elemZ, order);
			STOP_CLOCK(dBench);
			BN_free(order);

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

	START_CLOCK(dBench);
	 if(EC_POINT_is_at_infinity(self->group, self->P)) {
		STOP_CLOCK(dBench);
		 Py_INCREF(Py_True);
		 return Py_True;
	 }

	 STOP_CLOCK(dBench);
	 Py_INCREF(Py_False);
	 return Py_False;
}

static PyObject *ECE_add(PyObject *o1, PyObject *o2) {
	ECElement *lhs = NULL, *rhs = NULL, *ans = NULL;
	BIGNUM *order = NULL;
	int foundLHS = FALSE, foundRHS = FALSE;

	Check_Types2(o1, o2, lhs, rhs, foundLHS, foundRHS);

   if(foundLHS) {
		debug("found lhs.\n");
		// if rhs == ZR, then convert lhs to a bn otherwise fail.
		if(rhs->point_init && rhs->type == ZR) {
			BIGNUM *lhs_val = BN_new();
			order = BN_new();
			setBigNum((PyLongObject *) o1, &lhs_val);
			ans = createNewPoint(ZR, rhs); // ->group, rhs->ctx);
			EC_GROUP_get_order(ans->group, order, ans->ctx);
			START_CLOCK(dBench);
			BN_mod_add(ans->elemZ, lhs_val, rhs->elemZ, order, ans->ctx);
			STOP_CLOCK(dBench);
			BN_free(lhs_val);
			BN_free(order);
			UPDATE_BENCHMARK(ADDITION, dBench);
			return (PyObject *) ans;
		}
	}
	else if(foundRHS) {
		debug("found rhs.\n");
		// if lhs == ZR, then convert rhs to a bn otherwise fail.
		if(lhs->point_init && lhs->type == ZR) {
			BIGNUM *rhs_val = BN_new();
			order = BN_new();
			setBigNum((PyLongObject *) o2, &rhs_val);
			ans = createNewPoint(ZR, lhs); // ->group, lhs->ctx);
			EC_GROUP_get_order(ans->group, order, ans->ctx);
			START_CLOCK(dBench);
			BN_mod_add(ans->elemZ, lhs->elemZ, rhs_val, order, ans->ctx);
			STOP_CLOCK(dBench);
			BN_free(rhs_val);
			BN_free(order);
			UPDATE_BENCHMARK(ADDITION, dBench);
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
			order = BN_new();
			ans = createNewPoint(ZR, lhs); // ->group, lhs->ctx);
			EC_GROUP_get_order(ans->group, order, ans->ctx);
			START_CLOCK(dBench);
			BN_mod_add(ans->elemZ, lhs->elemZ, rhs->elemZ, order, ans->ctx);
			STOP_CLOCK(dBench);
			BN_free(order);
			UPDATE_BENCHMARK(ADDITION, dBench);
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
	BIGNUM *order = NULL;
	int foundLHS = FALSE, foundRHS = FALSE;

	Check_Types2(o1, o2, lhs, rhs, foundLHS, foundRHS);

	if(foundLHS) {
		debug("found lhs.\n");
		// if rhs == ZR, then convert lhs to a bn otherwise fail.
		// only supported for elements of Long (lhs) and ZR (rhs)
		if(rhs->point_init && rhs->type == ZR) {
			BIGNUM *lhs_val = BN_new();
			order = BN_new();
			setBigNum((PyLongObject *) o1, &lhs_val);
			ans = createNewPoint(ZR, rhs); // ->group, rhs->ctx);
			EC_GROUP_get_order(ans->group, order, ans->ctx);
			START_CLOCK(dBench);
			BN_mod_sub(ans->elemZ, lhs_val, rhs->elemZ, order, ans->ctx);
			STOP_CLOCK(dBench);
			BN_free(lhs_val);
			BN_free(order);

			UPDATE_BENCHMARK(SUBTRACTION, dBench);
			return (PyObject *) ans;
		}
	}
	else if(foundRHS) {
		debug("found rhs.\n");
		// if lhs == ZR, then convert rhs to a bn otherwise fail.
		// only supported for elements of ZR (lhs) and Long (rhs)
		if(lhs->point_init && lhs->type == ZR) {
			BIGNUM *rhs_val = BN_new();
			order = BN_new();
			setBigNum((PyLongObject *) o2, &rhs_val);
			ans = createNewPoint(ZR, lhs); // ->group, lhs->ctx);
			EC_GROUP_get_order(ans->group, order, ans->ctx);
			START_CLOCK(dBench);
			BN_mod_sub(ans->elemZ, lhs->elemZ, rhs_val, order, ans->ctx);
			STOP_CLOCK(dBench);
			BN_free(rhs_val);
			BN_free(order);

			UPDATE_BENCHMARK(SUBTRACTION, dBench);
			return (PyObject *) ans;
		}
	}
	else {
		// check whether we have two Points
		Point_Init(lhs);
		Point_Init(rhs);

		if(ElementZR(lhs, rhs)) {
			IS_SAME_GROUP(lhs, rhs);
			order = BN_new();
			ans = createNewPoint(ZR, lhs); // ->group, lhs->ctx);
			EC_GROUP_get_order(ans->group, order, ans->ctx);
			START_CLOCK(dBench);
			BN_mod_sub(ans->elemZ, lhs->elemZ, rhs->elemZ, order, ans->ctx);
			STOP_CLOCK(dBench);

			UPDATE_BENCHMARK(SUBTRACTION, dBench);
			return (PyObject *) ans;
		}
		else {
			// not defined for other combinations
			EXIT_IF(TRUE, "invalid combination of operands.");
		}
	}


	EXIT_IF(TRUE, "invalid arguments.");
}

// TODO: Not complete...need to figure out how to multiply two points
// on an elliptic curve using point addition.
static PyObject *ECE_mul(PyObject *o1, PyObject *o2) {
	ECElement *lhs = NULL, *rhs = NULL, *ans = NULL;
	BIGNUM *order = NULL;
	int foundLHS = FALSE, foundRHS = FALSE;

	Check_Types2(o1, o2, lhs, rhs, foundLHS, foundRHS);

	if(foundLHS) {
		debug("found lhs.\n");
		// if rhs == ZR, then convert lhs to a bn otherwise fail.
		// only supported for elements of Long (lhs) and ZR (rhs)
		if(rhs->point_init && rhs->type == ZR) {
			BIGNUM *lhs_val = BN_new();
			order = BN_new();
			setBigNum((PyLongObject *) o1, &lhs_val);
			ans = createNewPoint(ZR, rhs); // ->group, rhs->ctx);
			EC_GROUP_get_order(ans->group, order, ans->ctx);
			START_CLOCK(dBench);
			BN_mod_mul(ans->elemZ, lhs_val, rhs->elemZ, order, ans->ctx);
			STOP_CLOCK(dBench);
			BN_free(lhs_val);
			BN_free(order);

			UPDATE_BENCHMARK(MULTIPLICATION, dBench);
			return (PyObject *) ans;
		}
	}
	else if(foundRHS) {
		debug("found rhs.\n");
		// if lhs == ZR, then convert rhs to a bn otherwise fail.
		// only supported for elements of ZR (lhs) and Long (rhs)
		if(lhs->point_init && lhs->type == ZR) {
			BIGNUM *rhs_val = BN_new();
			order = BN_new();
			setBigNum((PyLongObject *) o2, &rhs_val);
			ans = createNewPoint(ZR, lhs); // ->group, lhs->ctx);
			EC_GROUP_get_order(ans->group, order, ans->ctx);
			START_CLOCK(dBench);
			BN_mod_mul(ans->elemZ, lhs->elemZ, rhs_val, order, ans->ctx);
			STOP_CLOCK(dBench);
			BN_free(rhs_val);
			BN_free(order);

			UPDATE_BENCHMARK(MULTIPLICATION, dBench);
			return (PyObject *) ans;
		}
	}
	else {
		// check whether we have two Points
		Point_Init(lhs);
		Point_Init(rhs);
		IS_SAME_GROUP(lhs, rhs);

		if(ElementG(lhs, rhs)) {
			ans = createNewPoint(G, lhs); // ->group, lhs->ctx);
			START_CLOCK(dBench);
			EC_POINT_add(ans->group, ans->P, lhs->P, rhs->P, ans->ctx);
			STOP_CLOCK(dBench);
		}
		else if(ElementZR(lhs, rhs)) {
			order = BN_new();
			ans = createNewPoint(ZR, lhs); // ->group, lhs->ctx);
			EC_GROUP_get_order(ans->group, order, ans->ctx);
			START_CLOCK(dBench);
			BN_mod_mul(ans->elemZ, lhs->elemZ, rhs->elemZ, order, ans->ctx);
			STOP_CLOCK(dBench);
			BN_free(order);
		}
		else {

			EXIT_IF(TRUE, "elements are not of the same type.");
		}

		UPDATE_BENCHMARK(MULTIPLICATION, dBench);
		return (PyObject *) ans;
	}


	ErrorMsg("invalid argument.");
}

// TODO:
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
			ans = createNewPoint(ZR, rhs); // ->group, rhs->ctx);
			START_CLOCK(dBench);
			BN_div(ans->elemZ, rm, lhs_val, rhs->elemZ, ans->ctx);
			STOP_CLOCK(dBench);
			BN_free(lhs_val);
			BN_free(rm);

			UPDATE_BENCHMARK(DIVISION, dBench);
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
			ans = createNewPoint(ZR, lhs); // ->group, lhs->ctx);
			START_CLOCK(dBench);
			BN_div(ans->elemZ, rm, lhs->elemZ, rhs_val, ans->ctx);
			STOP_CLOCK(dBench);
			BN_free(rhs_val);
			BN_free(rm);

			UPDATE_BENCHMARK(DIVISION, dBench);
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
				ans = createNewPoint(G, lhs);
				START_CLOCK(dBench);
				EC_POINT_add(ans->group, ans->P, lhs->P, rhs_neg->P, ans->ctx);
				STOP_CLOCK(dBench);

				//PyObject_Del(rhs_neg);
				Py_XDECREF(rhs_neg);
			}
		}
		else if(ElementZR(lhs, rhs)) {
			ans = createNewPoint(ZR, lhs); // ->group, lhs->ctx);
			rm = BN_new();
			START_CLOCK(dBench);
			BN_div(ans->elemZ, rm, lhs->elemZ, rhs->elemZ, ans->ctx);
			BN_free(rm);
			STOP_CLOCK(dBench);
		}
		else {

			EXIT_IF(TRUE, "elements not the same type.");
		}

		UPDATE_BENCHMARK(DIVISION, dBench);
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
			ans = createNewPoint(ZR, rhs); // ->group, rhs->ctx);
			START_CLOCK(dBench);
			BN_mod(ans->elemZ, lhs_val, rhs->elemZ, ans->ctx);
			STOP_CLOCK(dBench);
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
			ans = createNewPoint(ZR, lhs); // ->group, lhs->ctx);
			START_CLOCK(dBench);
			BN_mod(ans->elemZ, lhs->elemZ, rhs_val, ans->ctx);
			STOP_CLOCK(dBench);
			BN_free(rhs_val);
			return (PyObject *) ans;
		}
	}
	else {
		Point_Init(lhs);
		Point_Init(rhs);

		if(ElementZR(lhs, rhs)) {
			ans = createNewPoint(ZR, lhs); // ->group, lhs->ctx);
			// reall calls BN_div with the dv se to NULL.
			BN_mod(ans->elemZ, lhs->elemZ, rhs->elemZ, ans->ctx);

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
	BIGNUM *order = NULL;
	int foundLHS = FALSE, foundRHS = FALSE;

	Check_Types2(o1, o2, lhs, rhs, foundLHS, foundRHS);

	if(foundLHS) {
		// TODO: implement for elements of Long ** ZR
		if(rhs->point_init && rhs->type == ZR) {
			BIGNUM *lhs_val = BN_new();
			order = BN_new();
			setBigNum((PyLongObject *) o1, &lhs_val);
			ans = createNewPoint(ZR, rhs); // ->group, rhs->ctx);
			EC_GROUP_get_order(ans->group, order, ans->ctx);
			START_CLOCK(dBench);
			BN_mod_exp(ans->elemZ, lhs_val, rhs->elemZ, order, ans->ctx);
			STOP_CLOCK(dBench);
			BN_free(lhs_val);
			BN_free(order);

			UPDATE_BENCHMARK(EXPONENTIATION, dBench);
			return (PyObject *) ans;
		}
		EXIT_IF(TRUE, "element type combination not supported.");
	}
	else if(foundRHS) {
		// TODO: implement for elements of G ** Long or ZR ** Long
		START_CLOCK(dBench);
		long rhs = PyLong_AsLong(o2);
		if(lhs->type == ZR) {
			if(PyErr_Occurred() || rhs >= 0) {
				// clear error and continue
//					PyErr_Print(); // for debug purposes
					PyErr_Clear();
					BIGNUM *rhs_val = BN_new();
					order = BN_new();
					setBigNum((PyLongObject *) o2, &rhs_val);

					ans = createNewPoint(ZR, lhs); // ->group, lhs->ctx);
					EC_GROUP_get_order(ans->group, order, ans->ctx);
					BN_mod_exp(ans->elemZ, lhs->elemZ, rhs_val, order, ans->ctx);
					BN_free(rhs_val);
					BN_free(order);
					STOP_CLOCK(dBench);
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
					ans = createNewPoint(G, lhs); // ->group, lhs->ctx);
					EC_POINT_mul(ans->group, ans->P, NULL, lhs->P, rhs_val, ans->ctx);

//					ans = ec_point_mul(lhs->group, lhs->P, rhs_val, lhs->ctx);
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

		UPDATE_BENCHMARK(EXPONENTIATION, dBench);
		return (PyObject *) ans;
	}
	else {
		// check whether we have two Points
		Point_Init(lhs);
		Point_Init(rhs);
		IS_SAME_GROUP(lhs, rhs);

		if(lhs->type == G && rhs->type == ZR) {
//			ans = ec_point_mul(lhs->nid, lhs->group, lhs->P, rhs->elemZ, lhs->ctx);
			ans = createNewPoint(G, lhs);
			EC_POINT_mul(ans->group, ans->P, NULL, lhs->P, rhs->elemZ, ans->ctx);
		}
		else if(ElementZR(lhs, rhs)) {
			ans = createNewPoint(ZR, lhs); // ->group, lhs->ctx);
			order = BN_new();
			EC_GROUP_get_order(ans->group, order, ans->ctx);
			START_CLOCK(dBench);
			BN_mod_exp(ans->elemZ, lhs->elemZ, rhs->elemZ, order, ans->ctx);
			STOP_CLOCK(dBench);
			BN_free(order);
		}
		else {

			EXIT_IF(TRUE, "cannot exponentiate two points.");
		}
		UPDATE_BENCHMARK(EXPONENTIATION, dBench);
		return (PyObject *) ans;
	}

	EXIT_IF(TRUE, "invalid arguments.");
}

/* assume 'self' is a valid ECElement instance */
ECElement *invertECElement(ECElement *self) {
	ECElement *newObj = NULL;
	if(self->type == G) {
		newObj = createNewPoint(G, self); // ->group, self->ctx);
		EC_POINT_copy(newObj->P, self->P);
		START_CLOCK(dBench);
		if(EC_POINT_invert(newObj->group, newObj->P, newObj->ctx)) {
			STOP_CLOCK(dBench);

			return newObj;
		}
		//PyObject_Del(newObj);
		Py_XDECREF(newObj);
	}
	else if(self->type == ZR) {
		// get modulus p and feed into
		BIGNUM *p = BN_new(); // , *a = BN_new(), *b = BN_new();
//		EC_GROUP_get_curve_GFp(self->group, p, a, b, self->ctx);
		EC_GROUP_get_order(self->group, p, self->ctx);
//		BN_free(a);
//		BN_free(b);
		START_CLOCK(dBench);
		BIGNUM *x = BN_mod_inverse(NULL, self->elemZ, p, self->ctx);
		STOP_CLOCK(dBench);
		if(x != NULL) {
			newObj = createNewPoint(ZR, self); // ->group, self->ctx);
			BN_copy(newObj->elemZ, x);
			BN_free(x);
			BN_free(p);
//			printf("Nothing to see here ppl.\n");
//			char *xstr = BN_bn2dec(newObj->elemZ);
//			debug("P -> x = %s\n", xstr);
//			OPENSSL_free(xstr);

			return newObj;
		}
		//PyObject_Del(newObj);
		Py_XDECREF(newObj);
		BN_free(p);

	}
	/* error */
//	ErrorMsg("invalid element type")
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
	EC_POINT_get_affine_coordinates_GFp(self->group, self->P, x, y, self->ctx);
	BN_set_negative(y, TRUE);

	newObj = createNewPoint(G, self); // ->group, self->ctx);
	EC_POINT_set_affine_coordinates_GFp(newObj->group, newObj->P, x, y, newObj->ctx);
	if(EC_POINT_is_on_curve(newObj->group, newObj->P, newObj->ctx)) {
		return newObj;
	}
	/* error */
	return NULL;
}

static PyObject *ECE_neg(PyObject *o1) {
	ECElement *obj1 = NULL, *obj2 = NULL;

	if(PyEC_Check(o1)) {
		obj1 = (ECElement *) o1;
		Point_Init(obj1);

		START_CLOCK(dBench);
		if(obj1->type == G) {
			if((obj2 = negatePoint(obj1)) != NULL) {
				STOP_CLOCK(dBench);
				return (PyObject *) obj2;
			}
			//PyObject_Del(obj2);
			Py_XDECREF(obj2);
		}
		else if(obj1->type == ZR) {
			// consider supporting this type.
			obj2 = createNewPoint(ZR, obj1);
			if(BN_copy(obj2->elemZ, obj1->elemZ) != NULL) {
				int negate;
				if(!BN_is_negative(obj2->elemZ)) negate = -1;
				else negate = 0;
				BN_set_negative(obj2->elemZ, negate);

				return (PyObject *) obj2;
			}
			//PyObject_Del(obj2);
			Py_XDECREF(obj2);
		}

	}


	EXIT_IF(TRUE, "invalid argument.");
}

static PyObject *ECE_long(PyObject *o1) {
	return NULL;
}

static PyObject *ECE_convertToZR(ECElement *self, PyObject *args) {
	ECElement *obj = NULL, *gobj = NULL;
	PyObject *retXY = NULL;

	/* gobj - initialized ec group object */
	/* obj - ecc point object on an elliptic curve */
	/* retXY => whether to return just x (Py_True) or x and y (Py_False) */
	if(PyArg_ParseTuple(args, "OOO", &gobj, &obj, &retXY)) {
		Group_Init(gobj);

		if(PyEC_Check(obj)) {
			// convert to
			Point_Init(obj);
			if(obj->type == G) {
				BIGNUM *x = BN_new(), *y = BN_new();
				EC_POINT_get_affine_coordinates_GFp(gobj->group, obj->P, x, y, gobj->ctx);
				if(PyBool_Check(retXY)) {
					// see if retXY is Py_True or Py_False
					if(retXY == Py_True) {
						debug("Py_True detected.\n");
						ECElement *X = createNewPoint(ZR, gobj); // ->group, gobj->ctx);
						ECElement *Y = createNewPoint(ZR, gobj); // ->group, gobj->ctx);
						BN_copy(X->elemZ, x);
						BN_copy(Y->elemZ, y);
						BN_free(x); BN_free(y);
						return (PyObject *) PyTuple_Pack(2, (PyObject *) X, (PyObject *) Y);
					}
					else {
						BN_free(y);
						ECElement *newObj = createNewPoint(ZR, gobj); // ->group, gobj->ctx);
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
	if(PyEC_Check(arg)) {
		ECElement *gobj = (ECElement *) arg;
		Group_Init(gobj);

		ECElement *order = createNewPoint(ZR, gobj); // ->group, self->ctx);
		EC_GROUP_get_order(self->group, order->elemZ, NULL);
		// return the order of the group
		return (PyObject *) order;
	}
	EXIT_IF(TRUE, "invalid argument.");
}

static PyObject *ECE_bitsize(ECElement *self, PyObject *arg) {
	if(PyEC_Check(arg)) {
		ECElement *gobj = (ECElement *) arg;
		Group_Init(gobj);

		BIGNUM *elemZ = BN_new();
		EC_GROUP_get_order(gobj->group, elemZ, NULL);
		size_t max_len = BN_num_bytes(elemZ) - RESERVED_ENCODING_BYTES;
		debug("order len in bytes => '%zd'\n", max_len);

		BN_free(elemZ);
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
			START_CLOCK(dBench);
			if(BN_cmp(lhs_val, rhs->elemZ) == 0) {
				if(opid == Py_EQ) result = TRUE;
			}
			else if(opid == Py_NE) result = TRUE;
			STOP_CLOCK(dBench);
			BN_free(lhs_val);
		}
		else {
			EXIT_IF(TRUE, "comparison types not supported."); }
	}
	else if(foundLongRHS) {
		if(lhs->type == ZR) {
			BIGNUM *rhs_val = BN_new();
			BN_set_word(rhs_val, PyLong_ToUnsignedLong(o2));
			START_CLOCK(dBench);
			if(BN_cmp(lhs->elemZ, rhs_val) == 0) {
				if(opid == Py_EQ) result = TRUE;
			}
			else if(opid == Py_NE) result = TRUE;
			STOP_CLOCK(dBench);
			BN_free(rhs_val);
		}
		else {

			EXIT_IF(TRUE, "comparison types not supported."); }
	}
	else {
//		Point_Init(lhs)
//		Point_Init(rhs)

		START_CLOCK(dBench);
		if(ElementG(lhs, rhs)) {
			if(EC_POINT_cmp(lhs->group, lhs->P, rhs->P, lhs->ctx) == 0) {
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
		STOP_CLOCK(dBench);
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
	if(PyEC_Check(arg)) {
		ECElement *gobj = (ECElement *) arg;
		Group_Init(gobj);

		ECElement *genObj = createNewPoint(G, gobj); // ->group, gobj->ctx);
		const EC_POINT *gen = EC_GROUP_get0_generator(gobj->group);
		EC_POINT_copy(genObj->P, gen);

		return (PyObject *) genObj;
	}
	EXIT_IF(TRUE, "invalid argument.");
}

/*
 * Takes an arbitrary string and returns a group element
 */
EC_POINT *element_from_hash(EC_GROUP *group, uint8_t *input, int input_len) {

	EC_POINT *P = NULL;
	BIGNUM *x = BN_new(), *y = BN_new();
	int TryNextX = TRUE;
	BIGNUM *p = BN_new(), *a = BN_new(), *b = BN_new();
	BN_CTX *ctx = BN_CTX_new();
	EC_GROUP_get_curve_GFp(group, p, a, b, ctx);
	BN_free(a);
	BN_free(b); // a,b not needed here...

	START_CLOCK(dBench);
	// assume input string is a binary string, then set x to (x mod q)
	x = BN_bin2bn((const uint8_t *) input, input_len, NULL);
	BN_mod(x, x, p, ctx);
	P = EC_POINT_new(group);
	do {
		// set x coordinate and then test whether it's on curve
		char *xstr = BN_bn2dec(x);
		debug("Generating another x => %s\n", xstr);
		OPENSSL_free(xstr);
		EC_POINT_set_compressed_coordinates_GFp(group, P, x, 1, ctx);
		EC_POINT_get_affine_coordinates_GFp(group, P, x, y, ctx);

		if(BN_is_zero(x) || BN_is_zero(y)) {
			BN_add(x, x, BN_value_one());
			continue;
		}

		if(EC_POINT_is_on_curve(group, P, ctx)) {
			TryNextX = FALSE;
		}
		else {
			BN_add(x, x, BN_value_one());
		}
	}while(TryNextX);

	STOP_CLOCK(dBench);
	BN_free(x);
	BN_free(y);
	BN_free(p);
	BN_CTX_free(ctx);
	return P;
}

static PyObject *ECE_hash(ECElement *self, PyObject *args) {

	char *msg = NULL;
	int msg_len;
	GroupType type;
	ECElement *hashObj = NULL, *gobj = NULL;

	// TODO: consider hashing string then generating an element from it's output
	if(PyArg_ParseTuple(args, "Os#i", &gobj, &msg, &msg_len, &type)) {
		Group_Init(gobj);
		// hash the message, then generate an element from the hash_buf
		uint8_t hash_buf[HASH_LEN+1];
		if(type == G) {
			START_CLOCK(dBench);
			hash_to_bytes((uint8_t *) msg, msg_len, HASH_LEN, hash_buf, HASH_FUNCTION_STR_TO_G_CRH);
			debug("Message => '%s'\n", msg);
			debug("Hash output => ");
			printf_buffer_as_hex(hash_buf, HASH_LEN);

			hashObj = createNewPoint(G, gobj); // ->group, gobj->ctx);
			hashObj->P = element_from_hash(gobj->group, (uint8_t *) hash_buf, HASH_LEN);
			STOP_CLOCK(dBench);
			return (PyObject *) hashObj;
		}
		else if(type == ZR) {
			START_CLOCK(dBench);
			hash_to_bytes((uint8_t *) msg, msg_len, HASH_LEN, hash_buf, HASH_FUNCTION_STR_TO_ZR_CRH);
			debug("Message => '%s'\n", msg);
			debug("Hash output => ");
			printf_buffer_as_hex(hash_buf, HASH_LEN);

			hashObj = createNewPoint(ZR, gobj); // ->group, gobj->ctx);
			BN_bin2bn((const uint8_t *) hash_buf, HASH_LEN, hashObj->elemZ);
			STOP_CLOCK(dBench);

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
	int msg_len, bits = -1, ctr = 1, ERROR_SET = FALSE; // always have a ctr start from 1
	BIGNUM *x = NULL, *y = NULL;
	ECElement *gobj = NULL;

	if(PyArg_ParseTuple(args, "OO|i", &gobj, &old_m, &bits)) {
		Group_Init(gobj);

		if(PyBytes_Check(old_m)) {
			old_msg = (uint8_t *) PyBytes_AS_STRING(old_m);
			msg_len = strlen((char *) old_msg);
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
		BIGNUM *order = BN_new();
		EC_GROUP_get_order(gobj->group, order, NULL);
		int max_len = (BN_num_bits(order) / BYTE);
		debug("max msg len => '%d'\n", max_len);

		char msg[max_len+2];
		msg[0] = msg_len & 0xFF;
		snprintf((msg+1), max_len+1, "%s", old_msg); //copying message over
		msg_len = msg_len + 1; //we added an extra byte

		debug("msg_len accepted => '%d'\n", msg_len);
		BN_free(order);

		if(bits > 0) {
			debug("bits were specified.\n");
		}
		else {
			// use default of 32-bits (4 bytes) to represent ctr
			if(msg_len + 1 <= max_len) {
				// concatenate msg
				int len = msg_len + sizeof(uint32_t);
				char *input = (char *) malloc(len + 1);
				memset(input, 0, len);
				memcpy(input, msg, msg_len);
				int TryNextCTR = TRUE;
				ECElement *encObj = NULL;
				do {

					/* 				1-byte    < max_len    ctr
					 * encoding [   size   |    msg     | \x01 \x00 \x00 \x00]
					 */
					*((uint32_t*)(input + msg_len)) = (uint32_t) ctr;
					len = strlen(input); // accounts for null bytes (if any) at the end

					if(len > max_len) {
						/* message probably cannot be encoded, reduce size */
						ERROR_SET=TRUE;
						break;
					}

					debug("input hex msg => ");
					// check if msg len is big enough to fit into length
					printf_buffer_as_hex((uint8_t *) input, len);
					encObj = createNewPoint(G, gobj); // ->group, gobj->ctx);
					x = BN_bin2bn((const uint8_t *) input, len, NULL);
					y = BN_new();
					char *xstr = BN_bn2dec(x);
					debug("gen x => %s\n", xstr);
					OPENSSL_free(xstr);
					EC_POINT_set_compressed_coordinates_GFp(encObj->group, encObj->P, x, 1, encObj->ctx);
					EC_POINT_get_affine_coordinates_GFp(encObj->group, encObj->P, x, y, encObj->ctx);

					if(BN_is_zero(x) || BN_is_zero(y)) {
						ctr++;
						continue;
					}

					if(EC_POINT_is_on_curve(encObj->group, encObj->P, encObj->ctx)) {
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
				EXIT_IF(TRUE, "message too large for selected group. Call object 'bitsize()' function for maximum message size.");

			}
		}

		// concatenate 'ctr' to buffer and set x coordinate and plot on curve
		// if point not on curve, increment ctr by 1
	}

	EXIT_IF(ERROR_SET, "Ran out of counters. So, could not be encode message at given length. make it smaller.");
	Py_INCREF(Py_False);

	return Py_False;
}

/*
 * Decode a group element to a message (PyUnicode_String)
 */
static PyObject *ECE_decode(ECElement *self, PyObject *args) {
	ECElement *obj = NULL, *gobj = NULL;

	if(PyArg_ParseTuple(args, "OO", &gobj, &obj)) {
		Group_Init(gobj);

		if(PyEC_Check(obj)) {
			BIGNUM *x = BN_new(), *y = BN_new();
			START_CLOCK(dBench);
			// TODO: verify that element is on the curve before getting coordinates
			EC_POINT_get_affine_coordinates_GFp(gobj->group, obj->P, x, y, gobj->ctx);

			int x_len = BN_num_bytes(x);
			uint8_t *xstr = (uint8_t*) malloc(x_len + 1);
			memset(xstr, 0, x_len);
			debug("Size of xstr => '%d'\n", x_len);
			BN_bn2bin(x, xstr);
			debug("Decoded x => ");
			printf_buffer_as_hex((uint8_t *) xstr, x_len);

//			printf_buffer_as_hex((uint8_t *) xstr, x_len-sizeof(uint32_t));
//			uint8_t msg[x_len-sizeof(uint32_t) + 1];
//			strncpy((char *) msg, (char *) xstr, x_len-sizeof(uint32_t));

			STOP_CLOCK(dBench);
			BN_free(x);
			BN_free(y);

			// TODO: redo this portion
			// int size_msg = msg[0];
			int size_msg = xstr[0];  // first byte should be length of string and can throw away the rest.
//			char m[129];
//			*m = '\0';
//			strncat(m, (char*)(msg+1), size_msg);
			char m[129];
			*m = '\0';
			strncat(m, (char*)(xstr+1), size_msg);

			OPENSSL_free(xstr);
			//return PyUnicode_FromFormat("%s", m);
			return PyBytes_FromStringAndSize(m, size_msg);
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
			START_CLOCK(dBench);
			size_t len = EC_POINT_point2oct(obj->group, obj->P, POINT_CONVERSION_COMPRESSED,  p_buf, MAX_BUF, obj->ctx);
			EXIT_IF(len == 0, "could not serialize point.");

			STOP_CLOCK(dBench);
			debug("Serialized point => ");
			printf_buffer_as_hex(p_buf, len);
			size_t length = 0;
			char *base64_buf = NewBase64Encode(p_buf, len, FALSE, &length);

			PyObject *result = PyBytes_FromString((const char *) base64_buf);
			PyObject *obj2 = PyBytes_FromFormat("%d:", obj->type);
			PyBytes_ConcatAndDel(&obj2, result);

			return obj2;
		}
		else if(obj->point_init && obj->type == ZR) {
			size_t len = BN_num_bytes(obj->elemZ);
			uint8_t z_buf[len+1];
			memset(z_buf, 0, len);
			START_CLOCK(dBench);
			if(BN_bn2bin(obj->elemZ, z_buf) == len) {
				// we're okay
				// convert z_buf to base64 and the rest is history.
				STOP_CLOCK(dBench);
				size_t length = 0;
				char *base64_buf = NewBase64Encode(z_buf, len, FALSE, &length);

				PyObject *result = PyBytes_FromString((const char *) base64_buf);
				PyObject *obj2 = PyBytes_FromFormat("%d:", obj->type);
				PyBytes_ConcatAndDel(&obj2, result);
				return obj2;
			}
		}
	}


	return NULL;
}

static PyObject *Deserialize(ECElement *self, PyObject *args)
{
	PyObject *obj = NULL;
	ECElement *gobj = NULL;

	if(PyArg_ParseTuple(args, "OO", &gobj, &obj)) {
		Group_Init(gobj);
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
				START_CLOCK(dBench);
				EC_POINT_oct2point(gobj->group, newObj->P, (const uint8_t *) buf, len, gobj->ctx);

				if(EC_POINT_is_on_curve(newObj->group, newObj->P, newObj->ctx)) {
					STOP_CLOCK(dBench);
					return (PyObject *) newObj;
				}
			}
			else if(type == ZR) {
				ECElement *newObj = createNewPoint(type, gobj); // ->group, gobj->ctx);
				START_CLOCK(dBench);
				BN_bin2bn((const uint8_t *) buf, len, newObj->elemZ);
				STOP_CLOCK(dBench);
				return (PyObject *) newObj;
			}

			Py_INCREF(Py_False);
			return Py_False;
		}
		else {
			EXIT_IF(TRUE, "invalid object type");
		}
	}
	EXIT_IF(TRUE, "invalid argument");
}

#ifdef BENCHMARK_ENABLED
InitBenchmark_CAPI(_init_benchmark, dBench, 2);
StartBenchmark_CAPI(_start_benchmark, dBench);
EndBenchmark_CAPI(_end_benchmark, dBench);
GetBenchmark_CAPI(_get_benchmark, dBench);
GetAllBenchmarks_CAPI(_get_all_results, dBench);
ClearBenchmarks_CAPI(_clear_benchmark, dBench);
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
	0,                         /*tp_str*/
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
    0,                         /*tp_repr*/
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

struct module_state {
	PyObject *error;
#ifdef BENCHMARK_ENABLED
	Benchmark *dBench;
#endif
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
		{"InitBenchmark", (PyCFunction)_init_benchmark, METH_NOARGS, "Initialize a benchmark object"},
		{"StartBenchmark", (PyCFunction)_start_benchmark, METH_VARARGS, "Start a new benchmark with some options"},
		{"EndBenchmark", (PyCFunction)_end_benchmark, METH_VARARGS, "End a given benchmark"},
		{"GetBenchmark", (PyCFunction)_get_benchmark, METH_VARARGS, "Returns contents of a benchmark object"},
		{"GetGeneralBenchmarks", (PyCFunction) _get_all_results, METH_VARARGS, "Retrieve general benchmark info as a dictionary."},
		{"ClearBenchmark", (PyCFunction)_clear_benchmark, METH_VARARGS, "Clears content of benchmark object"},
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
#ifdef BENCHMARK_ENABLED
	Py_CLEAR(GETSTATE(m)->dBench);
#endif
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

#define INITERROR return NULL
PyMODINIT_FUNC
PyInit_elliptic_curve(void) 		{
#else
#define INITERROR return
void initelliptic_curve(void) 		{
#endif
	PyObject *m;
    if(PyType_Ready(&ECType) < 0)
    	INITERROR;

#if PY_MAJOR_VERSION >= 3
	m = PyModule_Create(&moduledef);
#else
	m = Py_InitModule("elliptic_curve", ec_methods);
#endif

	if(m == NULL)
		INITERROR;
	struct module_state *st = GETSTATE(m);
	st->error = PyErr_NewException("elliptic_curve.Error", NULL, NULL);
	if(st->error == NULL) {
		Py_DECREF(m);
		INITERROR;
	}

#ifdef BENCHMARK_ENABLED
    if(import_benchmark() < 0) {
    	Py_DECREF(m);
    	INITERROR;
    }
    if(PyType_Ready(&BenchmarkType) < 0)
    	INITERROR;
    st->dBench = PyObject_New(Benchmark, &BenchmarkType);
    dBench = st->dBench;
    dBench->bench_initialized = FALSE;
    InitClear(dBench);
#endif

	Py_INCREF(&ECType);
	PyModule_AddObject(m, "elliptic_curve", (PyObject *)&ECType);
    Py_INCREF(&BenchmarkType);
    PyModule_AddObject(m, "benchmark", (PyObject *)&BenchmarkType);

	PyModule_AddIntConstant(m, "G", G);
	PyModule_AddIntConstant(m, "ZR", ZR);
	PyECErrorObject = st->error;
#ifdef BENCHMARK_ENABLED
	ADD_BENCHMARK_OPTIONS(m);
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

#if PY_MAJOR_VERSION >= 3
	return m;
#endif
}
