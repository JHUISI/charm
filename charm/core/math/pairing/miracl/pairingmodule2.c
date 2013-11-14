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
 *   @file    pairingmodule2.c
 *
 *   @brief   charm interface over MIRACL's pairing-based operations
 *
 *   @author  ayo.akinyele@charm-crypto.com
 * 	@remark	 this version of the pairing module uses the MIRACL library (www.shamus.ie).
 *   At the moment, only useful for academic purposes and should be treated as such.
 *   To build into Charm, you'll need to acquire the MIRACL source and compile with the
 *   build script located in the miracl dir. See the online documentation at charm-crypto.com
 *   for how to install.
 *
 ************************************************************************/

#include "pairingmodule2.h"


int exp_rule(Group_t lhs, Group_t rhs)
{
	if(lhs == pyZR_t && rhs == pyZR_t) return TRUE;
	if(lhs == pyG1_t && rhs == pyZR_t) return TRUE;
	if(lhs == pyG2_t && rhs == pyZR_t) return TRUE;
	if(lhs == pyGT_t && rhs == pyZR_t) return TRUE;
	return FALSE; /* Fail all other cases */
}

int mul_rule(Group_t lhs, Group_t rhs)
{
	if(lhs == rhs) return TRUE;
	if(lhs == pyZR_t || rhs == pyZR_t) return TRUE;
	return FALSE; /* Fail all other cases */
}

int add_rule(Group_t lhs, Group_t rhs)
{
	if(lhs == rhs && lhs != pyGT_t) return TRUE;
	return FALSE; /* Fail all other cases */
}

int sub_rule(Group_t lhs, Group_t rhs)
{
	if(lhs == rhs && lhs != pyGT_t) return TRUE;
	return FALSE; /* Fail all other cases */
}

int div_rule(Group_t lhs, Group_t rhs)
{
	if(lhs == rhs) return TRUE;
	return FALSE; /* Fail all other cases */
}

int pair_rule(Group_t lhs, Group_t rhs)
{
	if(lhs == pyG1_t && rhs == pyG2_t) return TRUE;
	else if(lhs == pyG2_t && rhs == pyG1_t) return TRUE;
	return FALSE; /* Fall all other cases : assume MNT? */
}

int check_type(Group_t type) {
	if(type == pyZR_t || type == pyG1_t || type == pyG2_t || type == pyGT_t) return TRUE;
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
	Element *obj1 = NULL, *obj2 = NULL;				\
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
	if(Check_Types(obj1->element_type, obj2->element_type, m))	\
		return (n)(obj1, obj2); \
	return NULL;				\
}

PyObject *mpzToLongObj(mpz_t m) {
	/* borrowed from gmpy - then modified */
	int size = (mpz_sizeinbase(m, 2) + PyLong_SHIFT - 1) / PyLong_SHIFT;
	int i, isNeg = (mpz_sgn(m) < 0) ? TRUE : FALSE;
	mpz_t temp;
	PyLongObject *l = _PyLong_New(size);
	if (!l)
		return NULL;
	mpz_init_set(temp, m);
	for (i = 0; i < size; i++) {
		l->ob_digit[i] = (digit)(mpz_get_ui(temp) & PyLong_MASK);
		mpz_fdiv_q_2exp(temp, temp, PyLong_SHIFT);
	}
	i = size;
	while ((i > 0) && (l->ob_digit[i - 1] == 0))
		i--;
	if(isNeg) {
		Py_SIZE(l) = -i;
	}
	else {
		Py_SIZE(l) = i;
	}
	mpz_clear(temp);
	return (PyObject *) l;
}

void longObjToMPZ (mpz_t m, PyLongObject * p)
{
	int size, i, tmp = Py_SIZE(p);
	int isNeg = FALSE;
	mpz_t temp, temp2;
	mpz_init (temp);
	mpz_init (temp2);
	if (tmp > 0)
		size = tmp;
	else {
		size = -tmp;
		isNeg = TRUE;
	}
	mpz_set_ui (m, 0);
	for (i = 0; i < size; i++)
	{
		mpz_set_ui (temp, p->ob_digit[i]);
		mpz_mul_2exp (temp2, temp, PyLong_SHIFT * i);
		mpz_add (m, m, temp2);
	}
	mpz_clear (temp);
	mpz_clear (temp2);
	if(isNeg) mpz_neg(m, m);
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
int Check_Types(Group_t l_type, Group_t r_type, char op)
{	
	switch (op) {
		// Rules: elements must be of the same type, multiplicative operations should be only used for
		// elements in field GT
		case 'a':	
			if(l_type == pyGT_t || r_type == pyGT_t) { return FALSE; }
			break;
		case 's':
			if(l_type == pyGT_t || r_type == pyGT_t) { return FALSE; }
			break;
		case 'e':
			if(l_type != pyG1_t && r_type != pyG2_t) { return FALSE; }
			break;
		case 'p':
			// rule for exponentiation for types
			if(l_type != pyG1_t && l_type != pyG2_t && l_type != pyGT_t && l_type != pyZR_t) { return FALSE; }
			// && r_type != ZR)
			// else { 
			//	PyErr_SetString(ElementError, "Only fields => [G1_t,G2,GT,Zr] ** Zr");
			//	return FALSE; 
			//}			
			break;
		default:
			break;
	}
	
	return TRUE;
	
}

// assumes that pairing structure has been initialized
static Element *createNewElement(Group_t element_type, Pairing *pairing) {
	debug("Create an object of type Element\n");
	Element *retObject = PyObject_New(Element, &ElementType);
	if(element_type == pyZR_t) {
		retObject->e = element_init_ZR(0);
		retObject->element_type = pyZR_t;
	}
	else if(element_type == pyG1_t) {
		retObject->e = element_init_G1();
		retObject->element_type = pyG1_t;
	}
	else if(element_type == pyG2_t) {
		retObject->e = element_init_G2();
		retObject->element_type = pyG2_t;
	}
	else if(element_type == pyGT_t) {
		retObject->e = element_init_GT(pairing);
		retObject->element_type = pyGT_t;
	}
	else {
		// init without a type -- caller must set e and element_type
	}
	
	retObject->elem_initialized = TRUE;
	retObject->elem_initPP = FALSE;
	retObject->pairing = pairing;
	Py_INCREF(retObject->pairing);
	return retObject;	
}

Element *convertToZR(PyObject *longObj, PyObject *elemObj) {
	Element *self = (Element *) elemObj;
	Element *new = createNewElement(pyZR_t, self->pairing);

	mpz_t x;
	mpz_init(x);
#if PY_MAJOR_VERSION < 3
	PyObject *longObj2 = PyNumber_Long(longObj);
	longObjToMPZ(x, (PyLongObject *) longObj2);
	Py_DECREF(longObj2);
#else
	longObjToMPZ(x, (PyLongObject *) longObj);
#endif
	element_set_mpz(new, x);
	mpz_clear(x);
	return new;
}

void 	Pairing_dealloc(Pairing *self)
{
	if(self->group_init) {
		element_delete(pyZR_t, self->order);
		pairing_clear(self->pair_obj);
		self->pair_obj = NULL;
		self->order = NULL;
	}

#ifdef BENCHMARK_ENABLED
	if(self->dBench != NULL) {
//		PrintPyRef("releasing benchmark object", self->dBench);
		Py_CLEAR(self->dBench);
		if(self->gBench != NULL) {
//			PrintPyRef("releasing operations object", self->gBench);
			Py_CLEAR(self->gBench);
		}
	}
#endif
	Py_TYPE(self)->tp_free((PyObject *) self);
}

void	Element_dealloc(Element* self)
{
	// add reference count to objects
	if(self->elem_initialized) {
		element_delete(self->element_type, self->e);
		Py_DECREF(self->pairing);
	}
	
	Py_TYPE(self)->tp_free((PyObject*)self);
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
//	printf("orig input => \n");
//	printf_buffer_as_hex(input_buf, input_len);

	memset(new_input, 0, new_input_len+1);
	new_input[0] = first_block; // block number (always 0 by default)
	new_input[1] = hash_prefix; // set hash prefix
	memcpy((uint8_t *)(new_input+2), input_buf, input_len); // copy input bytes

//	printf("new input => \n");
//	printf_buffer_as_hex(new_input, new_input_len);
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

/*!
 * Hash a group element to a byte array.  This calls hash_to_bytes().
 *
 * @param element		The input element.
 * @param hash_len		Length of the output hash (in bytes).
 * @param output_buf	A pre-allocated output buffer.
 * @param hash_num		Index number of the hash function to use (changes the output).
 * @return				FENC_ERROR_NONE or an error code.
 */
int hash_element_to_bytes(Element *element, int hash_size, uint8_t* output_buf, int prefix)
{
	int result = TRUE;
	unsigned int buf_len;

	buf_len = element_length_in_bytes(element);
	uint8_t *temp_buf = (uint8_t *)malloc(buf_len+1);
	if (temp_buf == NULL) {
		return FALSE;
	}

	element_to_bytes(temp_buf, element);
	result = hash_to_bytes(temp_buf, buf_len, output_buf, hash_size, prefix);
	free(temp_buf);

	return TRUE;
}

PyObject *Element_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    Element *self;
	
    self = (Element *)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->elem_initialized = FALSE;
		self->pairing = NULL;
		self->element_type = NONE_G;
    }
	
    return (PyObject *)self;
}

