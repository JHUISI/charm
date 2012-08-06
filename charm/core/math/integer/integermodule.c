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
 *   @file    integermodule.c
 *
 *   @brief   charm interface over GMP multi-precision integers
 *
 *   @author  ayo.akinyele@charm-crypto.com
 *
 ************************************************************************/

#include "integermodule.h"

#define CAST_TO_LONG(obj, lng) 	\
	if(PyInt_Check(obj)) { 			\
		lng = PyInt_AS_LONG(obj); }	\
	else {							\
	  Py_INCREF(Py_NotImplemented);	\
	  return Py_NotImplemented; }	\


inline size_t size(mpz_t n) {
	return mpz_sizeinbase(n, 2);
}

void longObjToMPZ(mpz_t m, PyObject * o) {
	PyLongObject *p = (PyLongObject *) PyNumber_Long(o);
	int size, i, tmp = Py_SIZE(p);
	mpz_t temp, temp2;
	mpz_init(temp);
	mpz_init(temp2);
	if (tmp > 0)
		size = tmp;
	else
		size = -tmp;
	mpz_set_ui(m, 0);
	for (i = 0; i < size; i++) {
		mpz_set_ui(temp, p->ob_digit[i]);
		mpz_mul_2exp(temp2, temp, PyLong_SHIFT * i);
		mpz_add(m, m, temp2);
	}
	mpz_clear(temp);
	mpz_clear(temp2);
	Py_XDECREF(p);
}

//void longObjToBN(BIGNUM *m, PyObject *o) {
//	PyLongObject *p = (PyLongObject *) PyNumber_Long(o);
//	int size, i, tmp = Py_SIZE(p);
//	BIGNUM *temp = BN_new(), *temp2 = BN_new();
//	BN_init(temp);
//	BN_init(temp2);
//	if (tmp > 0)
//		size = tmp;
//	else
//		size = -tmp;
//	BN_zero(m, 0);
//	for (i = 0; i < size; i++) {
//		BN_set_word(temp, p->ob_digit[i]);
//		mpz_mul_2exp(temp2, temp, PyLong_SHIFT * i);
//		mpz_add(m, m, temp2);
//	}
//	mpz_clear(temp);
//	mpz_clear(temp2);
//}

PyObject *bnToLongObj(BIGNUM *m) {
	PyLongObject *v = NULL;
	BN_ULONG t;
	int bits = BN_num_bits(m), i = 0;
	int ndigits = (bits + PyLong_SHIFT - 1) / PyLong_SHIFT;
	int digitsleft = ndigits;
	int bitsleft = bits;

	v = _PyLong_New(ndigits);
	if (v != NULL) {
		digit *p = v->ob_digit;
		for(i = 0; i < m->dmax; i++) {
			t = m->d[i];
			*p++ = (digit)(t & PyLong_MASK);
			i++;
			digitsleft--;
			bitsleft -= PyLong_SHIFT;
		}
	}

	return (PyObject *) v;
}

int bnToMPZ(BIGNUM *p, mpz_t m) {
	int size;
	if (!BN_is_negative(p))
		size = p->top;
	else
		size = -(p->top);

	if(BN_BITS2 == GMP_NUMB_BITS) {
		// expand the mpz_t type
		if(!_mpz_realloc(m, size))
			return FALSE;
		memcpy(&m->_mp_d[0], &p->d[0], size * sizeof(p->d[0]));
		m->_mp_size = size;
	}

	return TRUE;
}

// generate a BN from an mpz_t type
int mpzToBN(mpz_t m, BIGNUM *b) {
	int size = (m->_mp_size >= 0) ? m->_mp_size : -m->_mp_size;

	// make sure mpz will fit into BN
	if(BN_BITS2 == GMP_NUMB_BITS) {
		BN_zero(b);
		if(bn_expand2(b, size) == NULL)
			return FALSE;
		b->top = size;
		memcpy(&b->d[0], &m->_mp_d[0], size * sizeof(b->d[0]));
		bn_correct_top(b);
	}

	debug("Original input m => ");
	print_mpz(m, 10);
	debug("GMP num bits => '%i'\n", GMP_NUMB_BITS);
	debug("BN num bits => '%i'\n", BN_BITS2);
	return TRUE;
}

PyObject *mpzToLongObj(mpz_t m) {
	/* borrowed from gmpy */
	int size = (mpz_sizeinbase(m, 2) + PyLong_SHIFT - 1) / PyLong_SHIFT;
	int i;
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
	Py_SIZE( l) = i;
	mpz_clear(temp);
	return (PyObject *) l;
}

void print_mpz(mpz_t x, int base) {
#ifdef DEBUG
	if(base <= 2 || base > 64) return;
	size_t x_size = mpz_sizeinbase(x, base) + 2;
	char *x_str = (char *) malloc(x_size);
	x_str = mpz_get_str(x_str, base, x);
	debug("Element => '%s'\n", x_str);
	debug("Order of Element => '%zd'\n", x_size);
	free(x_str);
#endif
}

void print_bn_dec(const BIGNUM *bn) {
#ifdef DEBUG
	printf("BIGNUM *bn => ");
	char *pstr = BN_bn2dec(bn);
	printf("%s\n", pstr);
	OPENSSL_free(pstr);
#endif
}

