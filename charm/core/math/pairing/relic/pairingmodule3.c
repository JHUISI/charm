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
 *   @file    pairingmodule3.c
 *
 *   @brief   charm interface over RELIC's pairing-based crypto module
 *
 *   @author  ayo.akinyele@charm-crypto.com
 *
 ************************************************************************/

// TODO: fix 1 / a (ZR) ==> 0 instead of inverse of a!

#include "pairingmodule3.h"

int exp_rule(GroupType lhs, GroupType rhs)
{
	if(lhs == ZR && rhs == ZR) return TRUE;
	if(lhs == G1 && rhs == ZR) return TRUE;
	if(lhs == G2 && rhs == ZR) return TRUE;
	if(lhs == GT && rhs == ZR) return TRUE;
	return FALSE; /* Fail all other cases */
}

int mul_rule(GroupType lhs, GroupType rhs)
{
	if(lhs == rhs) return TRUE;
	if(lhs == ZR || rhs == ZR) return TRUE;
	return FALSE; /* Fail all other cases */
}

int add_rule(GroupType lhs, GroupType rhs)
{
	if(lhs == rhs && lhs != GT) return TRUE;
	return FALSE; /* Fail all other cases */
}

int sub_rule(GroupType lhs, GroupType rhs)
{
	if(lhs == rhs && lhs != GT) return TRUE;
	return FALSE; /* Fail all other cases */
}

int div_rule(GroupType lhs, GroupType rhs)
{
	if(lhs == rhs) return TRUE;
	return FALSE; /* Fail all other cases */
}

int pair_rule(GroupType lhs, GroupType rhs)
{
	if(lhs == G1 && rhs == G2) return TRUE;
	return FALSE; /* Fall all other cases: only for MNT case */
}

int check_type(GroupType type) {
	if(type == ZR || type == G1 || type == G2 || type == GT) return TRUE;
	return FALSE;
}

#define ERROR_TYPE(operand, ...) "unsupported "#operand" operand types: "#__VA_ARGS__

#define UNARY(f, m, n) \
static PyObject *f(PyObject *v) { \
	if(PyElement_Check(v)) {  \
	   Element *obj1 = (Element *) v; \
	   return (n)(obj1);	\
	} return NULL; \
}

#define BINARY(f, m, n) \
static PyObject *f(PyObject *v, PyObject *w) { \
	Element *obj1 = NULL, *obj2 = NULL;			\
	int obj1_long = FALSE, obj2_long = FALSE; 	\
	debug("Performing the '%s' operation.\n", __func__); \
	if(PyElement_Check(v)) {	\
		obj1 = (Element *) v; } \
	else if(PyNumber_Check(v)) { obj1 = convertToZR(v, w); obj1_long = TRUE; }  \
	else { PyErr_SetString(ElementError, ERROR_TYPE(left, int,bytes,str)); \
		return NULL; }			\
	if(PyElement_Check(w)) {	\
		obj2 = (Element *) w; } \
	else if(PyNumber_Check(w)) { obj2 = convertToZR(w, v); obj2_long = TRUE; }  \
 	else { PyErr_SetString(ElementError, ERROR_TYPE(right, int,bytes,str)); \
		return NULL; }		\
	if(Check_Types(obj1->element_type, obj2->element_type, m))	{ \
		PyObject *obj3 = (n)(obj1, obj2); \
		if(obj1_long) PyObject_Del(obj1); 	\
		if(obj2_long) PyObject_Del(obj2);	\
		return obj3;  }	\
	return NULL;				\
}

PyObject *intToLongObj(integer_t x)
{
	/* borrowed from gmpy */
	int size;
	bn_size_str(&size, x, 2);
	size = (size + PyLong_SHIFT - 1) / PyLong_SHIFT;
	int i;
	integer_t m;
	dig_t t;
	bn_inits(m);
	PyLongObject *l = _PyLong_New (size);
	if (!l)
		return NULL;
	bn_copy(m, x);
#ifdef DEBUG
	printf("%s: integer :=> ", __FUNCTION__);
	bn_print(m);
#endif
	for (i = 0; i < size; i++)
	{
		bn_get_dig(&t, m);
		l->ob_digit[i] = (digit) (((uint32_t) t) & PyLong_MASK);
		bn_rsh(m, m, PyLong_SHIFT);
#ifdef DEBUG
		printf("%s: integer :=> ", __FUNCTION__);
		bn_print(m);
#endif
	}
	i = size;
	while ((i > 0) && (l->ob_digit[i - 1] == 0))
		i--;
	Py_SIZE(l) = i;
	bn_free(m);
	return (PyObject *) l;
}

int longObjToInt(integer_t m, PyLongObject * p)
{
	int size, i, tmp = Py_SIZE(p);
	if(m == NULL) return -1;
	integer_t t, t2;
	bn_inits(t);
	bn_inits(t2);

	if (tmp > 0)
		size = tmp;
	else
		size = -tmp; // negate size value

	bn_zero(m);
	for (i = 0; i < size; i++)
	{
		bn_set_dig(t, p->ob_digit[i]);
		bn_lsh(t2, t, PyLong_SHIFT * i);
		bn_add(m, m, t2);
	}
	bn_free(t);
	bn_free(t2);

	return 0;
}


char *convert_buffer_to_hex(uint8_t * data, size_t len)
{
	size_t i;
	char tmp1[3];
	char *tmp = (char *) malloc(len * 3);
	memset(tmp, 0, len*3 - 1);
	
	for (i = 0; i < len; i++) {
		snprintf(tmp1, 3, "%02X ", data[i]);
		strcat(tmp, tmp1);
	}	
	
	return tmp;
}

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

// simply checks that the elements satisfy the properties for the given
// binary operation. Whitelist approach: only return TRUE for valid cases, otherwise FALSE
int Check_Types(GroupType l_type, GroupType r_type, char op)
{	
	switch (op) {
		// Rules: elements must be of the same type, multiplicative operations should be only used for
		// elements in field GT
		case 'a':	
			if(l_type == GT || r_type == GT) { return FALSE; }
			break;
		case 's':
			if(l_type == GT || r_type == GT) { return FALSE; }			
			break;
		case 'e':
			if(l_type != G1 && r_type != G2) { return FALSE; }
			break;
		case 'p':
			// rule for exponentiation for types
			if(l_type != G1 && l_type != G2 && l_type != GT && l_type != ZR) { return FALSE; }
			break;
		default:
			break;
	}
	
	return TRUE;
	
}

// assumes that pairing structure has been initialized
static Element *createNewElement(GroupType element_type, Pairing *pairing) {
	debug("Create an object of type Element\n");
	Element *retObject = PyObject_New(Element, &ElementType);
//	retObject->e = (element_ptr) malloc(sizeof(element_t));
	if(element_type == ZR) {
		element_init_Zr(retObject->e, 0); // , pairing->pair_obj);
		retObject->element_type = ZR;
	}
	else if(element_type == G1) {

		element_init_G1(retObject->e); // , pairing->pair_obj);
		retObject->element_type = G1;
	}
	else if(element_type == G2) {
		element_init_G2(retObject->e); // , pairing->pair_obj);
		retObject->element_type = G2;
	}
	else if(element_type == GT) {
		element_init_GT(retObject->e); // , pairing->pair_obj);
		retObject->element_type = GT;
	}
	
	retObject->elem_initialized = TRUE;
	retObject->pairing = NULL;
	retObject->safe_pairing_clear = FALSE;
	retObject->param_buf = NULL;		
	
	return retObject;	
}

