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
	if(lhs == ZR_t && rhs == ZR_t) return TRUE;
	if(lhs == G1_t && rhs == ZR_t) return TRUE;
	if(lhs == G2_t && rhs == ZR_t) return TRUE;
	if(lhs == GT_t && rhs == ZR_t) return TRUE;
	return FALSE; /* Fail all other cases */
}

int mul_rule(Group_t lhs, Group_t rhs)
{
	if(lhs == rhs) return TRUE;
	if(lhs == ZR_t || rhs == ZR_t) return TRUE;
	return FALSE; /* Fail all other cases */
}

int add_rule(Group_t lhs, Group_t rhs)
{
	if(lhs == rhs && lhs != GT_t) return TRUE;
	return FALSE; /* Fail all other cases */
}

int sub_rule(Group_t lhs, Group_t rhs)
{
	if(lhs == rhs && lhs != GT_t) return TRUE;
	return FALSE; /* Fail all other cases */
}

int div_rule(Group_t lhs, Group_t rhs)
{
	if(lhs == rhs) return TRUE;
	return FALSE; /* Fail all other cases */
}

int pair_rule(Group_t lhs, Group_t rhs)
{
	if(lhs == G1_t && rhs == G2_t) return TRUE;
	return FALSE; /* Fall all other cases : assume MNT? */
}

int check_type(Group_t type) {
	if(type == ZR_t || type == G1_t || type == G2_t || type == GT_t) return TRUE;
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

PyObject *mpzToLongObj (mpz_t m)
{
	/* borrowed from gmpy */
	int size = (mpz_sizeinbase (m, 2) + PyLong_SHIFT - 1) / PyLong_SHIFT;
	int i;
	mpz_t temp;
	PyLongObject *l = _PyLong_New (size);
	if (!l)
		return NULL;
	mpz_init_set (temp, m);
	for (i = 0; i < size; i++)
	{
		l->ob_digit[i] = (digit) (mpz_get_ui (temp) & PyLong_MASK);
		mpz_fdiv_q_2exp (temp, temp, PyLong_SHIFT);
	}
	i = size;
	while ((i > 0) && (l->ob_digit[i - 1] == 0))
		i--;
	Py_SIZE(l) = i;
	mpz_clear (temp);
	return (PyObject *) l;
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
			if(l_type == GT_t || r_type == GT_t) { return FALSE; }
			break;
		case 's':
			if(l_type == GT_t || r_type == GT_t) { return FALSE; }
			break;
		case 'e':
			if(l_type != G1_t && r_type != G2_t) { return FALSE; }
			break;
		case 'p':
			// rule for exponentiation for types
			if(l_type != G1_t && l_type != G2_t && l_type != GT_t && l_type != ZR_t) { return FALSE; }
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
	if(element_type == ZR_t) {
		retObject->e = element_init_ZR(0);
		retObject->element_type = ZR_t;
	}
	else if(element_type == G1_t) {
		retObject->e = element_init_G1();
		retObject->element_type = G1_t;
	}
	else if(element_type == G2_t) {
		retObject->e = element_init_G2();
		retObject->element_type = G2_t;
	}
	else if(element_type == GT_t) {
		retObject->e = element_init_GT(pairing);
		retObject->element_type = GT_t;
	}
	else {
		// init without a type -- caller must set e and element_type
	}
	
	retObject->elem_initialized = TRUE;
	retObject->pairing = pairing;
	retObject->safe_pairing_clear = FALSE;
	return retObject;	
}

Element *convertToZR(PyObject *longObj, PyObject *elemObj) {
	Element *self = (Element *) elemObj;
	Element *new = createNewElement(ZR_t, self->pairing);

	mpz_t x;
	mpz_init(x);
#if PY_MAJOR_VERSION < 3
	longObj = PyNumber_Long(longObj);
#endif
	longObjToMPZ(x, (PyLongObject *) longObj);
	element_set_mpz(new, x);
	mpz_clear(x);
	return new;
}

void 	Pairing_dealloc(Pairing *self)
{
	if(self->safe) {
		pairing_clear(self->pair_obj);
		element_delete(ZR_t, self->order);
		self->pair_obj = NULL;
		self->order = NULL;
	}

	Py_TYPE(self)->tp_free((PyObject *) self);
}

void	Element_dealloc(Element* self)
{
	// add reference count to objects
	if(self->elem_initialized) {
//		debug_e("Clear element_t => '%B'\n", self->e);
		element_delete(self->element_type, self->e);
	}
	
	if(self->safe_pairing_clear) {
		pairing_clear(self->pairing->pair_obj);
		self->pairing->pair_obj = NULL;
		element_delete(ZR_t, self->pairing->order);
		self->pairing->order = NULL;
		PyObject_Del(self->pairing);
	}

	Py_TYPE(self)->tp_free((PyObject*)self);
}

//// helper method
//ssize_t read_file(FILE *f, char** out)
//{
//	if(f != NULL) {
//		/* See how big the file is */
//		fseek(f, 0L, SEEK_END);
//		ssize_t out_len = ftell(f);
//		debug("out_len: %zd\n", out_len);
//		if(out_len <= MAX_LEN) {
//			/* allocate that amount of memory only */
//			if((*out = (char *) malloc(out_len+1)) != NULL) {
//				fseek(f, 0L, SEEK_SET);
//				fread(*out, sizeof(char), out_len, f);
//				return out_len;
//			}
//		}
//	}
//
//	return 0;
//}

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
int hash_to_bytes(uint8_t *input_buf, int input_len, int hash_size, uint8_t* output_buf, uint32_t hash_num)
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

		SHA1Input(&sha_context, (unsigned char*)&(block_hdr[0]), sizeof(block_hdr));
		SHA1Input(&sha_context, (unsigned char *)input_buf, input_len);

		SHA1Result(&sha_context);
		if (hash_size <= 20) {
			memcpy(output_buf, sha_context.Message_Digest, hash_size);
			hash_size = 0;
		} else {
			memcpy(output_buf, sha_context.Message_Digest, 20);
			input_buf = (uint8_t *) output_buf;
			hash_size -= 20;
			output_buf += 20;
		}
	}

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
	result = hash_to_bytes(temp_buf, buf_len, hash_size, output_buf, prefix);

	free(temp_buf);

	return TRUE;
}

