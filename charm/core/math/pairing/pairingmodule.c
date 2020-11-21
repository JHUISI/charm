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
 *   @file    pairingmodule.c
 *
 *   @brief   charm interface over PBC library
 *
 *   @author  ayo.akinyele@charm-crypto.com
 *
 ************************************************************************/

#include "pairingmodule.h"

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
	else if(lhs == G2 && rhs == G1) return TRUE;
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
		if(obj1_long) Py_XDECREF(obj1); 	\
		if(obj2_long) Py_XDECREF(obj2);	\
		return obj3;  }	\
	return NULL;				\
}

// TODO: update these two functions to convert neg numbers
PyObject *mpzToLongObj (mpz_t m)
{
	/* borrowed from gmpy */
	int size = (mpz_sizeinbase (m, 2) + PyLong_SHIFT - 1) / PyLong_SHIFT;
	int i, isNeg = (mpz_sgn(m) < 0) ? TRUE : FALSE;
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
	if(isNeg) {
		Py_SIZE(l) = -i;
	}
	else {
		Py_SIZE(l) = i;
	}
	mpz_clear (temp);
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
	char *tmp = (char *) malloc(len*2 + 2);
	char *tmp2 = tmp;
	memset(tmp, 0, len*2+1);

	for(i = 0; i < len; i++)
		tmp += sprintf(tmp, "%02x", data[i]);

	return tmp2;
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
	if(element_type == ZR) {
		element_init_Zr(retObject->e, pairing->pair_obj);
		retObject->element_type = ZR;
	}
	else if(element_type == G1) {
		element_init_G1(retObject->e, pairing->pair_obj);
		retObject->element_type = G1;
	}
	else if(element_type == G2) {
		element_init_G2(retObject->e, pairing->pair_obj);
		retObject->element_type = G2;
	}
	else if(element_type == GT) {
		element_init_GT(retObject->e, pairing->pair_obj);
		retObject->element_type = GT;
	}
	
	retObject->elem_initialized = TRUE;
	retObject->elem_initPP = FALSE;
	retObject->pairing = pairing;
	Py_INCREF(retObject->pairing);
	return retObject;	
}

Element *convertToZR(PyObject *longObj, PyObject *elemObj) {
	Element *self = (Element *) elemObj;
	Element *new = createNewElement(ZR, self->pairing);

	mpz_t x;
	mpz_init(x);
#if PY_MAJOR_VERSION < 3
	PyObject *longObj2 = PyNumber_Long(longObj);
	longObjToMPZ(x, (PyLongObject *) longObj2);
	Py_DECREF(longObj2);
#else
	longObjToMPZ(x, (PyLongObject *) longObj);
#endif
	element_set_mpz(new->e, x);
	mpz_clear(x);
	return new;
}

