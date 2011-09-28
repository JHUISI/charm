/*
 * Elliptic Curve Module - based on lib MIRACL
 * TODO: need parameter setting,
 */
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
ECElement *createNewPoint(GroupType type, EC_GROUP *group, BN_CTX *ctx) {

	ECElement *newObj = PyObject_New(ECElement, &ECType);
	if(type == ZR) {
		newObj->type = type;
		newObj->elemZ = BN_new();
		newObj->P = NULL;
	}
	else if(type == G) {
		newObj->type = type;
		newObj->P = EC_POINT_new(group);
		newObj->elemZ = NULL;
	}
	else {
		PyObject_Del(newObj);
		return NULL;
	}
	newObj->point_init = TRUE;
	newObj->nid = -1;
	newObj->group = group;
	newObj->group_init = FALSE;
	newObj->ctx = ctx;
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
	ECElement *obj;

	Group_Init(self)

	if(PyArg_ParseTuple(args, "i", &type)) {

		if(type == G) {
			debug("init element in group G.\n");
			obj = createNewPoint(G, self->group, self->ctx);
			return (PyObject *) obj;
		}
		else if(type == ZR) {
			debug("init element of ZR.\n");
			obj = createNewPoint(ZR, self->group, self->ctx);
			return (PyObject *) obj;
		}
		else {
			ErrorMsg("invalid type selected.");
		}
	}
	ErrorMsg("invalid argument.")
}

PyObject *ECE_random(ECElement *self, PyObject *args) {

	GroupType type = NONE_G;
	Group_Init(self);

	if(PyArg_ParseTuple(args, "i", &type)) {
		if(type == G) {
			// generate a random element from ec group G.
			// call 'EC_POINT_set_compressed_coordinates_GFp' w/ group, P, x, 1, ctx
			// call 'EC_POINT_set_affine_coordinates_GFp' w/ group, P, x/y, ctx
			// test group membership 'EC_POINT_is_on_curve'
			ECElement *objG = createNewPoint(G, self->group, self->ctx);
			BIGNUM *x = BN_new(), *y = BN_new(), *order = BN_new();
			EC_GROUP_get_order(self->group, order, self->ctx);
			int FindAnotherPoint = TRUE;
//			START_CLOCK(dBench);
			do {
				// generate random point
				BN_rand_range(x, order);
				EC_POINT_set_compressed_coordinates_GFp(self->group, objG->P, x, 1, objG->ctx);
				EC_POINT_get_affine_coordinates_GFp(self->group, objG->P, x, y, objG->ctx);
				// make sure point is on curve and not zero

				if(BN_is_zero(x) || BN_is_zero(y)) {
					FindAnotherPoint = TRUE;
					continue;
				}

				if(EC_POINT_is_on_curve(self->group, objG->P, objG->ctx)) {
					FindAnotherPoint = FALSE;
				}
//				char *xstr = BN_bn2dec(x);
//				char *ystr = BN_bn2dec(y);
//				debug("P -> x = %s\n", xstr);
//				debug("P -> y = %s\n", ystr);
//				OPENSSL_free(xstr);
//				OPENSSL_free(ystr);
			} while(FindAnotherPoint);

//			STOP_CLOCK(dBench);
			BN_free(x);
			BN_free(y);
			BN_free(order);
			return (PyObject *) objG;
		}
		else if(type == ZR) {
			ECElement *objZR = createNewPoint(ZR, self->group, self->ctx);
			BIGNUM *order = BN_new();
			EC_GROUP_get_order(self->group, order, self->ctx);
			objZR->elemZ = BN_new();
//			START_CLOCK(dBench);
			BN_rand_range(objZR->elemZ, order);
//			STOP_CLOCK(dBench);
			BN_free(order);

			return (PyObject *) objZR;
		}
		else {

			ErrorMsg("invalid object type.");
		}
	}


	ErrorMsg("invalid argument.");
}

