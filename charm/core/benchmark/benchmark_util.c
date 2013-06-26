

PyObject *InitBenchmark(PyObject *self, PyObject *args) {
	Benchmark *benchObj = NULL;
	GROUP_OBJECT *group = NULL;
	if(!PyArg_ParseTuple(args, "O", &group))
		return NULL;

	VERIFY_GROUP(group);
	if(group->dBench == NULL) {
		benchObj = PyObject_New(Benchmark, &BenchmarkType);
		/* setup granular options */
#ifdef GRANULAR
		Operations *cntr = (Operations *) malloc(sizeof(Operations));
		benchObj->data_ptr = (void *) cntr; // store data structure
#endif
		CLEAR_ALLDBENCH(benchObj);
		PyClearBenchmark(benchObj);
		benchObj->bench_initialized = TRUE;
		benchObj->bench_inprogress = FALSE;
		benchObj->identifier = BenchmarkIdentifier;
		debug("%s: bench id set: '%i'\n", __FUNCTION__, benchObj->identifier);
		debug("Initialized benchmark object.\n");

		// set benchmark field in group object
		group->dBench = benchObj;
		Py_RETURN_TRUE;
	}
	else if(group->dBench->bench_inprogress == FALSE && group->dBench->bench_initialized == TRUE) {
		// if we have initialized the benchmark object and ended a benchmark execution:
		// action: reset the fields
		CLEAR_ALLDBENCH(group->dBench);
		PyClearBenchmark(group->dBench);
		group->dBench->bench_initialized = TRUE;
		group->dBench->bench_inprogress = FALSE;
		group->dBench->identifier = BenchmarkIdentifier;
		Py_RETURN_TRUE;
	}
	else if(group->dBench->bench_inprogress == TRUE) {
		printf("Benchmark in progress.\n");
	}
	debug("Benchmark already initialized.\n");
	Py_RETURN_FALSE;
}

PyObject *StartBenchmark(PyObject *self, PyObject *args)
{
	PyObject *list = NULL;
	GROUP_OBJECT *group = NULL;
	if(PyArg_ParseTuple(args, "OO", &group, &list))
	{
		VERIFY_GROUP(group);
		if(PyList_Check(list) && group->dBench->bench_initialized == TRUE && group->dBench->bench_inprogress == FALSE && BenchmarkIdentifier == group->dBench->identifier)
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
	return NULL;
}

PyObject *EndBenchmark(PyObject *self, PyObject *args)
{
	GROUP_OBJECT *group = NULL;
	if(PyArg_ParseTuple(args, "O", &group)) {
		debug("%s: bench init: '%i'\n", __FUNCTION__, b->bench_initialized);
		debug("%s: bench id: '%i'\n", __FUNCTION__, b->identifier);
		if(group->dBench->bench_initialized == TRUE && group->dBench->bench_inprogress == TRUE && group->dBench->identifier == BenchmarkIdentifier) {
			PyEndBenchmark(group->dBench);
			debug("%s: bench id: '%i'\n", __FUNCTION__, group->dBench->identifier);
//			Operations *c = (Operations *) group->dBench->data_ptr;
//			free(c);
			Py_RETURN_TRUE;
		}
	}
	printf("Invalid benchmark identifier.\n");
	Py_RETURN_FALSE;
}

PyObject *GetAllBenchmarks(PyObject *self, PyObject *args)
{
	GROUP_OBJECT *group = NULL;
	if(PyArg_ParseTuple(args, "O", &group)) {
		VERIFY_GROUP(group);

		if(group->dBench->bench_inprogress == FALSE && group->dBench->identifier == BenchmarkIdentifier) {
			debug("%s: bench id: '%i'\n", __FUNCTION__, group->dBench->identifier);
			// return GetResultsWithPair(group->dBench);
			return GET_RESULTS_FUNC(group->dBench);
		}
		else if(group->dBench->bench_inprogress == TRUE) {
			printf("Benchmark in progress.\n");
		}
		else {
			printf("Invalid benchmark identifier.\n");
		}
	}
	Py_RETURN_FALSE;
}

PyObject *GetBenchmark(PyObject *self, PyObject *args) {
	char *opt = NULL;
	GROUP_OBJECT *group = NULL;
	if(PyArg_ParseTuple(args, "Os", &group, &opt))
	{
		VERIFY_GROUP(group);
		if(group->dBench->bench_inprogress == FALSE && group->dBench->identifier == BenchmarkIdentifier) {
			return Retrieve_result(group->dBench, opt);
		}
	}
	Py_RETURN_FALSE;
}

static PyObject *GranularBenchmark(PyObject *self, PyObject *args)
{
	PyObject *dict = NULL;
	GROUP_OBJECT *group = NULL;
	if(!PyArg_ParseTuple(args, "O", &group)) {
		PyErr_SetString(BENCH_ERROR, "invalid benchmark identifier.");
		return NULL;
	}

	if(group->dBench->bench_inprogress == FALSE && BenchmarkIdentifier == group->dBench->identifier) {
		PyObject *MulList = PyCreateList(group->dBench, MULTIPLICATION);
		PyObject *DivList = PyCreateList(group->dBench, DIVISION);
		PyObject *AddList = PyCreateList(group->dBench, ADDITION);
		PyObject *SubList = PyCreateList(group->dBench, SUBTRACTION);
		PyObject *ExpList = PyCreateList(group->dBench, EXPONENTIATION);
		dict = PyDict_New();
		if(dict == NULL) return NULL;
		//PrintPyRef('MulList Before =>', MulList);
		PyDict_SetItemString(dict, "Mul", MulList);
		PyDict_SetItemString(dict, "Div", DivList);
		PyDict_SetItemString(dict, "Add", AddList);
		PyDict_SetItemString(dict, "Sub", SubList);
		PyDict_SetItemString(dict, "Exp", ExpList);
		Py_DECREF(MulList);
		Py_DECREF(DivList);
		Py_DECREF(AddList);
		Py_DECREF(SubList);
		Py_DECREF(ExpList);
		//PrintPyRef('MulList After =>', MulList);
	}
	else {
		debug("%s: invalid id = '%d'\n", __FUNCTION__, id);
	}

	return dict;
}