PyObject *Pairing_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	Pairing *self = (Pairing *) type->tp_alloc(type, 0);
	if(self != NULL) {
		self->group_init = FALSE;
		self->curve      = -1;
#ifdef BENCHMARK_ENABLED
		memset(self->bench_id, 0, ID_LEN);
		self->dBench = NULL;
		self->gBench = NULL;
#endif
	}

	return (PyObject *) self;
}

int Element_init(Element *self, PyObject *args, PyObject *kwds)
{
	return -1;
}


int Pairing_init(Pairing *self, PyObject *args, PyObject *kwds)
{
	char *params = NULL, *param_string = NULL;
	size_t b_len = 0;
	int aes_sec = -1;
    static char *kwlist[] = {"aes_sec", "params", "param_string", NULL};
	
    if (! PyArg_ParseTupleAndKeywords(args, kwds, "|iss#", kwlist,
                                      &aes_sec, &params, &param_string, &b_len)) {
    	PyErr_SetString(ElementError, "invalid arguments");
        return -1; 
	}

    if(aes_sec != -1) {
    	if(aes_sec == MNT160) {
			self->pair_obj = pairing_init(aes_sec);
			self->order    = order(self->pair_obj);
			self->curve	  = MNT; // only supported at this point
			pairing_init_finished 	  = FALSE;
    	}
    	else if(aes_sec == BN256) {
			self->pair_obj = pairing_init(aes_sec);
			self->order    = order(self->pair_obj);
			self->curve	  = BN; // only supported at this point
			pairing_init_finished 	  = FALSE;
    	}
    	else if(aes_sec == SS512) {
			self->pair_obj = pairing_init(aes_sec);
			self->order    = order(self->pair_obj);
			self->curve	  = SS; // only supported at this point
			pairing_init_finished 	  = FALSE;
    	}
    }

    self->group_init = TRUE;
    return 0;
}

/*
PyObject *Element_call(Element *elem, PyObject *args, PyObject *kwds)
{
	PyObject *object;
	Element *newObject;
	
	if(!PyArg_ParseTuple(args, "O:ref", &object)) {
		printf("Could not retrieve object.\n");
		return NULL;
	}
	
	newObject = (Element *) object;
	print("Elment->e => \n", newObject->element_type, newObject->e);
	debug("Element->type => '%d'\n", newObject->element_type);
	
	return NULL;
}
*/

static PyObject *Element_elem(Element* self, PyObject* args)
{
	Element *retObject, *group = NULL;
	int type;
	PyObject *long_obj = NULL;
	
	if(!PyArg_ParseTuple(args, "Oi|O", &group, &type, &long_obj)) {
		PyErr_SetString(ElementError, "invalid arguments.\n");
		return NULL;
	}
	
	debug("init an element.\n");

	if(type >= pyZR_t && type <= pyGT_t) {
		retObject = createNewElement(type, group->pairing);
	}
	else {
		PyErr_SetString(ElementError, "unrecognized group type.");
		return NULL;
	}

	if(long_obj != NULL && _PyLong_Check(long_obj)) {
		mpz_t m;
		mpz_init(m);
#if PY_MAJOR_VERSION < 3
		PyObject *longObj2 = PyNumber_Long(long_obj);
		longObjToMPZ(m, (PyLongObject *) longObj2);
		Py_DECREF(longObj2);
#else
		longObjToMPZ(m, (PyLongObject *) long_obj);
#endif
		element_set_mpz(retObject, m);
		mpz_clear(m);
	}
	
	/* return Element object */
	return (PyObject *) retObject;
}

PyObject *Pairing_print(Element* self)
{
	return PyUnicode_FromString("");
}

// TODO: use element_vnprintf to copy the result into element type
PyObject *Element_print(Element* self)
{
	PyObject *strObj;
	debug("Contents of element object\n");

	if(check_type(self->element_type) && self->elem_initialized) {
		int len = element_length_to_str(self);
		unsigned char *tmp = (unsigned char *) malloc(len + 1);
		memset(tmp, 0, len);
		element_to_str(&tmp, self);
		tmp[len] = '\0';

		strObj = PyUnicode_FromString((const char *) tmp);
		free(tmp);
		return strObj;
	}

	return PyUnicode_FromString("");
}

