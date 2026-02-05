
#if defined(__APPLE__)
// benchmark new
PyObject *Benchmark_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
  Benchmark *self;
  self = (Benchmark *)type->tp_alloc(type, 0);
  if(self != NULL) {
    self->bench_initialized = FALSE;
    self->bench_inprogress = FALSE;  // false until we StartBenchmark( ... )
    self->op_add = self->op_sub = self->op_mult = 0;
    self->op_div = self->op_exp = self->op_pair = 0;
    self->cpu_time_ms = self->real_time_ms = 0.0;
    self->cpu_option = self->real_option = FALSE;
    debug("Creating new benchmark object.\n");
  }
  return (PyObject *) self;
}

// benchmark init
int Benchmark_init(Benchmark *self, PyObject *args, PyObject *kwds)
{
  return 0;
}
// benchmark dealloc
void Benchmark_dealloc(Benchmark *self) {
  debug("Releasing benchmark object.\n");
  Py_TYPE(self)->tp_free((PyObject*)self);
}

PyTypeObject BenchmarkType = {
  PyVarObject_HEAD_INIT(NULL, 0)
  "profile.Benchmark",       /*tp_name*/
  sizeof(Benchmark),         /*tp_basicsize*/
  0,                         /*tp_itemsize*/
  (destructor)Benchmark_dealloc, /*tp_dealloc*/
  0,                         /*tp_print*/
  0,                         /*tp_getattr*/
  0,                         /*tp_setattr*/
  0,                /*tp_reserved*/
  0, /*tp_repr*/
  0,               /*tp_as_number*/
  0,                         /*tp_as_sequence*/
  0,                         /*tp_as_mapping*/
  0,   /*tp_hash */
  0,                         /*tp_call*/
  0, /*tp_str*/
  0,                         /*tp_getattro*/
  0,                         /*tp_setattro*/
  0,                         /*tp_as_buffer*/
  Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
  "Benchmark objects",           /* tp_doc */
  0,                   /* tp_traverse */
  0,                   /* tp_clear */
  0,          /* tp_richcompare */
  0,                   /* tp_weaklistoffset */
  0,                   /* tp_iter */
  0,                   /* tp_iternext */
  0,             /* tp_methods */
  0,             /* tp_members */
  0,                         /* tp_getset */
  0,                         /* tp_base */
  0,                         /* tp_dict */
  0,                         /* tp_descr_get */
  0,                         /* tp_descr_set */
  0,                         /* tp_dictoffset */
  (initproc)Benchmark_init,      /* tp_init */
  0,                         /* tp_alloc */
  Benchmark_new,                 /* tp_new */
};

#endif

void Operations_dealloc(Operations *self)
{
	debug("Releasing operations object.\n");
	Py_TYPE(self)->tp_free((PyObject *) self);
}

PyObject *Operations_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	Operations *self = (Operations *) type->tp_alloc(type, 0);
	if(self != NULL) {
		/* initialize */
		self->op_init = FALSE;
	}

	return (PyObject *) self;
}

int Operations_init(Operations *self, PyObject *args, PyObject *kwds)
{
	self->op_init = TRUE;
	return 0;
}

/* for python 3.x */
PyTypeObject OperationsType = {
	PyVarObject_HEAD_INIT(NULL, 0)
	"profile.Operations",             /*tp_name*/
	sizeof(Operations),         /*tp_basicsize*/
	0,                         /*tp_itemsize*/
	(destructor)Operations_dealloc, /*tp_dealloc*/
	0,                         /*tp_print*/
	0,                         /*tp_getattr*/
	0,                         /*tp_setattr*/
	0,			   				/*tp_reserved*/
	0, 							/*tp_repr*/
	0,               		   /*tp_as_number*/
	0,                         /*tp_as_sequence*/
	0,                         /*tp_as_mapping*/
	0,                         /*tp_hash */
	0,                         /*tp_call*/
	0,                         /*tp_str*/
	0,                         /*tp_getattro*/
	0,                         /*tp_setattro*/
	0,                         /*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
	"Granular benchmark objects",           /* tp_doc */
	0,		               /* tp_traverse */
	0,		               /* tp_clear */
	0,		       		   /* tp_richcompare */
	0,		               /* tp_weaklistoffset */
	0,		               /* tp_iter */
	0,		               /* tp_iternext */
	0, 			            /* tp_methods */
	0,             			   /* tp_members */
	0,                         /* tp_getset */
	0,                         /* tp_base */
	0,                         /* tp_dict */
	0,                         /* tp_descr_get */
	0,                         /* tp_descr_set */
	0,                         /* tp_dictoffset */
	(initproc)Operations_init,      /* tp_init */
	0,                         /* tp_alloc */
	Operations_new,                 /* tp_new */
};