// take a previous hash and concatenate with serialized bytes of element and hashes into output buf
int hash2_element_to_bytes(Element *element, uint8_t* last_buf, int hash_size, uint8_t* output_buf) {
	int result = TRUE;
	// assume last buf contains a hash
	unsigned int last_buflen = hash_size;
	unsigned int buf_len = element_length_in_bytes(element);

	uint8_t* temp_buf = (uint8_t *) malloc(buf_len + 1);
	memset(temp_buf, '\0', buf_len);
	if(temp_buf == NULL) {
		return FALSE;
	}

	element_to_bytes((unsigned char *) temp_buf, element);
	// create output buffer
	uint8_t* temp2_buf = (uint8_t *) malloc(last_buflen + buf_len + 4);
	memset(temp2_buf, 0, (last_buflen + buf_len));
//	// copy first input buffer (last_buf) into target buffer
//	strncat((char *) temp2_buf, (char *) last_buf, last_buflen);
//	// copy element buffer (temp_buf) into target buffer
//	strncat((char *) temp2_buf, (char *) temp_buf, buf_len);
	int i;
	for(i = 0; i < last_buflen; i++) {
		temp2_buf[i] = last_buf[i];
	}

	int j = 0;
	for(i = last_buflen; i < (last_buflen + buf_len); i++) {
		temp2_buf[i] = temp_buf[j];
		j++;
	}
	// hash the temp2_buf to bytes
	result = hash_to_bytes(temp2_buf, (last_buflen + buf_len), hash_size, output_buf, HASH_FUNCTION_ELEMENTS);

	free(temp2_buf);
	free(temp_buf);
	return TRUE;
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

	result = hash_to_bytes(temp_buf, (input_len + hash_size), hash_size, output_buf, HASH_FUNCTION_STRINGS);

	PyObject_Del(last);
	return TRUE;
}