static PyObject *ECE_is_infinity(ECElement *self, PyObject *args) {

	Point_Init(self)
	if(self->type != G) {
		ErrorMsg("element not of type G.");
		return NULL;
	}

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

	Check_Types2(o1, o2, lhs, rhs, foundLHS, foundRHS)

   if(foundLHS) {
		debug("found lhs.\n");
		// if rhs == ZR, then convert lhs to a bn otherwise fail.
		if(rhs->point_init && rhs->type == ZR) {
			BIGNUM *lhs_val = BN_new();
			order = BN_new();
			setBigNum((PyLongObject *) o1, &lhs_val);
			ans = createNewPoint(ZR, rhs->group, rhs->ctx);
			EC_GROUP_get_order(ans->group, order, ans->ctx);
			START_CLOCK(dBench);
			BN_mod_add(ans->elemZ, lhs_val, rhs->elemZ, order, ans->ctx);
			STOP_CLOCK(dBench);
			BN_free(lhs_val);
			BN_free(order);
			UPDATE_BENCHMARK(ADDITION, dBench)
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
			ans = createNewPoint(ZR, lhs->group, lhs->ctx);
			EC_GROUP_get_order(ans->group, order, ans->ctx);
			START_CLOCK(dBench);
			BN_mod_add(ans->elemZ, lhs->elemZ, rhs_val, order, ans->ctx);
			STOP_CLOCK(dBench);
			BN_free(rhs_val);
			BN_free(order);
			UPDATE_BENCHMARK(ADDITION, dBench)
			return (PyObject *) ans;
		}
	}
	else {
		// check whether we have two Points
		Point_Init(lhs)
		Point_Init(rhs)
		if(ElementZR(lhs, rhs)) {
			// easy, just call BN_add
			order = BN_new();
			ans = createNewPoint(ZR, lhs->group, lhs->ctx);
			EC_GROUP_get_order(ans->group, order, ans->ctx);
			START_CLOCK(dBench);
			BN_mod_add(ans->elemZ, lhs->elemZ, rhs->elemZ, order, ans->ctx);
			STOP_CLOCK(dBench);
			BN_free(order);
			UPDATE_BENCHMARK(ADDITION, dBench)
			return (PyObject *) ans;
		}
		else { // if(lhs->type == G && rhs->type == ZR) or vice versa operation undefined...

			ErrorMsg("adding the a group element G to ZR is undefined.")
		}
	}


	ErrorMsg("invalid arguments.")
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

	Check_Types2(o1, o2, lhs, rhs, foundLHS, foundRHS)

	if(foundLHS) {
		debug("found lhs.\n");
		// if rhs == ZR, then convert lhs to a bn otherwise fail.
		// only supported for elements of Long (lhs) and ZR (rhs)
		if(rhs->point_init && rhs->type == ZR) {
			BIGNUM *lhs_val = BN_new();
			order = BN_new();
			setBigNum((PyLongObject *) o1, &lhs_val);
			ans = createNewPoint(ZR, rhs->group, rhs->ctx);
			EC_GROUP_get_order(ans->group, order, ans->ctx);
			START_CLOCK(dBench);
			BN_mod_sub(ans->elemZ, lhs_val, rhs->elemZ, order, ans->ctx);
			STOP_CLOCK(dBench);
			BN_free(lhs_val);
			BN_free(order);

			UPDATE_BENCHMARK(SUBTRACTION, dBench)
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
			ans = createNewPoint(ZR, lhs->group, lhs->ctx);
			EC_GROUP_get_order(ans->group, order, ans->ctx);
			START_CLOCK(dBench);
			BN_mod_sub(ans->elemZ, lhs->elemZ, rhs_val, order, ans->ctx);
			STOP_CLOCK(dBench);
			BN_free(rhs_val);
			BN_free(order);

			UPDATE_BENCHMARK(SUBTRACTION, dBench)
			return (PyObject *) ans;
		}
	}
	else {
		// check whether we have two Points
		Point_Init(lhs)
		Point_Init(rhs)

		if(ElementZR(lhs, rhs)) {
			order = BN_new();
			ans = createNewPoint(ZR, lhs->group, lhs->ctx);
			EC_GROUP_get_order(ans->group, order, ans->ctx);
			START_CLOCK(dBench);
			BN_mod_sub(ans->elemZ, lhs->elemZ, rhs->elemZ, order, ans->ctx);
			STOP_CLOCK(dBench);

			UPDATE_BENCHMARK(SUBTRACTION, dBench)
			return (PyObject *) ans;
		}
		else {
			// not defined for other combinations

			ErrorMsg("invalid combination of operands.");
		}
	}


	ErrorMsg("invalid arguments.");
}