Element *convertToZR(PyObject *longObj, PyObject *elemObj) {
	Element *self = (Element *) elemObj;
	Element *new = createNewElement(ZR, self->pairing);

	integer_t x;
	bn_inits(x);
#if PY_MAJOR_VERSION < 3
	longObj = PyNumber_Long(longObj);
#endif
	longObjToInt(x, (PyLongObject *) longObj);
	element_set_int(new->e, x);
	bn_free(x);
	return new;
}

void 	Pairing_dealloc(Pairing *self)
{
	if(self->safe) {
		debug("Clear pairing => \n");
		pairing_clear();
	}

	debug("Releasing pairing object!\n");
	Py_TYPE(self)->tp_free((PyObject *) self);
}

void	Element_dealloc(Element* self)
{
	if(self->elem_initialized && self->e) {
		debug_e("Clear element_t => \n", self->e);
		element_clear(self->e);
	}
	
	if(self->param_buf) {
//		debug("param_buf => %p\n", ); get_config?
	}
	
	if(self->safe_pairing_clear) {
		/* do nothing */
	}

	Py_TYPE(self)->tp_free((PyObject*)self);
}

// helper method 
ssize_t read_file(FILE *f, char** out) 
{
	if(f != NULL) {
		/* See how big the file is */
		fseek(f, 0L, SEEK_END);
		ssize_t out_len = ftell(f);
		debug("out_len: %zd\n", out_len);
		if(out_len <= MAX_LEN) {
			/* allocate that amount of memory only */
			if((*out = (char *) malloc(out_len+1)) != NULL) {
				fseek(f, 0L, SEEK_SET);
				if(fread(*out, sizeof(char), out_len, f) > 0)
				    return out_len;
				else
				    return -1;
			}
		}
	}

	return 0;
}

// take a previous hash and concatenate with serialized bytes of element and hashes into output buf
int hash2_element_to_bytes(element_t *e, uint8_t* last_buf, int hash_size, uint8_t* output_buf) {
	// assume last buf contains a hash
	int last_buflen = hash_size;
	int buf_len = SHA_LEN;
	uint8_t temp_buf[SHA_LEN + 1];
	memset(temp_buf, 0, SHA_LEN);
	element_to_key(*e, temp_buf, SHA_LEN, HASH_FUNCTION_ELEMENTS);

	uint8_t temp2_buf[last_buflen + buf_len + 1];
	memset(temp2_buf, 0, (last_buflen + buf_len));
	strncat((char *) temp2_buf, (char *) last_buf, last_buflen);
	strncat((char *) temp2_buf, (char *) temp_buf, SHA_LEN);

	debug("%s: input buf...\n", __FUNCTION__);
	printf_buffer_as_hex(temp2_buf, last_buflen + buf_len);
	// hash the temp2_buf to bytes
	int result = hash_buffer_to_bytes(temp2_buf, (last_buflen + buf_len), output_buf, hash_size, HASH_FUNCTION_STRINGS);
	return result;
}

int hash2_buffer_to_bytes(uint8_t *input_str, int input_len, uint8_t *last_hash, int hash_size, uint8_t *output_buf) {

	// concatenate last_buf + input_str (to len), then hash to bytes into output_buf
	int result;
	// copy the last hash buffer into temp buf
	// copy the current input string into buffer
	PyObject *last = PyBytes_FromStringAndSize((const char *) last_hash, (Py_ssize_t) hash_size);
	PyObject *input = PyBytes_FromStringAndSize((const char *) input_str, (Py_ssize_t) input_len);

	PyBytes_ConcatAndDel(&last, input);
	uint8_t *temp_buf = (uint8_t *) PyBytes_AsString(last);

	// hash the contents of temp_buf
	debug("last_hash => ");
	printf_buffer_as_hex(last_hash, hash_size);

	debug("input_str => ");
	printf_buffer_as_hex(input_str, input_len);

	debug("temp_buf => ");
	printf_buffer_as_hex(temp_buf, input_len + hash_size);

	result = hash_buffer_to_bytes(temp_buf, (input_len + hash_size), output_buf, hash_size, HASH_FUNCTION_STRINGS+1);

	PyObject_Del(last);
	return result;
}

PyObject *Element_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    Element *self;
	
    self = (Element *)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->elem_initialized = FALSE;
		self->safe_pairing_clear = FALSE;
//		self->pairing = NULL;
		self->element_type = NIL;
		self->param_buf = NULL;
    }
	
    return (PyObject *)self;
}

PyObject *Pairing_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	Pairing *self = (Pairing *) type->tp_alloc(type, 0);
	if(self != NULL) {
		self->safe = TRUE;
	}

	return (PyObject *) self;
}

int Pairing_init(Pairing *self, PyObject *args)
{
	return 0;
}


int Element_init(Element *self, PyObject *args, PyObject *kwds)
{
	int bits = 0, string_len = 0;
	int seed = -1;
	char *string = NULL;
//	Pairing *pairing;
//	uint8_t hash_id[HASH_LEN+1];
	
    static char *kwlist[] = {"bits", "string", "seed", NULL};
	
    if (! PyArg_ParseTupleAndKeywords(args, kwds, "|is#i", kwlist,
                                      &bits, &string, &string_len, &seed)) {
    	PyErr_SetString(ElementError, "invalid arguments");
        return -1; 
	}

    if(pairing_init() != ELEMENT_OK) {
//    	printf("%s: Using RELIC library...\n", __FUNCTION__);
    	PyErr_SetString(ElementError, "could not initialize pairing object.");
    	return -1;
    }

	self->elem_initialized = FALSE;
	self->safe_pairing_clear = TRUE;
    return 0;
}
 
static PyObject *Element_elem(Element* self, PyObject* args)
{
	Element *retObject, *group = NULL;
	int type;
	PyObject *long_obj = NULL;
	
	if(!PyArg_ParseTuple(args, "Oi|O", &group, &type, &long_obj)) {
		EXIT_IF(TRUE, "invalid arguments.");
	}
	
	debug("init an element.\n");
	if(type == ZR) {
		retObject = createNewElement(type, group->pairing);
	}
	else {
		EXIT_IF(TRUE, "unrecognized group type.");
	}

	if(long_obj != NULL && PyLong_Check(long_obj)) {
		integer_t m;
		bn_inits(m);
		longObjToInt(m, (PyLongObject *) long_obj);
		element_set_int(retObject->e, m);
		bn_free(m);
	}
	
	/* return Element object */
	return (PyObject *) retObject;		
}


PyObject *Element_print(Element* self)
{
	PyObject *strObj;
	debug("Contents of element object\n");

	if(self->elem_initialized) {

//		element_printf("element_t :=> \n", self->e);

		char str[MAX_BUF + 1];
		memset(str, 0, MAX_BUF);
	 	element_to_str(str, MAX_BUF, self->e);;
		strObj = PyUnicode_FromStringAndSize((const char *) str, MAX_BUF);
		if(strObj != NULL)
			return strObj;
		else
			return PyUnicode_FromString("");
	}

	return PyUnicode_FromString("");
}

