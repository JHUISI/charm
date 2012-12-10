#include <Python.h>
#include <structmember.h>

static PyTypeObject BaseType;
static PyObject *BaseError;
#define PyBase_Check(obj) PyObject_TypeCheck(obj, &BaseType)
#define TRUE	1
#define FALSE	0
#define PKG  "charm.core.crypto."
enum MOP {NONE = 0, MODE_ECB, MODE_CBC, MODE_CFB, MODE_PGP, MODE_OFB, MODE_CTR};
enum ALG {AES, DES, DES3};

typedef struct {
	PyObject_HEAD
	int initialized;
} Base;

// define functions here
/* Description: an example of inputs cryptobase.selectPRF(AES, ('This is a key 456', MODE_ECB))
 *
 */
static PyObject *selectPRF(Base *self, PyObject *args) {
	PyObject *tuple, *module, *module_dict, *new_func, *prf;
	int alg;
	char *ALG = NULL;

	if(!PyArg_ParseTuple(args, "iO", &alg, &tuple)) {
		PyErr_SetString(BaseError, "1st argument is algorithm and 2nd is tuple of arguments.");
		return NULL;
	}

	switch(alg) {
		case AES: ALG = PKG"AES"; break;
		case DES: ALG = PKG"DES"; break;
		case DES3: ALG = PKG"DES3"; break;
		default: ALG = PKG"AES"; break; /* default */
	}

	module = PyImport_ImportModule(ALG);
	if (!module) {
		Py_XDECREF (module);
		return NULL;
	}
	// printf("module ptr => %p\n", module);
	module_dict = PyModule_GetDict (module);
	Py_DECREF (module);
	new_func = PyDict_GetItemString(module_dict, "new");
	// printf("new_func ptr => %p\n", new_func);
	if (!PyCallable_Check(new_func))
	{
		PyErr_SetString(BaseError, "ALG.new is not callable.");
		return NULL;
	}
	prf = PyObject_CallObject(new_func, tuple);
	PyObject *ret = PyObject_CallMethod(prf, "setMode", "i", TRUE);
	if(ret == NULL) {
		// return error
		PyErr_SetString(BaseError, "Could not call setMode on ALG object.");
		Py_DECREF(prf);
		return NULL;
	}
	Py_DECREF(ret);
	return prf;
}

static PyObject *selectPRP(Base *self, PyObject *args) {
	PyObject *tuple, *module, *module_dict, *new_func, *prp;
	int alg;
	char *ALG = NULL;

	if(!PyArg_ParseTuple(args, "iO", &alg, &tuple)) {
		PyErr_SetString(BaseError, "1st argument is algorithm and 2nd is tuple of arguments.");
		return NULL;
	}

	switch(alg) {
		case AES: ALG = PKG"AES"; break;
		case DES: ALG = PKG"DES"; break;
		case DES3: ALG = PKG"DES3"; break;
		default: ALG = PKG"AES"; break; /* default */
	}

	module = PyImport_ImportModule(ALG);
	if (!module) {
		Py_XDECREF (module);
		return NULL;
	}
	module_dict = PyModule_GetDict (module);
	Py_DECREF (module);
	new_func = PyDict_GetItemString(module_dict, "new");

	if (!PyCallable_Check(new_func))
	{
		PyErr_SetString(BaseError, "ALG.new is not callable.");
		return NULL;
	}
	prp = PyObject_CallObject(new_func, tuple);
	return prp;
}

//static PyObject *selectHash(Base *self, PyObject *args) {
//	return NULL;
//}

static PyTypeObject BaseType = {
	PyVarObject_HEAD_INIT(NULL, 0)
    "crypto.Base",             /*tp_name*/
    sizeof(Base),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    0, 						   /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,       				   /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0, // (ternaryfunc) Base_call, /*tp_call*/
    0, // (reprfunc) Base_print,   /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT, 	   /*tp_flags*/
    "Crypto Base modular objects",    /* tp_doc */
};

struct module_state {
	PyObject *error;
};

#if PY_MAJOR_VERSION >= 3
#define GETSTATE(m) ((struct module_state *) PyModule_GetState(m))
#else
#define GETSTATE(m) (&_state)
static struct module_state _state;
#endif

static PyMethodDef module_methods[] = {
	{"selectPRF", (PyCFunction)selectPRF, METH_VARARGS, "selects a Pseudo-random Function given specific requirements."},
	{"selectPRP", (PyCFunction)selectPRP, METH_VARARGS, "selects a Pseudo-random Permutation given specific requirements."},
	// may need adapter functions here as well?
	{NULL}
};

#if PY_MAJOR_VERSION >= 3
static int base_traverse(PyObject *m, visitproc visit, void *arg) {
	Py_VISIT(GETSTATE(m)->error);
	return 0;
}

static int base_clear(PyObject *m) {
	Py_CLEAR(GETSTATE(m)->error);
    Py_XDECREF(BaseError);
	return 0;
}

static struct PyModuleDef moduledef = {
		PyModuleDef_HEAD_INIT,
		"cryptobase",
		NULL,
		sizeof(struct module_state),
		module_methods,
		NULL,
		base_traverse,
		base_clear,
		NULL
};

#define INITERROR return NULL
PyMODINIT_FUNC
PyInit_cryptobase(void) 		{
#else
#define INITERROR return
void initcryptobase(void) 		{
#endif
	PyObject *m;
    if(PyType_Ready(&BaseType) < 0) INITERROR;

    // initialize module
#if PY_MAJOR_VERSION >= 3
	m = PyModule_Create(&moduledef);
#else
	m = Py_InitModule("cryptobase", module_methods);
#endif
	// add integer type to module
	if(m == NULL) INITERROR;
	Py_INCREF(&BaseType);
    PyModule_AddObject(m, "cryptobase", (PyObject *)&BaseType);
    // algorithms
    PyModule_AddIntConstant(m, "AES", AES);
    PyModule_AddIntConstant(m, "DES", DES);
    PyModule_AddIntConstant(m, "DES3", DES3);

    // mode of operation
	PyModule_AddIntConstant(m, "MODE_ECB", MODE_ECB);
	PyModule_AddIntConstant(m, "MODE_CBC", MODE_CBC);
	PyModule_AddIntConstant(m, "MODE_CFB", MODE_CFB);
	PyModule_AddIntConstant(m, "MODE_PGP", MODE_PGP);
	PyModule_AddIntConstant(m, "MODE_OFB", MODE_OFB);
	PyModule_AddIntConstant(m, "MODE_CTR", MODE_CTR);

	// add integer error to module
	struct module_state *st = GETSTATE(m);
	st->error = PyErr_NewException("base.Error", NULL, NULL);
	if(st->error == NULL) {
		Py_DECREF(m);
		INITERROR;
	}
    BaseError = st->error;
    Py_INCREF(BaseError);
//    PyModule_AddObject(m, "base.error", BaseError);
#if PY_MAJOR_VERSION >= 3
	return m;
#endif
}