// TODO: Not complete...need to figure out how to multiply two points
// on an elliptic curve using point addition.
static PyObject *ECE_mul(PyObject *o1, PyObject *o2) {
	ECElement *lhs = NULL, *rhs = NULL, *ans = NULL;
	BIGNUM *order = NULL;
	int foundLHS = FALSE, foundRHS = FALSE;

	Check_Types2(o1, o2, lhs, rhs, foundLHS, foundRHS)

	if(foundLHS) {
		debug("found lhs.\n");
		// if rhs == ZR, then convert lhs to a bn otherwise fail.
		// only supported for elements of Long (lhs) and ZR (rhs)
		if(rhs->point_init && rhs->type == ZR) {
			BIGNUM *lhs_val = BN_new();
			order = BN_new();
			setBigNum((PyLongObject *) o1, &lhs_val);
			ans = createNewPoint(ZR, rhs->group, rhs->ctx);
			EC_GROUP_get_order(ans->group, order, ans->ctx);
			START_CLOCK(dBench);
			BN_mod_mul(ans->elemZ, lhs_val, rhs->elemZ, order, ans->ctx);
			STOP_CLOCK(dBench);
			BN_free(lhs_val);
			BN_free(order);

			UPDATE_BENCHMARK(MULTIPLICATION, dBench)
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
			ans = createNewPoint(ZR, lhs->group, lhs->ctx);
			EC_GROUP_get_order(ans->group, order, ans->ctx);
			START_CLOCK(dBench);
			BN_mod_mul(ans->elemZ, lhs->elemZ, rhs_val, order, ans->ctx);
			STOP_CLOCK(dBench);
			BN_free(rhs_val);
			BN_free(order);

			UPDATE_BENCHMARK(MULTIPLICATION, dBench)
			return (PyObject *) ans;
		}
	}
	else {
		// check whether we have two Points
		Point_Init(lhs)
		Point_Init(rhs)

		if(ElementG(lhs, rhs)) {
			ans = createNewPoint(G, lhs->group, lhs->ctx);
			START_CLOCK(dBench);
			EC_POINT_add(ans->group, ans->P, lhs->P, rhs->P, ans->ctx);
			STOP_CLOCK(dBench);
		}
		else if(ElementZR(lhs, rhs)) {
			order = BN_new();
			ans = createNewPoint(ZR, lhs->group, lhs->ctx);
			EC_GROUP_get_order(ans->group, order, ans->ctx);
			START_CLOCK(dBench);
			BN_mod_mul(ans->elemZ, lhs->elemZ, rhs->elemZ, order, ans->ctx);
			STOP_CLOCK(dBench);
			BN_free(order);
		}
		else {

			ErrorMsg("elements are not of the same type.");
		}

		UPDATE_BENCHMARK(MULTIPLICATION, dBench)
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

	Check_Types2(o1, o2, lhs, rhs, foundLHS, foundRHS)

	if(foundLHS) {
		debug("found lhs.\n");
		// if rhs == ZR, then convert lhs to a bn otherwise fail.
		// only supported for elements of Long (lhs) and ZR (rhs)
		if(rhs->point_init && rhs->type == ZR) {
			BIGNUM *lhs_val = BN_new();
			rm = BN_new();
			setBigNum((PyLongObject *) o1, &lhs_val);
			ans = createNewPoint(ZR, rhs->group, rhs->ctx);
			START_CLOCK(dBench);
			BN_div(ans->elemZ, rm, lhs_val, rhs->elemZ, ans->ctx);
			STOP_CLOCK(dBench);
			BN_free(lhs_val);
			BN_free(rm);

			UPDATE_BENCHMARK(DIVISION, dBench)
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
			ans = createNewPoint(ZR, lhs->group, lhs->ctx);
			START_CLOCK(dBench);
			BN_div(ans->elemZ, rm, lhs->elemZ, rhs_val, ans->ctx);
			STOP_CLOCK(dBench);
			BN_free(rhs_val);
			BN_free(rm);

			UPDATE_BENCHMARK(DIVISION, dBench)
			return (PyObject *) ans;
		}
	}
	else {
		// check whether we have two Points
		Point_Init(lhs)
		Point_Init(rhs)

		if(ElementG(lhs, rhs)) {
			ECElement *rhs_neg = negatePoint(rhs);
			if(rhs_neg != NULL) {
				ans = createNewPoint(G, lhs->group, lhs->ctx);
				START_CLOCK(dBench);
				EC_POINT_add(ans->group, ans->P, lhs->P, rhs_neg->P, ans->ctx);
				STOP_CLOCK(dBench);

				PyObject_Del(rhs_neg);

				return (PyObject *) ans;
			}
		}
		else if(ElementZR(lhs, rhs)) {
			ans = createNewPoint(ZR, lhs->group, lhs->ctx);
			rm = BN_new();
			START_CLOCK(dBench);
			BN_div(ans->elemZ, rm, lhs->elemZ, rhs->elemZ, ans->ctx);
			BN_free(rm);
			STOP_CLOCK(dBench);
		}
		else {

			ErrorMsg("elements not the same type.");
		}


		UPDATE_BENCHMARK(DIVISION, dBench)
		return (PyObject *) ans;
	}


	ErrorMsg("invalid argument.");
}

static PyObject *ECE_rem(PyObject *o1, PyObject *o2) {
	;
	ECElement *lhs = NULL, *rhs = NULL, *ans = NULL;
	int foundLHS = FALSE, foundRHS = FALSE;

	Check_Types2(o1, o2, lhs, rhs, foundLHS, foundRHS)

	if(foundLHS) {
		debug("found lhs.\n");
		// if rhs == ZR, then convert lhs to a bn otherwise fail.
		// only supported for elements of Long (lhs) and ZR (rhs)
		if(rhs->point_init && rhs->type == ZR) {
			BIGNUM *lhs_val = BN_new();
			setBigNum((PyLongObject *) o1, &lhs_val);
			ans = createNewPoint(ZR, rhs->group, rhs->ctx);
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
			ans = createNewPoint(ZR, lhs->group, lhs->ctx);
			START_CLOCK(dBench);
			BN_mod(ans->elemZ, lhs->elemZ, rhs_val, ans->ctx);
			STOP_CLOCK(dBench);
			BN_free(rhs_val);
			return (PyObject *) ans;
		}
	}
	else {
		Point_Init(lhs)
		Point_Init(rhs)

		if(ElementZR(lhs, rhs)) {
			ans = createNewPoint(ZR, lhs->group, lhs->ctx);
			// reall calls BN_div with the dv se to NULL.
			BN_mod(ans->elemZ, lhs->elemZ, rhs->elemZ, ans->ctx);

			return (PyObject *) ans;
		}
		else {

			ErrorMsg("invalid combination of element types")
		}
	}


	ErrorMsg("invalid argument type.")
}

ECElement *ec_point_mul(EC_GROUP *group, EC_POINT *point, BIGNUM *value, BN_CTX *ctx) {

	// get the cofactor
//	BIGNUM *cofactor = BN_new(), *order = BN_new();
//	EC_GROUP_get_cofactor(group, cofactor, NULL);
//	EC_GROUP_get_order(group, order, NULL);

	// save the generator for the group
//	if(EC_POINT_is_on_curve(group, point, ctx)) {
//		EC_GROUP_set_generator(group, point, order, cofactor);
//	}

	ECElement *ans = createNewPoint(G, group, ctx);
	START_CLOCK(dBench);
//	EC_POINT_mul(group, ans->P, value, NULL, NULL, ctx);
	EC_POINT_mul(group, ans->P, NULL, point, value, ctx);
	STOP_CLOCK(dBench);
//	BN_free(cofactor);
//	BN_free(order);
	return ans;
}

static PyObject *ECE_pow(PyObject *o1, PyObject *o2, PyObject *o3) {
	ECElement *lhs = NULL, *rhs = NULL, *ans = NULL;
	BIGNUM *order = NULL;
	int foundLHS = FALSE, foundRHS = FALSE;

	Check_Types2(o1, o2, lhs, rhs, foundLHS, foundRHS)

	if(foundLHS) {
		// TODO: implement for elements of Long ** ZR
		if(rhs->point_init && rhs->type == ZR) {
			BIGNUM *lhs_val = BN_new();
			order = BN_new();
			setBigNum((PyLongObject *) o1, &lhs_val);
			ans = createNewPoint(ZR, rhs->group, rhs->ctx);
			EC_GROUP_get_order(ans->group, order, ans->ctx);
			START_CLOCK(dBench);
			BN_mod_exp(ans->elemZ, lhs_val, rhs->elemZ, order, ans->ctx);
			STOP_CLOCK(dBench);
			BN_free(lhs_val);
			BN_free(order);

			UPDATE_BENCHMARK(EXPONENTIATION, dBench)
			return (PyObject *) ans;
		}
		ErrorMsg("element type combination not supported.")
	}
	else if(foundRHS) {
		// TODO: implement for elements of G ** Long or ZR ** Long
		if(lhs->point_init && lhs->type == ZR) {

			if(_PyLong_Sign(o2) == -1)  {
				debug("finding modular inverse.\n");
				ans = invertECElement(lhs);
			}
			else {
				BIGNUM *rhs_val = BN_new();
				order = BN_new();
				setBigNum((PyLongObject *) o2, &rhs_val);

				ans = createNewPoint(ZR, lhs->group, lhs->ctx);
				EC_GROUP_get_order(ans->group, order, ans->ctx);
				START_CLOCK(dBench);
				BN_mod_exp(ans->elemZ, lhs->elemZ, rhs_val, order, ans->ctx);
				STOP_CLOCK(dBench);
				BN_free(rhs_val);
				BN_free(order);
			}
//			UPDATE_BENCHMARK(EXPONENTIATION, dBench)
//			return (PyObject *) ans;
		}
		else if(lhs->point_init && lhs->type == G) {
			BIGNUM *rhs_val = BN_new();
			setBigNum((PyLongObject *) o2, &rhs_val);
			// ans = createNewPoint(G, lhs->group, lhs->ctx);
			// EC_POINT_copy(ans->P, lhs->P);
			// EC_POINT_mul(ans->group, ans->P, rhs_val, NULL, NULL, ans->ctx);
			ans = ec_point_mul(lhs->group, lhs->P, rhs_val, lhs->ctx);
		}
		else {
			ErrorMsg("element type combination not supported.")
		}

		UPDATE_BENCHMARK(EXPONENTIATION, dBench)
		return (PyObject *) ans;
	}
	else {
		// check whether we have two Points
		Point_Init(lhs)
		Point_Init(rhs)

//		if(lhs->type == ZR && rhs->type == G) {
			// ans = createNewPoint(G, lhs->group, lhs->ctx);
			// EC_POINT_copy(ans->P, rhs->P);
			// EC_POINT_mul(ans->group, ans->P, lhs->elemZ, NULL, NULL, ans->ctx);
//			ans = ec_point_mul(lhs->group, rhs->P, lhs->elemZ, lhs->ctx);
//		}
		if(lhs->type == G && rhs->type == ZR) {
			// ans = createNewPoint(G, lhs->group, lhs->ctx);
			// EC_POINT_copy(ans->P, lhs->P);
			// EC_POINT_mul(ans->group, ans->P, rhs->elemZ, NULL, NULL, ans->ctx);
			ans = ec_point_mul(lhs->group, lhs->P, rhs->elemZ, lhs->ctx);
		}
		else if(ElementZR(lhs, rhs)) {
			ans = createNewPoint(ZR, lhs->group, lhs->ctx);
			order = BN_new();
			EC_GROUP_get_order(ans->group, order, ans->ctx);
			START_CLOCK(dBench);
			BN_mod_exp(ans->elemZ, lhs->elemZ, rhs->elemZ, order, ans->ctx);
			STOP_CLOCK(dBench);
			BN_free(order);
		}
		else {

			ErrorMsg("cannot exponentiate two points.")
		}
		UPDATE_BENCHMARK(EXPONENTIATION, dBench)
		return (PyObject *) ans;
	}


	ErrorMsg("invalid arguments.")
}

/* assume 'self' is a valid ECElement instance */
ECElement *invertECElement(ECElement *self) {
	ECElement *newObj = NULL;
	if(self->type == G) {
		newObj = createNewPoint(G, self->group, self->ctx);
		EC_POINT_copy(newObj->P, self->P);
		START_CLOCK(dBench);
		if(EC_POINT_invert(newObj->group, newObj->P, newObj->ctx)) {
			STOP_CLOCK(dBench);

			return newObj;
		}
		PyObject_Del(newObj);
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
			newObj = createNewPoint(ZR, self->group, self->ctx);
			BN_copy(newObj->elemZ, x);
			BN_free(x);
			BN_free(p);
//			printf("Nothing to see here ppl.\n");
//			char *xstr = BN_bn2dec(newObj->elemZ);
//			debug("P -> x = %s\n", xstr);
//			OPENSSL_free(xstr);

			return newObj;
		}
		PyObject_Del(newObj);
		BN_free(p);

	}
	/* error */
//	ErrorMsg("invalid element type")
	return NULL;
}