static PyObject *Element_random(Element* self, PyObject* args)
{
	Element *retObject,*group = NULL;
	int arg1;
	int e_type = -1, seed = -1;

	/* create a new object */
	if(!PyArg_ParseTuple(args, "Oi|i", &group, &arg1, &seed))
		return NULL;

	START_CLOCK(dBench);
	VERIFY_GROUP(group);
	retObject = PyObject_New(Element, &ElementType);
	debug("init random element in '%d'\n", arg1);
// mem alloc alternatives
//		retObject->e = (element_ptr) malloc(sizeof(element_t));
	if(arg1 == ZR) {
		element_init_Zr(retObject->e, 0);
		e_type = ZR;
	}
	else if(arg1 == G1) {
		element_init_G1(retObject->e);
		e_type = G1;
	}
	else if(arg1 == G2) {
		element_init_G2(retObject->e);
		e_type = G2;
	}
	else if(arg1 == GT) {
		EXIT_IF(TRUE, "cannot generate random elements in GT.");
	}
	else {
		EXIT_IF(TRUE, "unrecognized group type.");
	}

	/* create new Element object */
	element_random(retObject->e);
	STOP_CLOCK(dBench);
	retObject->elem_initialized = TRUE;
	retObject->pairing = NULL;
	retObject->safe_pairing_clear = FALSE;
	retObject->param_buf = NULL;
	retObject->element_type = e_type;
	return (PyObject *) retObject;
}

static PyObject *Element_add(Element *self, Element *other)
{
	Element *newObject;
	
	debug("Starting '%s'\n", __func__);
#ifdef DEBUG
	if(self->e) {
		element_printf("Left: e => \n", self->e);
	}
	
	if(other->e) {
		element_printf("Right: e => \n", other->e);
	}
#endif
	IS_SAME_GROUP(self, other);
	EXIT_IF(add_rule(self->element_type, other->element_type) == FALSE, "invalid add operation.");
	// start micro benchmark
	START_CLOCK(dBench);
	newObject = createNewElement(self->element_type, self->pairing);
	element_add(newObject->e, self->e, other->e);
	STOP_CLOCK(dBench);
	if(newObject != NULL) UPDATE_BENCH(ADDITION, newObject->element_type, dBench);
	return (PyObject *) newObject;
}

static PyObject *Element_sub(Element *self, Element *other)
{
	Element *newObject;
	
	debug("Starting '%s'\n", __func__);
#ifdef DEBUG	
	if(self->e) {
		element_printf("Left: e => \n", self->e);
	}
	
	if(other->e) {
		element_printf("Right: e => \n", other->e);
	}
#endif
	IS_SAME_GROUP(self, other);
	EXIT_IF(sub_rule(self->element_type, other->element_type) == FALSE, "invalid sub operation.");

	START_CLOCK(dBench);
	newObject = createNewElement(self->element_type, self->pairing);
	element_sub(newObject->e, self->e, other->e);		
	STOP_CLOCK(dBench);
	if(newObject != NULL) UPDATE_BENCH(SUBTRACTION, newObject->element_type, dBench);
	return (PyObject *) newObject;
}


/* requires more care -- understand possibilities first */
static PyObject *Element_mul(PyObject *lhs, PyObject *rhs)
{
	Element *self = NULL, *other = NULL, *newObject = NULL;
	integer_t z;
	int found_int = FALSE;

	// lhs or rhs must be an element type
	if(PyElement_Check(lhs)) {
		self = (Element *) lhs;
	}
	else if(PyLong_Check(lhs)) {
		bn_inits(z);
		longObjToInt(z, (PyLongObject *) lhs);
		found_int = TRUE;
	}

	if(PyElement_Check(rhs)) {
		other = (Element *) rhs;
	}
	else if(PyLong_Check(rhs)) {
		bn_inits(z);
		longObjToInt(z, (PyLongObject *) rhs);
		found_int = TRUE;
	}

	debug("Starting '%s'\n", __func__);
	if(PyElement_Check(lhs) && found_int) {
		// lhs is the element type
		START_CLOCK(dBench);
		newObject = createNewElement(self->element_type, self->pairing);
		// multiplication is commutative
		element_mul_int(newObject->e, self->e, z);
		bn_free(z);
		STOP_CLOCK(dBench);
	}
	else if(PyElement_Check(rhs) && found_int) {
		// rhs is the element type
		START_CLOCK(dBench);
		newObject = createNewElement(other->element_type, other->pairing);
		// multiplication is commutative
		element_mul_int(newObject->e, other->e, z);
		bn_free(z);
		STOP_CLOCK(dBench);
	}
	else if(PyElement_Check(lhs) && PyElement_Check(rhs)) {
		// both are element types
		IS_SAME_GROUP(self, other);
		EXIT_IF(mul_rule(self->element_type, other->element_type) == FALSE, "invalid mul operation.");

		if(self->element_type != ZR && other->element_type == ZR) {
			START_CLOCK(dBench);
			newObject = createNewElement(self->element_type, self->pairing);
			element_mul_zr(newObject->e, self->e, other->e);
			STOP_CLOCK(dBench);
		}
		else if(other->element_type != ZR && self->element_type == ZR) {
			// START_CLOCK
			START_CLOCK(dBench);
			newObject = createNewElement(other->element_type, self->pairing);
			element_mul_zr(newObject->e, other->e, self->e);
			STOP_CLOCK(dBench);
		}
		else { // all other cases
			// START_CLOCK
			START_CLOCK(dBench);
			newObject = createNewElement(self->element_type, self->pairing);
			element_mul(newObject->e, self->e, other->e);
			STOP_CLOCK(dBench);
		}
	}
	else {
		EXIT_IF(TRUE, "invalid types.");
	}

	if(newObject != NULL) UPDATE_BENCH(MULTIPLICATION, newObject->element_type, dBench);
	return (PyObject *) newObject;
}

static PyObject *Element_div(PyObject *lhs, PyObject *rhs)
{
	Element *self = NULL, *other = NULL, *newObject = NULL;
	integer_t z;
	int found_int = FALSE;

	// lhs or rhs must be an element type
	if(PyElement_Check(lhs)) {
		self = (Element *) lhs;
	}
	else if(PyLong_Check(lhs)) {
		bn_inits(z);
		longObjToInt(z, (PyLongObject *) lhs);
		found_int = TRUE;
	}

	if(PyElement_Check(rhs)) {
		other = (Element *) rhs;
	}
	else if(PyLong_Check(rhs)) {
		bn_inits(z);
		longObjToInt(z, (PyLongObject *) rhs);
		found_int = TRUE;
	}

	debug("Starting '%s'\n", __func__);
	if(PyElement_Check(lhs) && found_int) {
		// lhs is the element type
		START_CLOCK(dBench);
//		EXIT_IF(div_rule(self->element_type, ZR) == FALSE, "invalid div operation.");
		newObject = createNewElement(self->element_type, self->pairing);
		other = createNewElement(self->element_type, self->pairing);
		if(element_div_int(newObject->e, self->e, z) == ELEMENT_DIV_ZERO) {
			Py_XDECREF(newObject);
			//newObject = NULL;
			bn_free(z);
			EXIT_IF(TRUE, "divide by zero error!");
		}
		STOP_CLOCK(dBench);
	}
	else if(PyElement_Check(rhs) && found_int) {
		// rhs is the element type
		START_CLOCK(dBench);
//		EXIT_IF(div_rule(ZR, other->element_type) == FALSE, "invalid div operation.");
		newObject = createNewElement(other->element_type, other->pairing);
		if(element_int_div(newObject->e, z, other->e) == ELEMENT_DIV_ZERO) {
			Py_XDECREF(newObject);
			// newObject = NULL;
			bn_free(z);
			EXIT_IF(TRUE, "divide by zero error!");
		}
		STOP_CLOCK(dBench);
	}
	else if(PyElement_Check(lhs) && PyElement_Check(rhs)) {
		// both are element types
		IS_SAME_GROUP(self, other);
		EXIT_IF(div_rule(self->element_type, other->element_type) == FALSE, "invalid div operation.");

		START_CLOCK(dBench);
		newObject = createNewElement(self->element_type, self->pairing);
		if(element_div(newObject->e, self->e, other->e) == ELEMENT_DIV_ZERO) {
			PyObject_Del(newObject);
			newObject = NULL;
			EXIT_IF(TRUE, "divide by zero error!");
		}
		STOP_CLOCK(dBench);
	}
	else {
		EXIT_IF(TRUE, "invalid types.");
		PyErr_SetString(ElementError, "invalid types");
		return NULL;
	}

	bn_free(z);
	if(newObject != NULL) UPDATE_BENCH(DIVISION, newObject->element_type, dBench);
	return (PyObject *) newObject;
}
 