PyObject *InitBenchmark(PyObject *self, PyObject *args) {
	Benchmark *benchObj = NULL;
	GROUP_OBJECT *group = NULL;
	if(!PyArg_ParseTuple(args, "O", &group)) {
		PyErr_SetString(BENCH_ERROR, "InitBenchmark - invalid argument.");
		return NULL;
	}

	VERIFY_GROUP(group);
	if(group->dBench == NULL) {
		benchObj = PyObject_New(Benchmark, &BenchmarkType);
		if (benchObj == NULL) {
			PyErr_SetString(BENCH_ERROR, "out of memory.");
			return NULL;
		}

		/* setup granular options */
		if(group->gBench == NULL) {
			group->gBench = PyObject_New(Operations, &OperationsType);
			CLEAR_ALLDBENCH(group->gBench);
		}
		benchObj->num_options = 0;
		benchObj->op_add = benchObj->op_sub = benchObj->op_mult = 0;
		benchObj->op_div = benchObj->op_exp = benchObj->op_pair = 0;
		benchObj->cpu_time_ms = 0.0;
		benchObj->real_time_ms = 0.0;
		benchObj->bench_initialized = TRUE;
		benchObj->bench_inprogress = FALSE;
		benchObj->identifier = BenchmarkIdentifier;
		debug("%s: bench id set: '%i'\n", __FUNCTION__, benchObj->identifier);
		debug("Initialized benchmark object.\n");
		// set benchmark field in group object
		group->dBench = benchObj;
		RAND_pseudo_bytes(group->bench_id, ID_LEN);
		Py_RETURN_TRUE;
	}
	else if(group->dBench->bench_inprogress == FALSE && group->dBench->bench_initialized == TRUE) {
		// if we have initialized the benchmark object and ended a benchmark execution:
		// action: reset the fields
		debug("Reset benchmark state.\n");
		if(group->gBench != NULL) {
			CLEAR_ALLDBENCH(group->gBench);
		}
		PyClearBenchmark(group->dBench);
		group->dBench->bench_initialized = TRUE;
		group->dBench->bench_inprogress = FALSE;
		group->dBench->identifier = BenchmarkIdentifier;
		Py_RETURN_TRUE;
	}
	else if(group->dBench->bench_inprogress == TRUE) {
		debug("Benchmark in progress.\n");
	}
	debug("Benchmark already initialized.\n");
	Py_RETURN_FALSE;
}

PyObject *StartBenchmark(PyObject *self, PyObject *args)
{
	PyObject *list = NULL;
	GROUP_OBJECT *group = NULL;
	if(!PyArg_ParseTuple(args, "OO", &group, &list)) {
		PyErr_SetString(BENCH_ERROR, "StartBenchmark - invalid argument.");
		return NULL;
	}

	VERIFY_GROUP(group);
	if(group->dBench == NULL) {
		PyErr_SetString(BENCH_ERROR, "uninitialized benchmark object.");
		return NULL;
	}
	else if(PyList_Check(list) && group->dBench->bench_initialized == TRUE && group->dBench->bench_inprogress == FALSE
			&& group->dBench->identifier == BenchmarkIdentifier)
	{
		debug("%s: bench id: '%i'\n", __FUNCTION__, group->dBench->identifier);
		size_t size = PyList_Size(list);
		PyStartBenchmark(group->dBench, list, size);
		debug("list size => %zd\n", size);
		debug("benchmark enabled and initialized!\n");
		Py_RETURN_TRUE;
	}
	Py_RETURN_FALSE;
}

PyObject *EndBenchmark(PyObject *self, PyObject *args)
{
	GROUP_OBJECT *group = NULL;
	if(!PyArg_ParseTuple(args, "O", &group)) {
		PyErr_SetString(BENCH_ERROR, "EndBenchmark - invalid argument.");
		return NULL;
	}

	VERIFY_GROUP(group);
	if(group->dBench == NULL) {
		PyErr_SetString(BENCH_ERROR, "uninitialized benchmark object.");
		return NULL;
	}
	else if(group->dBench->bench_initialized == TRUE && group->dBench->bench_inprogress == TRUE && group->dBench->identifier == BenchmarkIdentifier) {
		PyEndBenchmark(group->dBench);
		debug("%s: bench id: '%i'\n", __FUNCTION__, group->dBench->identifier);
		Py_RETURN_TRUE;
	}
	Py_RETURN_FALSE;
}