static PyObject *ECE_invert(PyObject *o1) {

	if(PyEC_Check(o1)) {
		ECElement *obj1 = (ECElement *) o1;
		Point_Init(obj1)

		ECElement *obj2 = invertECElement(obj1);

		if(obj2 != NULL) {

			return (PyObject *) obj2;
		}

		ErrorMsg("could not find inverse of element.")
	}

	ErrorMsg("invalid argument type.");
}

/* assume 'self' is a valid ECElement instance */
ECElement *negatePoint(ECElement *self) {
	ECElement *newObj = NULL;

	BIGNUM *x = BN_new(), *y = BN_new();
	EC_POINT_get_affine_coordinates_GFp(self->group, self->P, x, y, self->ctx);
	BN_set_negative(y, TRUE);

	newObj = createNewPoint(G, self->group, self->ctx);
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
		Point_Init(obj1)

		START_CLOCK(dBench);
		if(obj1->type == G) {
			if((obj2 = negatePoint(obj1)) != NULL) {
				STOP_CLOCK(dBench);
				return (PyObject *) obj2;
			}
			PyObject_Del(obj2);
		}
		else if(obj1->type == ZR) {
			// consider supporting this type.
		}

	}


	ErrorMsg("invalid argument.");
}

static PyObject *ECE_long(PyObject *o1) {
	return NULL;
}