static PyObject *Element_invert(Element *self)
{
	Element *newObject = NULL;
	
	debug("Starting '%s'\n", __func__);
#ifdef DEBUG	
	if(self->e) {
		element_printf("e => \n", self->e);
	}
#endif
	
	START_CLOCK(dBench);
	newObject = createNewElement(self->element_type, self->pairing);
	element_invert(newObject->e, self->e);
	STOP_CLOCK(dBench);
	return (PyObject *) newObject;
}

static PyObject *Element_negate(Element *self)
{
	Element *newObject = NULL;

	debug("Starting '%s'\n", __func__);
#ifdef DEBUG
	if(self->e) {
		element_printf("e => \n", self->e);
	}
#endif

	START_CLOCK(dBench);
	newObject = createNewElement(self->element_type, self->pairing);
	element_neg(newObject->e, self->e);
	STOP_CLOCK(dBench);

	return (PyObject *) newObject;
}

static PyObject *Element_pow(PyObject *o1, PyObject *o2, PyObject *o3)
{
	Element *newObject = NULL, *lhs_o1 = NULL, *rhs_o2 = NULL;
	int longFoundLHS = FALSE, longFoundRHS = FALSE;
	integer_t n;

	Check_Types2(o1, o2, lhs_o1, rhs_o2, longFoundLHS, longFoundRHS);

	if(longFoundLHS) {
		// o1 is a long type and o2 is a element type
		// o1 should be element and o2 should be mpz
		if(rhs_o2->element_type == ZR) {
//			printf("%s: testing longFoundLHS\n", __FUNCTION__);
			START_CLOCK(dBench);
			bn_inits(n);
			longObjToInt(n, (PyLongObject *) o1);
			newObject = createNewElement(rhs_o2->element_type, rhs_o2->pairing);
			element_set_int(newObject->e, n);
			element_pow_zr(newObject->e, newObject->e, rhs_o2->e);
			bn_free(n);
			PyObject_Del(lhs_o1);
			STOP_CLOCK(dBench);
		}
		else {
			EXIT_IF(TRUE, "undefined exponentiation operation.");
		}
	}
	else if(longFoundRHS) {
		// o2 is a long type
		START_CLOCK(dBench);
		long rhs = PyLong_AsLong(o2);
		if(PyErr_Occurred() || rhs >= 0) {
//			printf("%s: testing longFoundLHS\n", __FUNCTION__);
			// clear error and continue
			// PyErr_Print(); // for debug purposes
			PyErr_Clear();
			newObject = createNewElement(lhs_o1->element_type, lhs_o1->pairing);
			bn_inits(n);
			longObjToInt(n, (PyLongObject *) o2);
			element_pow_int(newObject->e, lhs_o1->e, n);
			bn_free(n);
		}
		else if(rhs == -1) {
			// compute inverse
			newObject = createNewElement(lhs_o1->element_type, lhs_o1->pairing);
			element_invert(newObject->e, lhs_o1->e);
		}
		else {
			EXIT_IF(TRUE, "undefined exponentiation operation.");
		}
		STOP_CLOCK(dBench);
	}
	else if(Check_Elements(o1, o2)) {
		debug("Starting '%s'\n", __func__);
		IS_SAME_GROUP(lhs_o1, rhs_o2);
		EXIT_IF(exp_rule(lhs_o1->element_type, rhs_o2->element_type) == FALSE, "invalid exp operation");
		if(rhs_o2->element_type == ZR) {
			START_CLOCK(dBench);
			newObject = createNewElement(lhs_o1->element_type, lhs_o1->pairing);
			element_pow_zr(newObject->e, lhs_o1->e, rhs_o2->e);
			STOP_CLOCK(dBench);
		}
		else {
			// we have a problem
			EXIT_IF(TRUE, "undefined exponentiation operation");
		}
	}
	else {
		EXIT_IF(!PyElement_Check(o1), ERROR_TYPE(left, int, bytes, str));
		EXIT_IF(!PyElement_Check(o2), ERROR_TYPE(right, int, bytes, str));
	}

	// STOP_CLOCK
	if(newObject != NULL) UPDATE_BENCH(EXPONENTIATION, newObject->element_type, dBench);
	return (PyObject *) newObject;
}

/* We assume the element has been initialized into a specific field (G1,G2,GT,or Zr), then
they have the opportunity to set the
 
 */
static PyObject *Element_set(Element *self, PyObject *args)
{
    Element *object = NULL;
    int errcode = TRUE;
    unsigned int value;

    EXITCODE_IF(self->elem_initialized == FALSE, "must initialize element to a field (G1,G2,GT, or Zr)", FALSE);

    debug("Creating a new element\n");
    if(PyArg_ParseTuple(args, "i", &value)) {
            // convert into an int using PyArg_Parse(...)
            // set the element
            START_CLOCK(dBench);
            element_set_si(self->e, value);
            STOP_CLOCK(dBench);
    }
    else if(PyArg_ParseTuple(args, "O", &object)){
            START_CLOCK(dBench);
            element_set(self->e, object->e);
            STOP_CLOCK(dBench);
    }
    else { //
    	EXITCODE_IF(TRUE, "type not supported: signed int or Element object", FALSE);
    }

    return Py_BuildValue("i", errcode);
}

/* Takes a list of two objects in G1 & G2 respectively and computes the multi-pairing
PyObject *multi_pairing(Element *groupObj, PyObject *listG1, PyObject *listG2) {

	int GroupSymmetric = FALSE;
	// check for symmetric vs. asymmetric
	if(pairing_is_symmetric(groupObj->pairing->pair_obj)) {
		GroupSymmetric = TRUE;
	}

	int length = PySequence_Length(listG1);

	EXIT_IF(length != PySequence_Length(listG2), "unequal number of pairing elements.");
	if(length > 0) {

		element_t g1[length];
		element_t g2[length];
		int i, l = 0, r = 0;

		for(i = 0; i < length; i++) {
			PyObject *tmpObject1 = PySequence_GetItem(listG1, i);
			PyObject *tmpObject2 = PySequence_GetItem(listG2, i);

			if(PyElement_Check(tmpObject1) && PyElement_Check(tmpObject2)) {
				Element *tmp1 = (Element *) tmpObject1;
				Element *tmp2 = (Element *) tmpObject2;
				if(GroupSymmetric == TRUE && (tmp1->element_type == G1 || tmp1->element_type == G2)) {
					element_init_same_as(g1[l], tmp1->e);
					element_set(g1[l], tmp1->e);
					l++;
				}
				else if(tmp1->element_type == G1) {
					element_init_G1(g1[l], groupObj->pairing->pair_obj);
					element_set(g1[l], tmp1->e);
					l++;
				}

				if(GroupSymmetric == TRUE && (tmp2->element_type == G1 || tmp2->element_type == G2)) {
					element_init_same_as(g2[r], tmp2->e);
					element_set(g2[r], tmp2->e);
					r++;
				}
				else if(tmp2->element_type == G2) {
					element_init_G2(g2[r], groupObj->pairing->pair_obj);
					element_set(g2[r], tmp2->e);
					r++;
				}
			}
			Py_DECREF(tmpObject1);
			Py_DECREF(tmpObject2);
		}

		Element *newObject = NULL;
		if(l == r) {
			newObject = createNewElement(GT, groupObj->pairing);
			element_prod_pairing(newObject->e, g1, g2, l); // pairing product calculation
		}
		else {
			EXIT_IF(TRUE, "invalid pairing element types in list.");
		}

		// clean up
		for(i = 0; i < l; i++) { element_clear(g1[i]); }
		for(i = 0; i < r; i++) { element_clear(g2[i]); }
		return (PyObject *) newObject;
	}

	EXIT_IF(TRUE, "list is empty.");
}
*/