void 	Pairing_dealloc(Pairing *self)
{
	if(self->param_buf != NULL) {
		debug("param_buf => %p\n", self->param_buf);
		free(self->param_buf);
	}

	debug("Clear pairing => 0x%p\n", self->pair_obj);
	if(self->group_init == TRUE) {
		pairing_clear(self->pair_obj);
		pbc_param_clear(self->p);
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
	debug("Releasing pairing object!\n");
	Py_TYPE(self)->tp_free((PyObject *) self);
}

void	Element_dealloc(Element* self)
{
	if(self->elem_initialized == TRUE && self->e != NULL) {
		debug_e("Clear element_t => '%B'\n", self->e);
		if(self->elem_initPP == TRUE) {
			element_pp_clear(self->e_pp);
		}
		element_clear(self->e);
		Py_DECREF(self->pairing);
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

char * init_pbc_param(char *file, pairing_t *pairing)
{
	pbc_param_t params;
	FILE *fp;
	size_t count;
	char *buf = NULL;
	fp = fopen(file, "r");
	
	if(fp == NULL) {
		fprintf(stderr, "Error reading file!\n");
		return NULL;
	}
	
	debug("Reading '%s'\n", file);
	count = read_file(fp, &buf);
	debug("param='%s'\n", buf);
	fclose(fp);	

	if(pbc_param_init_set_buf(params, buf, count) == 0) {
		/* initialize the pairing_t struct with params */
		pairing_init_pbc_param(*pairing, params);
		debug("Pairing init!\n");
	}
	else {
		printf("Error: could not init pbc_param_t.\n");
		return NULL;
	}
	
	return buf;
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
	const int new_input_len = input_len + 2; // extra byte for prefix
	uint8_t new_input[new_input_len];
//	printf("orig input => \n");
//	printf_buffer_as_hex(input_buf, input_len);
	memset(new_input, 0, new_input_len);
	new_input[0] = (uint8_t)1; // block number (always 1 by default)
	new_input[1] = hash_prefix; // set hash prefix
	memcpy(new_input+2, input_buf, input_len); // copy input bytes

//	printf("new input => \n");
//	printf_buffer_as_hex(new_input, new_input_len);
	// prepare output buf
	memset(output_buf, 0, hash_len);

	if (hash_len <= HASH_LEN) {
		SHA256_Init(&sha2);
		SHA256_Update(&sha2, new_input, new_input_len);
		uint8_t md[HASH_LEN];
		SHA256_Final(md, &sha2);
		memcpy(output_buf, md, hash_len);
	}
	else {
		// apply variable-size hash technique to get desired size
		// determine block count.
		int blocks = (int) ceil(((double) hash_len) / HASH_LEN);
		uint8_t md2[(blocks * HASH_LEN)];
		for(int i = 0; i < blocks; i++) {
			/* compute digest = SHA-2( i || prefix || input_buf ) || ... || SHA-2( n-1 || prefix || input_buf ) */
			uint8_t md[HASH_LEN];
			new_input[0] = (uint8_t)(i+1);
			SHA256_Init(&sha2);
			int size = new_input_len;
			SHA256_Update(&sha2, new_input, size);
			SHA256_Final(md, &sha2);
			memcpy(md2 +(i * HASH_LEN), md, HASH_LEN);
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

int hash_element_to_bytes(element_t *element, int hash_size, uint8_t* output_buf, int prefix)
{
	unsigned int buf_len;
	
	buf_len = element_length_in_bytes(*element);
	uint8_t *temp_buf = (uint8_t *)malloc(buf_len+1);
	if (temp_buf == NULL)
		return FALSE;
	
	element_to_bytes(temp_buf, *element);
	if(prefix == 0)
		prefix = HASH_FUNCTION_ELEMENTS;
	else if(prefix < 0)
		// convert into a positive number
		prefix *= -1;
	int result = hash_to_bytes(temp_buf, buf_len, output_buf, hash_size, prefix);
	free(temp_buf);
	
	return result;
}

// take a previous hash and concatenate with serialized bytes of element and hashes into output buf
int hash2_element_to_bytes(element_t *element, uint8_t* last_buf, int hash_size, uint8_t* output_buf) {
	// assume last buf contains a hash
	unsigned int last_buflen = hash_size;
	unsigned int buf_len = element_length_in_bytes(*element);

	uint8_t* temp_buf = (uint8_t *) malloc(buf_len + 1);
	memset(temp_buf, '\0', buf_len);
	if(temp_buf == NULL) {
		return FALSE;
	}

	element_to_bytes((unsigned char *) temp_buf, *element);
	// create output buffer
	uint8_t* temp2_buf = (uint8_t *) malloc(last_buflen + buf_len + 1);
	memset(temp2_buf, 0, (last_buflen + buf_len));
	int i;
	for(i = 0; i < last_buflen; i++)
		temp2_buf[i] = last_buf[i];

	int j = 0;
	for(i = last_buflen; i < (last_buflen + buf_len); i++)
	{
		temp2_buf[i] = temp_buf[j];
		j++;
	}
	// hash the temp2_buf to bytes
	int result = hash_to_bytes(temp2_buf, (last_buflen + buf_len), output_buf, hash_size, HASH_FUNCTION_ELEMENTS);

	free(temp2_buf);
	free(temp_buf);
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

	result = hash_to_bytes(temp_buf, (input_len + hash_size), output_buf, hash_size, HASH_FUNCTION_STRINGS);

	Py_XDECREF(last);
	return result;
}

PyObject *Element_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    Element *self;
	
    self = (Element *)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->elem_initialized = FALSE;
        self->elem_initPP = FALSE;
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
		self->param_buf = NULL;
		memset(self->hash_id, 0, ID_LEN);
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
	static char *buf;
	char *param_buf2 = NULL;
	PyObject *n = NULL, *short_val = NULL;
	int qbits = 0, rbits = 0;
	size_t b_len = 0;
	int seed = -1;
	uint8_t hash_id[HASH_LEN+1];
	
    static char *kwlist[] = {"file", "n", "qbits", "rbits", "short", "string", "seed", NULL};
	
    if (! PyArg_ParseTupleAndKeywords(args, kwds, "|sOiiOs#i", kwlist,
                                      &self->params, &n, &qbits, &rbits, &short_val, &param_buf2, &b_len, &seed)) {
    	PyErr_SetString(ElementError, "invalid arguments");
        return -1; 
	}
	if (self->params && !n && !qbits && !rbits && !short_val && !param_buf2) {
		// check if file exists
		int f = open(self->params, O_RDONLY);
		if(f < 0) {
			PyErr_SetString(ElementError, "failed to read params file.");
			return 0;
		}
		close(f);
		buf = init_pbc_param(self->params, &self->pair_obj);
		
		if(buf != NULL) {
			debug("Initialized pairings type: '%s'\n", self->params);
			self->param_buf = buf;
			hash_to_bytes((uint8_t *) buf, strlen(buf), hash_id, HASH_LEN, HASH_FUNCTION_STRINGS);
			memcpy((char *) self->hash_id, (char *) hash_id, ID_LEN);
			printf_buffer_as_hex(self->hash_id, ID_LEN);
		}
	}
	else if(param_buf2 && !n && !qbits && !rbits && !short_val) {
		// parameters is provided in string
		debug("Paramter String => '%s'\n", param_buf2);
		pbc_param_init_set_buf(self->p, param_buf2, b_len);
		pairing_init_pbc_param(self->pair_obj, self->p);
		debug("hashing pairing parameters...\n");

		hash_to_bytes((uint8_t *) param_buf2, b_len, hash_id, HASH_LEN, HASH_FUNCTION_STRINGS);
		memcpy((char *) self->hash_id, (char *) hash_id, ID_LEN);
		printf_buffer_as_hex(self->hash_id, ID_LEN);
	}
	else if (n && !(qbits || rbits)) {
		// if n is provided, and qbits and rbits are not
		debug("n set, but q and r are NOT set!\n");
		if(short_val == Py_True) {
			// type f curve
			if(!PyLong_Check(n)) {
				PyErr_SetString(ElementError, "n is expected to be short and a long type.");
				return -1;
			}
			long bits = PyLong_AsLong(n);
			pbc_param_init_f_gen(self->p, (int) bits);
		}
		else {
			if(!PyLong_Check(n)) {
				PyErr_SetString(ElementError, "n is expected to be large and a long type.");
				return -1;
			}

			// type a1 curve
			mpz_t n_val;
			mpz_init(n_val);
			longObjToMPZ(n_val, (PyLongObject *) n);

			pbc_param_init_a1_gen(self->p, n_val);
			mpz_clear(n_val);
			// TODO: add hash_id to these calls
		}
		pairing_init_pbc_param(self->pair_obj, self->p);
	}
    // if qbits and rbits are provided, and n is not
	else if (qbits && rbits && !n) {
		debug("q and r set, but NOT n!\n");
		if(short_val == Py_True)
			pbc_param_init_e_gen(self->p, rbits, qbits);
		else
			pbc_param_init_a_gen(self->p, rbits, qbits);
		pairing_init_pbc_param(self->pair_obj, self->p);
		// TODO: add hash_id to these calls
	}
	// figure out how to expose func to find type d and g curves
	else {
		PyErr_SetString(ElementError, "cannot derive curve type and parameters.");
		return -1;
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
		EXIT_IF(TRUE, "invalid argument.");
	}
	
	newObject = (Element *) object;
	// element_printf("Elment->e => '%B'\n", newObject->e);
	debug("Element->type => '%d'\n", newObject->element_type);
	
	return NULL;
}
*/
 
static PyObject *Element_elem(Element* self, PyObject* args)
{
	Element *retObject = NULL;
	Pairing *group = NULL;
	int type;
	PyObject *long_obj = NULL;
	
	if(!PyArg_ParseTuple(args, "Oi|O", &group, &type, &long_obj)) {
		EXIT_IF(TRUE, "invalid arguments.");
	}
	VERIFY_GROUP(group);
	
	debug("init an element.\n");
	if(type >= ZR && type <= GT) {
		retObject = createNewElement(type, group);
	}
	else {
		EXIT_IF(TRUE, "unrecognized group type.");
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
		element_set_mpz(retObject->e, m);
		mpz_clear(m);
	}
	
	/* return Element object */
	return (PyObject *) retObject;		
}

PyObject *Pairing_print(Pairing* self)
{
	if(self->param_buf != NULL)
		return PyUnicode_FromString((char *) self->param_buf);
	else {
		pbc_param_out_str(stdout, self->p);
		return PyUnicode_FromString("");
	}

	return PyUnicode_FromString("");
}

PyObject *Element_print(Element* self)
{
	PyObject *strObj;
	char *tmp = (char *) malloc(MAX_LEN);
	memset(tmp, 0, MAX_LEN);
	size_t max = MAX_LEN;
	debug("Contents of element object\n");

	if(self->elem_initialized) {
		element_snprintf(tmp, max, "%B", self->e);
		strObj = PyUnicode_FromString((const char *) tmp);
		free(tmp);
		return strObj;
	}

	free(tmp);
	return PyUnicode_FromString("");
}

static PyObject *Element_random(Element* self, PyObject* args)
{
	Element *retObject;
	Pairing *group = NULL;
	int arg1;
	int e_type = -1, seed = -1;

	/* create a new object */
	if(!PyArg_ParseTuple(args, "Oi|i", &group, &arg1, &seed))
		return NULL;

	VERIFY_GROUP(group);
	retObject = PyObject_New(Element, &ElementType);
	debug("init random element in '%d'\n", arg1);
	if(arg1 == ZR) {
		element_init_Zr(retObject->e, group->pair_obj);
		e_type = ZR;
	}
	else if(arg1 == G1) {
		element_init_G1(retObject->e, group->pair_obj);
		e_type = G1;
	}
	else if(arg1 == G2) {
		element_init_G2(retObject->e, group->pair_obj);
		e_type = G2;
	}
	else if(arg1 == GT) {
		EXIT_IF(TRUE, "cannot generate random elements in GT.");
	}
	else {
		EXIT_IF(TRUE, "unrecognized group type.");
	}

	if(seed > -1) {
		pbc_random_set_deterministic((uint32_t) seed);
	}
	/* create new Element object */
	element_random(retObject->e);
	retObject->elem_initialized = TRUE;
	retObject->elem_initPP = FALSE;
	retObject->element_type = e_type;
	/* set the group object for element operations */
	retObject->pairing = group;
	Py_INCREF(retObject->pairing);
	return (PyObject *) retObject;
}

static PyObject *Element_add(Element *self, Element *other)
{
	Element *newObject;
	
	debug("Starting '%s'\n", __func__);
#ifdef DEBUG
	if(self->e) {
		element_printf("Left: e => '%B'\n", self->e);		
	}
	
	if(other->e) {
		element_printf("Right: e => '%B'\n", other->e);				
	}
#endif
	IS_SAME_GROUP(self, other);
	EXIT_IF(add_rule(self->element_type, other->element_type) == FALSE, "invalid add operation.");
	// start micro benchmark
	newObject = createNewElement(self->element_type, self->pairing);
	element_add(newObject->e, self->e, other->e);
#ifdef BENCHMARK_ENABLED
	UPDATE_BENCH(ADDITION, newObject->element_type, newObject->pairing);
#endif
	return (PyObject *) newObject;
}

static PyObject *Element_sub(Element *self, Element *other)
{
	Element *newObject;
	
	debug("Starting '%s'\n", __func__);
#ifdef DEBUG	
	if(self->e) {
		element_printf("Left: e => '%B'\n", self->e);		
	}
	
	if(other->e) {
		element_printf("Right: e => '%B'\n", other->e);				
	}
#endif
	IS_SAME_GROUP(self, other);
	EXIT_IF(sub_rule(self->element_type, other->element_type) == FALSE, "invalid sub operation.");

	newObject = createNewElement(self->element_type, self->pairing);
	element_sub(newObject->e, self->e, other->e);
#ifdef BENCHMARK_ENABLED
	UPDATE_BENCH(SUBTRACTION, newObject->element_type, newObject->pairing);
#endif
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
		newObject = createNewElement(self->element_type, self->pairing);
		element_mul_si(newObject->e, self->e, z);
	}
	else if(PyElement_Check(rhs) && found_int) {
		// rhs is the element type
		newObject = createNewElement(other->element_type, other->pairing);
		element_mul_si(newObject->e, other->e, z);
	}
	else if(PyElement_Check(lhs) && PyElement_Check(rhs)) {
		// both are element types
		IS_SAME_GROUP(self, other);
		EXIT_IF(mul_rule(self->element_type, other->element_type) == FALSE, "invalid mul operation.");

		if(self->element_type != ZR && other->element_type == ZR) {
			newObject = createNewElement(self->element_type, self->pairing);
			element_mul_zn(newObject->e, self->e, other->e);		
		}
		else if(other->element_type != ZR && self->element_type == ZR) {
			newObject = createNewElement(other->element_type, self->pairing);
			element_mul_zn(newObject->e, other->e, self->e);
		}
		else { // all other cases
			newObject = createNewElement(self->element_type, self->pairing);
			element_mul(newObject->e, self->e, other->e);		
		}
	}
	else {
		EXIT_IF(TRUE, "invalid types.");
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
		newObject = createNewElement(self->element_type, self->pairing);
		if(z == 2) element_halve(newObject->e, self->e);
		else {
			other = createNewElement(self->element_type, self->pairing);
			element_set_si(other->e, z);
			element_div(newObject->e, self->e, other->e);
			Py_DECREF(other);
		}
	}
	else if(PyElement_Check(rhs) && found_int) {
		// rhs is the element type
		newObject = createNewElement(other->element_type, other->pairing);
		if(z == 2) element_halve(newObject->e, other->e);
		else {
			self = createNewElement(other->element_type, other->pairing);
			element_set_si(self->e, z);
			element_div(newObject->e, self->e, other->e);
			Py_DECREF(self);
		}
	}
	else if(PyElement_Check(lhs) && PyElement_Check(rhs)) {
		// both are element types
		IS_SAME_GROUP(self, other);
		EXIT_IF(div_rule(self->element_type, other->element_type) == FALSE, "invalid div operation.");

		newObject = createNewElement(self->element_type, self->pairing);
		element_div(newObject->e, self->e, other->e);
	}
	else {
		EXIT_IF(TRUE, "invalid types.");
		PyErr_SetString(ElementError, "invalid types");
		return NULL;
	}
#ifdef BENCHMARK_ENABLED
	UPDATE_BENCH(DIVISION, newObject->element_type, newObject->pairing);
#endif
	return (PyObject *) newObject;
}
 
static PyObject *Element_invert(Element *self)
{
	Element *newObject;
	
	debug("Starting '%s'\n", __func__);
#ifdef DEBUG	
	if(self->e) {
		element_printf("e => '%B'\n", self->e);		
	}
#endif
	
	newObject = createNewElement(self->element_type, self->pairing);
	element_invert(newObject->e, self->e);
	return (PyObject *) newObject;
}

static PyObject *Element_negate(Element *self)
{
	Element *newObject;

	debug("Starting '%s'\n", __func__);
#ifdef DEBUG
	if(self->e) {
		element_printf("e => '%B'\n", self->e);
	}
#endif

	newObject = createNewElement(self->element_type, self->pairing);
	element_neg(newObject->e, self->e);

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
		if(rhs_o2->element_type == ZR) {
			mpz_init(n);
			element_to_mpz(n, rhs_o2->e);

			lhs_o1 = convertToZR(o1, o2);
			newObject = createNewElement(rhs_o2->element_type, rhs_o2->pairing);
			// both must be ZR, no need for pp check
			element_pow_mpz(newObject->e, lhs_o1->e, n);
			mpz_clear(n);
			Py_DECREF(lhs_o1);
		}
		else {
			EXIT_IF(TRUE, "undefined exponentiation operation.");
		}
	}
	else if(longFoundRHS) {
		// o2 is a long type
		long rhs = PyLong_AsLong(o2);
		if(PyErr_Occurred() || rhs >= 0) {
			// clear error and continue
			// PyErr_Print(); // for debug purposes
			PyErr_Clear();
			newObject = createNewElement(lhs_o1->element_type, lhs_o1->pairing);
			mpz_init(n);
#if PY_MAJOR_VERSION < 3
			PyObject *longObj2 = PyNumber_Long(o2);
			longObjToMPZ(n, (PyLongObject *) longObj2);
			Py_DECREF(longObj2);
#else
			longObjToMPZ(n, (PyLongObject *) o2);
#endif
			if(lhs_o1->elem_initPP == TRUE) {
				// n = g ^ e where g has been pre-processed
				element_pp_pow(newObject->e, n, lhs_o1->e_pp);
			}
			else {
				element_pow_mpz(newObject->e, lhs_o1->e, n);
			}
			mpz_clear(n);
		}
		else if(rhs == -1) {
			// compute inverse
			newObject = createNewElement(lhs_o1->element_type, lhs_o1->pairing);
			element_invert(newObject->e, lhs_o1->e);
		}
		else {
			EXIT_IF(TRUE, "undefined exponentiation operation.");
		}
	}
	else if(Check_Elements(o1, o2)) {
		debug("Starting '%s'\n", __func__);
		debug_e("LHS: e => '%B'\n", lhs_o1->e);
		debug_e("RHS: e => '%B'\n", rhs_o2->e);

		IS_SAME_GROUP(lhs_o1, rhs_o2);
		EXIT_IF(exp_rule(lhs_o1->element_type, rhs_o2->element_type) == FALSE, "invalid exp operation");
		if(rhs_o2->element_type == ZR) {
			newObject = createNewElement(lhs_o1->element_type, lhs_o1->pairing);
			//printf("Calling pp func: '%d'\n", lhs_o1->elem_initPP);
			if(lhs_o1->elem_initPP == TRUE) {
				// n = g ^ e where g has been pre-processed
				mpz_init(n);
				element_to_mpz(n, rhs_o2->e);
				element_pp_pow(newObject->e, n, lhs_o1->e_pp);
				mpz_clear(n);
			}
			else {
				element_pow_zn(newObject->e, lhs_o1->e, rhs_o2->e);
			}
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
	
#ifdef BENCHMARK_ENABLED
	UPDATE_BENCH(EXPONENTIATION, newObject->element_type, newObject->pairing);
#endif
	return (PyObject *) newObject;
}

/* We assume the element has been initialized into a specific field (G1,G2,GT,or Zr),
 * before setting the element. */
static PyObject *Element_set(Element *self, PyObject *args)
{
    Element *object;
    long int value;
    int errcode = TRUE;

	if(self->elem_initialized == FALSE){
		PyErr_SetString(PyExc_ValueError, "Must initialize element to a field (G1, G2, or GT).");
		return NULL;
	}

    debug("Creating a new element\n");
    if(PyArg_ParseTuple(args, "l", &value)) {
            // convert into an int using PyArg_Parse(...)
            // set the element
            debug("Setting element to '%li'\n", value);
            if(value == 0)
                    element_set0(self->e);
            else if(value == 1)
                    element_set1(self->e);
            else {
                    debug("Value '%i'\n", (signed int) value);
                    element_set_si(self->e, (signed int) value);
            }
    }
    else if(PyArg_ParseTuple(args, "O", &object)){
            element_set(self->e, object->e);
    }
    else {
    	// PyArg_ParseTuple already set the due error type and string
            return NULL;
    }

    return Py_BuildValue("i", errcode);
}

static PyObject  *Element_initPP(Element *self, PyObject *args)
{
	if(self->elem_initPP == TRUE){
		PyErr_SetString(PyExc_ValueError, "Pre-processing table alreay initialized.");
		return NULL;
	}

	if(self->elem_initialized == FALSE){
		PyErr_SetString(PyExc_ValueError, "Must initialize element to a field (G1, G2, or GT).");
		return NULL;
	}

    /* initialize and store preprocessing information in e_pp */
    if(self->element_type >= G1 && self->element_type <= GT) {
		element_pp_init(self->e_pp, self->e);
		self->elem_initPP = TRUE;
		Py_RETURN_TRUE;
    }

    Py_RETURN_FALSE;
}

/* Takes a list of two objects in G1 & G2 respectively and computes the multi-pairing */
PyObject *multi_pairing(Pairing *groupObj, PyObject *listG1, PyObject *listG2) {

	int GroupSymmetric = FALSE;
	// check for symmetric vs. asymmetric
	if(pairing_is_symmetric(groupObj->pair_obj)) {
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
					element_init_G1(g1[l], groupObj->pair_obj);
					element_set(g1[l], tmp1->e);
					l++;
				}

				if(GroupSymmetric == TRUE && (tmp2->element_type == G1 || tmp2->element_type == G2)) {
					element_init_same_as(g2[r], tmp2->e);
					element_set(g2[r], tmp2->e);
					r++;
				}
				else if(tmp2->element_type == G2) {
					element_init_G2(g2[r], groupObj->pair_obj);
					element_set(g2[r], tmp2->e);
					r++;
				}
			}
			Py_DECREF(tmpObject1);
			Py_DECREF(tmpObject2);
		}

		Element *newObject = NULL;
		if(l == r) {
			newObject = createNewElement(GT, groupObj);
			element_prod_pairing(newObject->e, g1, g2, l); // pairing product calculation
		}
		else {
			EXIT_IF(TRUE, "invalid pairing element types in list.");
		}

		/* clean up */
		for(i = 0; i < l; i++) { element_clear(g1[i]); }
		for(i = 0; i < r; i++) { element_clear(g2[i]); }
		return (PyObject *) newObject;
	}

	EXIT_IF(TRUE, "list is empty.");
}

/* this is a type method that is visible on the global or class level. Therefore,
   the function prototype needs the self (element class) and the args (tuple of Element objects).
 */
PyObject *Apply_pairing(PyObject *self, PyObject *args)
{
	// lhs => G1 and rhs => G2
	Element *newObject, *lhs, *rhs;
	Pairing *group = NULL;
	PyObject *lhs2, *rhs2;
	
	debug("Applying pairing...\n");	
	if(!PyArg_ParseTuple(args, "OO|O:pairing_prod", &lhs2, &rhs2, &group)) {
		// EXIT_IF(TRUE, "invalid arguments: G1, G2, groupObject.");
		return NULL;
	}
	
	if(PySequence_Check(lhs2) && PySequence_Check(rhs2)) {
		VERIFY_GROUP(group);
		return multi_pairing(group, lhs2, rhs2);
	}
	
	if(!PyElement_Check(lhs2)){
		PyErr_SetString(PyExc_TypeError, "Left value is not a valid Element or Sequence of Elements type.");
		return NULL;
	}

	if(!PyElement_Check(rhs2)){
		PyErr_SetString(PyExc_TypeError, "Right value is not a valid Element or Sequence of Elements type.");
		return NULL;
	}

	lhs = (Element *) lhs2;
	rhs = (Element *) rhs2;
	IS_SAME_GROUP(lhs, rhs);
	if(pairing_is_symmetric(lhs->pairing->pair_obj)) {
		debug("Pairing is symmetric.\n");
		debug_e("LHS: '%B'\n", lhs->e);
		debug_e("RHS: '%B'\n", rhs->e);
		newObject = createNewElement(GT, lhs->pairing);
		pairing_apply(newObject->e, lhs->e, rhs->e, rhs->pairing->pair_obj);
#ifdef BENCHMARK_ENABLED
		UPDATE_BENCHMARK(PAIRINGS, newObject->pairing->dBench);
#endif
		return (PyObject *) newObject;
	}

	if(lhs->element_type == rhs->element_type){
		if(lhs->element_type == G1){
			PyErr_SetString(PyExc_ValueError, "Both elements are of type G1 in asymmetric pairing");
			return NULL;
		}
		if(lhs->element_type == G2){
			PyErr_SetString(PyExc_ValueError, "Both elements are of type G2 in asymmetric pairing");
			return NULL;
		}
		PyErr_SetString(PyExc_ValueError, "Unexpected elements type in asymmetric pairing product");
		return NULL;
	}

	// execute asymmetric pairing
	debug_e("LHS: '%B'\n", lhs->e);
	debug_e("RHS: '%B'\n", rhs->e);
	newObject = createNewElement(GT, lhs->pairing);
	if(lhs->element_type == G1)
		pairing_apply(newObject->e, lhs->e, rhs->e, rhs->pairing->pair_obj);
	else if(lhs->element_type == G2)
		pairing_apply(newObject->e, rhs->e, lhs->e, rhs->pairing->pair_obj);

#ifdef BENCHMARK_ENABLED
	UPDATE_BENCHMARK(PAIRINGS, newObject->pairing->dBench);
#endif
	return (PyObject *) newObject;

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
	
	if(!PyElement_Check(object)) EXIT_IF(TRUE, "not a valid element object.");
	EXIT_IF(object->elem_initialized == FALSE, "null element object.");
	int hash_size = HASH_LEN;
	uint8_t hash_buf[hash_size + 1];
	if(!hash_element_to_bytes(&object->e, hash_size, hash_buf, label)) {
		PyErr_SetString(ElementError, "failed to hash element");
		return NULL;
	}
	hash_hex = convert_buffer_to_hex(hash_buf, hash_size);
	printf_buffer_as_hex(hash_buf, hash_size);

	str = PyBytes_FromString((const char *) hash_hex);
	free(hash_hex);
	return str;
}

// The hash function should be able to handle elements of various types and accept
// a field to hash too. For example, a string can be hashed to Zr or G1, an element in G1 can be
static PyObject *Element_hash(Element *self, PyObject *args) {
	Element *newObject = NULL, *object = NULL;
	Pairing *group = NULL;
	PyObject *objList = NULL, *tmpObject = NULL, *tmpObj = NULL;
	int result, i;
	GroupType type = ZR;
	
	char *tmp = NULL, *str;
	// make sure args have the right type -- check that args contain a "string" and "string"
	if(!PyArg_ParseTuple(args, "OO|i", &group, &objList, &type)) {
		EXIT_IF(TRUE, "invalid object types");
	}

	VERIFY_GROUP(group);
	int hash_len = mpz_sizeinbase(group->pair_obj->r, 2) / BYTE;
	uint8_t hash_buf[hash_len];
	memset(hash_buf, 0, hash_len);

	// first case: is a string and type may or may not be set
	if(PyBytes_CharmCheck(objList)) {
		str = NULL;
		PyBytes_ToString2(str, objList, tmpObj);
		if(type == ZR) {
			// create an element of Zr
			// hash bytes using SHA1
			int str_length = (int) strlen(str);
			result = hash_to_bytes((uint8_t *) str, str_length, hash_buf, hash_len, HASH_FUNCTION_STR_TO_Zr_CRH);
			// extract element in hash
			if(!result) { 
				tmp = "could not hash to bytes.";
				goto cleanup; 
			}
			newObject = createNewElement(ZR, group);
			element_from_hash(newObject->e, hash_buf, hash_len);
		}
		else if(type == G1 || type == G2) { // depending on the curve hashing to G2 might not be supported
		    // element to G1	
			debug("Hashing string '%s'\n", str);
			debug("Target GroupType => '%d'", type);
			// hash bytes using SHA1
			int str_length = (int) strlen(str);
			result = hash_to_bytes((uint8_t *) str, str_length, hash_buf, hash_len, HASH_FUNCTION_Zr_TO_G1_ROM);
			if(!result) { 
				tmp = "could not hash to bytes.";
				goto cleanup; 
			}			
			newObject = createNewElement(type, group);
			element_from_hash(newObject->e, hash_buf, hash_len);
		}
		else {
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
				result = hash_element_to_bytes(&object->e, hash_len, hash_buf, 0);
			}
			else if(PyBytes_CharmCheck(tmpObject)) {
				str = NULL;
				PyBytes_ToString2(str, tmpObject, tmpObj);
				int str_length = strlen((char *) str);
				result = hash_to_bytes((uint8_t *) str, str_length, hash_buf, hash_len, HASH_FUNCTION_STR_TO_Zr_CRH);
				debug("hash str element =>");
				printf_buffer_as_hex(hash_buf, hash_len);
			}
			Py_DECREF(tmpObject);

			// convert the contents of tmp_buf to a string?
			for(i = 1; i < size; i++) {
				tmpObject = PySequence_GetItem(objList, i);
				if(PyElement_Check(tmpObject)) {
					object = (Element *) tmpObject;
					uint8_t out_buf[hash_len+1];
					memset(out_buf, 0, hash_len);
					// current hash_buf output concatenated with object are sha1 hashed into hash_buf
					result = hash2_element_to_bytes(&object->e, hash_buf, hash_len, out_buf);
					debug("hash element => ");
					printf_buffer_as_hex(out_buf, hash_len);
					memcpy(hash_buf, out_buf, hash_len);
				}
				else if(PyBytes_CharmCheck(tmpObject)) {
					str = NULL;
					PyBytes_ToString2(str, tmpObject, tmpObj);
					result = hash2_buffer_to_bytes((uint8_t *) str, strlen((char *) str), hash_buf, hash_len, hash_buf);
				}
				Py_DECREF(tmpObject);
			}

			if(type == ZR) { newObject = createNewElement(ZR, group); }
			else if(type == G1) { newObject = createNewElement(G1, group); }
			else {
				tmp = "invalid object type";
				goto cleanup;
			}

			element_from_hash(newObject->e, hash_buf, hash_len);
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
			newObject = createNewElement(G1, group);
			debug_e("Hashing element '%B' to G1...\n", object->e);
			// hash the element to the G1 field (uses sha1 as well)
			result = hash_element_to_bytes(&object->e, hash_len, (unsigned char *) hash_buf, 0);
			if(!result) {
				tmp = "could not hash to bytes";
				goto cleanup;
			}
			element_from_hash(newObject->e, hash_buf, hash_len);
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


	if(tmpObj != NULL) Py_XDECREF(tmpObj);
	return (PyObject *) newObject;

cleanup:
	if(newObject != NULL) Py_XDECREF(newObject);
	if(tmpObj != NULL) Py_XDECREF(tmpObj);
	EXIT_IF(TRUE, tmp);
}

static PyObject *Element_equals(PyObject *lhs, PyObject *rhs, int opid) {
	Element *self = NULL, *other = NULL;
	int result = -1; // , value;

	EXIT_IF(opid != Py_EQ && opid != Py_NE, "comparison supported: '==' or '!='");
	// check type of lhs & rhs
	if(PyElement_Check(lhs) && PyElement_Check(rhs)) {
		self = (Element *) lhs;
		other = (Element *) rhs;
	}

	debug("Starting '%s'\n", __func__);
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
			mpz_t val;
			mpz_init(val);
			element_to_mpz(val, value->e);
			PyObject *obj = mpzToLongObj(val);
			mpz_clear(val);
			return obj;
		}
	}
	EXIT_IF(TRUE, "cannot convert this type of object to an integer.");
}

static long Element_index(Element *o1) {
	long result = -1;

	if(o1->element_type == ZR) {
		mpz_t o;
		mpz_init(o);
		element_to_mpz(o, o1->e);
		PyObject *temp = mpzToLongObj(o);
		result = PyObject_Hash(temp);
		mpz_clear(o);
		Py_XDECREF(temp);
	}
	if(o1->element_type != NONE_G){
		uint8_t *buff;
		size_t len;
		len = element_length_in_bytes(o1->e);
		buff = (uint8_t*) malloc(len);
		element_to_bytes(buff, o1->e);
		result = PyObject_Hash(PyBytes_FromStringAndSize((char*)buff, len));
		free(buff);
	}
	return result;
}

UNARY(instance_negate, 'i', Element_negate)
UNARY(instance_invert, 'i', Element_invert)
BINARY(instance_add, 'a', Element_add)
BINARY(instance_sub, 's', Element_sub)

static PyObject *Serialize_cmp(PyObject *self, PyObject *args) {

	Element *element = NULL;
	int compression = 1;

#if PY_MAJOR_VERSION >= 3 && PY_MINOR_VERSION >= 3
	if(!PyArg_ParseTuple(args, "O|p:serialize", &element, &compression))
#else
	if(!PyArg_ParseTuple(args, "O|i:serialize", &element, &compression))
#endif
        return NULL;

	if(!PyElement_Check(element)) {
		PyErr_SetString(PyExc_TypeError, "Invalid element type.");
		return NULL;
	}
	if(element->elem_initialized == FALSE) {
		PyErr_SetString(PyExc_ValueError, "Element not initialized.");
		return NULL;
	}

	int elem_len = 0;
	uint8_t *data_buf = NULL;
	size_t bytes_written;

	if(element->element_type == ZR || element->element_type == GT) {
		elem_len = element_length_in_bytes(element->e);
		data_buf = (uint8_t *) malloc(elem_len + 1);
		if(data_buf == NULL)
			return PyErr_NoMemory();
		// write to char buffer
		bytes_written = element_to_bytes(data_buf, element->e);
		debug("result => ");
		printf_buffer_as_hex(data_buf, bytes_written);
	}
	else if(element->element_type != NONE_G) {
	// object initialized now retrieve element and serialize to a char buffer.
		if(compression){
			elem_len = element_length_in_bytes_compressed(element->e);
		}else{
			elem_len = element_length_in_bytes(element->e);
		}
		data_buf = (uint8_t *) malloc(elem_len + 1);
		if(data_buf == NULL)
			return PyErr_NoMemory();
		// write to char buffer
		if(compression){
			bytes_written = element_to_bytes_compressed(data_buf, element->e);
		} else {
			bytes_written = element_to_bytes(data_buf, element->e);
		}
	}
	else {
		PyErr_SetString(PyExc_TypeError, "Invalid element type.");
		return NULL;
	}

	// convert to base64 and return as a string?
	size_t length = 0;
	char *base64_data_buf = NewBase64Encode(data_buf, bytes_written, FALSE, &length);
	//PyObject *result = PyUnicode_FromFormat("%d:%s", element->element_type, (const char *) base64_data_buf);
	// free(base64_data_buf);
	PyObject *result = PyBytes_FromFormat("%d:%s", element->element_type, (const char *) base64_data_buf);
	debug("base64 enc => '%s'\n", base64_data_buf);
	free(base64_data_buf);
	free(data_buf);
	return result;
}

static PyObject *Deserialize_cmp(PyObject *self, PyObject *args) {
	Element *origObject = NULL;
	Pairing *group = NULL;
	PyObject *object;
	int compression = 1;

#if PY_MAJOR_VERSION >= 3 && PY_MINOR_VERSION >= 3
	if(!PyArg_ParseTuple(args, "OO|p:deserialize", &group, &object, &compression))
#else
	if(!PyArg_ParseTuple(args, "OO|i:deserialize", &group, &object, &compression))
#endif
		return NULL;

	VERIFY_GROUP(group);

	if(!PyBytes_Check(object)){
		PyErr_SetString(PyExc_TypeError, "Serialized object must be bytes.");
		return NULL;
	}

	uint8_t *serial_buf = (uint8_t *) PyBytes_AsString(object);
	int type = atoi((const char *) &(serial_buf[0]));
	uint8_t *base64_buf = (uint8_t *)(serial_buf + 2);

	size_t deserialized_len = 0;
	uint8_t *binary_buf = NewBase64Decode((const char *) base64_buf, strlen((char *) base64_buf), &deserialized_len);

	if((type == ZR || type == GT) && deserialized_len > 0) {
	//				debug("result => ");
	//				printf_buffer_as_hex(binary_buf, deserialized_len);
		origObject = createNewElement(type, group);
		element_from_bytes(origObject->e, binary_buf);
		free(binary_buf);
		return (PyObject *) origObject;
	}
	else if((type == G1 || type == G2) && deserialized_len > 0) {
		// now convert element back to an element type (assume of type ZR for now)
		origObject = createNewElement(type, group);
		if(compression) {
			element_from_bytes_compressed(origObject->e, binary_buf);
		} else {
			element_from_bytes(origObject->e, binary_buf);
		}
		free(binary_buf);
		return (PyObject *) origObject;
	}

	PyErr_SetString(PyExc_ValueError, "Nothing to deserialize in element.");
	return NULL;
}

void print_mpz(mpz_t x, int base) {
#ifdef DEBUG
	if(base <= 2 || base > 64) return;
	size_t x_size = mpz_sizeinbase(x, base) + 2;
	char *x_str = (char *) malloc(x_size);
	x_str = mpz_get_str(x_str, base, x);
	printf("Element => '%s'\n", x_str);
	printf("Order of Element => '%zd'\n", x_size);
	free(x_str);
#endif
}

int check_membership(Element *elementObj) {
	int result = -1;
	element_t e;

	if(elementObj->element_type == ZR) {
		/* check value is between 1 and order */
		mpz_t zr;
		mpz_init(zr);
		element_to_mpz(zr, elementObj->e);
		int ans = mpz_cmp(zr, elementObj->pairing->pair_obj->Zr->order);
		result = ans <= 0 ? TRUE : FALSE;
		mpz_clear(zr);
	}
	/* for G1, G2, and GT test e^q == 1 (mod q)? */
	else if(elementObj->element_type == G1) {
		element_init_G1(e, elementObj->pairing->pair_obj);
		element_pow_mpz(e, elementObj->e, elementObj->pairing->pair_obj->G1->order);
//		element_printf("Elment->e => '%B'\n", e);
		result = element_is1(e) ? TRUE : FALSE; // TODO: verify this
		element_clear(e);
	}
	else if(elementObj->element_type == G2) {
		element_init_G2(e, elementObj->pairing->pair_obj);
		element_pow_mpz(e, elementObj->e, elementObj->pairing->pair_obj->G2->order);
//		element_printf("Elment->e => '%B'\n", e);
		result = element_is1(e) ? TRUE : FALSE; // TODO: verify this
		element_clear(e);
	}
	else if(elementObj->element_type == GT) {
		element_init_GT(e, elementObj->pairing->pair_obj);
		element_pow_mpz(e, elementObj->e, elementObj->pairing->pair_obj->GT->order);
//		element_printf("Elment->e => '%B'\n", e);
		result = element_is1(e) ? TRUE : FALSE; // TODO: verify this
		element_clear(e);
	}
	else {/* not a valid type */ }
	return result;
}


static PyObject *Group_Check(Element *self, PyObject *args) {

	Pairing *group = NULL;
	Element *object = NULL;
	if(PyArg_ParseTuple(args, "OO", &group, &object)) {
		VERIFY_GROUP(group); /* verify group object is still active */
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
		EXIT_IF(TRUE, "invalid group object.");
	}
	VERIFY_GROUP(group);
	PyObject *object = (PyObject *) mpzToLongObj(group->pair_obj->r);
	return object; /* returns a PyInt */
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
	GetField(countZR, type, ZR, gBench);
	GetField(countG1, type, G1, gBench);
	GetField(countG2, type, G2, gBench);
	GetField(countGT, type, GT, gBench);

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
  (reprfunc)Element_print, /*tp_str*/
  0,                         /*tp_getattro*/
  0,                         /*tp_setattro*/
  0,                         /*tp_as_buffer*/
  Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
  "Pairing element objects",           /* tp_doc */
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
  (reprfunc)Element_print,   /*tp_repr*/
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
  "Pairing element objects",           /* tp_doc */
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
  {"preproc", T_INT, offsetof(Element, elem_initPP), 0,
  "determine pre-processing status"},
  {NULL}  /* Sentinel */
};

PyMethodDef Element_methods[] = {
  {"initPP", (PyCFunction)Element_initPP, METH_NOARGS, "Initialize the pre-processing field of element."},
  {"set", (PyCFunction)Element_set, METH_VARARGS, "Set an element to a fixed value."},
  {NULL}  /* Sentinel */
};

PyMethodDef pairing_methods[] = {
	{"init", (PyCFunction)Element_elem, METH_VARARGS, "Create an element in group Zr and optionally set value."},
	{"pair", (PyCFunction)Apply_pairing, METH_VARARGS, "Apply pairing between an element of G1 and G2 and returns an element mapped to GT"},
	{"hashPair", (PyCFunction)sha2_hash, METH_VARARGS, "Compute a sha1 hash of an element type"},
	{"H", (PyCFunction)Element_hash, METH_VARARGS, "Hash an element type to a specific field: Zr, G1, or G2"},
	{"random", (PyCFunction)Element_random, METH_VARARGS, "Return a random element in a specific group: G1, G2, Zr"},
	{"serialize", (PyCFunction)Serialize_cmp, METH_VARARGS, "Serialize an element type into bytes."},
	{"deserialize", (PyCFunction)Deserialize_cmp, METH_VARARGS, "De-serialize an bytes object into an element object"},
	{"ismember", (PyCFunction) Group_Check, METH_VARARGS, "Group membership test for element objects."},
	{"order", (PyCFunction) Get_Order, METH_VARARGS, "Get the group order for a particular field."},
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
	//return pairings_clear(m);
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

  PyModule_AddIntConstant(m, "ZR", ZR);
  PyModule_AddIntConstant(m, "G1", G1);
  PyModule_AddIntConstant(m, "G2", G2);
  PyModule_AddIntConstant(m, "GT", GT);

#ifdef BENCHMARK_ENABLED
  ADD_BENCHMARK_OPTIONS(m);
  PyModule_AddStringConstant(m, "Pair", 	  _PAIR_OPT);
  PyModule_AddStringConstant(m, "Granular", _GRAN_OPT);
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