PyObject *GetAllBenchmarks(PyObject *self, PyObject *args)
{
	GROUP_OBJECT *group = NULL;
	if(!PyArg_ParseTuple(args, "O", &group)) {
		PyErr_SetString(BENCH_ERROR, "GetGeneralBenchmarks - invalid argument.");
		return NULL;
	}
	VERIFY_GROUP(group);
	if(group->dBench == NULL) {
		PyErr_SetString(BENCH_ERROR, "uninitialized benchmark object.");
		return NULL;
	}
	else if(group->dBench->bench_inprogress == FALSE && group->dBench->identifier == BenchmarkIdentifier) {
		debug("%s: bench id: '%i'\n", __FUNCTION__, group->dBench->identifier);
		// return GetResultsWithPair(group->dBench);
		return GET_RESULTS_FUNC(group->dBench);
	}
	else if(group->dBench->bench_inprogress == TRUE) {
		printf("Benchmark in progress.\n");
	}
	else {
		debug("Invalid benchmark identifier.\n");
	}
	Py_RETURN_FALSE;
}

PyObject *GetBenchmark(PyObject *self, PyObject *args) {
	char *opt = NULL;
	GROUP_OBJECT *group = NULL;
	if(!PyArg_ParseTuple(args, "Os", &group, &opt))
	{
		PyErr_SetString(BENCH_ERROR, "GetBenchmark - invalid argument.");
		return NULL;
	}

	VERIFY_GROUP(group);
	if(group->dBench == NULL) {
		PyErr_SetString(BENCH_ERROR, "uninitialized benchmark object.");
		return NULL;
	}
	else if(group->dBench->bench_inprogress == FALSE && group->dBench->identifier == BenchmarkIdentifier) {
		return Retrieve_result(group->dBench, opt);
	}
	else if(group->dBench->bench_inprogress == TRUE) {
		printf("Benchmark in progress.\n");
	}
	Py_RETURN_FALSE;
}

static PyObject *GranularBenchmark(PyObject *self, PyObject *args)
{
	PyObject *dict = NULL;
	GROUP_OBJECT *group = NULL;
	if(!PyArg_ParseTuple(args, "O", &group)) {
		PyErr_SetString(BENCH_ERROR, "GetGranularBenchmark - invalid argument.");
		return NULL;
	}

	if(group->gBench == NULL || group->dBench == NULL) {
		PyErr_SetString(BENCH_ERROR, "uninitialized benchmark object.");
		return NULL;
	}
	else if(group->dBench->bench_inprogress == FALSE && BenchmarkIdentifier == group->dBench->identifier) {
		if(group->dBench->granular_option == FALSE) {
			PyErr_SetString(BENCH_ERROR, "granular option was not set.");
			return NULL;
		}
		dict = PyDict_New();
		if(dict == NULL) return NULL;
		if(group->dBench->op_mult > 0) {
			PyObject *MulList = PyCreateList(group->gBench, MULTIPLICATION);
			//PrintPyRef('MulList Before =>', MulList);
			PyDict_SetItemString(dict, "Mul", MulList);
			Py_DECREF(MulList);
		}

		if(group->dBench->op_div > 0) {
			PyObject *DivList = PyCreateList(group->gBench, DIVISION);
			PyDict_SetItemString(dict, "Div", DivList);
			Py_DECREF(DivList);
		}

		if(group->dBench->op_add > 0) {
			PyObject *AddList = PyCreateList(group->gBench, ADDITION);
			PyDict_SetItemString(dict, "Add", AddList);
			Py_DECREF(AddList);
		}

		if(group->dBench->op_sub > 0) {
			PyObject *SubList = PyCreateList(group->gBench, SUBTRACTION);
			PyDict_SetItemString(dict, "Sub", SubList);
			Py_DECREF(SubList);
		}

		if(group->dBench->op_exp > 0) {
			PyObject *ExpList = PyCreateList(group->gBench, EXPONENTIATION);
			PyDict_SetItemString(dict, "Exp", ExpList);
			Py_DECREF(ExpList);
		}
		//PrintPyRef('MulList After =>', MulList);
	}
	else if(group->dBench->bench_inprogress == TRUE) {
		printf("Benchmark in progress.\n");
	}
	else {
		PyErr_SetString(BENCH_ERROR, "uninitialized benchmark object.");
	}

	return dict;
}