/* this is a type method that is visible on the global or class level. Therefore,
   the function prototype needs the self (element class) and the args (tuple of Element objects).
 */
PyObject *Apply_pairing(Element *self, PyObject *args)
{
	// lhs => G1 and rhs => G2
	Element *newObject, *lhs, *rhs, *group = NULL;
	PyObject *lhs2, *rhs2;

	debug("Applying pairing...\n");
	if(!PyArg_ParseTuple(args, "OO|O", &lhs2, &rhs2, &group)) {
		EXIT_IF(TRUE, "invalid arguments: G1, G2, groupObject.");
	}

//	if(PySequence_Check(lhs2) && PySequence_Check(rhs2)) {
//		VERIFY_GROUP(group);
//		return multi_pairing(group, lhs2, rhs2);
//	}

	if(PyElement_Check(lhs2) && PyElement_Check(rhs2)) {

		lhs = (Element *) lhs2;
		rhs = (Element *) rhs2;
		IS_SAME_GROUP(lhs, rhs);

		if(pair_rule(lhs->element_type, rhs->element_type) == TRUE) {
			debug("Pairing is symmetric.\n");
			debug_e("LHS: '%B'\n", lhs->e);
			debug_e("RHS: '%B'\n", rhs->e);
			START_CLOCK(dBench);
			newObject = createNewElement(GT, lhs->pairing);
			pairing_apply(newObject->e, lhs->e, rhs->e);
			STOP_CLOCK(dBench);
			UPDATE_BENCHMARK(PAIRINGS, dBench);
			return (PyObject *) newObject;
		}
	}
	EXIT_IF(TRUE, "pairings only apply to elements of G1 x G2 --> GT");
}

PyObject *sha1_hash(Element *self, PyObject *args) {
	Element *object;
	PyObject *str = NULL;
	uint8_t *hash_hex = NULL;
	uint8_t label = 0x00;

	debug("Hashing the element...\n");
	EXIT_IF(!PyArg_ParseTuple(args, "O|c", &object, &label), "missing element object");

	EXIT_IF(object->elem_initialized == FALSE, "null element object.");
	START_CLOCK(dBench);
	int hash_size = SHA_LEN;
	uint8_t hash_buf[hash_size + 1];
	memset(hash_buf, 0, hash_size);
	// hash element to a buffer
	element_to_key(object->e, hash_buf, hash_size, label);

	hash_hex = convert_buffer_to_hex(hash_buf, (size_t) hash_size);
//	printf_buffer_as_hex(hash_buf, hash_size);

//	str = PyBytes_FromStringAndSize((const char *) hash_buf, hash_size);
	str = PyBytes_FromString((const char *) hash_hex);
	free(hash_hex);
	STOP_CLOCK(dBench);
	return str;
}

// note that this is a class instance function and thus, self will refer to the class object 'element'
// the args will contain the references to the objects passed in by the caller.
// The hash function should be able to handle elements of various types and accept
// a field to hash too. For example, a string can be hashed to Zr or G1, an element in G1 can be
static PyObject *Element_hash(Element *self, PyObject *args) {
	Element *newObject = NULL, *object = NULL, *group = NULL;
	PyObject *objList = NULL, *tmpObject = NULL;
	// hashing element to Zr
	uint8_t hash_buf[SHA_LEN+1];
	memset(hash_buf, '\0', SHA_LEN);
	int result, i;
	GroupType type = ZR;
	char *tmp = NULL, *str;

	// make sure args have the right type -- check that args contain a "string" and "string"
	if(!PyArg_ParseTuple(args, "OO|i", &group, &objList, &type)) {
		tmp = "invalid object types";
		goto cleanup;
	}

	VERIFY_GROUP(group);
	// first case: is a string and type may or may not be set
	if(PyBytes_CharmCheck(objList)) {
		str = NULL;
		PyBytes_ToString(str, objList);
		if(type == ZR) {
			debug("Hashing string '%s' to Zr...\n", str);
			// create an element of Zr
			// hash bytes using SHA1
			START_CLOCK(dBench);
			newObject = createNewElement(ZR, group->pairing);
			// extract element in hash
			result = element_from_hash(newObject->e, (uint8_t *) str, strlen(str));
			if(result != ELEMENT_OK) {
				tmp = "could not hash to bytes.";
				goto cleanup;
			}
			STOP_CLOCK(dBench);
		}
		else if(type == G1 || type == G2) {
		    // element to G1
			debug("Hashing string '%s'\n", str);
			debug("Target GroupType => '%d'", type);
			START_CLOCK(dBench);
			newObject = createNewElement(type, group->pairing);
			// hash bytes using SHA
			result = element_from_hash(newObject->e, (uint8_t *) str, strlen(str));
			if(result != ELEMENT_OK) {
				tmp = "could not hash to bytes.";
				goto cleanup;
			}
			STOP_CLOCK(dBench);
		}
		else {
			// not supported, right?
			tmp = "cannot hash a string to that field. Only Zr or G1.";
			goto cleanup;
		}
	}
	// element type to ZR or G1. Can also contain multiple elements
	// second case: is a tuple of elements of which could be a string or group elements
	else if(PySequence_Check(objList)) {
		int size = PySequence_Length(objList);
		if(size > 0) {
			// its a tuple of Elements
			tmpObject = PySequence_GetItem(objList, 0);
			if(PyElement_Check(tmpObject)) {
				object = (Element *) tmpObject;
				START_CLOCK(dBench);
				result = element_to_key(object->e, hash_buf, SHA_LEN, 0);
				STOP_CLOCK(dBench);
			}
			else if(PyBytes_CharmCheck(tmpObject)) {
				str = NULL;
				PyBytes_ToString(str, tmpObject);
				START_CLOCK(dBench);
				result = hash_buffer_to_bytes((uint8_t *) str, strlen(str), hash_buf, SHA_LEN, HASH_FUNCTION_STR_TO_Zr_CRH);
				STOP_CLOCK(dBench);
				debug("hash str element =>");
				printf_buffer_as_hex(hash_buf, SHA_LEN);
			}
			Py_DECREF(tmpObject);

			uint8_t out_buf[SHA_LEN+1];
			// convert the contents of tmp_buf to a string?
			for(i = 1; i < size; i++) {
				tmpObject = PySequence_GetItem(objList, i);
				if(PyElement_Check(tmpObject)) {
					object = (Element *) tmpObject;
					START_CLOCK(dBench);
					memset(out_buf, '\0', SHA_LEN);
					// current hash_buf output concatenated with object are sha1 hashed into hash_buf
					result = hash2_element_to_bytes(&object->e, hash_buf, SHA_LEN, out_buf); // TODO: fix this
					STOP_CLOCK(dBench);
					debug("hash element => ");
					printf_buffer_as_hex(out_buf, SHA_LEN);
					memcpy(hash_buf, out_buf, SHA_LEN);
				}
				else if(PyBytes_CharmCheck(tmpObject)) {
					str = NULL;
					PyBytes_ToString(str, tmpObject);
					START_CLOCK(dBench);
					// this assumes that the string is the first object (NOT GOOD, change)
					result = hash2_buffer_to_bytes((uint8_t *) str, strlen(str), hash_buf, SHA_LEN, out_buf); // TODO: fix this
					memcpy(hash_buf, out_buf, SHA_LEN);
					// hash2_element_to_bytes()
					STOP_CLOCK(dBench);
				}
				Py_DECREF(tmpObject);
			}
			START_CLOCK(dBench);
			if(type == ZR) { newObject = createNewElement(ZR, group->pairing); }
			else if(type == G1) { newObject = createNewElement(G1, group->pairing); }
			else {
				tmp = "invalid object type";
				goto cleanup;
			}

			element_from_hash(newObject->e, hash_buf, SHA_LEN);
			STOP_CLOCK(dBench);
		}
	}
	// third case: a tuple with one element and
	else if(PyElement_Check(objList)) {
			// one element
		object = (Element *) objList;
		if(object->elem_initialized == FALSE) {
			tmp = "element not initialized.";
			goto cleanup;
		}

		// TODO: add type == ZR?
		// Hash an element of Zr to an element of G1.
		if(type == G1) {
			START_CLOCK(dBench);
			newObject = createNewElement(G1, group->pairing);
			// hash the element to the G1 field (uses sha2 as well)
			// START_CLOCK
			result = element_to_key(object->e, hash_buf, SHA_LEN, 0);
			if(result != ELEMENT_OK) {
				tmp = "could not hash to bytes";
				goto cleanup;
			}
			element_from_hash(newObject->e, hash_buf, HASH_LEN);
			STOP_CLOCK(dBench);
		}
		else {
			tmp = "can only hash an element of Zr to G1. Random Oracle model.";
			goto cleanup;
		}
	}
    else {
		tmp = "invalid object types";
		goto cleanup;
	}


	return (PyObject *) newObject;

cleanup:
	if(newObject != NULL) PyObject_Del(newObject);
	EXIT_IF(TRUE, tmp);
}