void printf_buffer_as_hex(uint8_t *data, size_t len) {
#ifdef DEBUG
	size_t i;

	for (i = 0; i < len; i++) {
		printf("%02x ", data[i]);
	}
	printf("\n");
#endif
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
int hash_to_bytes(uint8_t *input_buf, int input_len, int hash_size,
		uint8_t *output_buf, uint32_t hash_num) {
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

		SHA1Input(&sha_context, (uint8_t *) &(block_hdr[0]), sizeof(block_hdr));
		SHA1Input(&sha_context, (uint8_t *) input_buf, input_len);

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

int hash_to_group_element(mpz_t x, int block_num, uint8_t *output_buf) {

	size_t count = 0;
	uint8_t *rop_buf = (uint8_t *) mpz_export(NULL, &count, 1, sizeof(char), 0,
			0, x);

	debug("rop_buf...\n");
	printf_buffer_as_hex(rop_buf, count);
	// create another buffer with block_num and rop_buf as input. Maybe use snprintf?
	if (block_num > 0) {
		int len = count + sizeof(uint32_t);
		uint8_t *tmp_buf = (uint8_t *) malloc(len + 1);
		memset(tmp_buf, 0, len);
		// sprintf(tmp_buf, "%d%s", block_num, (char *) rop_buf);
		uint32_t block_str = (uint32_t) block_num;
		*((uint32_t*) tmp_buf) = block_str;
		strncat((char *) (tmp_buf + sizeof(uint32_t)), (const char *) rop_buf,
				count);

		debug("tmp_buf after strcat...\n");
		printf_buffer_as_hex(tmp_buf, len);

		hash_to_bytes(tmp_buf, len, HASH_LEN, output_buf,
				HASH_FUNCTION_KEM_DERIVE);
		free(tmp_buf);
	} else {
		hash_to_bytes(rop_buf, (int) count, HASH_LEN, output_buf,
				HASH_FUNCTION_KEM_DERIVE);
	}

	return TRUE;
}

void _reduce(Integer *object) {
	if (object != NULL)
		mpz_mod(object->e, object->e, object->m);
}

void Integer_dealloc(Integer* self) {
	/* clear structure */
	mpz_clear(self->m);
	mpz_clear(self->e);
	Py_TYPE(self)->tp_free((PyObject*) self);
}

PyObject *Integer_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
	Integer *self;

	self = (Integer *) type->tp_alloc(type, 0);
	if (self != NULL) {
		/* initialize fields here */
		mpz_init(self->e);
		mpz_init(self->m);
		self->initialized = TRUE;
	}
	return (PyObject *) self;
}

int Integer_init(Integer *self, PyObject *args, PyObject *kwds) {
	PyObject *num = NULL, *mod = NULL;
	static char *kwlist[] = { "number", "modulus", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|O", kwlist, &num, &mod)) {
		return -1;
	}

	// check if they are of type long
	if(PyInteger_Check(num)) {
		Integer *num1 = (Integer *) num;
		mpz_set(self->e, num1->e);
		if(mod != NULL)  {
			if(PyInteger_Check(mod)) {
				Integer *mod1 = (Integer *) mod;
				mpz_set(self->m, mod1->e);
			}
			else if(_PyLong_Check(mod)) longObjToMPZ(self->m, mod);
			else {
				PyErr_SetString(IntegerError, "invalid type for modulus");
				return -1;
			}
		}
	}
	else if(_PyLong_Check(num)) {
		longObjToMPZ(self->e, num);
	}
	// raise error
	else if (PyBytes_Check(num)) {
		// convert directly to a char string of bytes
		char *bytes = PyBytes_AS_STRING(num);
		int bytes_len = strlen(bytes);
		mpz_import(self->e, bytes_len, 1, sizeof(bytes[0]), 0, 0, bytes);
	} else if (PyUnicode_Check(num)) {
		// cast to a bytes object, then interpret as a string of bytes
		const char *bytes = PyBytes_AS_STRING(PyUnicode_AsUTF8String(num));
		int bytes_len = strlen(bytes);
		mpz_import(self->e, bytes_len, 1, sizeof(bytes[0]), 0, 0, bytes);
	} else {
		return -1;
	}

	if (mod != NULL) {
		if (_PyLong_Check(mod)) {
			longObjToMPZ(self->m, mod);
		}
	}
	// else leave self->m set to 0.

	return 0;
}

static PyObject *Integer_equals(PyObject *o1, PyObject *o2, int opid) {
	Integer *lhs = NULL, *rhs = NULL;
	int foundLHS = FALSE, foundRHS = FALSE, result = -1;
	unsigned long int lhs_value = 0, rhs_value = 0;

	if(opid != Py_EQ && opid != Py_NE) {
		ErrorMsg("only comparison supported is '==' or '!='");
		return NULL;
	}

	Check_Types(o1, o2, lhs, rhs, foundLHS, foundRHS, lhs_value, rhs_value);
	mpz_t l, r;
	if (foundLHS) {
		debug("foundLHS\n");
		if (mpz_sgn(rhs->m) == 0) {
			result = mpz_cmp_ui(rhs->e, lhs_value);
		} else {
			mpz_init(r);
			mpz_mod(r, rhs->e, rhs->m);
			result = mpz_cmp_ui(r, lhs_value);
			mpz_clear(r);
		}
	} else if (foundRHS) {
		debug("foundRHS!\n");

		if (mpz_sgn(lhs->m) == 0) {
			result = mpz_cmp_ui(lhs->e, rhs_value);
		} else {
			mpz_init(l);
			mpz_mod(l, lhs->e, lhs->m);
			result = mpz_cmp_ui(l, rhs_value);
			mpz_clear(l);
		}
	} else {
		if (lhs->initialized && rhs->initialized) {
			debug("Modulus equal? %d =?= 0\n", mpz_cmp(lhs->m, rhs->m));
			if (mpz_sgn(lhs->m) == 0 && mpz_sgn(rhs->m) == 0) {
				result = mpz_cmp(lhs->e, rhs->e);
			} else if (mpz_cmp(lhs->m, rhs->m) == 0) {
				mpz_init(l);
				mpz_init(r);
				mpz_mod(l, lhs->e, lhs->m);
				mpz_mod(r, rhs->e, rhs->m);
				result = mpz_cmp(l, r);
				mpz_clear(l);
				mpz_clear(r);
			} else {
				ErrorMsg("cannot compare integers with different modulus.");
			}
		}
	}

	if(opid == Py_EQ) {
		if(result == 0) {
			Py_INCREF(Py_True); return Py_True;
		}
		Py_INCREF(Py_False); return Py_False;
	}
	else { /* Py_NE */
		if(result != 0) {
			Py_INCREF(Py_True); return Py_True;
		}
		Py_INCREF(Py_False); return Py_False;
	}
}

PyObject *Integer_print(Integer *self) {
	PyObject *strObject = NULL;
	if (self->initialized) {
		size_t e_size = mpz_sizeinbase(self->e, 10) + 2;
		char *e_str = (char *) malloc(e_size);
		mpz_get_str(e_str, 10, self->e);

		if (mpz_sgn(self->m) != 0) {
			size_t m_size = mpz_sizeinbase(self->m, 10) + 2;
			char *m_str = (char *) malloc(m_size);
			mpz_get_str(m_str, 10, self->m);
			strObject = PyUnicode_FromFormat("%s mod %s", (const char *) e_str,
					(const char *) m_str);
			free(m_str);
		} else {
			strObject = PyUnicode_FromFormat("%s", (const char *) e_str);
		}
		free(e_str);
		return strObject;
	}
//
//	if (self->state_init) {
//		return PyUnicode_FromString("");
//	}

	PyErr_SetString(IntegerError, "invalid integer object.");
	return NULL;
}

Integer *createNewInteger(mpz_t m) {
	Integer *newObject = PyObject_New(Integer, &IntegerType);

	//mpz_init(newObject->e);
	//mpz_init_set(newObject->m, m);
	newObject->initialized = TRUE;

	return newObject;
}

Integer *createNewIntegerNoMod(void) {
	Integer *newObject = PyObject_New(Integer, &IntegerType);

	//mpz_init(newObject->e);
	//mpz_init(newObject->m);
	newObject->initialized = TRUE;

	return newObject;
}

static PyObject *Integer_set(Integer *self, PyObject *args) {
	PyObject *obj = NULL;
	Integer *intObj = NULL;

	if (PyArg_ParseTuple(args, "O", &obj)) {

		if (PyInteger_Check(obj)) {
			intObj = (Integer *) obj;
			self->initialized = TRUE;
			mpz_set(self->e, intObj->e);
			mpz_set(self->m, intObj->m);
			return Py_BuildValue("i", TRUE);
		}
	}

	return Py_BuildValue("i", FALSE);
}

static PyObject *Integer_add(PyObject *o1, PyObject *o2) {
	// determine type of each side
	Integer *lhs = NULL, *rhs = NULL, *rop = NULL;
	int foundLHS = FALSE, foundRHS = FALSE;
	unsigned long int lhs_value = 0, rhs_value = 0;

	Check_Types(o1, o2, lhs, rhs, foundLHS, foundRHS, lhs_value, rhs_value);
	// perform operation
	if (foundLHS) {
		// debug("foundLHS\n");
		rop = createNewInteger(rhs->m);
		mpz_init(rop->e);
		mpz_init_set(rop->m, rhs->m);
		mpz_add_ui(rop->e, rhs->e, lhs_value);
	} else if (foundRHS) {
		// debug("foundRHS!\n");
		rop = createNewInteger(lhs->m);
		mpz_init(rop->e);
		mpz_init_set(rop->m, lhs->m);
		mpz_add_ui(rop->e, lhs->e, rhs_value);
	} else {
		if (lhs->initialized && rhs->initialized) {
			debug("Modulus equal? %d =?= 0\n", mpz_cmp(lhs->m, rhs->m));
			if (mpz_cmp(lhs->m, rhs->m) == 0) {
				rop = createNewInteger(lhs->m);
				mpz_init(rop->e);
				mpz_init_set(rop->m, lhs->m);
				mpz_add(rop->e, lhs->e, rhs->e);
			} else {
				EXIT_IF(TRUE, "cannot add integers with different modulus.");
			}
		}
	}

	UPDATE_BENCHMARK(ADDITION, dBench);
	return (PyObject *) rop;
}

static PyObject *Integer_sub(PyObject *o1, PyObject *o2) {
	// determine type of each side
	Integer *lhs = NULL, *rhs = NULL, *rop = NULL;
	int foundLHS = FALSE, foundRHS = FALSE;
	unsigned long int lhs_value = 0, rhs_value = 0;

	Check_Types(o1, o2, lhs, rhs, foundLHS, foundRHS, lhs_value, rhs_value);
	// perform operation
	if (foundLHS) {
		// debug("foundLHS\n");
		rop = createNewInteger(rhs->m);
		mpz_init(rop->e);
		mpz_init_set(rop->m, rhs->m);
		mpz_ui_sub(rop->e, lhs_value, rhs->e);
	} else if (foundRHS) {
		// debug("foundRHS!\n");
		rop = createNewInteger(lhs->m);
		mpz_init(rop->e);
		mpz_init_set(rop->m, lhs->m);
		mpz_sub_ui(rop->e, lhs->e, rhs_value);
	} else {
		if (lhs->initialized && rhs->initialized) {
			debug("Modulus equal? %d =?= 0\n", mpz_cmp(lhs->m, rhs->m));
			if (mpz_cmp(lhs->m, rhs->m) == 0) {
				rop = createNewInteger(lhs->m);
				mpz_init(rop->e);
				mpz_init_set(rop->m, lhs->m);
				mpz_sub(rop->e, lhs->e, rhs->e);
			} else {
				EXIT_IF(TRUE,"cannot subtract integers with different modulus.");
			}
		}
	}

	UPDATE_BENCHMARK(SUBTRACTION, dBench);
	return (PyObject *) rop;
}

static PyObject *Integer_mul(PyObject *o1, PyObject *o2) {
	// determine type of each side
	Integer *lhs = NULL, *rhs = NULL, *rop = NULL;
	int foundLHS = FALSE, foundRHS = FALSE;
	unsigned long int lhs_value = 0, rhs_value = 0;

	Check_Types(o1, o2, lhs, rhs, foundLHS, foundRHS, lhs_value, rhs_value);
	// perform operation
	if (foundLHS) {
		// debug("foundLHS\n");
		rop = createNewInteger(rhs->m);
		mpz_init(rop->e);
		mpz_init_set(rop->m, rhs->m);
		mpz_mul_ui(rop->e, rhs->e, lhs_value);
	} else if (foundRHS) {
		// debug("foundRHS!\n");
		rop = createNewInteger(lhs->m);
		mpz_init(rop->e);
		mpz_init_set(rop->m, lhs->m);
		mpz_mul_ui(rop->e, lhs->e, rhs_value);
	} else {
		if (lhs->initialized && rhs->initialized) {
			debug("Modulus equal? %d =?= 0\n", mpz_cmp(lhs->m, rhs->m));
			if (mpz_cmp(lhs->m, rhs->m) == 0) {
				rop = createNewInteger(lhs->m);
				mpz_init(rop->e);
				mpz_init_set(rop->m, lhs->m);
				mpz_mul(rop->e, lhs->e, rhs->e);
			} else {
				EXIT_IF(TRUE, "cannot multiply integers with different modulus.");
			}
		}
	}

	UPDATE_BENCHMARK(MULTIPLICATION, dBench);
	return (PyObject *) rop;
}

static PyObject *Integer_invert(PyObject *o1) {
	Integer *base = NULL, *rop = NULL;
	if (PyInteger_Check(o1)) {
		// let's try to compute inverse
		base = (Integer *) o1;
		if (base->initialized) {
			rop = createNewInteger(base->m);
			mpz_init(rop->e);
			mpz_init_set(rop->m, base->m);
			int errcode = mpz_invert(rop->e, base->e, base->m);
			if (errcode > 0) {
				return (PyObject *) rop;
			}
			EXIT_IF(TRUE, "could not find a modular inverse");
		}
	}
	EXIT_IF(TRUE, "not an integer object type.");
}

static PyObject *Integer_long(PyObject *o1) {
	if (PyInteger_Check(o1)) {
		Integer *value = (Integer *) o1;
		if (mpz_sgn(value->m) != 0)
			_reduce(value);
		return mpzToLongObj(value->e);
	}

	EXIT_IF(TRUE, "invalid object type.");
}

/** a / b mod N ...
 *  only defined when b is invertible modulo N, meaning a*b mod N = c*b mod N iff b has b^-1 s.t.
 *  b*b^-1 = 1 mod N. NOT IMPLEMENTED CORRECTLY! TODO: redo
 */
static PyObject *Integer_div(PyObject *o1, PyObject *o2) {
	Integer *lhs = NULL, *rhs = NULL, *rop = NULL;
	int foundLHS = FALSE, foundRHS = FALSE;
	unsigned long int lhs_value = 0, rhs_value = 0;

	Check_Types(o1, o2, lhs, rhs, foundLHS, foundRHS, lhs_value, rhs_value);

	//	printf("does this really work?!?\n");
	if (foundRHS && rhs_value > 0) {
		//		printf("foundRHS + rhs_value > 0.");
		if (mpz_divisible_ui_p(lhs->e, rhs_value) != 0) {
			if (mpz_sgn(lhs->m) == 0) {
				rop = createNewInteger(lhs->m);
				mpz_init(rop->e);
				mpz_init_set(rop->m, lhs->m);
				mpz_divexact_ui(rop->e, lhs->e, rhs_value);
			}
		} else {
			rop = createNewInteger(lhs->m);
			mpz_init(rop->e);
			mpz_init_set(rop->m, lhs->m);
			mpz_tdiv_q_ui(rop->e, lhs->e, rhs_value);
		}
	} else if (foundLHS && lhs_value > 0) {
		//		printf("foundLHS + lhs_value > 0.");
		mpz_t tmp;
		mpz_init_set_ui(tmp, lhs_value);
		if (mpz_divisible_p(tmp, rhs->e) != 0 && mpz_sgn(rhs->m) == 0) {
			rop = createNewInteger(rhs->m);
			mpz_init(rop->e);
			mpz_init_set(rop->m, rhs->m);
			mpz_divexact(rop->e, tmp, rhs->e);
		}
		mpz_clear(tmp);
	} else {
		//		printf("lhs and rhs init? => ");
		if (lhs->initialized && rhs->initialized) {
			if (mpz_cmp(lhs->m, rhs->m) == 0 && mpz_sgn(lhs->m) > 0) {
				mpz_t rhs_inv;
				mpz_init(rhs_inv);
				mpz_invert(rhs_inv, rhs->e, rhs->m);
				debug("rhs_inv...\n");
				print_mpz(rhs_inv, 10);

				rop = createNewInteger(lhs->m);
				mpz_init(rop->e);
				mpz_init_set(rop->m, lhs->m);
				mpz_mul(rop->e, lhs->e, rhs_inv);
				mpz_mod(rop->e, rop->e, rop->m);
				mpz_clear(rhs_inv);
			} else if (mpz_cmp(lhs->m, rhs->m) == 0 && mpz_sgn(lhs->m) == 0) {
				rop = createNewInteger(lhs->m);
				mpz_init(rop->e);
				mpz_init_set(rop->m, lhs->m);
				mpz_div(rop->e, lhs->e, rhs->e);
			}
		}
	}

	if (mpz_sgn(rop->e) == 0) {
		//PyObject_Del(rop);
		Py_XDECREF(rop);
		EXIT_IF(TRUE, "division failed: could not find modular inverse.");
	}

	UPDATE_BENCHMARK(DIVISION, dBench);
	return (PyObject *) rop;
}

static PyObject *Integer_pow(PyObject *o1, PyObject *o2, PyObject *o3) {
	Integer *lhs = NULL, *rhs = NULL, *rop = NULL;
	int foundLHS = FALSE, foundRHS = FALSE;

	Check_Types2(o1, o2, lhs, rhs, foundLHS, foundRHS);

	// TODO: handle foundLHS (e.g. 2 ** <int.Elem>)
	if (foundRHS) {
		debug("foundRHS!\n");
		long rhs = PyLong_AsLong(o2);
		if(PyErr_Occurred() || rhs >= 0) {
			//PyErr_Print(); // for debug purposes
			PyErr_Clear();
			debug("exponent is positive\n");
			int sgn = mpz_sgn(lhs->m);
			if(sgn > 0)  {
				if(mpz_odd_p(lhs->m) > 0) {
					mpz_t exp;
 					mpz_init(exp);
					longObjToMPZ(exp, o2);
					print_mpz(exp, 10);
					rop = createNewInteger(lhs->m);
					mpz_init(rop->e);
					mpz_init_set(rop->m, lhs->m);
					mpz_powm_sec(rop->e, lhs->e, exp, rop->m);
					mpz_clear(exp);
				 }
			}
			else if(sgn == 0) { // no modulus
				unsigned long int exp = PyLong_AsUnsignedLong(o2);
				EXIT_IF(PyErr_Occurred(), "integer too large to exponentiate without modulus.");
				rop = createNewInteger(lhs->m);
				mpz_init(rop->e);
				mpz_init_set(rop->m, lhs->m);
				mpz_pow_ui(rop->e, lhs->e, exp);
			}
			else {
				EXIT_IF(TRUE, "cannot exponentiate integers without modulus.");
			}
		}
		else if(rhs == -1) {
			debug("find modular inverse.\n");
			PyObject *obj = Integer_invert((PyObject *) lhs);
			if(obj == NULL) return NULL;
			rop = (Integer *) obj;
		}
	} else if (foundLHS) {
		// find modular inverse
		//		debug("find modular inverse?\n");
		//		PyObject *obj = Integer_invert((PyObject *) lhs);
		//		if(obj == NULL) {
		//			return NULL;
		//		}
		//		rop = (Integer *) obj;
		ErrorMsg("left operand should be a charm.integer type.");
	} else {
		if (lhs->initialized && rhs->initialized) {
			// result takes modulus of base
			debug("both integer objects: ");
			if (mpz_sgn(lhs->m) > 0) {
				rop = createNewInteger(lhs->m);
				mpz_init(rop->e);
				mpz_init_set(rop->m, lhs->m);
				mpz_powm_sec(rop->e, lhs->e, rhs->e, rop->m);
			}
			// lhs is a reg int
			else if (mpz_fits_ulong_p(lhs->e) && mpz_fits_ulong_p(rhs->e)) {
				// convert base (lhs) to an unsigned long (if possible)
				unsigned long int base = mpz_get_ui(lhs->e);
				unsigned long int exp = mpz_get_ui(rhs->e);
				rop = createNewIntegerNoMod();
				mpz_init(rop->e);
				mpz_init(rop->m);
				mpz_ui_pow_ui(rop->e, base, exp);
			}
			// lhs reg int and rhs can be represented as ulong
			else if (mpz_fits_ulong_p(rhs->e)) {
				unsigned long int exp = mpz_get_ui(rhs->e);
				rop = createNewIntegerNoMod();
				mpz_init(rop->e);
				mpz_init(rop->m);
				mpz_pow_ui(rop->e, lhs->e, exp);
			} else { // last option...
				// cannot represent reg ints as ulong's, so error out.
				EXIT_IF(TRUE, "could not exponentiate integers.");
			}
		}
	}
		
	UPDATE_BENCHMARK(EXPONENTIATION, dBench);
	return (PyObject *) rop;
}

/*
 * Description: hash elements into a group element
 * inputs: group elements, p, q, and True or False (return value mod p when TRUE and value mod q when FALSE)
 */
static PyObject *Integer_hash(PyObject *self, PyObject *args) {
	PyObject *object, *order, *order2;
	Integer *pObj, *qObj;
	uint8_t *rop_buf = NULL;
	mpz_t p, q, v, tmp;
	mpz_init(p);
	mpz_init(q);
	mpz_init(v);
	mpz_init(tmp);
	int modP = FALSE;

	if (PyArg_ParseTuple(args, "OOO|i", &object, &order, &order2, &modP)) {
		// one single integer group element
		if (PyInteger_Check(order) && PyInteger_Check(order2)) {
			pObj = (Integer *) order;
			qObj = (Integer *) order2;
			mpz_set(p, pObj->e);
			mpz_set(q, qObj->e);
			mpz_mul_ui(tmp, q, 2);
			mpz_add_ui(tmp, tmp, 1);

			if (mpz_cmp(tmp, p) != 0) {
				PyErr_SetString(IntegerError,
						"can only encode messages into groups where p = 2*q+1.");
				goto cleanup;
			}
		} else {
			PyErr_SetString(IntegerError,
					"failed to specify large primes p and q.");
			goto cleanup;
		}

		int i, object_size = PySequence_Length(object);

		// dealing with a tuple element here...
		if (object_size > 0) {

			int o_size = 0;
			// get length of all objects
			for (i = 0; i < object_size; i++) {
				PyObject *tmpObject = PySequence_GetItem(object, i);
				if (PyInteger_Check(tmpObject)) {
					Integer *object1 = (Integer *) tmpObject;
					if (object1->initialized) {
						o_size += size(object1->e);
					}
				}
				Py_XDECREF(tmpObject);
			}

			/* allocate space big enough to hold exported objects */
			rop_buf = (uint8_t *) malloc(o_size + 1);
			memset(rop_buf, 0, o_size);
			int cur_ptr = 0;
			/* export objects here using mpz_export into allocated buffer */
			for (i = 0; i < object_size; i++) {
				PyObject *tmpObject = PySequence_GetItem(object, i);

				if (PyInteger_Check(tmpObject)) {
					Integer *tmpObject2 = (Integer *) tmpObject;
					if (tmpObject2->initialized) {
						uint8_t *target_ptr = (uint8_t *) (rop_buf + cur_ptr);
						size_t len = 0;
						mpz_export(target_ptr, &len, 1, sizeof(char), 0, 0,
								tmpObject2->e);
						cur_ptr += size(tmpObject2->e);
					}
				}
				Py_XDECREF(tmpObject);
			}

			// hash the buffer
			uint8_t hash_buf2[HASH_LEN + 1];
			hash_to_bytes(rop_buf, o_size, HASH_LEN, hash_buf2,
					HASH_FUNCTION_KEM_DERIVE);
			free(rop_buf);

			// mpz_import hash to a element from 1 to q-1 inclusive.
			mpz_import(tmp, HASH_LEN, 1, sizeof(hash_buf2[0]), 0, 0, hash_buf2);
			// now hash to match desired output size of q.
			if (modP)
				mpz_mod(tmp, tmp, p);
			else
				mpz_mod(tmp, tmp, q);
			debug("print group tuple...\n");
			print_mpz(tmp, 2);

			// calculate ceiling |q|/160 => blocks
			int i, blocks = ceil((double) size(q) / (HASH_LEN * 8));
			debug("blocks => '%d'\n", blocks);
			size_t out_len = HASH_LEN * blocks;
			uint8_t out_buf[(out_len * 2) + 1];
			memset(out_buf, 0, out_len*2);

			if (blocks > 1) {
				for (i = 1; i <= blocks; i++) {
					// how to add num in front of tmp_buf?
					// compute sha1( i || tmp_buf ) ->
					uint8_t *ptr = (uint8_t *) &out_buf[HASH_LEN * i];
					debug("pointer to block => '%p\n", ptr);
					// doesn't work like this yet
					hash_to_group_element(tmp, i, ptr);
				}
			} else {
				debug("Only 1 block to hash.\n");
				hash_to_group_element(tmp, -1, out_buf);
			}

			debug("print out_len => '%zd'\n", out_len);
			debug("print out_buf...\n");
			printf_buffer_as_hex(out_buf, out_len);
			// convert v' to mpz_t type mod q => v
			mpz_import(v, out_len, 1, sizeof(char), 0, 0, out_buf);
			mpz_t modulus;
			if (modP) {
				// v = v' mod p
				debug("doing mod p\n");
				mpz_mod(v, v, p);
				// y = v^2 mod q
				mpz_powm_ui(v, v, 2, q);
				mpz_init_set(modulus, q);
			} else {
				debug("doing mod q\n");
				mpz_mod(v, v, q);
				// y = v^2 mod p : return y mod p
				mpz_powm_ui(v, v, 2, p);
				mpz_init_set(modulus, p);
			}
			debug("print v => \n");
			print_mpz(v, 10);
			Integer *rop = createNewInteger(modulus);
			mpz_init_set(rop->e, v);
			mpz_init_set(rop->m, modulus);
			mpz_clear(p);
			mpz_clear(q);
			mpz_clear(v);
			mpz_clear(tmp);
			mpz_clear(modulus);
			return (PyObject *) rop;
		} else { /* non-tuple element - maybe single element? */
			Integer *obj = (Integer *) object;

			// make sure object was initialized
			if (!obj->initialized) {
				PyErr_SetString(IntegerError, "integer object not initialized.");
				goto cleanup;
			}
			// not a group element
			if (mpz_cmp(p, obj->m) != 0) {
				PyErr_SetString(IntegerError,
						"integer object not a group element.");
				goto cleanup;
			}

			// mpz_export base to a string (ignore modulus) => val
			size_t count = 0;
			rop_buf = (uint8_t *) mpz_export(NULL, &count, 1, sizeof(char), 0,
					0, obj->e);

			// hash the buffer
			uint8_t hash_buf[HASH_LEN + 1];
			hash_to_bytes(rop_buf, (int) count, HASH_LEN, hash_buf,
					HASH_FUNCTION_KEM_DERIVE);

			// mpz_import hash to a element from 1 to q-1 inclusive.
			mpz_import(tmp, HASH_LEN, 1, sizeof(hash_buf[0]), 0, 0, hash_buf);
			// now hash to match desired output size of q.
			if (modP)
				mpz_mod(tmp, tmp, p);
			else
				mpz_mod(tmp, tmp, q);
			print_mpz(tmp, 2);

			// calculate ceiling |q|/160 => blocks
			int i, blocks = ceil((double) size(q) / (HASH_LEN * 8));
			debug("blocks => '%d'\n", blocks);
			size_t out_len = HASH_LEN * blocks;
			uint8_t out_buf[out_len + 4];
			memset(out_buf, 0, out_len);

			for (i = 0; i < blocks; i++) {
				// how to add num in front of tmp_buf?
				// compute sha1( i || tmp_buf ) ->
				uint8_t *ptr = (uint8_t *) &out_buf[HASH_LEN * i];
				debug("pointer to block => '%p\n", ptr);
				// doesn't work like this yet
				hash_to_group_element(tmp, i, ptr);
			}

			// convert v' to mpz_t type mod q => v
			mpz_import(v, out_len, 1, sizeof(out_buf[0]), 0, 0, out_buf);
			mpz_t modulus;
			if (modP) {
				// v = v' mod p
				debug("doing mod p");
				mpz_mod(v, v, p);
				// y = v^2 mod q
				mpz_powm_ui(v, v, 2, q);
				mpz_init_set(modulus, q);
			} else {
				debug("doing mod q");
				mpz_mod(v, v, q);
				// y = v^2 mod p : return y mod p
				mpz_powm_ui(v, v, 2, p);
				mpz_init_set(modulus, p);
			}

			print_mpz(v, 10);
			Integer *rop = createNewInteger(modulus);
			mpz_init_set(rop->e, v);
			mpz_init_set(rop->e, modulus);
			mpz_clear(v);
			mpz_clear(p);
			mpz_clear(q);
			mpz_clear(tmp);
			mpz_clear(modulus);
			return (PyObject *) rop;
		}
		// a tuple of various elements

	}

cleanup:
	mpz_clear(v);
	mpz_clear(p);
	mpz_clear(q);
	mpz_clear(tmp);
	return NULL;

}

static PyObject *Integer_reduce(Integer *self, PyObject *arg) {

	if (!self->initialized) {
		PyErr_SetString(IntegerError, "invalid integer object.");
		Py_INCREF(Py_False);
		return Py_False;
	}

	_reduce(self);
	Py_INCREF(Py_True);
	return Py_True;
}

static PyObject *Integer_remainder(PyObject *o1, PyObject *o2) {

	Integer *lhs = NULL, *rhs = NULL, *rop;
	int foundLHS = FALSE, foundRHS = FALSE;
	// unsigned long int lhs_value, rhs_value;

	Check_Types2(o1, o2, lhs, rhs, foundLHS, foundRHS); // , lhs_value, rhs_value);

	if (foundLHS) {
		rop = createNewInteger(rhs->m);
		mpz_init(rop->e);
		mpz_init_set(rop->m, rhs->m);
		if (_PyLong_Check(o1)) {
			PyObject *tmp = PyNumber_Long(o1);
			mpz_t modulus;
			mpz_init(modulus);
			longObjToMPZ(modulus, tmp);
			mpz_mod(rop->e, rhs->e, modulus);
			mpz_set(rop->m, modulus);
			mpz_clear(modulus);
			Py_XDECREF(tmp);
		} else if (PyInteger_Check(o1)) {
			Integer *tmp_mod = (Integer *) o1;
			// ignore the modulus of tmp_mod
			mpz_mod(rop->e, rhs->e, tmp_mod->e);
			mpz_set(rop->m, tmp_mod->e);
		}
	} else if (foundRHS) {
		rop = createNewInteger(lhs->m);
		mpz_init(rop->e);
		mpz_init_set(rop->m, lhs->m);
		if (_PyLong_Check(o2)) {
			PyObject *tmp = PyNumber_Long(o2);
			mpz_t modulus;
			mpz_init(modulus);
			longObjToMPZ(modulus, tmp);
			mpz_mod(rop->e, lhs->e, modulus);
			mpz_set(rop->m, modulus);
			mpz_clear(modulus);
			Py_XDECREF(tmp);
		}
	} else {
		if (lhs->initialized && rhs->initialized) {
			rop = createNewInteger(rhs->e);
			mpz_init(rop->e);
			mpz_init_set(rop->m, rhs->e);
			mpz_mod(rop->e, lhs->e, rop->m);
		}
	}

	return (PyObject *) rop;
}

/* END: module function definitions */

/* START: helper function definition */
#define MAX_RABIN_MILLER_ROUNDS 255

static PyObject *testPrimality(PyObject *self, PyObject *arg) {
	int result = -1;

	if (arg != NULL) {
		if (_PyLong_Check(arg)) {
			PyObject *obj = PyNumber_Long(arg);
			mpz_t value;
			mpz_init(value);
			longObjToMPZ(value, obj);
			result = mpz_probab_prime_p(value, MAX_RUN);
			mpz_clear(value);
			Py_XDECREF(obj);
		} else if (PyInteger_Check(arg)) {
			Integer *obj = (Integer *) arg;
			if (obj->initialized)
				result = mpz_probab_prime_p(obj->e, MAX_RUN);
		}
	}

	if (result > 0) {
		debug("probably prime: %d\n", result);
		Py_INCREF(Py_True);
		return Py_True;
	} else if (result == 0) {
		debug("not prime.\n");
		Py_INCREF(Py_False);
		return Py_False;
	} else {
		PyErr_SetString(IntegerError, "invalid input.");
		return NULL;
	}
}

static PyObject *genRandomBits(Integer *self, PyObject *args) {
	unsigned int bits;

	if (PyArg_ParseTuple(args, "i", &bits)) {
		if (bits > 0) {
			// generate random number that is in 0 to 2^n-1 range.
			// TODO: fix code very very soon!
			PyLongObject *v;
			unsigned char buff[sizeof(long)];
			long t;
			int ndigits = (bits + PyLong_SHIFT - 1) / PyLong_SHIFT;
			int digitsleft = ndigits;
			int bitsleft = bits;

			v = _PyLong_New(ndigits);
			if (v != NULL) {
				digit *p = v->ob_digit;
				while (digitsleft > 1) {
					RAND_bytes(buff, sizeof(long));
					memcpy(&t, buff, sizeof(long));
					*p++ = (digit)(t & PyLong_MASK);
					digitsleft--;
					bitsleft -= PyLong_SHIFT;
				}

				if (digitsleft == 1) {
					RAND_bytes(buff, sizeof(long));
					memcpy(&t, buff, sizeof(long));
					unsigned long mask = (1 << bitsleft) - 1;
					*p++ = (digit)(t & PyLong_MASK & mask);
				}

			}
			return (PyObject *) v;
		}
	}

	EXIT_IF(TRUE, "number of bits must be > 0.");
}

static PyObject *genRandom(Integer *self, PyObject *args) {
	PyObject *obj = NULL;
	Integer *rop = NULL;
	mpz_t N;

	if (PyArg_ParseTuple(args, "O", &obj)) {

		if (_PyLong_Check(obj)) {
			mpz_init(N);
			longObjToMPZ(N, obj);
		} else if (PyInteger_Check(obj)) {
			Integer *obj1 = (Integer *) obj;
			mpz_init_set(N, obj1->e);
		} else {
			/* error */
			EXIT_IF(TRUE, "invalid object type.");
		}

		BIGNUM *s = BN_new(), *bN = BN_new();
		BN_one(s);
		mpzToBN(N, bN);
		rop = createNewInteger(N);
		mpz_init(rop->e);
		mpz_init_set(rop->m, N);

		BN_rand_range(s, bN);
		bnToMPZ(s, rop->e);
		print_bn_dec(s);
		BN_free(s);
		BN_free(bN);
		mpz_clear(N);
		return (PyObject *) rop;
	}
	EXIT_IF(TRUE, "invalid arguments.");
}

/* takes as input the number of bits and produces a prime number of that size. */
static PyObject *genRandomPrime(Integer *self, PyObject *args) {
	int bits, safe = FALSE;

	if (PyArg_ParseTuple(args, "i|i", &bits, &safe)) {
		if (bits > 0) {
			// mpz_t tmp;
			Integer *rop = createNewIntegerNoMod();
			mpz_init(rop->e);
			mpz_init(rop->m);

			BIGNUM *bn = BN_new();
			/* This routine generates safe prime only when safe=TRUE in which prime, p is selected
			 * iff (p-1)/2 is also prime.
			 */
			if(safe == TRUE) // safe is non-zero
				BN_generate_prime(bn, bits, safe, NULL, NULL, NULL, NULL);
			else
				/* generate strong primes only */
				BN_generate_prime(bn, bits, FALSE, NULL, NULL, NULL, NULL);

			debug("Safe prime => ");
			print_bn_dec(bn);
			bnToMPZ(bn, rop->e);
			BN_free(bn);
			return (PyObject *) rop;
		}
	}

	EXIT_IF(TRUE, "invalid input.");
}

static PyObject *encode_message(PyObject *self, PyObject *args) {
	//char *m; // handle arbitrary messages
	uint8_t *old_m;
	int m_size;
	PyObject *order, *order2, *old_msg;
	Integer *pObj, *qObj;
	mpz_t p, q, result;
	mpz_t tmp, exp, rop;
	Integer *rop2;

	if (PyArg_ParseTuple(args, "OOO", &old_msg, &order, &order2)) {
		// make sure p = 2 * q + 1
		if (PyInteger_Check(order) && PyInteger_Check(order2)) {
			mpz_init(p);
			mpz_init(q);
			mpz_init(result);

			pObj = (Integer *) order;
			qObj = (Integer *) order2;
			mpz_set(p, pObj->e);
			mpz_set(q, qObj->e);
			mpz_mul_ui(result, q, 2);
			mpz_add_ui(result, result, 1);

			if (mpz_cmp(result, p) != 0) {
				mpz_clear(p);
				mpz_clear(q);
				mpz_clear(result);
				EXIT_IF(TRUE, "can only encode messages into groups where p = 2*q+1.");
			}
		} else {
			EXIT_IF(TRUE, "failed to specify large primes p and q.");
		}
		mpz_clear(q);
		mpz_clear(result);

		// for python 3
		if(PyBytes_Check(old_msg)) {
			old_m = (uint8_t *) PyBytes_AS_STRING(old_msg);
			m_size = strlen((char *) old_m);
			debug("Message => ");
			printf_buffer_as_hex(old_m, m_size);
			debug("Size => '%d'\n", m_size);
		
			if(m_size > MSG_LEN-2) {
				mpz_clear(p);
				EXIT_IF(TRUE, "message too large. Cannot represent as an element of Zp.");
			}
		}
		else {
			mpz_clear(p);
			EXIT_IF(TRUE, "message not a bytes object");
		}

		//longest message can be is 128 characters (1024 bits) => check on this!!!
		char m[MSG_LEN+2]; //128 byte message, 1 byte length, null byte
		m[0] = m_size & 0xFF; //->this one works too...results in order 207
		snprintf((m+1), MSG_LEN+1, "%s", old_m); //copying message over
		m_size = m_size + 1; //we added an extra byte

		// p and q values valid
		mpz_init(tmp);
		mpz_import(tmp, m_size, 1, sizeof(m[0]), 0, 0, m);
		// bytes_to_mpz(tmp2, (const unsigned char *) m, (size_t) m_size);

		// perform encoding...
		// get the order object (only works for p = 2q + 1)
		mpz_init(exp);
		mpz_init(rop);
		mpz_add_ui(tmp, tmp, 1);

		// (p - 1) / 2
		mpz_sub_ui(exp, p, 1);
		mpz_divexact_ui(exp, exp, 2);
		// y ^ exp mod p
		mpz_powm(rop, tmp, exp, p);

		// check if rop is 1
		if (mpz_cmp_ui(rop, 1) == 0) {
			// if so, then we can return y
			debug("true case: just return y.\n");
			print_mpz(p, 10);
			print_mpz(tmp, 10);

			rop2 = createNewInteger(p);
			mpz_init(rop2->e);
			mpz_init_set(rop2->m, p);
			mpz_set(rop2->e, tmp);
		} else {
			// debug("Order of group => '%zd'\n", mpz_sizeinbase(p, 2));
			// -y mod p
			debug("false case: return -y mod p.\n");
			mpz_neg(tmp, tmp);
			mpz_mod(tmp, tmp, p);
			debug("tmp...\n");
			print_mpz(tmp, 10);
			debug("p...\n");
			print_mpz(p, 10);

			rop2 = createNewInteger(p);
			mpz_init(rop2->e);
			mpz_init_set(rop2->m, p);
			mpz_set(rop2->e, tmp);
		}
		mpz_clear(rop);
		mpz_clear(p);
		mpz_clear(exp);
		mpz_clear(tmp);
		return (PyObject *) rop2;
	}

	EXIT_IF(TRUE, "invalid input types.");
}

static PyObject *decode_message(PyObject *self, PyObject *args) {
	PyObject *element, *order, *order2;
	if (PyArg_ParseTuple(args, "OOO", &element, &order, &order2)) {
		if (PyInteger_Check(element) && PyInteger_Check(order)
				&& PyInteger_Check(order2)) {
			mpz_t p, q;
			Integer *elem, *pObj, *qObj; // mpz_init(elem);
			mpz_init(p);
			mpz_init(q);

			// convert to mpz_t types...
			elem = (Integer *) element;
			pObj = (Integer *) order;
			qObj = (Integer *) order2;
			mpz_set(p, pObj->e);
			mpz_set(q, qObj->e);
			// test if elem <= q
			if (mpz_cmp(elem->e, q) <= 0) {
				debug("true case: g <= q.\n");
				mpz_sub_ui(elem->e, elem->e, 1);
			} else {
				debug("false case: g > q. so, y = -elem mod p.\n");
				// y = -elem mod p
				mpz_neg(elem->e, elem->e);
				mpz_mod(elem->e, elem->e, p);
				mpz_sub_ui(elem->e, elem->e, 1);
			}

			size_t count = 0;
			unsigned char *Rop = (unsigned char *) mpz_export(NULL, &count, 1,
					sizeof(char), 0, 0, elem->e);
			debug("rop => '%s'\n", Rop);
			debug("count => '%zd'\n", count);

			int size_Rop = Rop[0];
			char m[MSG_LEN+1];
			*m = '\0';
			strncat(m, (const char *)(Rop+1), size_Rop);

			mpz_clear(p);
			mpz_clear(q);

			return PyBytes_FromFormat("%s", m);
		}
	}

	return Py_BuildValue("i", FALSE);
}

static PyObject *bitsize(PyObject *self, PyObject *args) {
	PyObject *object = NULL;
	int tmp_size;

	if (PyArg_ParseTuple(args, "O", &object)) {
		if (_PyLong_Check(object)) {
			mpz_t tmp;
			mpz_init(tmp);
			longObjToMPZ(tmp, object);
			tmp_size = size(tmp);
			mpz_clear(tmp);
			return Py_BuildValue("i", tmp_size);
		} else if (PyInteger_Check(object)) {
			Integer *obj = (Integer *) object;
			if (obj->initialized) {
				tmp_size = size(obj->e);
				return Py_BuildValue("i", tmp_size);
			}
		}
	}
	PyErr_SetString(IntegerError, "invalid input type.");
	return NULL;
}

static PyObject *testCoPrime(Integer *self, PyObject *arg) {
	mpz_t tmp, rop;
	int result = FALSE;

	if (!self->initialized) {
		PyErr_SetString(IntegerError, "integer object not initialized.");
		return NULL;
	}

	mpz_init(rop);
	if (arg != NULL) {
		PyObject *obj = PyNumber_Long(arg);
		if (obj != NULL) {
			mpz_init(tmp);
			longObjToMPZ(tmp, obj);
			mpz_gcd(rop, self->e, tmp);
			print_mpz(rop, 1);
			result = (mpz_cmp_ui(rop, 1) == 0) ? TRUE : FALSE;
			mpz_clear(tmp);
			Py_XDECREF(obj);
		}

	} else {
		mpz_gcd(rop, self->e, self->m);
		print_mpz(rop, 1);
		result = (mpz_cmp_ui(rop, 1) == 0) ? TRUE : FALSE;
	}
	mpz_clear(rop);

	if (result) {
		Py_INCREF(Py_True);
		return Py_True;
	} else {
		Py_INCREF(Py_False);
		return Py_False;
	}
}

/*
 * Description: B.isCongruent(A) => A === B mod N. Test whether A is congruent to B mod N.
 */
static PyObject *testCongruency(Integer *self, PyObject *args) {
	PyObject *obj = NULL;

	if (!self->initialized) {
		PyErr_SetString(IntegerError, "integer object not initialized.");
		return NULL;
	}

	if (PyArg_ParseTuple(args, "O", &obj)) {
		if (_PyLong_Check(obj)) {
			PyObject *obj2 = PyNumber_Long(obj);
			if (obj2 != NULL) {
				mpz_t rop;
				mpz_init(rop);
				longObjToMPZ(rop, obj2);
				Py_XDECREF(obj2);
				if (mpz_congruent_p(rop, self->e, self->m) != 0) {
					mpz_clear(rop);
					Py_INCREF(Py_True);
					return Py_True;
				} else {
					mpz_clear(rop);
					Py_INCREF(Py_False);
					return Py_False;
				}
			}
		} else if (PyInteger_Check(obj)) {
			Integer *obj2 = (Integer *) obj;
			if (obj2->initialized && mpz_congruent_p(obj2->e, self->e, self->m)
					!= 0) {
				Py_INCREF(Py_True);
				return Py_True;
			} else {
				Py_XDECREF(Py_False);
				return Py_False;
			}
		}

	}

	EXIT_IF(TRUE, "need long or int value to test congruency.");
}

static PyObject *legendre(PyObject *self, PyObject *args) {
	PyObject *obj1 = NULL, *obj2 = NULL;
	mpz_t a, p;
	mpz_init(a);
	mpz_init(p);

	if (PyArg_ParseTuple(args, "OO", &obj1, &obj2)) {
		if (_PyLong_Check(obj1)) {
			longObjToMPZ(a, obj1);
		} else if (PyInteger_Check(obj1)) {
			Integer *tmp = (Integer *) obj1;
			mpz_set(a, tmp->e);
		}

		if (_PyLong_Check(obj2)) {
			longObjToMPZ(p, obj2);
		} else if (PyInteger_Check(obj2)) {
			Integer *tmp2 = (Integer *) obj2;
			mpz_set(p, tmp2->e);
		}

		// make sure a,p have been set
		if (mpz_cmp_ui(a, 0) != 0 && mpz_cmp_ui(p, 0) != 0) {
			// make sure p is odd and positive prime number
			int prop_p = mpz_probab_prime_p(p, MAX_RUN);
			if (mpz_odd_p(p) > 0 && prop_p > 0) {
				return Py_BuildValue("i", mpz_legendre(a, p));
			} else {
				return Py_BuildValue("i", FALSE);
			}
		}
	}

	EXIT_IF(TRUE, "invalid input.");
}

static PyObject *gcdCall(PyObject *self, PyObject *args) {
	PyObject *obj1 = NULL, *obj2 = NULL;
	mpz_t op1, op2;

	if (PyArg_ParseTuple(args, "OO", &obj1, &obj2)) {
		if (_PyLong_Check(obj1)) {
			mpz_init(op1);
			longObjToMPZ(op1, obj1);
		} else if (PyInteger_Check(obj1)) {
			mpz_init(op1);
			Integer *tmp = (Integer *) obj1;
			mpz_set(op1, tmp->e);
		} else {
			ErrorMsg("invalid argument type: 1");
		}

		if (_PyLong_Check(obj2)) {
			mpz_init(op2);
			longObjToMPZ(op2, obj2);
		} else if (PyInteger_Check(obj2)) {
			mpz_init(op2);
			Integer *tmp = (Integer *) obj2;
			mpz_set(op2, tmp->e);
		} else {
			mpz_clear(op1);
			ErrorMsg("invalid argument type: 2");
		}

		Integer *rop = createNewIntegerNoMod();
		mpz_init(rop->e);
		mpz_init(rop->m);
		mpz_gcd(rop->e, op1, op2);
		mpz_clear(op1);
		mpz_clear(op2);
		return (PyObject *) rop;
	}

	EXIT_IF(TRUE, "invalid input.");
}

static PyObject *lcmCall(PyObject *self, PyObject *args) {
	PyObject *obj1 = NULL, *obj2 = NULL;
	mpz_t op1, op2;

	if (PyArg_ParseTuple(args, "OO", &obj1, &obj2)) {
		if (_PyLong_Check(obj1)) {
			mpz_init(op1);
			longObjToMPZ(op1, obj1);
		} else if (PyInteger_Check(obj1)) {
			mpz_init(op1);
			Integer *tmp = (Integer *) obj1;
			mpz_set(op1, tmp->e);
		} else {
			EXIT_IF(TRUE, "invalid argument type: 1");
		}

		if (_PyLong_Check(obj2)) {
			mpz_init(op2);
			longObjToMPZ(op2, obj2);
		} else if (PyInteger_Check(obj2)) {
			mpz_init(op2);
			Integer *tmp = (Integer *) obj2;
			mpz_set(op2, tmp->e);
		} else {
			mpz_clear(op1);
			EXIT_IF(TRUE, "invalid argument type: 2");
		}

		Integer *rop = createNewIntegerNoMod();
		mpz_init(rop->e);
		mpz_init(rop->m);
		mpz_lcm(rop->e, op1, op2);
		mpz_clear(op1);
		mpz_clear(op2);
		return (PyObject *) rop;
	}

	EXIT_IF(TRUE, "invalid input.");
}

static PyObject *serialize(PyObject *self, PyObject *args) {
	Integer *obj = NULL;

	if (!PyArg_ParseTuple(args, "O", &obj)) {
		ErrorMsg("invalid argument");
	}

	// export the object first
	size_t count1 = 0, count2 = 0;
	char *base64_rop = NULL, *base64_rop2 = NULL;
	PyObject *bytes1 = NULL, *bytes2 = NULL;
	if (mpz_sgn(obj->e) > 0) {
		uint8_t *rop = (uint8_t *) mpz_export(NULL, &count1, 1, sizeof(char),
				0, 0, obj->e);
		// convert string to base64 encoding
		size_t length = 0;
		base64_rop = NewBase64Encode(rop, count1, FALSE, &length);
		// convert to bytes (length : base64 integer)
		bytes1 = PyBytes_FromFormat("%d:%s:", (int) length,
				(const char *) base64_rop);
		free(base64_rop);
	}

	if (mpz_sgn(obj->m) > 0) {
		uint8_t *rop2 = (uint8_t *) mpz_export(NULL, &count2, 1, sizeof(char),
				0, 0, obj->m);
		size_t length2 = 0;
		base64_rop2 = NewBase64Encode(rop2, count2, FALSE, &length2);
		// convert to bytes
		bytes2 = PyBytes_FromFormat("%d:%s:", (int) length2,
				(const char *) base64_rop2);
		free(base64_rop2);
	}

	if (bytes2 != NULL && bytes1 != NULL) {
		PyBytes_ConcatAndDel(&bytes1, bytes2);
		return bytes1;
	} else if (bytes1 != NULL) {
		return bytes1;
	} else {
		EXIT_IF(TRUE, "invalid integer object.");
	}
}

void deserialize_helper(int length, char *encoded_value, mpz_t target)
{
	debug("encoded_value len => '%zd'", strlen(encoded_value));

	size_t deserialized_len = 0;
	uint8_t *buf = NewBase64Decode((const char *) encoded_value, length, &deserialized_len);

	mpz_import(target, deserialized_len, 1, sizeof(buf[0]), 0, 0, buf);
	free(buf);
}

static PyObject *deserialize(PyObject *self, PyObject *args) {
	PyObject *bytesObj = NULL;

	if (!PyArg_ParseTuple(args, "O", &bytesObj)) {
		EXIT_IF(TRUE, "invalid argument.");
	}

	unsigned char *serial_buf = (unsigned char *) PyBytes_AsString(bytesObj);
	/* get integer value */
	char delim[] = ":";
	char *token = NULL;
	token = strtok((char *) serial_buf, delim);
	// length
	int int_len = atoi((const char *) token);
	debug("length => '%d'\n", int_len);
	mpz_t x,m;
	mpz_init(x);
	mpz_init(m);

	// parse the first half of the bytes/str object
	token = strtok(NULL, delim);
	debug("encoded value x => '%s'\n", token);
	if(token != NULL) {
		deserialize_helper(int_len, token, x);
		debug("decoded value x => ");
		print_mpz(x, 10);
	}

	// parse modulus (if indeed modular integer)
	token = strtok(NULL, delim);
	if(token != NULL) {
		int_len = atoi((const char *) token);
		token = strtok(NULL, delim);
		deserialize_helper(int_len, token, m);
		debug("decoded value m => ");
		print_mpz(m, 10);
	}

	Integer *obj = NULL;
	if(mpz_sgn(m) > 0) {
		obj = createNewInteger(m);
		mpz_init(obj->e);
		mpz_init_set(obj->m, m);
	}
	else {
		obj = createNewIntegerNoMod();
		mpz_init(obj->e);
		mpz_init(obj->m);
	}
	mpz_set(obj->e, x);

	mpz_clear(x);
	mpz_clear(m);
	return (PyObject *) obj;
}

// class method for conversion
// integer.toBytes(x) => b'blah blah'
static PyObject *toBytes(PyObject *self, PyObject *args) {
	Integer *intObj = NULL;

	if (PyInteger_Check(args)) {
		intObj = (Integer *) args;
		size_t count = 0;
		unsigned char *Rop = (unsigned char *) mpz_export(NULL, &count, 1,
				sizeof(char), 0, 0, intObj->e);
		debug("Rop => '%s', len =>'%zd'\n", Rop, count);
		return PyBytes_FromStringAndSize((const char *) Rop, (Py_ssize_t) count);
	}

	EXIT_IF(TRUE, "invalid type.");
}

// class method for conversion for modular integer to an integer
// integer.toInt(x mod Y) => x
static PyObject *toInt(PyObject *self, PyObject *args) {
	Integer *intObj = NULL;

	if (PyInteger_Check(args)) {
		intObj = (Integer *) args;
		Integer *rop = createNewIntegerNoMod();
		mpz_init_set(rop->e, intObj->e);
		mpz_init(rop->m);

		return (PyObject *) rop;
	}

	EXIT_IF(TRUE, "invalid type.");
}


static PyObject *Integer_xor(PyObject *self, PyObject *other) {
	Integer *rop = NULL, *op1 = NULL, *op2 = NULL;

	if (PyInteger_Check(self))
		op1 = (Integer *) self;
	if (PyInteger_Check(other))
		op2 = (Integer *) other;

	EXIT_IF(op1 == NULL || op2 == NULL, "both types are not of charm integer types.");
	if (PyInteger_Init(op1, op2)) {
		rop = createNewIntegerNoMod();
		mpz_init(rop->e);
		mpz_init(rop->m);
		mpz_xor(rop->e, op1->e, op2->e);
		return (PyObject *) rop;
	}

	EXIT_IF(TRUE, "objects not initialized properly.");
}

#ifdef BENCHMARK_ENABLED
/* END: helper function definition */
InitBenchmark_CAPI(_init_benchmark, dBench, 3);
StartBenchmark_CAPI( _start_benchmark, dBench);
EndBenchmark_CAPI( _end_benchmark, dBench);
GetBenchmark_CAPI( _get_benchmark, dBench);
GetAllBenchmarks_CAPI(_get_all_results, dBench);
ClearBenchmarks_CAPI(_clear_benchmark, dBench);
#endif

PyMethodDef Integer_methods[] = {
	{ "set", (PyCFunction) Integer_set, METH_VARARGS, "initialize with another integer object." },
	{ "isCoPrime", (PyCFunction) testCoPrime, METH_O | METH_NOARGS, "determine whether two integers a and b are relatively prime." },
	{ "isCongruent", (PyCFunction) testCongruency, METH_VARARGS, "determine whether two integers are congruent mod n." },
	{ "reduce", (PyCFunction) Integer_reduce, METH_NOARGS, "reduce an integer object modulo N." },
	{ NULL }
};

#if PY_MAJOR_VERSION >= 3
PyNumberMethods integer_number = {
	Integer_add, /* nb_add */
	Integer_sub, /* nb_subtract */
	Integer_mul, /* nb_multiply */
	Integer_remainder, /* nb_remainder */
	0, /* nb_divmod */
	Integer_pow, /* nb_power */
	0, /* nb_negative */
	0, /* nb_positive */
	0, /* nb_absolute */
	0, /* nb_bool */
	(unaryfunc) Integer_invert, /* nb_invert */
	0, /* nb_lshift */
	0, /* nb_rshift */
	0, /* nb_and */
	Integer_xor, /* nb_xor */
	0, /* nb_or */
	(unaryfunc) Integer_long, /* nb_int */
	0, /* nb_reserved */
	0, /* nb_float */
	Integer_add, /* nb_inplace_add */
	Integer_sub, /* nb_inplace_subtract */
	Integer_mul, /* nb_inplace_multiply */
	Integer_remainder, /* nb_inplace_remainder */
	Integer_pow, /* nb_inplace_power */
	0, /* nb_inplace_lshift */
	0, /* nb_inplace_rshift */
	0, /* nb_inplace_and */
	0, /* nb_inplace_xor */
	0, /* nb_inplace_or */
	0, /* nb_floor_divide */
	Integer_div, /* nb_true_divide */
	0, /* nb_inplace_floor_divide */
	Integer_div, /* nb_inplace_true_divide */
	0, /* nb_index */
};

PyTypeObject IntegerType = {
	PyVarObject_HEAD_INIT(NULL, 0)
	"integer.Element", /*tp_name*/
	sizeof(Integer), /*tp_basicsize*/
	0, /*tp_itemsize*/
	(destructor)Integer_dealloc, /*tp_dealloc*/
	0, /*tp_print*/
	0, /*tp_getattr*/
	0, /*tp_setattr*/
	0, /*tp_reserved*/
	(reprfunc)Integer_print, /*tp_repr*/
	&integer_number, /*tp_as_number*/
	0, /*tp_as_sequence*/
	0, /*tp_as_mapping*/
	0, /*tp_hash */
	0, /*tp_call*/
	0, /*tp_str*/
	0, /*tp_getattro*/
	0, /*tp_setattro*/
	0, /*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
	"Modular Integer objects", /* tp_doc */
	0, /* tp_traverse */
	0, /* tp_clear */
	Integer_equals, /* tp_richcompare */
	0, /* tp_weaklistoffset */
	0, /* tp_iter */
	0, /* tp_iternext */
	Integer_methods, /* tp_methods */
	0, /* tp_members */
	0, /* tp_getset */
	0, /* tp_base */
	0, /* tp_dict */
	0, /* tp_descr_get */
	0, /* tp_descr_set */
	0, /* tp_dictoffset */
	(initproc)Integer_init, /* tp_init */
	0, /* tp_alloc */
	Integer_new, /* tp_new */
};
#else
/* python 2.x series */
PyNumberMethods integer_number = {
    Integer_add,                       /* nb_add */
    Integer_sub,                       /* nb_subtract */
    Integer_mul,                        /* nb_multiply */
    Integer_div,                       /* nb_divide */
    Integer_remainder,                      /* nb_remainder */
    0,						/* nb_divmod */
    Integer_pow,						/* nb_power */
    0,            		/* nb_negative */
    0,            /* nb_positive */
    0,            /* nb_absolute */
    0,          	/* nb_nonzero */
    (unaryfunc)Integer_invert,         /* nb_invert */
    0,                    /* nb_lshift */
    0,                    /* nb_rshift */
    0,                       /* nb_and */
    Integer_xor,                       /* nb_xor */
    0,                        /* nb_or */
    0,                    				/* nb_coerce */
    (unaryfunc)Integer_long,            /* nb_int */
    (unaryfunc)Integer_long,           /* nb_long */
    0,          /* nb_float */
    0,            /* nb_oct */
    0,            /* nb_hex */
    Integer_add,                      /* nb_inplace_add */
    Integer_sub,                      /* nb_inplace_subtract */
    Integer_mul,                      /* nb_inplace_multiply */
    Integer_div,                      /* nb_inplace_divide */
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

PyTypeObject IntegerType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "integer.Element",             /*tp_name*/
    sizeof(Integer),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)Integer_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    &integer_number,       /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0, 						/*tp_call*/
    (reprfunc)Integer_print,   /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_CHECKTYPES, /*tp_flags*/
    "Modular Integer objects",           /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    Integer_equals,		   /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    Integer_methods,           /* tp_methods */
    0,           /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc) Integer_init,      /* tp_init */
    0,                         /* tp_alloc */
    Integer_new,                 /* tp_new */
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