static PyObject *Element_random(Element* self, PyObject* args)
{
	Element *retObject;
	Pairing *group = NULL;
	int arg1;
	int seed = -1;
	
	/* create a new object */
	if(!PyArg_ParseTuple(args, "Oi|i", &group, &arg1, &seed))
		return NULL;

	VERIFY_GROUP(group);
	retObject = PyObject_New(Element, &ElementType);
	debug("init random element in '%d'\n", arg1);
	if(arg1 == pyZR_t) {
		retObject->e = element_init_ZR(0);
		retObject->element_type = pyZR_t;
	}
	else if(arg1 == pyG1_t) {
		retObject->e = element_init_G1();
		retObject->element_type = pyG1_t;
	}
	else if(arg1 == pyG2_t) {
		retObject->e = element_init_G2();
		retObject->element_type = pyG2_t;
	}
	else if(arg1 == pyGT_t) {
		PyErr_SetString(ElementError, "cannot generate random element in GT directly.");
		return NULL;
	}
	else {
		PyErr_SetString(ElementError, "unrecognized group type.");
		return NULL;
	}
	
	if(seed > -1) {
//		pbc_random_set_deterministic((uint32_t) seed);
	}
	/* create new Element object */
    element_random(retObject->element_type, group->pair_obj, retObject->e);

	retObject->elem_initialized = TRUE;
	retObject->elem_initPP = FALSE;
	retObject->pairing = group;
	Py_INCREF(retObject->pairing);
	return (PyObject *) retObject;	
}

static PyObject *Element_add(Element *self, Element *other)
{
	Element *newObject = NULL;
	
	debug("Starting '%s'\n", __func__);
#ifdef DEBUG
	if(self->e) {
//		element_printf("Left: e => '%B'\n", self->e);
	}
	
	if(other->e) {
//		element_printf("Right: e => '%B'\n", other->e);
	}
#endif

	if( add_rule(self->element_type, other->element_type) == FALSE) {
		PyErr_SetString(ElementError, "invalid add operation");
		return NULL;
	}
	// start micro benchmark

	newObject = createNewElement(self->element_type, self->pairing);
	element_add(newObject, self, other);
#ifdef BENCHMARK_ENABLED
	UPDATE_BENCH(ADDITION, newObject->element_type, newObject->pairing);
#endif
	return (PyObject *) newObject;
}

static PyObject *Element_sub(Element *self, Element *other)
{
	Element *newObject = NULL;
	
	debug("Starting '%s'\n", __func__);
#ifdef DEBUG	
	if(self->e) {
//		element_printf("Left: e => '%B'\n", self->e);
	}
	
	if(other->e) {
//		element_printf("Right: e => '%B'\n", other->e);
	}
#endif
	if( sub_rule(self->element_type, other->element_type) == FALSE) {
		PyErr_SetString(ElementError, "invalid sub operation");
		return NULL;
	}


	newObject = createNewElement(self->element_type, self->pairing);
	element_sub(newObject, self, other);
#ifdef BENCHMARK_ENABLED
	UPDATE_BENCH(SUBTRACTION, newObject->element_type, newObject->pairing);
#endif
	return (PyObject *) newObject;
}


static PyObject *Element_mul(PyObject *lhs, PyObject *rhs)
{
	Element *self = NULL, *other = NULL, *newObject = NULL;
	signed long int z;
	int found_int = FALSE;

	// lhs or rhs must be an element type
	if(PyElement_Check(lhs)) {
		self = (Element *) lhs;
	}
	else if(PyNumber_Check(lhs)) {
		if(PyArg_Parse(lhs, "l", &z)) {
			debug("Integer lhs: '%li'\n", z);
		}
		found_int = TRUE;
	}

	if(PyElement_Check(rhs)) {
		other = (Element *) rhs;
	}
	else if(PyNumber_Check(rhs)) {
		if(PyArg_Parse(rhs, "l", &z)) {
			debug("Integer rhs: '%li'\n", z);
		}
		found_int = TRUE;
	}

	debug("Starting '%s'\n", __func__);
	if(PyElement_Check(lhs) && found_int) {
		// lhs is the element type
		//
		newObject = createNewElement(self->element_type, self->pairing);
		element_mul_si(newObject, self, z);
		//
	}
	else if(PyElement_Check(rhs) && found_int) {
		// rhs is the element type
		//
		newObject = createNewElement(other->element_type, other->pairing);
		element_mul_si(newObject, other, z);
		//
	}
	else if(PyElement_Check(lhs) && PyElement_Check(rhs)) {
		// both are element types
		if( mul_rule(self->element_type, other->element_type) == FALSE) {
			PyErr_SetString(ElementError, "invalid mul operation");
			return NULL;
		}

		if(self->element_type != pyZR_t && other->element_type == pyZR_t) {
			newObject = createNewElement(self->element_type, self->pairing);
			element_mul_zn(newObject, self, other);
		}
		else if(other->element_type != pyZR_t && self->element_type == pyZR_t) {
			newObject = createNewElement(other->element_type, self->pairing);
			element_mul_zn(newObject, other, self);
		}
		else { // all other cases
			newObject = createNewElement(self->element_type, self->pairing);
			element_mul(newObject, self, other);
		}
	}
	else {
		PyErr_SetString(ElementError, "invalid types");
		return NULL;
	}
#ifdef BENCHMARK_ENABLED
	UPDATE_BENCH(MULTIPLICATION, newObject->element_type, newObject->pairing);
#endif
	return (PyObject *) newObject;
}