static PyObject *Element_equals(PyObject *lhs, PyObject *rhs, int opid) {
	Element *self = NULL, *other = NULL;
	int result = -1;

	EXIT_IF(opid != Py_EQ && opid != Py_NE, "comparison supported: '==' or '!='");
	// check type of lhs & rhs
	if(PyElement_Check(lhs) && PyElement_Check(rhs)) {
		self = (Element *) lhs;
		other = (Element *) rhs;
	}

	debug("Starting '%s'\n", __func__);
	START_CLOCK(dBench);
	if(self != NULL && other != NULL) {
		// lhs and rhs are both elements
		IS_SAME_GROUP(self, other);
		if(self->elem_initialized && other->elem_initialized) {
			result = element_cmp(self->e, other->e);
		}
		else {
			debug("one of the elements is not initialized.\n");
		}
	}
	STOP_CLOCK(dBench);

	if(opid == Py_EQ) {
		if(result == 0) {
			Py_RETURN_TRUE;
		}
		Py_RETURN_FALSE;
	}
	else { /* Py_NE */
		if(result != 0) {
			Py_RETURN_TRUE;
		}
		Py_RETURN_FALSE;
	}
}

static PyObject *Element_long(PyObject *o1) {
	if(PyElement_Check(o1)) {
		// finish this function
		Element *value = (Element *) o1;
		if(value->element_type == ZR) {
			integer_t val;
			bn_inits(val);
			element_to_int(val, value->e); // fix this
			PyObject *obj = intToLongObj(val); // borrowed reference
			bn_free(val);
			return obj;
		}
	}
	EXIT_IF(TRUE, "cannot cast pairing object to an integer.");
}

static long Element_index(Element *o1) {
	long result = -1;

	if(o1->element_type == ZR) {
		integer_t o;
		bn_inits(o);
		element_to_int(o, o1->e);  // fix this
		PyObject *temp = intToLongObj(o); // fix this
		result = PyObject_Hash(temp);
		bn_free(o);
		PyObject_Del(temp);
	}
	return result;
}

UNARY(instance_negate, 'i', Element_negate)
UNARY(instance_invert, 'i', Element_invert)
BINARY(instance_add, 'a', Element_add)
BINARY(instance_sub, 's', Element_sub)

static PyObject *Serialize_cmp(Element *o1, PyObject *args) {

	Element *self = NULL;
	EXIT_IF(!PyArg_ParseTuple(args, "O", &self), "invalid argument.");
	EXIT_IF(self->elem_initialized == FALSE, "element not initialized");

	int elem_len = 0;
	EXIT_IF(check_type(self->element_type) == FALSE, "invalid type.");
	START_CLOCK(dBench);
	// determine size of buffer we need to allocate
	elem_len = element_length(self->e);
	EXIT_IF(elem_len == 0, "uninitialized element.");

	uint8_t data_buf[elem_len + 1];
	memset(data_buf, 0, elem_len);
	// write to char buffer
	element_to_bytes(data_buf, elem_len, self->e);
	debug("result => ");
	printf_buffer_as_hex(data_buf, elem_len);

	// convert to base64 and return as a string?
	size_t length = 0;
	char *base64_data_buf = NewBase64Encode(data_buf, elem_len, FALSE, &length);
	PyObject *result = PyBytes_FromFormat("%d:%s", self->element_type, (const char *) base64_data_buf);
	debug("base64 enc => '%s'\n", base64_data_buf);
	free(base64_data_buf);
	STOP_CLOCK(dBench);
	return result;
}

static PyObject *Deserialize_cmp(Element *self, PyObject *args) {
	Element *origObject = NULL, *group = NULL;
	PyObject *object;

	if(PyArg_ParseTuple(args, "OO", &group, &object)) {
		START_CLOCK(dBench);
		VERIFY_GROUP(group);
		if(PyBytes_Check(object)) {
			uint8_t *serial_buf = (uint8_t *) PyBytes_AsString(object);
			int type = atoi((const char *) &(serial_buf[0]));
			uint8_t *base64_buf = (uint8_t *)(serial_buf + 2);

			size_t deserialized_len = 0;
			uint8_t *binary_buf = NewBase64Decode((const char *) base64_buf, strlen((char *) base64_buf), &deserialized_len);

			if((type >= ZR && type <= GT) && deserialized_len > 0) {
				debug("result => ");
				printf_buffer_as_hex(binary_buf, deserialized_len);
				origObject = createNewElement(type, group->pairing);
				element_from_bytes(origObject->e, binary_buf, deserialized_len);
				free(binary_buf);
				STOP_CLOCK(dBench);
				return (PyObject *) origObject;
			}
		}
		EXIT_IF(TRUE, "string object malformed.");
	}

	EXIT_IF(TRUE, "nothing to deserialize in element.");
}

static PyObject *Group_Check(Element *self, PyObject *args) {

	Element *group = NULL;
	PyObject *object = NULL;
	if(PyArg_ParseTuple(args, "OO", &group, &object)) {
		if(PyElement_Check(object)) {
			IS_PAIRING_OBJ_NULL(group); /* verify group object is still active */
			Element *elem = (Element *) object;

			int result = element_is_member(elem->e);
			LEAVE_IF(result == ELEMENT_INVALID_ARG, "invalid object type.");

			if(result == TRUE) {
				Py_INCREF(Py_True);
				return Py_True;
			}
			else {
				Py_INCREF(Py_False);
				return Py_False;
			}
		}
	}

	PyErr_SetString(ElementError, "invalid object type.");
	return NULL;
}

