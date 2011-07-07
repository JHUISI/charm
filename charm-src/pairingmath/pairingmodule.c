
#include "pairingmodule.h"

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
	debug("Performing the '%s' operation.\n", __func__); \
	if(PyElement_Check(v)) {			\
		obj1 = (Element *) v; } \
	else { return NULL; }		\
	if(PyElement_Check(w)) {	\
		obj2 = (Element *) w; } \
	else { return NULL; }		\
	if(Check_Types(obj1->element_type, obj2->element_type, m))	\
		return (n)(obj1, obj2); \
	return NULL;				\
}

#define BINARY3(f, m, n) \
static PyObject *f(PyObject *v, PyObject *w, PyObject *x) { \
  debug("Performing the '%s' operation.\n", __func__); \
  if(PyElement_Check(v) && PyElement_Check(w))  {  Element *obj1 = (Element *) v;  \
	Element *obj2 = (Element *) w; if(Check_Types(obj1->element_type, obj2->element_type, m)) { \
	return (n)(obj1, obj2);	}		\
	}				\
	return NULL;	\
}		

#define BINARY_NONE(f, m, n) \
static PyObject *f(PyObject *v, PyObject *w) { \
 Py_INCREF(Py_NotImplemented);	\
 return Py_NotImplemented;  }

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
		snprintf(tmp1, 3, "%02x ", data[i]);
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
			// && r_type != ZR)
			// else { 
			//	PyErr_SetString(ElementError, "Only fields => [G1,G2,GT,Zr] ** Zr");
			//	return FALSE; 
			//}			
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
	retObject->pairing = pairing;
	retObject->safe_pairing_clear = FALSE;
	retObject->param_buf = NULL;		
	
	return retObject;	
}

void 	Pairing_dealloc(Pairing *self)
{
	if(self->safe) {
		debug("Clear pairing => 0x%p\n", self->pair_obj);
		pairing_clear(self->pair_obj);
	}

	debug("Releasing pairing object!\n");
	Py_TYPE(self)->tp_free((PyObject *) self);
}

void	Element_dealloc(Element* self)
{
	// add reference count to objects
	if(self->elem_initialized && self->e) {
		debug_e("Clear element_t => '%B'\n", self->e);
		element_clear(self->e);
	}
	
	if(self->param_buf) {
		debug("param_buf => 0x%p\n", self->param_buf);
		free(self->param_buf);
	}
	
//	if(self->safe_pairing_clear && self->pairing) {
//		debug("Clear pairing => 0x%p\n", self->pairing);
//		pairing_clear(self->pairing);
//	}
	if(self->safe_pairing_clear) {
		PyObject_Del(self->pairing);
	}
		// dealloc each object, PyObject_Del?
//		int i;
//		for(i = 0; i < MAX_BENCH_OBJECTS; i++) {
//			activeObject = NULL;
//			if(dObjects[i] != NULL) {
//				if(dObjects[i]->bench_initialized) { // if initialized
//					debug("dObject with identifier: %d\n", dObjects[i]->identifier);
//					debug("Dealloc dObject[%d] with %p which points to: %p\n", dObjects[i]->identifier, &(dObjects[i]), dObjects[i]);
//					// printf("Add ctr = %d\n", dObjects[i]->op_add);
//					//Py_DECREF(dObjects[i]);
//					PyObject_Del(dObjects[i]);
//				}
//				else {
//					// not initialized, but has been allocated
//					debug("object allocated, but not initialized.\n");
//					//Py_DECREF(dObjects[i]);
//					PyObject_Del(dObjects[i]);
//				}
//			}
//		}

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
				fread(*out, sizeof(char), out_len, f);
				return out_len;
			}
		}
	}
	return 0;
}