static PyObject *Element_div(PyObject *lhs, PyObject *rhs)
{
	Element *self = NULL, *other = NULL, *newObject = NULL;
	signed long int z;
	int found_int = FALSE;

	// lhs or rhs must be an element type
	if(PyElement_Check(lhs)) {
		self = (Element *) lhs;
	}
	else if(PyNumber_Check(lhs)) {
		if(PyArg_Parse(lhs, "l", &z)) {
			debug("Integer lhs: '%li'\n", z);
		}
		found_int = TRUE;
	}

	if(PyElement_Check(rhs)) {
		other = (Element *) rhs;
	}
	else if(PyNumber_Check(rhs)) {
		if(PyArg_Parse(rhs, "l", &z)) {
			debug("Integer rhs: '%li'\n", z);
		}
		found_int = TRUE;
	}

	debug("Starting '%s'\n", __func__);
	if(PyElement_Check(lhs) && found_int) {
		// lhs is the element type

		if(z != 0) {
			newObject = createNewElement(self->element_type, self->pairing);
			other = createNewElement(self->element_type, self->pairing);
			element_set_si(other, z);
			element_div(newObject, self, other);
		}
		else {
			PyErr_SetString(ElementError, "divide by zero exception!");
			goto divbyzero;
		}

	}
	else if(PyElement_Check(rhs) && found_int) {
		// rhs is the element type

		if(z > 1 || z <= 0) {
			newObject = createNewElement(other->element_type, other->pairing);
			self = createNewElement(other->element_type, other->pairing);
			element_set_si(self, z);
			element_div(newObject, self, other); // come back to this (not working)
		}
		else if(z == 1) {
			newObject = createNewElement(other->element_type, other->pairing);
			element_invert(newObject, other);
		}

	}
	else if(PyElement_Check(lhs) && PyElement_Check(rhs)) {
		// both are element types
		if( div_rule(self->element_type, other->element_type) == FALSE) {
			PyErr_SetString(ElementError, "invalid div operation");
			return NULL;
		}


		newObject = createNewElement(self->element_type, self->pairing);
		element_div(newObject, self, other);

	}
	else {
		PyErr_SetString(ElementError, "invalid types");
		return NULL;
	}

#ifdef BENCHMARK_ENABLED
	UPDATE_BENCH(DIVISION, newObject->element_type, newObject->pairing);
#endif

divbyzero:
	return (PyObject *) newObject;
}

 
static PyObject *Element_invert(Element *self)
{
	Element *newObject = NULL;
	
//	debug("Starting '%s'\n", __func__);
//#ifdef DEBUG
//	if(self->e) {
//		element_printf("e => '%B'\n", self->e);
//	}
//#endif


	if(check_type(self->element_type)) {
		newObject = createNewElement(self->element_type, self->pairing);
		element_invert(newObject, self);
	}

	return (PyObject *) newObject;
}

static PyObject *Element_negate(Element *self)
{
	Element *newObject = NULL;


	newObject = createNewElement(self->element_type, self->pairing);
	element_neg(newObject, self);


	return (PyObject *) newObject;
}

static PyObject *Element_pow(PyObject *o1, PyObject *o2, PyObject *o3)
{
	Element *newObject = NULL, *lhs_o1 = NULL, *rhs_o2 = NULL;
	int longFoundLHS = FALSE, longFoundRHS = FALSE;
	mpz_t n;

	Check_Types2(o1, o2, lhs_o1, rhs_o2, longFoundLHS, longFoundRHS);

	if(longFoundLHS) {
		// o1 is a long type and o2 is a element type
		// o1 should be element and o2 should be mpz
		printf("operation undefined: '%d' ^ <pairing element>\n", rhs_o2->element_type);
//		if(rhs_o2->element_type == ZR) {
//
//			mpz_init(n);
//			element_to_mpz(n, rhs_o2);
//
//			lhs_o1 = convertToZR(o1, o2);
//			newObject = createNewElement(rhs_o2->element_type, rhs_o2->pairing);
//			element_pow_zr(newObject, lhs_o1, n);
//			mpz_clear(n);
//			PyObject_Del(lhs_o1);
//
//		}
	}
	else if(longFoundRHS) {
		// o2 is a long type
//		if(lhs_o1->element_type != pyZR_t) {

		long rhs = PyLong_AsLong(o2);
		if(PyErr_Occurred() || rhs >= 0) {
			// clear error and continue
			//PyErr_Print(); // for debug purposes
			PyErr_Clear();
			newObject = createNewElement(lhs_o1->element_type, lhs_o1->pairing);
			rhs_o2 = createNewElement(pyZR_t, lhs_o1->pairing);
			if(newObject->element_type != pyZR_t) {
				mpz_init(n);
#if PY_MAJOR_VERSION < 3
				PyObject *longObj2 = PyNumber_Long(o2);
				longObjToMPZ(n, (PyLongObject *) longObj2);
				Py_DECREF(longObj2);
#else
				longObjToMPZ(n, (PyLongObject *) o2);
#endif
				element_set_mpz(rhs_o2, n);
				element_pow_zr(newObject, lhs_o1, rhs_o2);
				mpz_clear(n);
			}
			else if(rhs >= 0 && rhs <= INT_MAX) {
				// if less than int for given architecture
				element_pow_int(newObject, lhs_o1, rhs);
			}
			else { // anything larger: convert to an MPZ type then raise to EXP value
				mpz_init(n);
#if PY_MAJOR_VERSION < 3
				PyObject *longObj2 = PyNumber_Long(o2);
				longObjToMPZ(n, (PyLongObject *) longObj2);
				Py_DECREF(longObj2);
#else
				longObjToMPZ(n, (PyLongObject *) o2);
#endif
				element_set_mpz(rhs_o2, n);
				element_pow_zr(newObject, lhs_o1, rhs_o2);
				mpz_clear(n);
			}
			Py_DECREF(rhs_o2);

		}
		else if(rhs == -1) {
			newObject = createNewElement(lhs_o1->element_type, lhs_o1->pairing);
			element_invert(newObject, lhs_o1);

		}
		else {
			EXIT_IF(TRUE, "unexpected error.");
		}
	}
	else if(Check_Elements(o1, o2)) {
		debug("Starting '%s'\n", __func__);
		EXIT_IF(exp_rule(lhs_o1->element_type, rhs_o2->element_type) == FALSE, "invalid exp operation.");

		if(rhs_o2->element_type == pyZR_t) {

			newObject = createNewElement(NONE_G, lhs_o1->pairing);
			element_pow_zr(newObject, lhs_o1, rhs_o2);

		}
	}
	else {
		EXIT_IF(!PyElement_Check(o1), ERROR_TYPE(left, int, bytes, str));
		EXIT_IF(!PyElement_Check(o2), ERROR_TYPE(right, int, bytes, str));
	}

#ifdef BENCHMARK_ENABLED
	UPDATE_BENCH(EXPONENTIATION, newObject->element_type, newObject->pairing);
#endif
	return (PyObject *) newObject;
}

/* We assume the element has been initialized into a specific field (G1_t,G2,GT,or Zr), then
they have the opportunity to set the
 
 */
static PyObject *Element_set(Element *self, PyObject *args)
{
    Element *object = NULL;
    int errcode = TRUE;
    long int value = -1;

    if(self->elem_initialized == FALSE) {
    	PyErr_SetString(ElementError, "must initialize element to a field (G1_t,G2,GT, or Zr)");
    	errcode = FALSE;
    	return Py_BuildValue("i", errcode);
    }

    debug("Creating a new element\n");
    if(PyArg_ParseTuple(args, "|lO", &value, &object)) {
            // convert into an int using PyArg_Parse(...)
            // set the element
    	if(value == -1 && self->element_type == pyZR_t) {
            debug("Setting element to '%li'\n", value);

            debug("Value '%i'\n", (signed int) value);
            element_set_si(self, (signed int) value);

		}
    	else if(object != NULL) {

    		if(self->element_type == object->element_type) {

    			element_set(self, object);

    		}
    		else {
    	    	PyErr_SetString(ElementError, "types are not the same!");
    	    	errcode = FALSE;
    	    	return Py_BuildValue("i", errcode);
    		}
        }
    }

    return Py_BuildValue("i", errcode);
}