PyObject *Element_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    Element *self;
	
    self = (Element *)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->elem_initialized = FALSE;
		self->safe_pairing_clear = FALSE;
		self->pairing = NULL;
		self->element_type = NONE_G;
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
	Pairing *pairing = NULL;
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
    	pairing = PyObject_New(Pairing, &PairingType);
		pairing->pair_obj = pairing_init(aes_sec);
		pairing->order    = order(pairing->pair_obj);
		pairing->curve	  = MNT; // only supported at this point
		pairing_init_finished 	  = FALSE;
    }

	self->pairing = pairing;
	self->elem_initialized = FALSE;
	self->safe_pairing_clear = TRUE;
    return 0;
}

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

	if(type >= ZR_t && type <= GT_t) {
		retObject = createNewElement(type, group->pairing);
	}
	else {
		PyErr_SetString(ElementError, "unrecognized group type.");
		return NULL;
	}

	if(long_obj != NULL && PyLong_Check(long_obj)) {
		mpz_t m;
		mpz_init(m);
		longObjToMPZ(m, (PyLongObject *) long_obj);
		element_set_mpz(retObject, m);
		mpz_clear(m);
	}
	
	/* return Element object */
	return (PyObject *) retObject;		
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
	Element *retObject, *group = NULL;
	int arg1;
	int seed = -1;
	
	/* create a new object */
	if(!PyArg_ParseTuple(args, "Oi|i", &group, &arg1, &seed))
		return NULL;

	START_CLOCK(dBench);
	retObject = PyObject_New(Element, &ElementType);
	debug("init random element in '%d'\n", arg1);
	if(arg1 == ZR_t) {
		retObject->e = element_init_ZR(0);
		retObject->element_type = ZR_t;
	}
	else if(arg1 == G1_t) {
		retObject->e = element_init_G1();
		retObject->element_type = G1_t;
	}
	else if(arg1 == G2_t) {
		retObject->e = element_init_G2();
		retObject->element_type = G2_t;
	}
	else if(arg1 == GT_t) {
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
    element_random(retObject->element_type, group->pairing->pair_obj, retObject->e);

	STOP_CLOCK(dBench);
	retObject->elem_initialized = TRUE;
	retObject->pairing = group->pairing;
	retObject->safe_pairing_clear = FALSE;
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
	START_CLOCK(dBench);
	newObject = createNewElement(self->element_type, self->pairing);
	element_add(newObject, self, other);
	STOP_CLOCK(dBench);
	UPDATE_BENCHMARK(ADDITION, dBench);
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

	START_CLOCK(dBench);
	newObject = createNewElement(self->element_type, self->pairing);
	element_sub(newObject, self, other);
	STOP_CLOCK(dBench);
	UPDATE_BENCHMARK(SUBTRACTION, dBench);
	return (PyObject *) newObject;
}


/* requires more care -- understand possibilities first */
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
		START_CLOCK(dBench);
		newObject = createNewElement(self->element_type, self->pairing);
		element_mul_si(newObject, self, z);
		STOP_CLOCK(dBench);
	}
	else if(PyElement_Check(rhs) && found_int) {
		// rhs is the element type
		START_CLOCK(dBench);
		newObject = createNewElement(other->element_type, other->pairing);
		element_mul_si(newObject, other, z);
		STOP_CLOCK(dBench);
	}
	else if(PyElement_Check(lhs) && PyElement_Check(rhs)) {
		// both are element types
		if( mul_rule(self->element_type, other->element_type) == FALSE) {
			PyErr_SetString(ElementError, "invalid mul operation");
			return NULL;
		}

		if(self->element_type != ZR_t && other->element_type == ZR_t) {
			START_CLOCK(dBench);
			newObject = createNewElement(self->element_type, self->pairing);
			element_mul_zn(newObject, self, other);
			STOP_CLOCK(dBench);
		}
		else if(other->element_type != ZR_t && self->element_type == ZR_t) {
			// START_CLOCK
			START_CLOCK(dBench);
			newObject = createNewElement(other->element_type, self->pairing);
			element_mul_zn(newObject, other, self);
			STOP_CLOCK(dBench);
		}
		else { // all other cases
			// START_CLOCK
			START_CLOCK(dBench);
			newObject = createNewElement(self->element_type, self->pairing);
			element_mul(newObject, self, other);
			STOP_CLOCK(dBench);
		}
	}
	else {
		PyErr_SetString(ElementError, "invalid types");
		return NULL;
	}

	UPDATE_BENCHMARK(MULTIPLICATION, dBench);
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
		START_CLOCK(dBench);
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
		STOP_CLOCK(dBench);
	}
	else if(PyElement_Check(rhs) && found_int) {
		// rhs is the element type
		START_CLOCK(dBench);
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
		STOP_CLOCK(dBench);
	}
	else if(PyElement_Check(lhs) && PyElement_Check(rhs)) {
		// both are element types
		if( div_rule(self->element_type, other->element_type) == FALSE) {
			PyErr_SetString(ElementError, "invalid div operation");
			return NULL;
		}

		START_CLOCK(dBench);
		newObject = createNewElement(self->element_type, self->pairing);
		element_div(newObject, self, other);
		STOP_CLOCK(dBench);
	}
	else {
		PyErr_SetString(ElementError, "invalid types");
		return NULL;
	}

	UPDATE_BENCHMARK(DIVISION, dBench);
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

	START_CLOCK(dBench);
	if(check_type(self->element_type)) {
		newObject = createNewElement(self->element_type, self->pairing);
		element_invert(newObject, self);
	}
	STOP_CLOCK(dBench);
	return (PyObject *) newObject;
}