static PyObject *ECE_convertToZR(ECElement *self, PyObject *args) {
	Group_NULL(self);
	Group_Init(self);
	ECElement *obj = NULL;
	PyObject *retXY = NULL;

	/* obj - ecc point object on an elliptic curve */
	/* retXY => whether to return just x (Py_True) or x and y (Py_False) */
	if(PyArg_ParseTuple(args, "OO", &obj, &retXY)) {
		if(PyEC_Check(obj)) {
			// convert to
			Point_Init(obj);
			if(obj->type == G) {
				BIGNUM *x = BN_new(), *y = BN_new();
				EC_POINT_get_affine_coordinates_GFp(self->group, obj->P, x, y, self->ctx);
				if(PyBool_Check(retXY)) {
					// see if retXY is Py_True or Py_False
					if(retXY == Py_True) {
						debug("Py_True detected.\n");
						ECElement *X = createNewPoint(ZR, self->group, self->ctx);
						ECElement *Y = createNewPoint(ZR, self->group, self->ctx);
						BN_copy(X->elemZ, x);
						BN_copy(Y->elemZ, y);
						BN_free(x); BN_free(y);
						return (PyObject *) PyTuple_Pack(2, (PyObject *) X, (PyObject *) Y);
					}
					else {
						BN_free(y);
						ECElement *newObj = createNewPoint(ZR, self->group, self->ctx);
						BN_copy(newObj->elemZ, x);
						BN_free(x);
						return (PyObject *) newObj;
					}
				}
			}
		}

		ErrorMsg("invalid type.");
	}
	ErrorMsg("invalid argument.");
}
//
//static PyObject *ECE_convertToZR(ECElement *self, PyObject *args) {
//	Group_NULL(self);
//	Group_Init(self);
//	ECElement *obj = NULL;
//
//	if(PyArg_ParseTuple(args, "O", &obj)) {
//		if(PyEC_Check(obj)) {
//			Point_Init(obj);
//			if(obj->type == G) {
//
//			}
//		}
//	}
//}

static PyObject *ECE_getOrder(ECElement *self) {
	Group_Init(self)
	ECElement *order = createNewPoint(ZR, self->group, self->ctx);
	EC_GROUP_get_order(self->group, order->elemZ, NULL);

	return (PyObject *) order;
}