static char * init_pbc_param(char *file, pairing_t *pairing)
{
	pbc_param_t params;
	FILE *fp;
	size_t count;
	char *buf = NULL;
	fp = fopen(file, "r");
	
	if(fp == NULL) {
		printf("Error reading file.\n");
		return NULL;
	}
	
	debug("Reading '%s'\n", file);
	count = read_file(fp, &buf);
	debug("param='%s'\n", buf);

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

int hash_element_to_bytes(element_t *element, int hash_size, uint8_t* output_buf)
{
	int result = TRUE;
	unsigned int buf_len;
	
	buf_len = element_length_in_bytes(*element);
	uint8_t *temp_buf = (uint8_t *)malloc(buf_len);
	if (temp_buf == NULL) {
		return FALSE;
	}
	
	element_to_bytes(temp_buf, *element);
	result = hash_to_bytes(temp_buf, buf_len, hash_size, output_buf, HASH_FUNCTION_ELEMENTS);
	
	free(temp_buf);
	
	return TRUE;
}

int hash2_element_to_bytes(element_t *element, uint8_t* last_buf, int hash_size, uint8_t* output_buf) {
	int result = TRUE;
	unsigned int last_buflen = strlen((char *) last_buf);

	unsigned int buf_len = element_length_in_bytes(*element);
	uint8_t* temp_buf = (uint8_t *) malloc(buf_len + 1);
	if(temp_buf == NULL) {
		return FALSE;
	}

	element_to_bytes((unsigned char *) temp_buf, *element);
	// create output buffer
	uint8_t* temp2_buf = (uint8_t *) malloc(last_buflen + buf_len + 1);
	memset(temp2_buf, 0, (last_buflen + buf_len));
	// copy first input buffer (last_buf) into target buffer
	strncat((char *) temp2_buf, (char *) last_buf, last_buflen);
	// copy element buffer (temp_buf) into target buffer
	strncat((char *) temp2_buf, (char *) temp_buf, buf_len);
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
	// NOTE: if you want variables to stick around, make sure you declare them as static or else
	// they will be deallocated!
//	pbc_param_t p;
	Pairing *pairing;
	static char *buf;
	char *buf2 = NULL;
	PyObject *n = NULL, *short_val = NULL;
	int qbits = 0, rbits = 0;
	size_t b_len = 0;
	int seed = -1;
	
    static char *kwlist[] = {"params", "n", "qbits", "rbits", "short", "param_string", "seed", NULL};
	
    if (! PyArg_ParseTupleAndKeywords(args, kwds, "|sOiiOs#i", kwlist,
                                      &self->params, &n, &qbits, &rbits, &short_val, &buf2, &b_len, &seed)) {
    	PyErr_SetString(ElementError, "invalid arguments");
        return -1; 
	}
	if (self->params && !n && !qbits && !rbits && !short_val && !buf2) {
		pairing = PyObject_New(Pairing, &PairingType);
		buf = init_pbc_param(self->params, &pairing->pair_obj);
		
		if(buf != NULL) {
			debug("Initialized pairings type: '%s'\n", self->params);
			self->param_buf = buf;
		}
		else {
			PyErr_SetString(ElementError, "failed to read params file.");
			return -1;
		}
	}
	else if(buf2 && !n && !qbits && !rbits && !short_val) {
		// parameters is provided in string
		pairing = PyObject_New(Pairing, &PairingType);
		debug("Paramter String => '%s'\n", buf2);
		pbc_param_init_set_buf(pairing->p, buf2, b_len);
		pairing_init_pbc_param(pairing->pair_obj, pairing->p);
	}
	else if (n && !(qbits || rbits)) {
		// if n is provided, and qbits and rbits are not
		debug("n set, but q and r are NOT set!\n");
		pairing = PyObject_New(Pairing, &PairingType);
		if(short_val == Py_True) {
			// type f curve
			if(!PyLong_Check(n)) {
				PyErr_SetString(ElementError, "n is expected to be short and an int or long type.");
				PyObject_Del(pairing);
				return -1;
			}
			long bits = PyLong_AsLong(n);
			pbc_param_init_f_gen(pairing->p, (int) bits);
		}
		else {
			if(!PyLong_Check(n)) {
				PyErr_SetString(ElementError, "n is expected to be large and a long type.");
				PyObject_Del(pairing);
				return -1;
			}

			// type a1 curve
			mpz_t n_val;
			mpz_init(n_val);
			longObjToMPZ(n_val, (PyLongObject *) n);

			pbc_param_init_a1_gen(pairing->p, n_val);
			mpz_clear(n_val);
		}
		pairing_init_pbc_param(pairing->pair_obj, pairing->p);
	}
    // if qbits and rbits are provided, and n is not
	else if (qbits && rbits && !n) {
		debug("q and r set, but NOT n!\n");
		pairing = PyObject_New(Pairing, &PairingType);
		if(short_val == Py_True)
			pbc_param_init_e_gen(pairing->p, rbits, qbits);
		else
			pbc_param_init_a_gen(pairing->p, rbits, qbits);
		pairing_init_pbc_param(pairing->pair_obj, pairing->p);
	}
	// figure out how to expose func to find type d and g curves
	else {
		PyErr_SetString(ElementError, "cannot derive curve type and parameters.");
		return -1;
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
	element_printf("Elment->e => '%B'\n", newObject->e);
	debug("Element->type => '%d'\n", newObject->element_type);
	
	return NULL;
}
 
static PyObject *Element_elem(Element* self, PyObject* args)
{
	Element *retObject;
	int type;
	PyObject *long_obj = NULL;
	
	if(self->pairing == NULL) {
		PyErr_SetString(ElementError, "pairing object is not set.");
		return NULL;
	}
	
	if(!PyArg_ParseTuple(args, "i|O", &type, &long_obj)) {
		PyErr_SetString(ElementError, "invalid arguments.\n");
		return NULL;
	}
	
	debug("init an element.\n");

	if(type >= ZR && type <= GT) {
		retObject = createNewElement(type, self->pairing);
	}
	else {
		PyErr_SetString(ElementError, "unrecognized group type.");
		return NULL;
	}

	if(PyLong_Check(long_obj)) {
		mpz_t m;
		mpz_init(m);
		longObjToMPZ(m, (PyLongObject *) long_obj);
		element_set_mpz(retObject->e, m);
		mpz_clear(m);
	}
	
	/* return Element object */
	return (PyObject *) retObject;		
}

// TODO: use element_vnprintf to copy the result into element type
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

	if(self->pairing && self->safe_pairing_clear) {
		if(self->param_buf != NULL) return PyUnicode_FromString((char *) self->param_buf);
		else {
			pbc_param_out_str(stdout, self->pairing->p);
			return PyUnicode_FromString("");
		}
	}

	return PyUnicode_FromString("");
}

static PyObject *Element_random(Element* self, PyObject* args)
{
	Element *retObject;
	int arg1;
	int e_type = -1, seed = -1;

	if(self->pairing == NULL) {
		printf("pairing is NULL.\n");
		return NULL;
	}
	
	/* create a new object */
	if(!PyArg_ParseTuple(args, "i|i", &arg1, &seed))
		return NULL;

	START_CLOCK(dBench);
	retObject = PyObject_New(Element, &ElementType);
	debug("init random element in '%d'\n", arg1);
	if(arg1 == ZR) {
		element_init_Zr(retObject->e, self->pairing->pair_obj);
		e_type = ZR; 
	}
	else if(arg1 == G1) {
		element_init_G1(retObject->e, self->pairing->pair_obj);
		e_type = G1;
	}
	else if(arg1 == G2) {
		element_init_G2(retObject->e, self->pairing->pair_obj);
		e_type = G2;
	}
	else if(arg1 == GT) {
		PyErr_SetString(ElementError, "cannot generate random element in GT.");
		return NULL;
	}
	else {
		PyErr_SetString(ElementError, "unrecognized group type.");
		return NULL;
	}
	
	if(seed > -1) {
		pbc_random_set_deterministic((uint32_t) seed);
	}
	/* create new Element object */
	element_random(retObject->e);
	STOP_CLOCK(dBench);
	retObject->elem_initialized = TRUE;
	retObject->pairing = self->pairing;
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
		element_printf("Left: e => '%B'\n", self->e);		
	}
	
	if(other->e) {
		element_printf("Right: e => '%B'\n", other->e);				
	}
#endif

	// start micro benchmark
	START_CLOCK(dBench);
	newObject = createNewElement(self->element_type, self->pairing);
	element_add(newObject->e, self->e, other->e);
	STOP_CLOCK(dBench);
	UPDATE_BENCHMARK(ADDITION, dBench)
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
	
	START_CLOCK(dBench);
	newObject = createNewElement(self->element_type, self->pairing);
	element_sub(newObject->e, self->e, other->e);		
	STOP_CLOCK(dBench);
	UPDATE_BENCHMARK(SUBTRACTION, dBench)
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
		element_mul_si(newObject->e, self->e, z);
		STOP_CLOCK(dBench);
	}
	else if(PyElement_Check(rhs) && found_int) {
		// rhs is the element type
		START_CLOCK(dBench);
		newObject = createNewElement(other->element_type, other->pairing);
		element_mul_si(newObject->e, other->e, z);
		STOP_CLOCK(dBench);
	}
	else if(PyElement_Check(lhs) && PyElement_Check(rhs)) {
		// both are element types
		if(self->element_type != ZR && other->element_type == ZR) {
			START_CLOCK(dBench);
			newObject = createNewElement(self->element_type, self->pairing);
			element_mul_zn(newObject->e, self->e, other->e);		
			STOP_CLOCK(dBench);
		}
		else if(other->element_type != ZR && self->element_type == ZR) {
			// START_CLOCK
			START_CLOCK(dBench);
			newObject = createNewElement(other->element_type, self->pairing);
			element_mul_zn(newObject->e, other->e, self->e);
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
		PyErr_SetString(ElementError, "invalid types");
		return NULL;
	}

	UPDATE_BENCHMARK(MULTIPLICATION, dBench)
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
		newObject = createNewElement(self->element_type, self->pairing);
		if(z == 2) element_halve(newObject->e, self->e);
		else {
			other = createNewElement(self->element_type, self->pairing);
			element_set_si(other->e, z);
			element_div(newObject->e, self->e, other->e);
		}
		STOP_CLOCK(dBench);
	}
	else if(PyElement_Check(rhs) && found_int) {
		// rhs is the element type
		START_CLOCK(dBench);
		newObject = createNewElement(other->element_type, other->pairing);
		if(z == 2) element_halve(newObject->e, other->e);
		else {
			self = createNewElement(other->element_type, other->pairing);
			element_set_si(self->e, z);
			element_div(newObject->e, self->e, other->e);
		}
		STOP_CLOCK(dBench);
	}
	else if(PyElement_Check(lhs) && PyElement_Check(rhs)) {
		// both are element types
		START_CLOCK(dBench);
		newObject = createNewElement(self->element_type, self->pairing);
		element_div(newObject->e, self->e, other->e);
		STOP_CLOCK(dBench);
	}
	else {
		PyErr_SetString(ElementError, "invalid types");
		return NULL;
	}

	UPDATE_BENCHMARK(DIVISION, dBench)
	return (PyObject *) newObject;
}
/*
static PyObject *Element_div(Element *self, Element *other)
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
	
	newObject = createNewElement(self->element_type, self->pairing);
	element_div(newObject->e, self->e, other->e);
	return (PyObject *) newObject;
}
*/
 