static PyObject *Element_setxy(Element *self, PyObject *args)
{
    Element *object1 = NULL, *object2 = NULL;
    int errcode = TRUE;

    if(self->elem_initialized == FALSE) {
    	PyErr_SetString(ElementError, "must initialize element to a field (G1_t,G2,GT, or Zr)");
    	return NULL;
    }

    debug("Creating a new element\n");
    if(PyArg_ParseTuple(args, "|OO", &object1, &object2)) {
            // convert into an int using PyArg_Parse(...)
            // set the element
    	if(self->element_type == pyG1_t) {
    		if(object1->element_type == object2->element_type && object1->element_type == pyZR_t) {
    			errcode = element_setG1(self, object1, object2);
    		}
    		else {
    	    	PyErr_SetString(ElementError, "types are not the same!");
    			return NULL;
    		}
        }
    }

	Py_RETURN_TRUE;
}

static PyObject  *Element_initPP(Element *self, PyObject *args)
{
    EXITCODE_IF(self->elem_initPP == TRUE, "initialized the pre-processing function already", FALSE);
    EXITCODE_IF(self->elem_initialized == FALSE, "must initialize element to a field (G1,G2, or GT)", FALSE);

    /* initialize and store preprocessing information in e_pp */
    if(self->element_type >= pyG1_t && self->element_type <= pyGT_t) {
    	int result;
    	element_pp_init(result, self);
    	if(result == FALSE) { Py_RETURN_FALSE; }
		self->elem_initPP = TRUE;
		Py_RETURN_TRUE;
    }

    Py_RETURN_FALSE;
}


/* Takes a list of two objects in G1 & G2 respectively and computes the multi-pairing */
PyObject *multi_pairing_asymmetric(Pairing *groupObj, PyObject *listG1, PyObject *listG2)
{
	int length = PySequence_Length(listG1);

	if(length != PySequence_Length(listG2)) {
		PyErr_SetString(ElementError, "unequal number of pairing elements.");
		return NULL;
	}

	if(length > 0) {

		element_t *g1[length];
		element_t *g2[length];
		int i, l = 0, r = 0;

		for(i = 0; i < length; i++) {
			PyObject *tmpObject1 = PySequence_GetItem(listG1, i);
			PyObject *tmpObject2 = PySequence_GetItem(listG2, i);

			if(PyElement_Check(tmpObject1) && PyElement_Check(tmpObject2)) {
				Element *tmp1 = (Element *) tmpObject1;
				Element *tmp2 = (Element *) tmpObject2;
				if(tmp1->element_type == pyG1_t) {
					g1[l] = element_init_G1();
					element_set_raw(groupObj, pyG1_t, g1[l], tmp1->e);
					l++;
				}
				if(tmp2->element_type == pyG2_t) {
 					g2[r] = element_init_G2();
					element_set_raw(groupObj, pyG2_t, g2[r], tmp2->e);
					r++;
				}
			}
			Py_DECREF(tmpObject1);
			Py_DECREF(tmpObject2);
		}

		Element *newObject = NULL;
		if(l == r) {
			newObject = createNewElement(pyGT_t, groupObj);
			element_prod_pairing(newObject, &g1, &g2, l); // pairing product calculation
		}
		else {
			PyErr_SetString(ElementError, "invalid pairing element types in list.");
		}

		/* clean up */
		for(i = 0; i < l; i++) { element_delete(pyG1_t, g1[i]); }
		for(i = 0; i < r; i++) { element_delete(pyG2_t, g2[i]); }
		return (PyObject *) newObject;
	}

	PyErr_SetString(ElementError, "list is empty.");
	return NULL;
}

/* this is a type method that is visible on the global or class level. Therefore,
   the function prototype needs the self (element class) and the args (tuple of Element objects).
 */
PyObject *Apply_pairing(Element *self, PyObject *args)
{
	// lhs => G1_t and rhs => G2
	Element *newObject = NULL, *lhs, *rhs;
	Pairing *group = NULL;
	PyObject *lhs2, *rhs2;
	
	debug("Applying pairing...\n");
	if(!PyArg_ParseTuple(args, "OO|O", &lhs2, &rhs2, &group)) {
		PyErr_SetString(ElementError, "missing element objects");
		return NULL;
	}

	if(PySequence_Check(lhs2) && PySequence_Check(rhs2)) {
		VERIFY_GROUP(group); /* defined iff using as multi-pairing */
		return multi_pairing_asymmetric(group, lhs2, rhs2);
	}
	else if(PyElement_Check(lhs2) && PyElement_Check(rhs2)) {

		lhs = (Element *) lhs2;
		rhs = (Element *) rhs2;

		if(Check_Elements(lhs, rhs) && pair_rule(lhs->element_type, rhs->element_type) == TRUE) {
			newObject = createNewElement(NONE_G, lhs->pairing);
			if(lhs->element_type == pyG1_t) {
				pairing_apply(newObject, lhs, rhs);
			}
			else if(lhs->element_type == pyG2_t) {
				pairing_apply(newObject, rhs, lhs);
			}
#ifdef BENCHMARK_ENABLED
			UPDATE_BENCHMARK(PAIRINGS, newObject->pairing->dBench);
#endif
			return (PyObject *) newObject;
		}
	}

	PyErr_SetString(ElementError, "pairings only apply to elements of G1 x G2 --> GT");
	return NULL;
}

PyObject *sha2_hash(Element *self, PyObject *args) {
	Element *object;
	PyObject *str;
	char *hash_hex = NULL;
	int label = 0;

	debug("Hashing the element...\n");
	if(!PyArg_ParseTuple(args, "O|i", &object, &label)) {
		PyErr_SetString(ElementError, "missing element object");
		return NULL;
	}

	if(!PyElement_Check(object)) {
		PyErr_SetString(ElementError, "not a valid element object.");
		return NULL;
	}
	if(!object->elem_initialized) {
		PyErr_SetString(ElementError, "null element object");
		return NULL;
	}

	int hash_size = HASH_LEN;
	uint8_t hash_buf[hash_size + 1];
	memset(hash_buf, 0, hash_size);
	if(object->element_type == pyGT_t) {
		element_hash_to_key(object, hash_buf, hash_size);

		hash_hex = convert_buffer_to_hex(hash_buf, hash_size);
		printf_buffer_as_hex(hash_buf, hash_size);
	}

	str = PyBytes_FromStringAndSize((const char *) hash_hex, hash_size);
	free(hash_hex);

	return str;
}