static PyObject *Get_Order(Element *self, PyObject *args) {
	PyObject *obj = NULL;
	EXIT_IF(!PyArg_ParseTuple(args, "O", &obj), "invalid group object");

	if(PyElement_Check(obj)) {
//		Element *group = (Element *) obj;
//		IS_PAIRING_OBJ_NULL(group);
		integer_t x;
		bn_inits(x);
		get_order(x);
		PyObject *object = (PyObject *) intToLongObj(x);
		bn_free(x);
		return object; /* returns a PyInt */
	}

	return NULL; /* most likely invalid */
}

#ifdef BENCHMARK_ENABLED
void Operations_clear()
{
	CLEAR_ALLDBENCH(dBench);
}

PyObject *PyCreateList(MeasureType type)
{
//	int groupTypes = 4;
	int count = -1;
	PyObject *objList = PyList_New(0);
	// Insert backwards from GT -> G2 -> G1 -> ZR
	GetField(count, type, GT, dBench);
	PyList_Insert(objList, 0, Py_BuildValue("i", count));
	GetField(count, type, G2, dBench);
	PyList_Insert(objList, 0, Py_BuildValue("i", count));
	GetField(count, type, G1, dBench);
	PyList_Insert(objList, 0, Py_BuildValue("i", count));
	GetField(count, type, ZR, dBench);
	PyList_Insert(objList, 0, Py_BuildValue("i", count));

	return objList;
}

static PyObject *Granular_benchmark(PyObject *self, PyObject *args)
{
	PyObject *dict = NULL;
	int id = -1;

	if(!PyArg_ParseTuple(args, "i", &id)) {
		PyErr_SetString(ElementError, "invalid benchmark identifier.");
		return NULL;
	}

	if(id == BenchmarkIdentifier) {
		dict = PyDict_New();
		PyDict_SetItem(dict, Py_BuildValue("i", MULTIPLICATION), PyCreateList(MULTIPLICATION));
		PyDict_SetItem(dict, Py_BuildValue("i", DIVISION), PyCreateList(DIVISION));
		PyDict_SetItem(dict, Py_BuildValue("i", ADDITION), PyCreateList(ADDITION));
		PyDict_SetItem(dict, Py_BuildValue("i", SUBTRACTION), PyCreateList(SUBTRACTION));
		PyDict_SetItem(dict, Py_BuildValue("i", EXPONENTIATION), PyCreateList(EXPONENTIATION));
	}

	return dict;
}
#endif

#if PY_MAJOR_VERSION >= 3

PyTypeObject PairingType = {
	PyVarObject_HEAD_INIT(NULL, 0)
	"pairing.Pairing",             /*tp_name*/
	sizeof(Pairing),         /*tp_basicsize*/
	0,                         /*tp_itemsize*/
	(destructor)Pairing_dealloc, /*tp_dealloc*/
	0,                         /*tp_print*/
	0,                         /*tp_getattr*/
	0,                         /*tp_setattr*/
	0,			   				/*tp_reserved*/
	0, /*tp_repr*/
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
	"Pairing group parameters",           /* tp_doc */
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
	(initproc)Pairing_init,      /* tp_init */
	0,                         /* tp_alloc */
	Pairing_new,                 /* tp_new */
};
#else
/* python 2.x series */
PyTypeObject PairingType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "pairing.Pairing",             /*tp_name*/
    sizeof(Pairing),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)Pairing_dealloc, /*tp_dealloc*/
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
    (reprfunc)Element_print,   /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "Pairing group parameters",           /* tp_doc */
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
    (initproc) Pairing_init,      /* tp_init */
    0,                         /* tp_alloc */
    Pairing_new,                 /* tp_new */
};

#endif

#ifdef BENCHMARK_ENABLED
// Benchmark methods
InitBenchmark_CAPI(_init_benchmark, dBench, BenchmarkIdentifier);
StartBenchmark_CAPI(_start_benchmark, dBench);
EndBenchmark_CAPI(_end_benchmark, dBench);
GetBenchmark_CAPI(_get_benchmark, dBench);
GetAllBenchmarks_CAPI(_get_all_results, dBench);
ClearBenchmarks_CAPI(_clear_benchmark, dBench);
#endif
// new
#if PY_MAJOR_VERSION >= 3
PyNumberMethods element_number = {
	    instance_add,            /* nb_add */
	    instance_sub,            /* nb_subtract */
	    Element_mul,            /* nb_multiply */
	    0,      		    /* nb_remainder */
	    0,					/* nb_divmod */
	    Element_pow,			/* nb_power */
	    instance_negate,            /* nb_negative */
	    0,            /* nb_positive */
	    0,            /* nb_absolute */
	    0,          	/* nb_bool */
	    (unaryfunc)instance_invert,  /* nb_invert */
	    0,                    /* nb_lshift */
	    0,                    /* nb_rshift */
	    0,                       /* nb_and */
	    0,                       /* nb_xor */
	    0,                        /* nb_or */
	    (unaryfunc)Element_long,           /* nb_int */
	    0,						/* nb_reserved */
	    0,          			/* nb_float */
	    instance_add,            /* nb_inplace_add */
	    instance_sub,            /* nb_inplace_subtract */
	    Element_mul,            /* nb_inplace_multiply */
	    0,      			/* nb_inplace_remainder */
	    Element_pow,		    /* nb_inplace_power */
	    0,                   /* nb_inplace_lshift */
	    0,                   /* nb_inplace_rshift */
	    0,                      /* nb_inplace_and */
	    0,                      /* nb_inplace_xor */
	    0,                       /* nb_inplace_or */
	    0,                  /* nb_floor_divide */
	    Element_div,                   /* nb_true_divide */
	    0,                 /* nb_inplace_floor_divide */
	    Element_div,                  /* nb_inplace_true_divide */
	    0,          /* nb_index */
};

PyTypeObject ElementType = {
	PyVarObject_HEAD_INIT(NULL, 0)
	"pairing.Element",             /*tp_name*/
	sizeof(Element),         /*tp_basicsize*/
	0,                         /*tp_itemsize*/
	(destructor)Element_dealloc, /*tp_dealloc*/
	0,                         /*tp_print*/
	0,                         /*tp_getattr*/
	0,                         /*tp_setattr*/
	0,			   				/*tp_reserved*/
	(reprfunc)Element_print, /*tp_repr*/
	&element_number,               /*tp_as_number*/
	0,                         /*tp_as_sequence*/
	0,                         /*tp_as_mapping*/
	(hashfunc)Element_index,   /*tp_hash */
	0,                         /*tp_call*/
	0,                         /*tp_str*/
	0,                         /*tp_getattro*/
	0,                         /*tp_setattro*/
	0,                         /*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
	"Pairing objects",           /* tp_doc */
	0,		               /* tp_traverse */
	0,		               /* tp_clear */
	Element_equals,		       /* tp_richcompare */
	0,		               /* tp_weaklistoffset */
	0,		               /* tp_iter */
	0,		               /* tp_iternext */
	Element_methods,             /* tp_methods */
	Element_members,             /* tp_members */
	0,                         /* tp_getset */
	0,                         /* tp_base */
	0,                         /* tp_dict */
	0,                         /* tp_descr_get */
	0,                         /* tp_descr_set */
	0,                         /* tp_dictoffset */
	(initproc)Element_init,      /* tp_init */
	0,                         /* tp_alloc */
	Element_new,                 /* tp_new */
};
#else
/* python 2.x series */
PyNumberMethods element_number = {
    instance_add,                       /* nb_add */
    instance_sub,                       /* nb_subtract */
    Element_mul,                        /* nb_multiply */
    Element_div,                       /* nb_divide */
    0,                      /* nb_remainder */
    0,						/* nb_divmod */
    Element_pow,						/* nb_power */
    instance_negate,            		/* nb_negative */
    0,            /* nb_positive */
    0,            /* nb_absolute */
    0,          	/* nb_nonzero */
    (unaryfunc)instance_invert,         /* nb_invert */
    0,                    /* nb_lshift */
    0,                    /* nb_rshift */
    0,                       /* nb_and */
    0,                       /* nb_xor */
    0,                        /* nb_or */
    0,                    				/* nb_coerce */
    0,            /* nb_int */
    (unaryfunc)Element_long,           /* nb_long */
    0,          /* nb_float */
    0,            /* nb_oct */
    0,            /* nb_hex */
    instance_add,                      /* nb_inplace_add */
    instance_sub,                      /* nb_inplace_subtract */
    Element_mul,                      /* nb_inplace_multiply */
    Element_div,                      /* nb_inplace_divide */
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

PyTypeObject ElementType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "pairing.Element",             /*tp_name*/
    sizeof(Element),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)Element_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    &element_number,       /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    (hashfunc)Element_index,   /*tp_hash */
    0, 						/*tp_call*/
    (reprfunc)Element_print,   /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_CHECKTYPES, /*tp_flags*/
    "Pairing objects",           /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    Element_equals,		   /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    Element_methods,           /* tp_methods */
    Element_members,           /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc) Element_init,      /* tp_init */
    0,                         /* tp_alloc */
    Element_new,                 /* tp_new */
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