/* global module methods (include isPrime, randomPrime, etc. here). */
static PyMethodDef module_methods[] = {
	{ "randomBits", (PyCFunction) genRandomBits, METH_VARARGS, "generate a random number of bits from 0 to 2^n-1." },
	{ "random", (PyCFunction) genRandom, METH_VARARGS, "generate a random number in range of 0 to n-1 where n is large number." },
	{ "randomPrime", (PyCFunction) genRandomPrime, METH_VARARGS, "generate a probabilistic random prime number that is n-bits." },
	{ "isPrime", (PyCFunction) testPrimality, METH_O, "probabilistic algorithm to whether a given integer is prime." },
	{ "encode", (PyCFunction) encode_message, METH_VARARGS, "encode a message as a group element where p = 2*q + 1 only." },
	{ "decode", (PyCFunction) decode_message, METH_VARARGS, "decode a message from a group element where p = 2*q + 1 to a message." },
	{ "hashInt", (PyCFunction) Integer_hash, METH_VARARGS, "hash to group elements in which p = 2*q+1." },
	{ "bitsize", (PyCFunction) bitsize, METH_VARARGS, "determine how many bits required to represent a given value." },
	{ "legendre", (PyCFunction) legendre, METH_VARARGS, "given a and a positive prime p compute the legendre symbol." },
	{ "gcd", (PyCFunction) gcdCall, METH_VARARGS, "compute the gcd of two integers a and b." },
	{ "lcm", (PyCFunction) lcmCall, METH_VARARGS, "compute the lcd of two integers a and b." },
	{ "serialize", (PyCFunction) serialize, METH_VARARGS, "Serialize an integer type into bytes." },
	{ "deserialize", (PyCFunction) deserialize, METH_VARARGS, "De-serialize an bytes object into an integer object" },
#ifdef BENCHMARK_ENABLED
	{ "InitBenchmark", (PyCFunction) _init_benchmark, METH_NOARGS, "Initialize a benchmark object" },
	{ "StartBenchmark", (PyCFunction) _start_benchmark, METH_VARARGS, "Start a new benchmark with some options" },
	{ "EndBenchmark", (PyCFunction) _end_benchmark, METH_VARARGS, "End a given benchmark" },
	{ "GetBenchmark", (PyCFunction) _get_benchmark, METH_VARARGS, "Returns contents of a benchmark object" },
	{ "GetGeneralBenchmarks", (PyCFunction) _get_all_results, METH_VARARGS, "Retrieve general benchmark info as a dictionary."},
	{ "ClearBenchmark", (PyCFunction)_clear_benchmark, METH_VARARGS, "Clears content of benchmark object"},
#endif
	{ "int2Bytes", (PyCFunction) toBytes, METH_O, "convert an integer object to a bytes object." },
	{ "toInt", (PyCFunction) toInt, METH_O, "convert modular integer into an integer object."},
	{ NULL, NULL }
};