// new version that uses same approach as Charm-C++
static PyObject *Element_hash(Element *self, PyObject *args)
{
	Element *newObject = NULL, *object = NULL;
	Pairing *group = NULL;
	PyObject *objList = NULL, *tmpObject = NULL;
	PyObject *tmp_obj = NULL;
	Group_t type = pyZR_t;
	int i;

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
		if(type >= pyZR_t && type < pyGT_t) {
			PyBytes_ToString2(str, objList, tmp_obj);
			int len = strlen(str);
			debug("Hashing string '%s' to Zr...\n", str);
			// create an element of Zr
			// hash bytes using SHA1
			newObject = createNewElement(NONE_G, group);
			newObject->element_type = type;

			element_init_hash(group);
			debug("Hashing string '%s' to Zr...: size=%d, newsize=%d\n", str, len, strlen(str));
			element_add_str_hash(group, str, len);
			element_finish_hash(newObject, type);
			if(tmp_obj != NULL) Py_DECREF(tmp_obj);
		}
		else {
			// not supported, right?
			tmp = "cannot hash a string to that field. Only Zr or G1_t.";
			goto cleanup;
		}
	}
	// second case: is a tuple of elements of which could be a string or group elements
	else if(PySequence_Check(objList)) {
		int size = PySequence_Length(objList);
		if(size > 0) {
			// its a tuple of Elements
			tmpObject = PySequence_GetItem(objList, 0);
			element_init_hash(group);
			if(PyElement_Check(tmpObject)) {
				object = (Element *) tmpObject;

				element_add_to_hash(object);

			}
			else if(PyBytes_CharmCheck(tmpObject)) {
				str = NULL;
				PyBytes_ToString2(str, tmpObject, tmp_obj);

				element_add_str_hash(group, str, strlen(str));

			}
			Py_DECREF(tmpObject);
			if(tmp_obj != NULL) Py_DECREF(tmp_obj);

			// loop over the remaining elements in list
			for(i = 1; i < size; i++) {
				tmpObject = PySequence_GetItem(objList, i);
				if(PyElement_Check(tmpObject)) {
					object = (Element *) tmpObject;

					element_add_to_hash(object);
				}
				else if(PyBytes_CharmCheck(tmpObject)) {
					str = NULL;
					PyBytes_ToString2(str, tmpObject, tmp_obj);

					element_add_str_hash(group, str, strlen(str));

				}
				Py_DECREF(tmpObject);
				if(tmp_obj != NULL) Py_DECREF(tmp_obj);
			}

			if(type >= pyZR_t && type < pyGT_t) { newObject = createNewElement(NONE_G, group); }
			else {
				tmp = "invalid object type";
				goto cleanup;
			}

			newObject->element_type = type;
			element_finish_hash(newObject, type);

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

		// Hash an element of Zr to an element of G1_t.
		if(type == pyG1_t) {

			newObject = createNewElement(NONE_G, group);
			newObject->element_type = type;
			// hash the element to the G1_t field (uses sha1 as well)
			element_init_hash(group);
			element_add_to_hash(object);
			element_finish_hash(newObject, type);

		}
		else {
			tmp = "can only hash an element of Zr to G1_t. Random Oracle.";
			goto cleanup;
		}
	}
    else {
		tmp = "invalid object types";
		goto cleanup;
	}


	return (PyObject *) newObject;

cleanup:
	PyErr_SetString(ElementError, tmp);
	if(newObject != NULL) Py_DECREF(newObject);
	return NULL;
}

static PyObject *Element_equals(PyObject *lhs, PyObject *rhs, int opid) {
	Element *self = NULL, *other = NULL;
	signed long int z;
	int found_int = FALSE, result = -1; // , value;

	if(opid != Py_EQ && opid != Py_NE) {
		PyErr_SetString(ElementError, "only comparison supported is '==' or '!='");
		goto cleanup;
	}

	// check type of lhs
	if(PyElement_Check(lhs)) {
		self = (Element *) lhs;
	}
	else if(PyNumber_Check(lhs)) {
		if(PyArg_Parse(lhs, "l", &z)) {
			debug("Integer lhs: '%li'\n", z);
		}
		found_int = (z == 0 || z == 1) ? TRUE : FALSE;
	}
	else {
		PyErr_SetString(ElementError, "types supported: element or int (0 or 1)");
		goto cleanup;
	}

	// check type of rhs
	if(PyElement_Check(rhs)) {
		other = (Element *) rhs;
	}
	else if(PyNumber_Check(rhs)) {
		if(PyArg_Parse(lhs, "l", &z)) {
			debug("Integer rhs: '%li'\n", z);
		}
		found_int = (z == 0 || z == 1) ? TRUE : FALSE;
	}
	else {
		PyErr_SetString(ElementError, "types supported: element or int (0 or 1)");
		goto cleanup;
	}

	debug("Starting '%s'\n", __func__);

	if(PyElement_Check(lhs) && found_int) {
		// lhs is the element type
		if(self->element_type == pyZR_t)
			result = element_is(self, z);
	}
	else if(PyElement_Check(rhs) && found_int) {
		if(other->element_type == pyZR_t)
			result = element_is(other, z);
	}
	else if(PyElement_Check(lhs) && PyElement_Check(rhs)) {
		// lhs and rhs are both elements
		if(self->elem_initialized && other->elem_initialized) {
			if(self->element_type == other->element_type)
				result = element_cmp(self, other);
		}
		else {
			debug("One of the elements is not initialized.\n");
		}
	}


	if(result == -1) {
		/* print error */
		PyErr_SetString(ElementError, "cannot compare different group types.\n");
		return NULL;
	}
cleanup:
//	value = (result == 0) ? TRUE : FALSE;

	if(opid == Py_EQ) {
		if(result == TRUE) {
			Py_RETURN_TRUE;
		}
		Py_RETURN_FALSE;
	}
	else { /* Py_NE */
		if(result == FALSE) {
			Py_RETURN_TRUE;
		}
		Py_RETURN_FALSE;
	}
}

static PyObject *Element_long(PyObject *o1) {
	if(PyElement_Check(o1)) {
		Element *value = (Element *) o1;
		/* can only handle elements in ZR */
		if(value->element_type == pyZR_t) {
			mpz_t val;
			mpz_init(val);
			element_to_mpz(value, val);
			PyObject *obj = mpzToLongObj(val);
			mpz_clear(val);
			return obj;
		}
	}
	PyErr_SetString(ElementError, "cannot cast pairing object to an integer.");
	return NULL;
}

static long Element_index(Element *o1) {
	long result = -1;

	if(PyElement_Check(o1)) {
		if(o1->element_type == pyZR_t) {
			mpz_t o;
			mpz_init(o);
			element_to_mpz(o1, o);
			PyObject *temp = mpzToLongObj(o);
			result = PyObject_Hash(temp);
			mpz_clear(o);
			Py_XDECREF(temp); //PyObject_Del(temp);
		}
	}
	return result;
}