static PyObject *Element_negate(Element *self)
{
	Element *newObject = NULL;

	START_CLOCK(dBench);
	newObject = createNewElement(self->element_type, self->pairing);
	element_neg(newObject, self);
	STOP_CLOCK(dBench);

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
		printf("operation undefined: <Python Int> ^ '%d'\n", rhs_o2->element_type);
//		if(rhs_o2->element_type == ZR) {
//			START_CLOCK(dBench);
//			mpz_init(n);
//			element_to_mpz(n, rhs_o2);
//
//			lhs_o1 = convertToZR(o1, o2);
//			newObject = createNewElement(rhs_o2->element_type, rhs_o2->pairing);
//			element_pow_zr(newObject, lhs_o1, n);
//			mpz_clear(n);
//			PyObject_Del(lhs_o1);
//			STOP_CLOCK(dBench);
//		}
	}
	else if(longFoundRHS) {
		// o2 is a long type
//		if(lhs_o1->element_type != ZR_t) {
		START_CLOCK(dBench);
		long rhs = PyLong_AsLong(o2);
		if(PyErr_Occurred() || rhs > 0) {
			// clear error and continue
			//PyErr_Print(); // for debug purposes
			PyErr_Clear();
			newObject = createNewElement(lhs_o1->element_type, lhs_o1->pairing);
			rhs_o2 = createNewElement(ZR_t, lhs_o1->pairing);
			mpz_init(n);
			longObjToMPZ(n, (PyLongObject *) o2);
			element_set_mpz(rhs_o2, n);
			element_pow_zr(newObject, lhs_o1, rhs_o2);
			PyObject_Del(rhs_o2);
			mpz_clear(n);
			STOP_CLOCK(dBench);
		}
		else if(rhs == -1) {
			newObject = createNewElement(lhs_o1->element_type, lhs_o1->pairing);
			element_invert(newObject, lhs_o1);
			STOP_CLOCK(dBench);
		}
		else {
			EXIT_IF(TRUE, "unexpected error.");
		}
	}
	else if(Check_Elements(o1, o2)) {
		debug("Starting '%s'\n", __func__);
		EXIT_IF(exp_rule(lhs_o1->element_type, rhs_o2->element_type) == FALSE, "invalid exp operation.");

		if(rhs_o2->element_type == ZR_t) {
			START_CLOCK(dBench);
			newObject = createNewElement(NONE_G, lhs_o1->pairing);
			element_pow_zr(newObject, lhs_o1, rhs_o2);
			STOP_CLOCK(dBench);
		}
	}
	else {
		EXIT_IF(!PyElement_Check(o1), ERROR_TYPE(left, int, bytes, str));
		EXIT_IF(!PyElement_Check(o2), ERROR_TYPE(right, int, bytes, str));
	}

	UPDATE_BENCHMARK(EXPONENTIATION, dBench);
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
    	if(value == -1 && self->element_type == ZR_t) {
            debug("Setting element to '%li'\n", value);
            START_CLOCK(dBench);
            debug("Value '%i'\n", (signed int) value);
            element_set_si(self, (signed int) value);
            STOP_CLOCK(dBench);
		}
    	else if(object != NULL) {

    		if(self->element_type == object->element_type) {
    			START_CLOCK(dBench);
    			element_set(self, object);
    			STOP_CLOCK(dBench);
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
    	errcode = FALSE;
    	return Py_BuildValue("i", errcode);
    }

//    if(check_type(self->element_type) == FALSE) {
//    	PyErr_SetString(ElementError, "must initialize element to a field (G1_t,G2,GT, or Zr)");
//    	errcode = FALSE;
//    	return Py_BuildValue("i", errcode);
//    }
//
    debug("Creating a new element\n");
    if(PyArg_ParseTuple(args, "|OO", &object1, &object2)) {
            // convert into an int using PyArg_Parse(...)
            // set the element
    	if(self->element_type == G1_t) {
    		if(object1->element_type == object2->element_type && object1->element_type == ZR_t) {
    			errcode = element_setG1(self, object1, object2);
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

/* Takes a list of two objects in G1 & G2 respectively and computes the multi-pairing */
PyObject *multi_pairing_asymmetric(Element *groupObj, PyObject *listG1, PyObject *listG2) {

//	int GroupSymmetric = FALSE;
	// check for symmetric vs. asymmetric
//	if(pairing_is_symmetric(groupObj->pairing->pair_obj)) {
//		GroupSymmetric = TRUE;
//	}

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
				if(tmp1->element_type == G1_t) {
					g1[l] = element_init_G1();
					element_set_raw(groupObj, G1_t, g1[l], tmp1->e);
					l++;
				}
				if(tmp2->element_type == G2_t) {
 					g2[r] = element_init_G2();
					element_set_raw(groupObj, G2_t, g2[r], tmp2->e);
					r++;
				}
			}
			Py_DECREF(tmpObject1);
			Py_DECREF(tmpObject2);
		}

		Element *newObject = NULL;
		if(l == r) {
			newObject = createNewElement(GT_t, groupObj->pairing);
			element_prod_pairing(newObject, &g1, &g2, l); // pairing product calculation
		}
		else {
			PyErr_SetString(ElementError, "invalid pairing element types in list.");
		}

		/* clean up */
		for(i = 0; i < l; i++) { element_delete(G1_t, g1[i]); }
		for(i = 0; i < r; i++) { element_delete(G2_t, g2[i]); }
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
	Element *newObject = NULL, *lhs, *rhs, *group = NULL;
	PyObject *lhs2, *rhs2;
	
	debug("Applying pairing...\n");
	if(!PyArg_ParseTuple(args, "OO|O", &lhs2, &rhs2, &group)) {
		PyErr_SetString(ElementError, "missing element objects");
		return NULL;
	}

	if(PySequence_Check(lhs2) && PySequence_Check(rhs2)) {
		VERIFY_GROUP(group);
		return multi_pairing_asymmetric(group, lhs2, rhs2);
	}
	else if(PyElement_Check(lhs2) && PyElement_Check(rhs2)) {

		lhs = (Element *) lhs2;
		rhs = (Element *) rhs2;

		if(Check_Elements(lhs, rhs) && pair_rule(lhs->element_type, rhs->element_type) == TRUE) {
			START_CLOCK(dBench);
			newObject = createNewElement(NONE_G, lhs->pairing);
			pairing_apply(newObject, lhs, rhs);
			STOP_CLOCK(dBench);
			UPDATE_BENCHMARK(PAIRINGS, dBench);
			return (PyObject *) newObject;
		}
	}

	PyErr_SetString(ElementError, "pairings only apply to elements of G1 x G2 --> GT");
	return NULL;
}

PyObject *sha1_hash(Element *self, PyObject *args) {
	Element *object;
	PyObject *str;
	char *hash_hex = NULL;
	int label = 0;

	debug("Hashing the element...\n");
	if(!PyArg_ParseTuple(args, "O|i", &object, &label)) {
		PyErr_SetString(ElementError, "missing element object");
		return NULL;
	}

	if(!object->elem_initialized) {
		PyErr_SetString(ElementError, "null element object");
		return NULL;
	}
	START_CLOCK(dBench);
	int hash_size = HASH_LEN;
	uint8_t hash_buf[hash_size + 1];
	if(!hash_element_to_bytes(object, hash_size, hash_buf, label)) {
		PyErr_SetString(ElementError, "failed to hash element");
		return NULL;
	}

	hash_hex = convert_buffer_to_hex(hash_buf, hash_size);
	printf_buffer_as_hex(hash_buf, hash_size);
	


	str = PyBytes_FromString((const char *) hash_hex);
	free(hash_hex);
	STOP_CLOCK(dBench);
	return str;
}

PyObject *sha1_hash2(Element *self, PyObject *args) {
	Element *object;
	PyObject *str;
	char *hash_hex = NULL;
	int label = 0;

	debug("Hashing the element...\n");
	if(!PyArg_ParseTuple(args, "O|i", &object, &label)) {
		PyErr_SetString(ElementError, "missing element object");
		return NULL;
	}

	if(!object->elem_initialized) {
		PyErr_SetString(ElementError, "null element object");
		return NULL;
	}
	START_CLOCK(dBench);
	int hash_size = HASH_LEN;
	uint8_t hash_buf[hash_size + 1];
	memset(hash_buf, 0, hash_size);
	if(object->element_type == GT_t) {
		element_hash_to_key(object, hash_buf, hash_size);

		hash_hex = convert_buffer_to_hex(hash_buf, hash_size);
		printf_buffer_as_hex(hash_buf, hash_size);
	}

	str = PyBytes_FromStringAndSize((const char *) hash_hex, hash_size);
	free(hash_hex);
	STOP_CLOCK(dBench);
	return str;
}

// new version that uses same approach as Charm-C++
static PyObject *Element_hash(Element *self, PyObject *args)
{
	Element *newObject = NULL, *object = NULL, *group = NULL;
	PyObject *objList = NULL, *tmpObject = NULL;
	Group_t type = ZR_t;
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
		PyBytes_ToString(str, objList);
		if(type >= ZR_t && type < GT_t) {
			debug("Hashing string '%s' to Zr...\n", str);
			// create an element of Zr
			// hash bytes using SHA1
			START_CLOCK(dBench);
			newObject = createNewElement(NONE_G, group->pairing);
			newObject->element_type = type;

			element_init_hash(group);
			element_add_str_hash(group, (char *) str, strlen((char *) str));
			element_finish_hash(newObject, type);
			STOP_CLOCK(dBench);
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
				START_CLOCK(dBench);
				element_add_to_hash(object);
				STOP_CLOCK(dBench);
			}
			else if(PyBytes_CharmCheck(tmpObject)) {
				str = NULL;
				PyBytes_ToString(str, tmpObject);
				START_CLOCK(dBench);
				element_add_str_hash(group, (char *) str, strlen((char *) str));
				STOP_CLOCK(dBench);
			}
			Py_DECREF(tmpObject);

			// loop over the remaining elements in list
			for(i = 1; i < size; i++) {
				tmpObject = PySequence_GetItem(objList, i);
				if(PyElement_Check(tmpObject)) {
					object = (Element *) tmpObject;
					START_CLOCK(dBench);
					element_add_to_hash(object);
					STOP_CLOCK(dBench);
				}
				else if(PyBytes_CharmCheck(tmpObject)) {
					str = NULL;
					PyBytes_ToString(str, tmpObject);
					START_CLOCK(dBench);
					element_add_str_hash(group, (char *) str, strlen((char *) str));
					STOP_CLOCK(dBench);
				}
				Py_DECREF(tmpObject);
			}
			START_CLOCK(dBench);
			if(type >= ZR_t && type < GT_t) { newObject = createNewElement(NONE_G, group->pairing); }
			else {
				tmp = "invalid object type";
				goto cleanup;
			}

			newObject->element_type = type;
			element_finish_hash(newObject, type);
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

		// Hash an element of Zr to an element of G1_t.
		if(type == G1_t) {
			START_CLOCK(dBench);
			newObject = createNewElement(NONE_G, group->pairing);
			newObject->element_type = type;
			// hash the element to the G1_t field (uses sha1 as well)
			element_init_hash(group);
			element_add_to_hash(object);
			element_finish_hash(newObject, type);
			STOP_CLOCK(dBench);
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
	if(newObject != NULL) PyObject_Del(newObject);
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
	START_CLOCK(dBench);
	if(PyElement_Check(lhs) && found_int) {
		// lhs is the element type
		if(self->element_type == ZR_t)
			result = element_is(self, z);
	}
	else if(PyElement_Check(rhs) && found_int) {
		if(other->element_type == ZR_t)
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
	STOP_CLOCK(dBench);

	if(result == -1) {
		/* print error */
		PyErr_SetString(ElementError, "cannot compare different group types.\n");
		return NULL;
	}
cleanup:
//	value = (result == 0) ? TRUE : FALSE;

	if(opid == Py_EQ) {
		if(result == TRUE) {
			Py_INCREF(Py_True); return Py_True;
		}
		Py_INCREF(Py_False); return Py_False;
	}
	else { /* Py_NE */
		if(result == FALSE) {
			Py_INCREF(Py_True); return Py_True;
		}
		Py_INCREF(Py_False); return Py_False;
	}
}

static PyObject *Element_long(PyObject *o1) {
	if(PyElement_Check(o1)) {
		Element *value = (Element *) o1;
		/* can only handle elements in ZR */
		if(value->element_type == ZR_t) {
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
		if(o1->element_type == ZR_t) {
			mpz_t o;
			mpz_init(o);
			element_to_mpz(o1, o);
			PyObject *temp = mpzToLongObj(o);
			result = PyObject_Hash(temp);
			mpz_clear(o);
			PyObject_Del(temp);
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

	if(self->elem_initialized == FALSE) {
		PyErr_SetString(ElementError, "element not initialized.");
		return NULL;
	}

	int elem_len = 0;
	uint8_t *data_buf = NULL;
	size_t bytes_written;
	START_CLOCK(dBench);

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
	STOP_CLOCK(dBench);
	return result;
}

static PyObject *Deserialize_cmp(Element *self, PyObject *args) {
	Element *origObject = NULL, *group = NULL;
	PyObject *object;

	if(PyArg_ParseTuple(args, "OO", &group, &object)) {
		START_CLOCK(dBench);
		if(PyBytes_Check(object)) {
			uint8_t *serial_buf = (uint8_t *) PyBytes_AsString(object);
			int type = atoi((const char *) &(serial_buf[0]));
			uint8_t *base64_buf = (uint8_t *)(serial_buf + 2);
//			printf("type => %d\n", type);
//			printf("base64 dec => '%s'\n", base64_buf);

			if(check_type(type) == TRUE && strlen((char *) base64_buf) > 0) {
//				debug("result => ");
//				printf_buffer_as_hex(binary_buf, deserialized_len);
				origObject = createNewElement(NONE_G, group->pairing);
				origObject->element_type = type;
				element_from_bytes(origObject, base64_buf);
				STOP_CLOCK(dBench);
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

	Element *group = NULL;
	PyObject *object = NULL;
	if(PyArg_ParseTuple(args, "OO", &group, &object)) {
		if(PyElement_Check(group) && PyElement_Check(object)) {
			IS_PAIRING_OBJ_NULL(group); /* verify group object is still active */
			Element *elem = (Element *) object;

			if(check_membership(elem) == TRUE) {
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

	Element *group = NULL;
	PyObject *obj  = NULL;
	if(!PyArg_ParseTuple(args, "O", &obj)) {
		PyErr_SetString(ElementError, "invalid group object.");
		return NULL;
	}

	if(PyElement_Check(obj)) {
		group = (Element *) obj;
		IS_PAIRING_OBJ_NULL(group);
		mpz_t d;
		mpz_init(d);
		object_to_mpz(group->pairing->order, d);
		PyObject *object = (PyObject *) mpzToLongObj(d);
		mpz_clear(d);
		return object; /* returns a PyInt */
	}
	return NULL;
}

/* TODO: move to cryptobase */
PyObject *AES_Encrypt(Element *self, PyObject *args)
{
	PyObject *keyObj = NULL; // string or bytes object
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
		PyBytes_ToString(keyStr, keyObj);
		//printf("key => '%s'\n", keyStr);
		//printf("message => '%s'\n", messageStr);
		// perform AES encryption using miracl
		char *cipher = NULL;

		int c_len = aes_encrypt(keyStr, messageStr, m_len, &cipher);

		PyObject *str = PyBytes_FromStringAndSize((const char *) cipher, c_len);
		free(cipher);
		return str;
	}

	PyErr_SetString(ElementError, "invalid objects.");
	return NULL;
}

PyObject *AES_Decrypt(Element *self, PyObject *args)
{
	PyObject *keyObj = NULL; // string or bytes object
	char *ciphertextStr;
	int c_len = 0;

	if(!PyArg_ParseTuple(args, "Os#", &keyObj, &ciphertextStr, &c_len)) {
		PyErr_SetString(ElementError, "invalid arguments.");
		return NULL;
	}

	char *keyStr;
	if(PyBytes_CharmCheck(keyObj)) {
		PyBytes_ToString(keyStr, keyObj);
//		printf("key => '%s'\n", keyStr);
//		printf("message => '%s'\n", ciphertextStr);
		// perform AES encryption using miracl
		char *message = NULL;

		int m_len = aes_decrypt(keyStr, ciphertextStr, c_len, &message);

		PyObject *str = PyBytes_FromStringAndSize((const char *) message, m_len);
		free(message);
		return str;
	}

	PyErr_SetString(ElementError, "invalid objects.");
	return NULL;

}



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
InitBenchmark_CAPI(_init_benchmark, dBench, 1);
StartBenchmark_CAPI(_start_benchmark, dBench);
EndBenchmark_CAPI(_end_benchmark, dBench);
GetBenchmark_CAPI(_get_benchmark, dBench);
ClearBenchmarks_CAPI(_clear_benchmark, dBench);

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
	Benchmark *dBench;
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
	// benchmark methods
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
	{"hashPair", (PyCFunction)sha1_hash2, METH_VARARGS, "Compute a sha1 hash of an element type"},
	{"SymEnc", (PyCFunction) AES_Encrypt, METH_VARARGS, "AES encryption args: key (bytes or str), message (str)"},
	{"SymDec", (PyCFunction) AES_Decrypt, METH_VARARGS, "AES decryption args: key (bytes or str), ciphertext (str)"},
	{"InitBenchmark", (PyCFunction)_init_benchmark, METH_NOARGS, "Initialize a benchmark object"},
	{"StartBenchmark", (PyCFunction)_start_benchmark, METH_VARARGS, "Start a new benchmark with some options"},
	{"EndBenchmark", (PyCFunction)_end_benchmark, METH_VARARGS, "End a given benchmark"},
	{"GetBenchmark", (PyCFunction)_get_benchmark, METH_VARARGS, "Returns contents of a benchmark object"},
	{"ClearBenchmark", (PyCFunction)_clear_benchmark, METH_VARARGS, "Clears content of benchmark object"},
    {NULL}  /* Sentinel */
};

#if PY_MAJOR_VERSION >= 3
static int pairings_traverse(PyObject *m, visitproc visit, void *arg) {
	Py_VISIT(GETSTATE(m)->error);
	return 0;
}

static int pairings_clear(PyObject *m) {
	Py_CLEAR(GETSTATE(m)->error);
	Py_CLEAR(GETSTATE(m)->dBench);
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

    if(import_benchmark() < 0)
    	INITERROR;
    if(PyType_Ready(&BenchmarkType) < 0)
    	INITERROR;
    st->dBench = PyObject_New(Benchmark, &BenchmarkType);
    dBench = st->dBench;
    dBench->bench_initialized = FALSE;
    InitClear(dBench);

    Py_INCREF(&PairingType);
    PyModule_AddObject(m, "params", (PyObject *)&PairingType);
    Py_INCREF(&ElementType);
    PyModule_AddObject(m, "pairing", (PyObject *)&ElementType);

    PyModule_AddIntConstant(m, "ZR", ZR_t);
    PyModule_AddIntConstant(m, "G1", G1_t);
    PyModule_AddIntConstant(m, "G2", G2_t);
    PyModule_AddIntConstant(m, "GT", GT_t);

//  PyModule_AddIntConstant(m, "CpuTime", CPU_TIME);
//	PyModule_AddIntConstant(m, "RealTime", REAL_TIME);
//	PyModule_AddIntConstant(m, "NativeTime", NATIVE_TIME);
//	PyModule_AddIntConstant(m, "Add", ADDITION);
//	PyModule_AddIntConstant(m, "Sub", SUBTRACTION);
//	PyModule_AddIntConstant(m, "Mul", MULTIPLICATION);
//	PyModule_AddIntConstant(m, "Div", DIVISION);
//	PyModule_AddIntConstant(m, "Exp", EXPONENTIATION);
//	PyModule_AddIntConstant(m, "Pair", PAIRINGS);

	ADD_BENCHMARK_OPTIONS(m);
	PyModule_AddIntConstant(m, "Pair", PAIRINGS);

	pairing_init_finished = TRUE;
	// builtin curves
	PyModule_AddIntConstant(m, "MNT160", MNT160);

#if PY_MAJOR_VERSION >= 3
	return m;
#endif
}