// end
PyMemberDef Element_members[] = {
	{"params", T_STRING, offsetof(Element, params), 0,
		"pairing type"},
	{"type", T_INT, offsetof(Element, element_type), 0,
		"group type"},
    {"initialized", T_INT, offsetof(Element, elem_initialized), 0,
		"determine initialization status"},
    {NULL}  /* Sentinel */
};

PyMethodDef Element_methods[] = {
	{"set", (PyCFunction)Element_set, METH_VARARGS, "Set an element to a fixed value."},
    {NULL}  /* Sentinel */
};

PyMethodDef pairing_methods[] = {
	{"init", (PyCFunction)Element_elem, METH_VARARGS, "Create an element in group ZR and optionally set value."},
	{"pair", (PyCFunction)Apply_pairing, METH_VARARGS, "Apply pairing between an element of G1 and G2 and returns an element mapped to GT"},
	{"hashPair", (PyCFunction)sha1_hash, METH_VARARGS, "Compute a sha1 hash of an element type"},
	{"H", (PyCFunction)Element_hash, METH_VARARGS, "Hash an element type to a specific field: Zr, G1, or G2"},
	{"random", (PyCFunction)Element_random, METH_VARARGS, "Return a random element in a specific group: G1, G2, Zr"},
	{"serialize", (PyCFunction)Serialize_cmp, METH_VARARGS, "Serialize an element type into bytes."},
	{"deserialize", (PyCFunction)Deserialize_cmp, METH_VARARGS, "De-serialize an bytes object into an element object"},
	{"ismember", (PyCFunction) Group_Check, METH_VARARGS, "Group membership test for element objects."},
	{"order", (PyCFunction) Get_Order, METH_VARARGS, "Get the group order for a particular field."},
#ifdef BENCHMARK_ENABLED
	{"InitBenchmark", (PyCFunction)_init_benchmark, METH_NOARGS, "Initialize a benchmark object"},
	{"StartBenchmark", (PyCFunction)_start_benchmark, METH_VARARGS, "Start a new benchmark with some options"},
	{"EndBenchmark", (PyCFunction)_end_benchmark, METH_VARARGS, "End a given benchmark"},
	{"GetBenchmark", (PyCFunction)_get_benchmark, METH_VARARGS, "Returns contents of a benchmark object"},
	{"GetGeneralBenchmarks", (PyCFunction) _get_all_results, METH_VARARGS, "Retrieve general benchmark info as a dictionary"},
	{"GetGranularBenchmarks", (PyCFunction) Granular_benchmark, METH_VARARGS, "Retrieve granular benchmarks as a dictionary"},
	{"ClearBenchmark", (PyCFunction)_clear_benchmark, METH_VARARGS, "Clears content of benchmark object"},
#endif
    {NULL}  /* Sentinel */
};

#if PY_MAJOR_VERSION >= 3
static int pairings_traverse(PyObject *m, visitproc visit, void *arg) {
	Py_VISIT(GETSTATE(m)->error);
	return 0;
}

static int pairings_clear(PyObject *m) {
	Py_CLEAR(GETSTATE(m)->error);
#ifdef BENCHMARK_ENABLED
	Operations *c = (Operations *) dBench->data_ptr;
	free(c);
	Py_CLEAR(GETSTATE(m)->dBench);
#endif
	return 0;
}

static int pairings_free(PyObject *m) {
	return 0;
}

static struct PyModuleDef moduledef = {
	PyModuleDef_HEAD_INIT,
	"pairing",
	NULL,
	sizeof(struct module_state),
	pairing_methods,
	NULL,
	pairings_traverse,
	(inquiry) pairings_clear, // clear function to call during GC clearing of the module object
	(freefunc) pairings_free //
};

#define INITERROR return NULL
PyMODINIT_FUNC
PyInit_pairing(void) 		{
#else
#define INITERROR return
void initpairing(void) 		{
#endif
    PyObject* m;
	
    if(PyType_Ready(&PairingType) < 0)
    	INITERROR;
    if(PyType_Ready(&ElementType) < 0)
        INITERROR;
#if PY_MAJOR_VERSION >= 3
    m = PyModule_Create(&moduledef);
#else
    m = Py_InitModule("pairing", pairing_methods);
#endif

    if(m == NULL)
		INITERROR;
	struct module_state *st = GETSTATE(m);
	st->error = PyErr_NewException("pairing.Error", NULL, NULL);
	if(st->error == NULL) {
		Py_DECREF(m);
		INITERROR;
	}
	ElementError = st->error;
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

    Operations *cntr = (Operations *) malloc(sizeof(Operations));
    dBench->data_ptr = (void *) cntr; // store data structure
    dBench->gran_init = &Operations_clear; // pointer to clearing the structure memory
    CLEAR_ALLDBENCH(dBench);
    InitClear(dBench);
#endif

    Py_INCREF(&PairingType);
    PyModule_AddObject(m, "params", (PyObject *)&PairingType);
    Py_INCREF(&ElementType);
    PyModule_AddObject(m, "pairing", (PyObject *)&ElementType);

    PyModule_AddIntConstant(m, "ZR", ZR);
    PyModule_AddIntConstant(m, "G1", G1);
    PyModule_AddIntConstant(m, "G2", G2);
    PyModule_AddIntConstant(m, "GT", GT);

#ifdef BENCHMARK_ENABLED
	ADD_BENCHMARK_OPTIONS(m);
	PyModule_AddIntConstant(m, "Pair", PAIRINGS);
	PyModule_AddIntConstant(m, "Granular", GRANULAR);
#endif

	/* only supporting one for now */
    PyModule_AddIntConstant(m, "BN158", 0);
    PyModule_AddIntConstant(m, "BN254", 1);
//    PyModule_AddIntConstant(m, "BN256", 2);
//    PyModule_AddIntConstant(m, "BN638", 3);
//    PyModule_AddIntConstant(m, "KSS508",4);

#if PY_MAJOR_VERSION >= 3
	return m;
#endif
}