UNARY(instance_negate, 'i', Element_negate)
UNARY(instance_invert, 'i', Element_invert)
BINARY(instance_add, 'a', Element_add)
BINARY(instance_sub, 's', Element_sub)

static PyObject *Serialize_cmp(Element *o1, PyObject *args) {

	Element *self = NULL;
	if(!PyArg_ParseTuple(args, "O", &self)) {
		PyErr_SetString(ElementError, "invalid argument.");
		return NULL;
	}

	if(!PyElement_Check(self)) {
		PyErr_SetString(ElementError, "not a valid element object.");
		return NULL;
	}
	if(self->elem_initialized == FALSE) {
		PyErr_SetString(ElementError, "element not initialized.");
		return NULL;
	}

	int elem_len = 0;
	uint8_t *data_buf = NULL;
	size_t bytes_written;


//	printf("element type => '%d'\n", self->element_type);
//	print("test output => ", self->element_type, self->e);
	if(check_type(self->element_type) == TRUE) {
		// determine size of buffer we need to allocate
		elem_len = element_length_in_bytes(self);
		data_buf = (uint8_t *) malloc(elem_len + 1);
		memset(data_buf, 0, elem_len);
		if(data_buf == NULL) {
			PyErr_SetString(ElementError, "out of memory.");
			return NULL;
		}

		// write to char buffer
		bytes_written = element_to_bytes(data_buf, self);
		if(elem_len != bytes_written) {
			PyErr_SetString(ElementError, "serialization failed. try again.");
			free(data_buf);
			return NULL;
		}
		debug("result => ");
		printf_buffer_as_hex(data_buf, bytes_written);
	}
	else {
		PyErr_SetString(ElementError, "invalid type.\n");
		return NULL;
	}

	PyObject *result = PyBytes_FromFormat("%d:%s", self->element_type, (const char *) data_buf);
	debug("enc => '%s'\n", data_buf);
	free(data_buf);

	return result;
}

static PyObject *Deserialize_cmp(Element *self, PyObject *args) {
	Element *origObject = NULL;
	Pairing *group = NULL;
	PyObject *object;

	if(PyArg_ParseTuple(args, "OO", &group, &object)) {
		VERIFY_GROUP(group);
		if(PyBytes_Check(object)) {
			uint8_t *serial_buf = (uint8_t *) PyBytes_AsString(object);
			int type = atoi((const char *) &(serial_buf[0]));
			uint8_t *base64_buf = (uint8_t *)(serial_buf + 2);
//			printf("type => %d\n", type);
//			printf("base64 dec => '%s'\n", base64_buf);

			if(check_type(type) == TRUE && strlen((char *) base64_buf) > 0) {
//				debug("result => ");
//				printf_buffer_as_hex(binary_buf, deserialized_len);
				origObject = createNewElement(NONE_G, group);
				origObject->element_type = type;
				element_from_bytes(origObject, base64_buf);

				return (PyObject *) origObject;
			}
		}
		PyErr_SetString(ElementError, "string object malformed.");
		return NULL;
	}

	PyErr_SetString(ElementError, "nothing to deserialize in element.");
	return NULL;
}