#if PY_MAJOR_VERSION >= 3
static int int_traverse(PyObject *m, visitproc visit, void *arg) {
	Py_VISIT(GETSTATE(m)->error);
	return 0;
}

static int int_clear(PyObject *m) {
	Py_CLEAR(GETSTATE(m)->error);
#ifdef BENCHMARK_ENABLED
	Py_CLEAR(GETSTATE(m)->dBench);
#endif
	return 0;
}

static struct PyModuleDef moduledef = {
	PyModuleDef_HEAD_INIT,
	"ecc",
	NULL,
	sizeof(struct module_state),
	module_methods,
	NULL,
	int_traverse,
	int_clear,
	NULL
};

#define INITERROR return NULL
PyMODINIT_FUNC
PyInit_integer(void) {
#else
#define INITERROR return
void initinteger(void) {
#endif
	PyObject *m;
	if (PyType_Ready(&IntegerType) < 0)
		INITERROR;
	// initialize module
#if PY_MAJOR_VERSION >= 3
	m = PyModule_Create(&moduledef);
#else
	m = Py_InitModule("integer", module_methods);
#endif
	// add integer type to module
	struct module_state *st = GETSTATE(m);
	st->error = PyErr_NewException("integer.Error", NULL, NULL);
	if (st->error == NULL) {
		Py_DECREF(m);
		INITERROR;
	}
	IntegerError = st->error;
#ifdef BENCHMARK_ENABLED
	if (import_benchmark() < 0) {
    	Py_DECREF(m);
    	INITERROR;
	}
	if (PyType_Ready(&BenchmarkType) < 0)
		INITERROR;
	st->dBench = PyObject_New(Benchmark, &BenchmarkType);
	dBench = st->dBench;
	dBench->bench_initialized = FALSE;
	InitClear(dBench);
#endif
	Py_INCREF(&IntegerType);
	PyModule_AddObject(m, "integer", (PyObject *) &IntegerType);
    Py_INCREF(&BenchmarkType);
    PyModule_AddObject(m, "benchmark", (PyObject *)&BenchmarkType);

#ifdef BENCHMARK_ENABLED
	// add integer error to module
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