static PyObject *ECE_equals(PyObject *o1, PyObject *o2, int opid) {
	if(opid != Py_EQ && opid != Py_NE) {
		ErrorMsg("'==' and '!=' only comparisons supported.")
	}

	int foundLongLHS = FALSE, foundLongRHS = FALSE, result = FALSE;
	ECElement *lhs = NULL, *rhs = NULL;
	Check_Types2(o1, o2, lhs, rhs, foundLongLHS, foundLongRHS)

	if(foundLongLHS) {
		if(rhs->type == ZR) {
			BIGNUM *lhs_val = BN_new();
			BN_set_word(lhs_val, PyLong_AsUnsignedLong(o1));
			START_CLOCK(dBench);
			if(BN_cmp(lhs_val, rhs->elemZ) == 0) {
				if(opid == Py_EQ) result = TRUE;
			}
			else if(opid == Py_NE) result = TRUE;
			STOP_CLOCK(dBench);
			BN_free(lhs_val);
		}
		else {
			PROFILE_STOP;
			ErrorMsg("comparison types not supported.") }
	}
	else if(foundLongRHS) {
		if(lhs->type == ZR) {
			BIGNUM *rhs_val = BN_new();
			BN_set_word(rhs_val, PyLong_AsUnsignedLong(o2));
			START_CLOCK(dBench);
			if(BN_cmp(lhs->elemZ, rhs_val) == 0) {
				if(opid == Py_EQ) result = TRUE;
			}
			else if(opid == Py_NE) result = TRUE;
			STOP_CLOCK(dBench);
			BN_free(rhs_val);
		}
		else {

			ErrorMsg("comparison types not supported.") }
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

			ErrorMsg("cannot compare point to an integer.\n") }
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

static PyObject *ECE_getGen(ECElement *self) {

	Group_Init(self)
	ECElement *genObj = createNewPoint(G, self->group, self->ctx);
	const EC_POINT *gen = EC_GROUP_get0_generator(self->group);
	EC_POINT_copy(genObj->P, gen);

	return (PyObject *) genObj;
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
	ECElement *hashObj = NULL;
	Group_Init(self)

	// TODO: consider hashing string then generating an element from it's output
	if(PyArg_ParseTuple(args, "s#i", &msg, &msg_len, &type)) {
		// hash the message, then generate an element from the hash_buf
		uint8_t hash_buf[HASH_LEN+1];
		if(type == G) {
			START_CLOCK(dBench);
			hash_to_bytes((uint8_t *) msg, msg_len, HASH_LEN, hash_buf, HASH_FUNCTION_STR_TO_G_CRH);
			debug("Message => '%s'\n", msg);
			debug("Hash output => ");
			printf_buffer_as_hex(hash_buf, HASH_LEN);

			hashObj = createNewPoint(G, self->group, self->ctx);
			hashObj->P = element_from_hash(self->group, (uint8_t *) hash_buf, HASH_LEN);
			STOP_CLOCK(dBench);
			return (PyObject *) hashObj;
		}
		else if(type == ZR) {
			START_CLOCK(dBench);
			hash_to_bytes((uint8_t *) msg, msg_len, HASH_LEN, hash_buf, HASH_FUNCTION_STR_TO_ZR_CRH);
			debug("Message => '%s'\n", msg);
			debug("Hash output => ");
			printf_buffer_as_hex(hash_buf, HASH_LEN);

			hashObj = createNewPoint(ZR, self->group, self->ctx);
			BN_bin2bn((const uint8_t *) hash_buf, HASH_LEN, hashObj->elemZ);
			STOP_CLOCK(dBench);

			return (PyObject *) hashObj;
		}
		else {

			ErrorMsg("invalid argument type")
		}
	}


	ErrorMsg("invalid arguments")
}

/*
 * Encode a message as a group element
 */
static PyObject *ECE_encode(ECElement *self, PyObject *args) {
	char *old_msg;
	//char *msg = NULL;
	int msg_len, bits = -1, ctr = 0;
	BIGNUM *x = NULL, *y = NULL;
	Group_Init(self)

	if(PyArg_ParseTuple(args, "s#|i", &old_msg, &msg_len, &bits)) {
		debug("Encoding hex msg => ");
		// check if msg len is big enough to fit into length
		printf_buffer_as_hex((uint8_t *) old_msg, msg_len);
		debug("len => '%d'\n", msg_len);

		// make sure msg will fit into group (get order num bits / 8)
		BIGNUM *order = BN_new();
		EC_GROUP_get_order(self->group, order, NULL);
		int max_len = (BN_num_bits(order) / BYTE);

		debug("max msg len => '%d'\n", max_len);

		//longest message can be is 128 characters (1024 bits) => check on this!!!
		char msg[max_len+1];
		snprintf(msg, max_len+1, "%02d%s", msg_len, old_msg); //2 digit number (always)
		msg_len = msg_len + 2;

		BN_free(order);

		if(bits > 0) {
			debug("bits were specified.\n");
		}
		else {
			// use default of 32-bits (4 bytes) to represent ctr
			if(msg_len + sizeof(uint32_t) <= max_len) {
				// concatenate msg
				int len = msg_len + sizeof(uint32_t);
				char *input = (char *) malloc(len + 1);
				memset(input, 0, len);
				memcpy(input, msg, msg_len);
				int TryNextCTR = TRUE;
				ECElement *encObj = NULL;
				do {
					*((uint32_t*)(input + msg_len)) = (uint32_t) ctr;
					debug("input hex msg => ");
					// check if msg len is big enough to fit into length
					printf_buffer_as_hex((uint8_t *) input, len);
					encObj = createNewPoint(G, self->group, self->ctx);
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
				printf("ERROR: message too large to be encoded. Max len = '%d'\n", max_len);
			}
		}

		// concatenate 'ctr' to buffer and set x coordinate and plot on curve
		// if point not on curve, increment ctr by 1
	}
	Py_INCREF(Py_False);

	return Py_False;
}

/*
 * Decode a group element to a message (PyUnicode_String)
 */
static PyObject *ECE_decode(ECElement *self, PyObject *args) {
	ECElement *obj = NULL;
	Group_Init(self)

	if(PyArg_ParseTuple(args, "O", &obj)) {
		if(PyEC_Check(obj)) {
			BIGNUM *x = BN_new(), *y = BN_new();
			START_CLOCK(dBench);
			EC_POINT_get_affine_coordinates_GFp(self->group, obj->P, x, y, self->ctx);

			int x_len = BN_num_bytes(x);
			uint8_t *xstr = (uint8_t*) malloc(x_len + 1);
			debug("Size of xstr => '%d'\n", x_len);
			BN_bn2bin(x, xstr);
			debug("Decoded x => ");
			printf_buffer_as_hex((uint8_t *) xstr, x_len-sizeof(uint32_t));
			uint8_t msg[x_len-sizeof(uint32_t) + 1];
			strncpy((char *) msg, (char *) xstr, x_len-sizeof(uint32_t));
			STOP_CLOCK(dBench);
			OPENSSL_free(xstr);
			BN_free(x);
			BN_free(y);

			char int_str[3];//two character representation of size (w/ null byte)
			//strncpy(int_str, (const char *)Rop, 3);
			//int_str[4] = '\0';

			*int_str = '\0';
			strncat(int_str, (char*)msg, 2);

			int size_msg = atoi(int_str);

			char m[129];

			*m = '\0';
			strncat(m, (char*)(msg+2), size_msg);

			return PyUnicode_FromFormat("%s", m);
		}
	}


	ErrorMsg("invalid argument")
}

static PyObject *Serialize(ECElement *self, PyObject *args) {
	Group_NULL(self)

	ECElement *obj = NULL;
	if(!PyArg_ParseTuple(args, "O", &obj)) {
		printf("ERROR: invalid argument.\n");
		return NULL;
	}


	if(obj != NULL && PyEC_Check(obj)) {
		// allows export a compressed string
		if(obj->point_init && obj->type == G) {
			uint8_t p_buf[MAX_BUF+1];
			memset(p_buf, 0, MAX_BUF);
			START_CLOCK(dBench);
			size_t len = EC_POINT_point2oct(obj->group, obj->P, POINT_CONVERSION_COMPRESSED,  p_buf, MAX_BUF, self->ctx);
			if(len == 0) {

				ErrorMsg("could not serialize point.")
			}

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
	Group_Init(self)

	if(PyArg_ParseTuple(args, "O", &obj)) {
		if(PyBytes_Check(obj)) {
			// char *buf = PyBytes_AsString(obj);
			unsigned char *serial_buf = (unsigned char *) PyBytes_AsString(obj);
			GroupType type = atoi((const char *) &(serial_buf[0]));
			uint8_t *base64_buf = (uint8_t *)(serial_buf + 2);
//			size_t len = strlen((const char *) base64_buf);

			size_t deserialized_len = 0;
			uint8_t *buf = NewBase64Decode((const char *) base64_buf, strlen((char *) base64_buf), &deserialized_len);
			size_t len = deserialized_len;
			debug("Deserialize this => ");
			printf_buffer_as_hex(buf, len);
			if(type == G) {
				ECElement *newObj = createNewPoint(type, self->group, self->ctx);
				START_CLOCK(dBench);
				EC_POINT_oct2point(self->group, newObj->P, (const uint8_t *) buf, len, self->ctx);

				if(EC_POINT_is_on_curve(newObj->group, newObj->P, newObj->ctx)) {
					STOP_CLOCK(dBench);
					return (PyObject *) newObj;
				}
			}
			else if(type == ZR) {
				ECElement *newObj = createNewPoint(type, self->group, self->ctx);
				START_CLOCK(dBench);
				BN_bin2bn((const uint8_t *) buf, len, newObj->elemZ);
				STOP_CLOCK(dBench);
				return (PyObject *) newObj;
			}

			Py_INCREF(Py_False);
			return Py_False;
		}
		else {
			ErrorMsg("invalid object type")
		}
	}
	ErrorMsg("invalid argument")
}


InitBenchmark_CAPI(_init_benchmark, dBench, 2)
StartBenchmark_CAPI(_start_benchmark, dBench)
EndBenchmark_CAPI(_end_benchmark, dBench)
GetBenchmark_CAPI(_get_benchmark, dBench)

PyMemberDef ECElement_members[] = {
	{"type", T_INT, offsetof(ECElement, type), 0,
		"group type"},
    {"initialized", T_INT, offsetof(ECElement, point_init), 0,
		"determine initialization status"},
    {NULL}  /* Sentinel */
};

PyMethodDef ECElement_methods[] = {
		{"init", (PyCFunction)ECE_init, METH_VARARGS, "Create an element in a specific group G or ZR."},
		{"random", (PyCFunction)ECE_random, METH_VARARGS, "Return a random element in a specific group G or ZR."},
		{"getOrder", (PyCFunction)ECE_getOrder, METH_NOARGS, "Return the order of a group."},
		{"getGenerator", (PyCFunction)ECE_getGen, METH_NOARGS, "Get the generator of the group."},
		{"isInf", (PyCFunction)ECE_is_infinity, METH_NOARGS, "Checks whether a point is at infinity."},
//		{"bitsize", (PyCFunction)ECE_bitsize, METH_NOARGS, "Returns number of bytes to represent a message."},
		{"serialize", (PyCFunction)Serialize, METH_VARARGS, "Serialize an element to a string"},
		{"deserialize", (PyCFunction)Deserialize, METH_VARARGS, "Deserialize an element to G or ZR"},
		{"hash", (PyCFunction)ECE_hash, METH_VARARGS, "Perform a hash of a string to a group element of G."},
		{"encode", (PyCFunction)ECE_encode, METH_VARARGS, "Encode string as a group element of G"},
		{"decode", (PyCFunction)ECE_decode, METH_VARARGS, "Decode group element to a string."},
		{"getXY", (PyCFunction)ECE_convertToZR, METH_VARARGS, "Returns the x and/or y coordinates of point on an elliptic curve."},
		{NULL}
};

#if PY_MAJOR_VERSION >= 3
PyNumberMethods ecc_number = {
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
	"ecc.Element",             /*tp_name*/
	sizeof(ECElement),         /*tp_basicsize*/
	0,                         /*tp_itemsize*/
	(destructor)ECElement_dealloc, /*tp_dealloc*/
	0,                         /*tp_print*/
	0,                         /*tp_getattr*/
	0,                         /*tp_setattr*/
	0,			   				/*tp_reserved*/
	(reprfunc)ECElement_print, /*tp_repr*/
	&ecc_number,               /*tp_as_number*/
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
PyNumberMethods ecc_number = {
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
    "ecc.Element",             /*tp_name*/
    sizeof(ECElement),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)ECElement_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    &ecc_number,       /*tp_as_number*/
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
	Benchmark *dBench;
};

#if PY_MAJOR_VERSION >= 3
#define GETSTATE(m) ((struct module_state *) PyModule_GetState(m))
#else
#define GETSTATE(m) (&_state)
static struct module_state _state;
#endif

static PyMethodDef ecc_methods[] = {
		{"InitBenchmark", (PyCFunction)_init_benchmark, METH_NOARGS, "Initialize a benchmark object"},
		{"StartBenchmark", (PyCFunction)_start_benchmark, METH_VARARGS, "Start a new benchmark with some options"},
		{"EndBenchmark", (PyCFunction)_end_benchmark, METH_VARARGS, "End a given benchmark"},
		{"GetBenchmark", (PyCFunction)_get_benchmark, METH_VARARGS, "Returns contents of a benchmark object"},
		{NULL, NULL}
};


#if PY_MAJOR_VERSION >= 3
static int ecc_traverse(PyObject *m, visitproc visit, void *arg) {
	Py_VISIT(GETSTATE(m)->error);
	return 0;
}

static int ecc_clear(PyObject *m) {
	Py_CLEAR(GETSTATE(m)->error);
	Py_CLEAR(GETSTATE(m)->dBench);
	return 0;
}

static struct PyModuleDef moduledef = {
		PyModuleDef_HEAD_INIT,
		"ecc",
		NULL,
		sizeof(struct module_state),
		ecc_methods,
		NULL,
		ecc_traverse,
		ecc_clear,
		NULL
};

#define INITERROR return NULL
PyMODINIT_FUNC
PyInit_ecc(void) 		{
#else
#define INITERROR return
void initecc(void) 		{
#endif
	PyObject *module;
    if(PyType_Ready(&ECType) < 0)
    	INITERROR;

#if PY_MAJOR_VERSION >= 3
	module = PyModule_Create(&moduledef);
#else
	module = Py_InitModule("ecc", ecc_methods);
#endif

	if(module == NULL)
		INITERROR;
	struct module_state *st = GETSTATE(module);
	st->error = PyErr_NewException("ecc.Error", NULL, NULL);
	if(st->error == NULL) {
		Py_DECREF(module);
		INITERROR;
	}

    if(import_benchmark() < 0)
    	INITERROR;
    if(PyType_Ready(&BenchmarkType) < 0)
    	INITERROR;
    st->dBench = PyObject_New(Benchmark, &BenchmarkType);
    dBench = st->dBench;
    dBench->bench_initialized = FALSE;

	Py_INCREF(&ECType);
	PyModule_AddObject(module, "ecc", (PyObject *)&ECType);
	PyModule_AddIntConstant(module, "G", G);
	PyModule_AddIntConstant(module, "ZR", ZR);
	PyECErrorObject = st->error;
//	PyObject *d = PyModule_GetDict(module);

	PyModule_AddIntConstant(module, "CpuTime", CPU_TIME);
	PyModule_AddIntConstant(module, "RealTime", REAL_TIME);
	PyModule_AddIntConstant(module, "NativeTime", NATIVE_TIME);
	PyModule_AddIntConstant(module, "Add", ADDITION);
	PyModule_AddIntConstant(module, "Sub", SUBTRACTION);
	PyModule_AddIntConstant(module, "Mul", MULTIPLICATION);
	PyModule_AddIntConstant(module, "Div", DIVISION);
	PyModule_AddIntConstant(module, "Exp", EXPONENTIATION);

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
	return module;
#endif
}