static PyObject *Group_Check(Element *self, PyObject *args) {

	Pairing *group = NULL;
	Element *object = NULL;
	if(PyArg_ParseTuple(args, "OO", &group, &object)) {
		VERIFY_GROUP(group);
		if(PyElement_Check(object)) {
			if(check_membership(object) == TRUE) {
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

	Pairing *group = NULL;
	if(!PyArg_ParseTuple(args, "O", &group)) {
		PyErr_SetString(ElementError, "invalid group object.");
		return NULL;
	}

	VERIFY_GROUP(group);
	mpz_t d;
	mpz_init(d);
	object_to_mpz(group->order, d);
	PyObject *object = (PyObject *) mpzToLongObj(d);
	mpz_clear(d);
	return object; /* returns a PyInt */
}

/* TODO: move to cryptobase */
PyObject *AES_Encrypt(Element *self, PyObject *args)
{
	PyObject *keyObj = NULL, *tmp_obj = NULL; // string or bytes object
	char *messageStr;
	int m_len = 0;

	if(!PyArg_ParseTuple(args, "Os#", &keyObj, &messageStr, &m_len)) {
		PyErr_SetString(ElementError, "invalid arguments.");
		return NULL;
	}

	if((m_len % aes_block_size) != 0) {
		PyErr_SetString(ElementError, "message not 16-byte block aligned. Add some padding.");
		return NULL;
	}

	char *keyStr;
	if(PyBytes_CharmCheck(keyObj)) {
		PyBytes_ToString2(keyStr, keyObj, tmp_obj);
		//printf("key => '%s'\n", keyStr);
		//printf("message => '%s'\n", messageStr);
		// perform AES encryption using miracl
		char *cipher = NULL;

		int c_len = aes_encrypt(keyStr, messageStr, m_len, &cipher);

		PyObject *str = PyBytes_FromStringAndSize((const char *) cipher, c_len);
		free(cipher);
		if(tmp_obj != NULL) Py_DECREF(tmp_obj);
		return str;
	}

	PyErr_SetString(ElementError, "invalid objects.");
	return NULL;
}

PyObject *AES_Decrypt(Element *self, PyObject *args)
{
	PyObject *keyObj = NULL, *tmp_obj = NULL; // string or bytes object
	char *ciphertextStr;
	int c_len = 0;

	if(!PyArg_ParseTuple(args, "Os#", &keyObj, &ciphertextStr, &c_len)) {
		PyErr_SetString(ElementError, "invalid arguments.");
		return NULL;
	}

	char *keyStr;
	if(PyBytes_CharmCheck(keyObj)) {
		PyBytes_ToString2(keyStr, keyObj, tmp_obj);
//		printf("key => '%s'\n", keyStr);
//		printf("message => '%s'\n", ciphertextStr);
		// perform AES encryption using miracl
		char *message = NULL;

		int m_len = aes_decrypt(keyStr, ciphertextStr, c_len, &message);

		PyObject *str = PyBytes_FromStringAndSize((const char *) message, m_len);
		free(message);
		if(tmp_obj != NULL) Py_DECREF(tmp_obj);
		return str;
	}

	PyErr_SetString(ElementError, "invalid objects.");
	return NULL;

}

#ifdef BENCHMARK_ENABLED

#define BenchmarkIdentifier 1
#define GET_RESULTS_FUNC	GetResultsWithPair
#define GROUP_OBJECT		Pairing
#define BENCH_ERROR			ElementError
/* helper function for granularBenchmar */
PyObject *PyCreateList(Operations *gBench, MeasureType type)
{
	int countZR = -1, countG1 = -1, countG2 = -1, countGT = -1;
	GetField(countZR, type, pyZR_t, gBench);
	GetField(countG1, type, pyG1_t, gBench);
	GetField(countG2, type, pyG2_t, gBench);
	GetField(countGT, type, pyGT_t, gBench);

	PyObject *objList = Py_BuildValue("[iiii]", countZR, countG1, countG2, countGT);
	return objList;
}

#include "benchmark_util.c"

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
	(reprfunc)Pairing_print, 	/*tp_repr*/
	0,               /*tp_as_number*/
	0,                         /*tp_as_sequence*/
	0,                         /*tp_as_mapping*/
	0,                         /*tp_hash */
	0,                         /*tp_call*/
    (reprfunc)Pairing_print,   /*tp_str*/
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
    (reprfunc)Pairing_print,   /*tp_repr*/
    0,       /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0, 						/*tp_call*/
    (reprfunc)Pairing_print,   /*tp_str*/
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
	{"type", T_INT, offsetof(Element, element_type), 0,
		"group type"},
    {"initialized", T_INT, offsetof(Element, elem_initialized), 0,
		"determine initialization status"},
    {NULL}  /* Sentinel */
};

PyMethodDef Element_methods[] = {
	{"initPP", (PyCFunction)Element_initPP, METH_NOARGS, "Initialize the pre-processing field of element."},
	{"set", (PyCFunction)Element_set, METH_VARARGS, "Set an element to a fixed value."},
	{"setPoint", (PyCFunction)Element_setxy, METH_VARARGS, "Set x and y coordinates of a G1 element object."},
    {NULL}  /* Sentinel */
};

PyMethodDef pairing_methods[] = {
	{"init", (PyCFunction)Element_elem, METH_VARARGS, "Create an element in a specific group: G1, G2, GT or Zr"},
	{"random", (PyCFunction)Element_random, METH_VARARGS, "Return a random element in a specific group: G1_t, G2, Zr"},
	{"H", (PyCFunction)Element_hash, METH_VARARGS, "Hash an element type to a specific field: Zr, G1_t, or G2"},
	{"serialize", (PyCFunction)Serialize_cmp, METH_VARARGS, "Serialize an element type into bytes."},
	{"deserialize", (PyCFunction)Deserialize_cmp, METH_VARARGS, "De-serialize an bytes object into an element object"},
	{"ismember", (PyCFunction) Group_Check, METH_VARARGS, "Group membership test for element objects."},
	{"order", (PyCFunction) Get_Order, METH_VARARGS, "Get the group order for a particular field."},

	{"pair", (PyCFunction)Apply_pairing, METH_VARARGS, "Apply pairing between an element of G1_t and G2 and returns an element mapped to GT"},
	{"hashPair", (PyCFunction)sha2_hash, METH_VARARGS, "Compute a sha1 hash of an element type"},
//	{"SymEnc", (PyCFunction) AES_Encrypt, METH_VARARGS, "AES encryption args: key (bytes or str), message (str)"},
//	{"SymDec", (PyCFunction) AES_Decrypt, METH_VARARGS, "AES decryption args: key (bytes or str), ciphertext (str)"},
#ifdef BENCHMARK_ENABLED
	{"InitBenchmark", (PyCFunction)InitBenchmark, METH_VARARGS, "Initialize a benchmark object"},
	{"StartBenchmark", (PyCFunction)StartBenchmark, METH_VARARGS, "Start a new benchmark with some options"},
	{"EndBenchmark", (PyCFunction)EndBenchmark, METH_VARARGS, "End a given benchmark"},
	{"GetBenchmark", (PyCFunction)GetBenchmark, METH_VARARGS, "Returns contents of a benchmark object"},
	{"GetGeneralBenchmarks", (PyCFunction)GetAllBenchmarks, METH_VARARGS, "Retrieve general benchmark info as a dictionary"},
	{"GetGranularBenchmarks", (PyCFunction) GranularBenchmark, METH_VARARGS, "Retrieve granular benchmarks as a dictionary"},
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
    Py_XDECREF(ElementError);
	return 0;
}

static int pairings_free(PyObject *m) {
	if(pairing_init_finished == FALSE)
		miracl_clean(); // mirsys was called
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
		(inquiry) pairings_clear,
		(freefunc) pairings_free
};

#define CLEAN_EXIT goto LEAVE;
#define INITERROR return NULL
PyMODINIT_FUNC
PyInit_pairing(void) 		{
#else
#define CLEAN_EXIT goto LEAVE;
#define INITERROR return
void initpairing(void) 		{
#endif
    PyObject* m;
	
#if PY_MAJOR_VERSION >= 3
    m = PyModule_Create(&moduledef);
#else
    m = Py_InitModule("pairing", pairing_methods);
#endif

    if(PyType_Ready(&PairingType) < 0)
        CLEAN_EXIT;
    if(PyType_Ready(&ElementType) < 0)
        CLEAN_EXIT;
#ifdef BENCHMARK_ENABLED
    if(import_benchmark() < 0)
        CLEAN_EXIT;
    if(PyType_Ready(&BenchmarkType) < 0)
        CLEAN_EXIT;
    if(PyType_Ready(&OperationsType) < 0)
    	CLEAN_EXIT;
#endif

    struct module_state *st = GETSTATE(m);
    st->error = PyErr_NewException("pairing.Error", NULL, NULL);
    if(st->error == NULL)
        CLEAN_EXIT;
    ElementError = st->error;
    Py_INCREF(ElementError);

    Py_INCREF(&ElementType);
    PyModule_AddObject(m, "pc_element", (PyObject *)&ElementType);
    Py_INCREF(&PairingType);
    PyModule_AddObject(m, "pairing", (PyObject *)&PairingType);

	PyModule_AddIntConstant(m, "ZR", pyZR_t);
	PyModule_AddIntConstant(m, "G1", pyG1_t);
	PyModule_AddIntConstant(m, "G2", pyG2_t);
	PyModule_AddIntConstant(m, "GT", pyGT_t);

#ifdef BENCHMARK_ENABLED
	ADD_BENCHMARK_OPTIONS(m);
	PyModule_AddStringConstant(m, "Pair", 	  _PAIR_OPT);
	PyModule_AddStringConstant(m, "Granular", _GRAN_OPT);
#endif

	// builtin curves
	PyModule_AddIntConstant(m, "MNT160", MNT160);
	PyModule_AddIntConstant(m, "BN256", BN256);
	PyModule_AddIntConstant(m, "SS512", SS512);
	PyModule_AddIntConstant(m, "SS1536", SS1536);

LEAVE:
    if (PyErr_Occurred()) {
		PyErr_Clear();
        Py_XDECREF(m);
    	INITERROR;
    }
	pairing_init_finished = TRUE;

#if PY_MAJOR_VERSION >= 3
	return m;
#endif
}