static PyObject *Element_invert(Element *self)
{
	Element *newObject;
	
	debug("Starting '%s'\n", __func__);
#ifdef DEBUG	
	if(self->e) {
		element_printf("e => '%B'\n", self->e);		
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
	Element *newObject;

	debug("Starting '%s'\n", __func__);
#ifdef DEBUG
	if(self->e) {
		element_printf("e => '%B'\n", self->e);
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

	Check_Types2(o1, o2, lhs_o1, rhs_o2, longFoundLHS, longFoundRHS)


	if(longFoundLHS) {
		// o1 is a long type
	}
	else if(longFoundRHS) {
		// o2 is a long type
	}
	else {
		debug("Starting '%s'\n", __func__);
		debug_e("LHS: e => '%B'\n", lhs_o1->e);
		debug_e("RHS: e => '%B'\n", rhs_o2->e);

		if(rhs_o2->element_type == ZR) {
			// element_pow_zn(newObject->e, lhs_o1->e, rhs_o1->e);
			START_CLOCK(dBench);
			newObject = createNewElement(lhs_o1->element_type, lhs_o1->pairing);
			mpz_t n;
			mpz_init(n);
			element_to_mpz(n, rhs_o2->e);
			element_pow_mpz(newObject->e, lhs_o1->e, n);
			mpz_clear(n);
			STOP_CLOCK(dBench);
		}
		else {
			// we have a problem
		}
	}
	
	
	// STOP_CLOCK
	UPDATE_BENCHMARK(EXPONENTIATION, dBench)
	return (PyObject *) newObject;
}

/* We assume the element has been initialized into a specific field (G1,G2,GT,or Zr), then
they have the opportunity to set the
 
 */
static PyObject *Element_set(Element *self, PyObject *args)
{
	Element *object;
	long int value;
	// char *str = NULL;
	int errcode = TRUE;
	
	if(self->elem_initialized == FALSE) {
		PyErr_SetString(ElementError, "must initialize element to a field (G1,G2,GT, or Zr)");
		errcode = FALSE;
		return Py_BuildValue("i", errcode);
	}
	
	debug("Creating a new element\n");
	if(PyArg_ParseTuple(args, "l", &value)) {
		// convert into an int using PyArg_Parse(...)
		// set the element
		debug("Setting element to '%li'\n", value);
		START_CLOCK(dBench);
		if(value == 0)
			element_set0(self->e);
		else if(value == 1)
			element_set1(self->e);
		else {
			debug("Value '%i'\n", (signed int) value);
			element_set_si(self->e, (signed int) value);
		}
		STOP_CLOCK(dBench);
	}
	else if(PyArg_ParseTuple(args, "O", &object)){
		START_CLOCK(dBench);
		element_set(self->e, object->e);
		STOP_CLOCK(dBench);
	}
	else { // 
		PyErr_SetString(ElementError, "type not supported: signed int or Element object");
		errcode = FALSE;
	}
	
	return Py_BuildValue("i", errcode);
}
/*
static PyObject *Element_dlog(Element *self, PyObject *args)
{
	Element *newObject, *lhs, *rhs;
	int errcode = TRUE;

	// make sure element has been initialized
	if(PyArg_ParseTuple(args, "OO", &lhs, &rhs)) {
		if(lhs->elem_initialized == TRUE && rhs->elem_initialized == TRUE) {
			newObject = createNewElement(ZR, self->pairing);
			element_dlog_pollard_rho(newObject->e, lhs->e, rhs->e);
			element_printf("x => '%B'\n", newObject->e);
		}
		else {
			errcode = FALSE;
		}
	}

	if(!errcode) {
		PyErr_SetString(ElementError, "must initialize lhs and rhs elements to G1,G2 or Zr.");
		return Py_BuildValue("i", errcode);
	}

	return (PyObject *) newObject;
}*/

/* this is a type method that is visible on the global or class level. Therefore,
   the function prototype needs the self (element class) and the args (tuple of Element objects).
 */
PyObject *Apply_pairing(Element *self, PyObject *args)
{
	// lhs => G1 and rhs => G2
	Element *newObject, *lhs, *rhs;
	
	debug("Applying pairing...\n");	
	if(!PyArg_ParseTuple(args, "OO", &lhs, &rhs)) {
		PyErr_SetString(ElementError, "missing element objects");
		return NULL;
	}
	
	if(pairing_is_symmetric(lhs->pairing->pair_obj)) {
		debug("Pairing is symmetric.\n");
		debug_e("LHS: '%B'\n", lhs->e);
		debug_e("RHS: '%B'\n", rhs->e);
		START_CLOCK(dBench);
		newObject = createNewElement(GT, lhs->pairing);
		pairing_apply(newObject->e, lhs->e, rhs->e, rhs->pairing->pair_obj);
		STOP_CLOCK(dBench);
		UPDATE_BENCHMARK(PAIRINGS, dBench);
		return (PyObject *) newObject;
	}

	if(Check_Types(lhs->element_type, rhs->element_type, 'e')) {
		// apply pairing
		debug_e("LHS: '%B'\n", lhs->e);
		debug_e("RHS: '%B'\n", rhs->e);
		START_CLOCK(dBench);
		newObject = createNewElement(GT, lhs->pairing);
		pairing_apply(newObject->e, lhs->e, rhs->e, rhs->pairing->pair_obj);
		STOP_CLOCK(dBench);
		UPDATE_BENCHMARK(PAIRINGS, dBench);
		return (PyObject *) newObject;
	}
	
	PyErr_SetString(ElementError, "pairings only apply to elements of G1 x G2 --> GT");
	return NULL;
}

PyObject *sha1_hash(Element *self, PyObject *args) {
	Element *object;
	PyObject *str;
	char *hash_hex = NULL;
	
	debug("Hashing the element...\n");
	if(!PyArg_ParseTuple(args, "O", &object)) {
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
	if(!hash_element_to_bytes(&object->e, hash_size, hash_buf)) {
		PyErr_SetString(ElementError, "failed to hash element");
		return NULL;
	}
	
	hash_hex = convert_buffer_to_hex(hash_buf, hash_size);
	printf_buffer_as_hex(hash_buf, hash_size);
	
	str = PyUnicode_FromString((const char *) hash_hex);
	free(hash_hex);
	STOP_CLOCK(dBench);
	return str;
}
/*
static PyObject *dealloc_benchmark(Element *self, PyObject *args) {
	Benchmark *bObject = NULL;
	if(PyArg_ParseTuple(args, "O", &bObject)) {
		if(bObject != NULL) {
			printf("Removing contents of bObject.\n");
			bObject->ob_type->tp_free((PyObject*)bObject);
		}
	}
	return Py_BuildValue("i", TRUE);
}
*/
// note that this is a class instance function and thus, self will refer to the class object 'element'
// the args will contain the references to the objects passed in by the caller.
// The hash function should be able to handle elements of various types and accept
// a field to hash too. For example, a string can be hashed to Zr or G1, an element in G1 can be
// hashed to GT?
static PyObject *Element_hash(Element *self, PyObject *args) {
	Element *newObject = NULL, *object = NULL;
	PyObject *objList = NULL, *tmpObject = NULL;
	// hashing element to Zr
	uint8_t hash_buf[HASH_LEN];
	int result, i;
	GroupType type = ZR;
	
	char *tmp = NULL;
	// make sure args have the right type -- check that args contain a "string" and "string"
	if(!PyArg_ParseTuple(args, "O|i", &objList, &type)) {
		tmp = "invalid object types";
		goto cleanup;
	}

	// first case: is a string and type may or may not be set
	if(PyUnicode_Check(objList)) {
		char *str = PyBytes_AsString(PyUnicode_AsASCIIString(objList));
		if(type == ZR) {
			debug("Hashing string '%s' to Zr...\n", str);
			// create an element of Zr
			// hash bytes using SHA1
			START_CLOCK(dBench);
			newObject = createNewElement(ZR, self->pairing);
			result = hash_to_bytes((uint8_t *) str, strlen((char *) str), HASH_LEN, hash_buf, type);
			// extract element in hash
			if(!result) { 
				tmp = "could not hash to bytes.";
				goto cleanup; 
			}			 
			element_from_hash(newObject->e, hash_buf, HASH_LEN);
			STOP_CLOCK(dBench);
		}
		else if(type == G1 || type == G2) {
		    // element to G1	
			debug("Hashing string '%s'\n", str);
			debug("Target GroupType => '%d'", type);
			START_CLOCK(dBench);
			newObject = createNewElement(type, self->pairing);
			// hash bytes using SHA1
			result = hash_to_bytes((uint8_t *) str, strlen((char *) str), HASH_LEN, hash_buf, type);
			if(!result) { 
				tmp = "could not hash to bytes.";
				goto cleanup; 
			}			
			element_from_hash(newObject->e, hash_buf, HASH_LEN);
			STOP_CLOCK(dBench);
		}
		else {
			// not supported, right?
			tmp = "cannot hash a string to that field. Only Zr or G1.";
			goto cleanup;
		}
	}
	// element type to ZR or G1. Can also contain multiple elements
//	else if(PyArg_ParseTuple(args, "O|i", &objList, &type)) {
	// second case: is a tuple of elements of which could be a string or group elements
	else if(PySequence_Check(objList)) {
		int size = PySequence_Length(objList);
		if(size > 0) {
			// its a tuple of Elements
			tmpObject = PySequence_GetItem(objList, 0);
			if(PyElement_Check(tmpObject)) {
				object = (Element *) tmpObject;
				START_CLOCK(dBench);
				result = hash_element_to_bytes(&object->e, HASH_LEN, hash_buf);
				STOP_CLOCK(dBench);
			}
			else if(PyUnicode_Check(tmpObject)) {
				char *str = PyBytes_AsString(PyUnicode_AsASCIIString(tmpObject));
				START_CLOCK(dBench);
				result = hash_to_bytes((uint8_t *) str, strlen((char *) str), HASH_LEN, hash_buf, HASH_FUNCTION_STR_TO_Zr_CRH);
				STOP_CLOCK(dBench);
			}
			Py_DECREF(tmpObject);

			// convert the contents of tmp_buf to a string?
			for(i = 1; i < size; i++) {
				tmpObject = PySequence_GetItem(objList, i);
				if(PyElement_Check(tmpObject)) {
					object = (Element *) tmpObject;
					START_CLOCK(dBench);
					// current hash_buf output concatenated with object are sha1 hashed into hash_buf
					result = hash2_element_to_bytes(&object->e, hash_buf, HASH_LEN, hash_buf);
					STOP_CLOCK(dBench);
				}
				else if(PyUnicode_Check(tmpObject)) {
					char *str = PyBytes_AsString(PyUnicode_AsASCIIString(tmpObject));
					START_CLOCK(dBench);
					// this assumes that the string is the first object (NOT GOOD, change)
//					result = hash_to_bytes((uint8_t *) str, strlen((char *) str), HASH_LEN, (unsigned char *) hash_buf, HASH_FUNCTION_STR_TO_Zr_CRH);
					result = hash2_buffer_to_bytes((uint8_t *) str, strlen((char *) str), hash_buf, HASH_LEN, hash_buf);
					// hash2_element_to_bytes()
					STOP_CLOCK(dBench);
				}
				Py_DECREF(tmpObject);
			}
			START_CLOCK(dBench);
			if(type == ZR) { newObject = createNewElement(ZR, self->pairing); }
			else if(type == G1) { newObject = createNewElement(G1, self->pairing); }
			else {
				tmp = "invalid object type";
				goto cleanup;
			}
			element_from_hash(newObject->e, hash_buf, HASH_LEN);
			STOP_CLOCK(dBench);
		}
	}
	// third case: a tuple with one element and
	else if(PyElement_Check(objList)) {
			// one element
		printf("third case is being executed...\n");
		object = (Element *) objList;
		if(object->elem_initialized == FALSE) {
			tmp = "element not initialized.";
			goto cleanup;
		}

		// TODO: add type == ZR?

		// Hash an element of Zr to an element of G1.
		if(type == G1) {
			START_CLOCK(dBench);
			newObject = createNewElement(G1, self->pairing);
			debug_e("Hashing element '%B' to G1...\n", object->e);
			// hash the element to the G1 field (uses sha1 as well)
			// START_CLOCK
			result = hash_element_to_bytes(&object->e, HASH_LEN, (unsigned char *) hash_buf);
			if(!result) {
				tmp = "could not hash to bytes";
				goto cleanup;
			}
			element_from_hash(newObject->e, hash_buf, HASH_LEN);
			STOP_CLOCK(dBench);
		}
		else {
			tmp = "can only hash an element of Zr to G1. Random Oracle.";
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

	if(opid != Py_EQ) {
		PyErr_SetString(ElementError, "only comparison supported is '=='");
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
		if(z == 0) result = element_is0(self->e);
		else result = element_is1(self->e);
	}
	else if(PyElement_Check(rhs) && found_int) {
		if(z == 0) result = element_is0(other->e);
		else result = element_is1(self->e);
	}
	else if(PyElement_Check(lhs) && PyElement_Check(rhs)) {
		// lhs and rhs are both elements
		if(self->elem_initialized && other->elem_initialized) {
			result = element_cmp(self->e, other->e);
		}
		else {
			debug("One of the elements is not initialized.\n");
		}
	}
	STOP_CLOCK(dBench);

cleanup:
//	value = (result == 0) ? TRUE : FALSE;
	if(result == 0) {
		Py_INCREF(Py_True);
		return Py_True;
	}

	Py_INCREF(Py_False);
	return Py_False; // Py_BuildValue("i", value);
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
	PyErr_SetString(ElementError, "cannot cast this type.");
	return NULL;
}

UNARY(instance_negate, 'i', Element_negate)
UNARY(instance_invert, 'i', Element_invert)
BINARY(instance_add, 'a', Element_add)
BINARY(instance_sub, 's', Element_sub)

static PyObject *Serialize_cmp(Element *o1, PyObject *args) {

	if(o1->pairing == NULL) {
		PyErr_SetString(ElementError, "pairing params not initialized.");
		return NULL;
	}
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
	if(self->element_type == ZR || self->element_type == GT) {
//		PyErr_SetString(ElementError, "cannot compress elements of Zr any further. Use 'serialize'.");
//		return NULL;
		elem_len = element_length_in_bytes(self->e);

		data_buf = (uint8_t *) malloc(elem_len + 1);
		if(data_buf == NULL) {
			PyErr_SetString(ElementError, "out of memory.");
			return NULL;
		}
		// write to char buffer
		bytes_written = element_to_bytes(data_buf, self->e);
		debug("result => ");
		printf_buffer_as_hex(data_buf, bytes_written);
	}
	else if(self->element_type != NONE_G) {
	// object initialized now retrieve element and serialize to a char buffer.
		elem_len = element_length_in_bytes_compressed(self->e);
		data_buf = (uint8_t *) malloc(elem_len + 1);
		if(data_buf == NULL) {
			PyErr_SetString(ElementError, "out of memory.");
			return NULL;
		}
		// write to char buffer
		bytes_written = element_to_bytes_compressed(data_buf, self->e);
	}
	else {
		PyErr_SetString(ElementError, "invalid type.\n");
		return NULL;
	}

	// convert to base64 and return as a string?
	size_t length = 0;
	char *base64_data_buf = NewBase64Encode(data_buf, bytes_written, FALSE, &length);
	//PyObject *result = PyUnicode_FromFormat("%d:%s", self->element_type, (const char *) base64_data_buf);
	// free(base64_data_buf);
	PyObject *result = PyBytes_FromFormat("%d:%s", self->element_type, (const char *) base64_data_buf);
	debug("base64 enc => '%s'\n", base64_data_buf);
	free(base64_data_buf);
	free(data_buf);
	STOP_CLOCK(dBench);
	return result;
}

static PyObject *Deserialize_cmp(Element *self, PyObject *args) {
	Element *origObject = NULL;
	PyObject *object;

	if(self->pairing == NULL) {
		PyErr_SetString(ElementError, "pairing params not initialized.");
		return NULL;
	}

	if(PyArg_ParseTuple(args, "O", &object)) {
		START_CLOCK(dBench);
		if(PyBytes_Check(object)) {
			uint8_t *serial_buf = (uint8_t *) PyBytes_AsString(object);
			int type = atoi((const char *) &(serial_buf[0]));
			uint8_t *base64_buf = (uint8_t *)(serial_buf + 2);
//			debug("type => %d\n", type);
//			debug("base64 dec => '%s'\n", base64_buf);
//			size_t deserialized_len = strlen((char *) binary_buf);
			size_t deserialized_len = 0;
			uint8_t *binary_buf = NewBase64Decode((const char *) base64_buf, strlen((char *) base64_buf), &deserialized_len);

			if((type == ZR || type == GT) && deserialized_len > 0) {
//				debug("result => ");
//				printf_buffer_as_hex(binary_buf, deserialized_len);
				origObject = createNewElement(type, self->pairing);
				element_from_bytes(origObject->e, binary_buf);
				free(binary_buf);
				STOP_CLOCK(dBench);
				return (PyObject *) origObject;
			}
			else if((type == G1 || type == G2) && deserialized_len > 0) {
				// now convert element back to an element type (assume of type ZR for now)
				origObject = createNewElement(type, self->pairing);
				element_from_bytes_compressed(origObject->e, binary_buf);
				free(binary_buf);
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

///**
// * Define the 3 benchmark methods here...
// */
//static PyObject *_init_benchmark(Element *self, PyObject *args) {
//	int i, id = -1;
//	// find the first unused identifier
//	for(i = 0; i < MAX_BENCH_OBJECTS; i++) {
//		if(dObjects[i]->bench_initialized == FALSE) {
//			id = i;
//			break;
//		}
//	}
//	// fail here if we cant find an unused identifier. basically, user has to delete some benchmarks in progress
//	if(id == -1) {
//		PyErr_SetString(BenchmarkError, "failed to find an unused benchmark object.");
//		return NULL;
//	}
//
//	debug("Using id=%d\n", id);
//	dObjects[id]->identifier = id;
//	// static Operations operations;
//
//	if(dObjects[id]->bench_initialized == FALSE) {
//		// self->bench_enabled = TRUE;
//		dObjects[id]->bench_initialized = TRUE;
//		dObjects[id]->op_add = dObjects[id]->op_sub = dObjects[id]->op_mult = 0;
//		dObjects[id]->op_div = dObjects[id]->op_exp = dObjects[id]->op_pair = 0;
//		dObjects[id]->aux_time_ms = dObjects[id]->real_time_ms = 0.0;
//		debug("Initialized benchmark object.\n");
//		debug("dObject[%d] with %p which points to: %p\n", dObjects[id]->identifier, &(dObjects[id]), dObjects[id]);
//		return Py_BuildValue("i", dObjects[id]->identifier);
//	}
//
//	PyErr_SetString(BenchmarkError, "failed to create benchmark object.");
//	return NULL;
//}
//
///*
// * Description: finds the benchmark object and only sets vars if not initialized, but allocated.
// * 1) get options and set
// */
//static PyObject *_start_benchmark(Element *self, PyObject *args) {
//	Benchmark *bObject = NULL;
//	PyObject *list = NULL;
//	int id = -1;
//
//	// check whether self is a valid ptr?
//	if(PyArg_ParseTuple(args, "iO", &id, &list)) {
//		if(id >= 0 && id < MAX_BENCH_OBJECTS) {
//			if(dObjects[id] != NULL && dObjects[id]->identifier == id) {
//				bObject = dObjects[id];
//
//				if(bObject->bench_initialized) {
//					size_t size = PyList_Size(list);
//					debug("list size => %d\n", size);
//					size_t result = PyStartBenchmark(bObject, list, size);
//					activeObject = bObject;
//					debug("data now points to: %p =?= %p\n", activeObject, bObject);
//					debug("benchmark enabled and initialized!!!\n");
//					return Py_BuildValue("i", result);
//				}
//			}
//		}
//		else {
//			PyErr_SetString(BenchmarkError, "invalid benchmark object.\n");
//			return NULL;
//		}
//	}
//	return NULL;
//}
//
//static PyObject *_end_benchmark(Element *self, PyObject *args) {
//	int errcode = FALSE;
//	if(activeObject != NULL) {
//		int id;
//		if(PyArg_ParseTuple(args, "i", &id)) {
//			if(id >= 0 && id < MAX_BENCH_OBJECTS) {
//				if(dObjects[id] != NULL && dObjects[id]->identifier == id) {
//					// bObject = dObjects[id];
//					PyEndBenchmark(dObjects[id]);
//					errcode = TRUE;
//					dObjects[id]->bench_initialized = FALSE;
//					debug("data now points to: %p =?= %p\n", activeObject, dObjects[id]);
//					activeObject = NULL;
//					return Py_BuildValue("i", errcode);
//				}
//			}
//		}
//	}
//	PyErr_SetString(BenchmarkError, "benchmarking not enabled.");
//	return Py_BuildValue("i", errcode);
//}

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

InitBenchmark_CAPI(_init_benchmark, dBench, 1)
StartBenchmark_CAPI(_start_benchmark, dBench)
EndBenchmark_CAPI(_end_benchmark, dBench)
GetBenchmark_CAPI(_get_benchmark, dBench)

// new
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
	0,                         /*tp_hash */
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
	{"params", T_STRING, offsetof(Element, params), 0,
		"pairing type"},
	{"type", T_INT, offsetof(Element, element_type), 0,
		"group type"},
//    {"first", T_OBJECT_EX, offsetof(Element, first), 0,
//		"first name"},
//    {"last", T_OBJECT_EX, offsetof(Element, last), 0,
//		"last name"},
    {"initialized", T_INT, offsetof(Element, elem_initialized), 0,
		"determine initialization status"},
    {NULL}  /* Sentinel */
};

PyMethodDef Element_methods[] = {
	// benchmark methods
	{"init", (PyCFunction)Element_elem, METH_VARARGS, "Create an element in a specific group: G1, G2, GT or Zr"},
	{"random", (PyCFunction)Element_random, METH_VARARGS, "Return a random element in a specific group: G1, G2, Zr"},
	{"set", (PyCFunction)Element_set, METH_VARARGS, "Set an element to a fixed value."},
	{"H", (PyCFunction)Element_hash, METH_VARARGS, "Hash an element type to a specific field: Zr, G1, or G2"},
	{"serialize", (PyCFunction)Serialize_cmp, METH_VARARGS, "Serialize an element type into bytes."},
	{"deserialize", (PyCFunction)Deserialize_cmp, METH_VARARGS, "De-serialize an bytes object into an element object"},
    {NULL}  /* Sentinel */
};

PyMethodDef pairing_methods[] = {
	{"pair", (PyCFunction)Apply_pairing, METH_VARARGS, "Apply pairing between an element of G1 and G2 and returns an element mapped to GT"},
	{"hash", (PyCFunction)sha1_hash, METH_VARARGS, "Compute a sha1 hash of an element type"},
	{"InitBenchmark", (PyCFunction)_init_benchmark, METH_NOARGS, "Initialize a benchmark object"},
	{"StartBenchmark", (PyCFunction)_start_benchmark, METH_VARARGS, "Start a new benchmark with some options"},
	{"EndBenchmark", (PyCFunction)_end_benchmark, METH_VARARGS, "End a given benchmark"},
	{"GetBenchmark", (PyCFunction)_get_benchmark, METH_VARARGS, "Returns contents of a benchmark object"},
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

static struct PyModuleDef moduledef = {
		PyModuleDef_HEAD_INIT,
		"pairing",
		NULL,
		sizeof(struct module_state),
		pairing_methods,
		NULL,
		pairings_traverse,
		pairings_clear,
		NULL
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

    Py_INCREF(&PairingType);
    PyModule_AddObject(m, "params", (PyObject *)&PairingType);
    Py_INCREF(&ElementType);
    PyModule_AddObject(m, "pairing", (PyObject *)&ElementType);

	PyModule_AddIntConstant(m, "ZR", ZR);
	PyModule_AddIntConstant(m, "G1", G1);
	PyModule_AddIntConstant(m, "G2", G2);
	PyModule_AddIntConstant(m, "GT", GT);

	PyModule_AddIntConstant(m, "CpuTime", CPU_TIME);
	PyModule_AddIntConstant(m, "RealTime", REAL_TIME);
	PyModule_AddIntConstant(m, "NativeTime", NATIVE_TIME);
	PyModule_AddIntConstant(m, "Add", ADDITION);
	PyModule_AddIntConstant(m, "Sub", SUBTRACTION);
	PyModule_AddIntConstant(m, "Mul", MULTIPLICATION);
	PyModule_AddIntConstant(m, "Div", DIVISION);
	PyModule_AddIntConstant(m, "Exp", EXPONENTIATION);
	PyModule_AddIntConstant(m, "Pair", PAIRINGS);
#if PY_MAJOR_VERSION >= 3
	return m;
#endif
}
