#define BENCHMARK_MODULE
#include "benchmarkmodule.h"

double CalcUsecs(struct timeval *start, struct timeval *stop) {
	double usec_per_second = 1000000;
	double result = usec_per_second * (stop->tv_sec - start->tv_sec);

	if(stop->tv_usec >= start->tv_usec) {
		result += (stop->tv_usec - start->tv_usec);
	}
	else {
		result -= (start->tv_usec - stop->tv_usec);
	}

//	if(result < 0) {
//		debug("start secs => '%ld' and usecs => '%d'\n", start->tv_sec, start->tv_usec);
//		debug("stop secs => '%ld' and usecs => '%d'\n", stop->tv_sec, stop->tv_usec);
//	}

	return result / usec_per_second;
}

int check_option(MeasureType o, Benchmark *d)  {
	int i;
	if(d != NULL && d->bench_initialized) {
		for(i = 0; i < d->num_options; i++) {
			MeasureType tmp = d->options_selected[i];
			if(tmp == o) { return TRUE; }
		}
	}
	return FALSE;
}


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

static int PyStartBenchmark(Benchmark *data, PyObject *opList, int opListSize)
{
	int i;
	if(!PyList_Check(opList)) {
		PyErr_SetString(BenchmarkError, "did not provide a list.");
		return FALSE;
	}

	PyObject *tmpObj;
	char *s;
	if(data != NULL) {
		int cnt = 0;
		/* initialize */
		data->cpu_option = data->real_option = data->granular_option = FALSE;
		for(i = 0; i < opListSize; i++) {
			PyObject *item = PyList_GetItem(opList, i);
			if(PyBytes_CharmCheck(item)) {
				s = NULL;
				tmpObj = NULL;
				PyBytes_ToString2(s, item, tmpObj);
				if(strcmp(s, _CPUTIME_OPT) == 0) {
					debug("enabled cputime option!\n");
					data->options_selected[cnt] = CPU_TIME;
					data->cpu_option = TRUE;
				}
				else if(strcmp(s, _REALTIME_OPT) == 0) {
					debug("enabled realtime option!\n");
					data->options_selected[cnt] = REAL_TIME;
					data->real_option = TRUE;
				}
				else if(strcmp(s, _ADD_OPT) == 0) {
					debug("enabled add option!\n");
					data->options_selected[cnt] = ADDITION;
					data->op_add = 0;
				}
				else if(strcmp(s, _SUB_OPT) == 0) {
					debug("enabled sub option!\n");
					data->options_selected[cnt] = SUBTRACTION;
					data->op_sub = 0;
				}
				else if(strcmp(s, _MUL_OPT) == 0) {
					debug("enabled mul option!\n");
					data->options_selected[cnt] = MULTIPLICATION;
					data->op_mult = 0;
				}
				else if(strcmp(s, _DIV_OPT) == 0) {
					debug("enabled div option!\n");
					data->options_selected[cnt] = DIVISION;
					data->op_div = 0;
				}
				else if(strcmp(s, _EXP_OPT) == 0) {
					debug("enabled exp option!\n");
					data->options_selected[cnt] = EXPONENTIATION;
					data->op_exp = 0;
				}
				else if(strcmp(s, _PAIR_OPT) == 0) {
					debug("enabled pair option!\n");
					data->options_selected[cnt] = PAIRINGS;
					data->op_pair = 0;
				}
				else if(strcmp(s, _GRAN_OPT) == 0) {
					debug("enabled granular option!\n");
					data->options_selected[cnt] = GRANULAR;
					data->granular_option = TRUE;
				}
				else {
					debug("not a valid option.\n");
				}
				cnt++;
                if (tmpObj!=NULL)
				    Py_DECREF(tmpObj);
			}
		}
		// set size of list
		data->num_options = cnt;
		debug("num_options set: %d\n", data->num_options);
		data->bench_initialized = TRUE;
		data->bench_inprogress = TRUE;

		//set timers for time-based measures (reduces the overhead of timer)
		if(data->cpu_option) { data->start_clock = clock(); }
		if(data->real_option) { gettimeofday(&data->start_time, NULL); }
		return TRUE;
	}
	return FALSE;
}

static int PyEndBenchmark(Benchmark *data)
{
	gettimeofday(&data->stop_time, NULL); // stop real time clock
	data->stop_clock = clock(); // stop cpu time clock
	int i;
	if(data != NULL && data->bench_initialized) {
		debug("Results....\n");
		for(i = 0; i < data->num_options; i++) {
			MeasureType option = data->options_selected[i];
			debug("option => %d\n", option);
			switch(option) {
				case CPU_TIME:  // compute processor time or clocks per sec
								data->cpu_time_ms = ((double)(data->stop_clock - data->start_clock))/CLOCKS_PER_SEC;
								debug("CPU Time:\t%f\n", data->cpu_time_ms);
								break;
				case REAL_TIME:	debug("realtime option was set!\n");
								data->real_time_ms = CalcUsecs(&data->start_time, &data->stop_time);
								debug("Real Time:\t%f\n", data->real_time_ms);
								break;
				case ADDITION: 		debug("add operations:\t\t%d\n", data->op_add); break;
				case SUBTRACTION:  debug("sub operations:\t\t%d\n", data->op_sub); break;
				case MULTIPLICATION:  debug("mult operations:\t\t%d\n", data->op_mult); break;
				case DIVISION:	debug("div operations:\t\t%d\n", data->op_div); break;
				case EXPONENTIATION: debug("exp operations:\t\t%d\n", data->op_exp); break;
				case PAIRINGS: debug("pairing operations:\t\t%d\n", data->op_pair); break;
				case GRANULAR: debug("granular option was set!\n"); break;
				default: debug("not a valid option.\n"); break;
			}
		}
		data->bench_inprogress = FALSE;
		return TRUE;
	}
	return FALSE;
}

static int PyUpdateBenchmark(MeasureType option, Benchmark *data) {
	int i, errcode = FALSE, foundOption = FALSE;
	// make sure option is set in benchmark

	if(data != NULL && data->bench_initialized) {
		for(i = 0; i < data->num_options; i++) {
			MeasureType tmp = data->options_selected[i];
			if(tmp == option) { foundOption = TRUE; break; }
		}
	}

	// if so, just increment the corresponding operation option counter
	if(foundOption) {
		switch(option) {
		case ADDITION: 		 data->op_add++; break;
		case SUBTRACTION:  	 data->op_sub++; break;
		case MULTIPLICATION: data->op_mult++; break;
		case DIVISION:		 data->op_div++; break;
		case EXPONENTIATION: data->op_exp++; break;
		case PAIRINGS: 		 data->op_pair++; break;
		default: debug("not a valid option.\n");
					 break;
		}
		errcode = TRUE;
	}
	return errcode;
}

static int PyClearBenchmark(Benchmark *data) {
	if(data == NULL) { return FALSE; }

	data->bench_initialized = FALSE;
	data->identifier = -1;
	data->op_add = data->op_sub = data->op_mult = 0;
	data->op_div = data->op_exp = data->op_pair = 0;
	data->cpu_time_ms = 0.0;
	data->real_time_ms = 0.0;
	data->cpu_option = FALSE;
	data->real_option = FALSE;
	data->granular_option = FALSE;
	memset(data->options_selected, 0, MAX_MEASURE);
	debug("Initialized benchmark object.\n");
	return TRUE;
}

PyObject *Benchmark_print(Benchmark *self) {
	if(self != NULL) {
		PyObject *cpu = PyFloat_FromDouble(self->cpu_time_ms);
		PyObject *real = PyFloat_FromDouble(self->real_time_ms);
		PyObject *results = _PyUnicode_FromFormat("<--- Results --->\nCPU Time:  %Sms\nReal Time: %Ss\nAdd:\t%i\nSub:\t%i\nMul:\t%i\nDiv:\t%i\nExp:\t%i\nPair:\t%i\n",
								cpu, real, self->op_add, self->op_sub, self->op_mult, self->op_div, self->op_exp, self->op_pair);

		PyClearBenchmark(self);
		return results;
	}
	return _PyUnicode_FromString("Benchmark object has not been initialized properly.");
}

PyObject *GetResults(Benchmark *self) {
	if(self != NULL) {
		return Py_BuildValue("{sfsfsisisisisi}",
						"CpuTime", self->cpu_time_ms, "RealTime", self->real_time_ms,
						"Add", self->op_add, "Sub", self->op_sub, "Mul", self->op_mult,
						"Div", self->op_div, "Exp", self->op_exp);
	}

	return _PyUnicode_FromString("Benchmark object has not been initialized properly.");
}

PyObject *GetResultsWithPair(Benchmark *self) {
	if(self != NULL) {
		return Py_BuildValue("{sfsfsisisisisisi}",
						"CpuTime", self->cpu_time_ms, "RealTime", self->real_time_ms,
						"Add", self->op_add, "Sub", self->op_sub, "Mul", self->op_mult,
						"Div", self->op_div, "Exp", self->op_exp, "Pair", self->op_pair);
	}

	return _PyUnicode_FromString("Benchmark object has not been initialized properly.");
}


PyObject *Retrieve_result(Benchmark *self, char *option) {
	PyObject *result = NULL;

	if(self != NULL) {
		if(strcmp(option, _CPUTIME_OPT) == 0) {
			result = PyFloat_FromDouble(self->cpu_time_ms);
		}
		else if(strcmp(option, _REALTIME_OPT) == 0) {
			result = PyFloat_FromDouble(self->real_time_ms);
		}
		else if(strcmp(option, _ADD_OPT) == 0) {
			result = PyToLongObj(self->op_add);
		}
		else if(strcmp(option, _SUB_OPT) == 0) {
			result = PyToLongObj(self->op_sub);
		}
		else if(strcmp(option, _MUL_OPT) == 0) {
			result = PyToLongObj(self->op_mult);
		}
		else if(strcmp(option, _DIV_OPT) == 0) {
			result = PyToLongObj(self->op_div);
		}
		else if(strcmp(option, _EXP_OPT) == 0) {
			result = PyToLongObj(self->op_exp);
		}
		else if(strcmp(option, _PAIR_OPT) == 0) {
			result = PyToLongObj(self->op_pair);
		}
		else {
			debug("not a valid option.\n");
		}
	}
	return result;
}

#if PY_MAJOR_VERSION >= 3
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

#else
PyTypeObject BenchmarkType = {
	PyVarObject_HEAD_INIT(NULL, 0)
	"profile.Benchmark",       /*tp_name*/
	sizeof(Benchmark),         /*tp_basicsize*/
	0,                         /*tp_itemsize*/
	(destructor)Benchmark_dealloc, /*tp_dealloc*/
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
	"Benchmark objects",           /* tp_doc */
	0,		               /* tp_traverse */
	0,		               /* tp_clear */
	0,		       		   /* tp_richcompare */
	0,		               /* tp_weaklistoffset */
	0,		               /* tp_iter */
	0,		               /* tp_iternext */
	0,             		   /* tp_methods */
	0,             			   /* tp_members */
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

struct module_state {
	PyObject *error;
};

#if PY_MAJOR_VERSION >= 3
#define GETSTATE(m) ((struct module_state *) PyModule_GetState(m))
#else
#define GETSTATE(m) (&_state)
static struct module_state _state;
#endif

// benchmark type methods (module scope)
static PyMethodDef module_methods[] = {
		{NULL}
};

#if PY_MAJOR_VERSION >= 3
static int bm_traverse(PyObject *m, visitproc visit, void *arg) {
	Py_VISIT(GETSTATE(m)->error);
	return 0;
}

static int bm_clear(PyObject *m) {
	Py_CLEAR(GETSTATE(m)->error);
	return 0;
}

static struct PyModuleDef moduledef = {
		PyModuleDef_HEAD_INIT,
		"benchmark",
		NULL,
		sizeof(struct module_state),
		module_methods,
		NULL,
		bm_traverse,
		bm_clear,
		NULL
};

#define INITERROR return NULL
PyMODINIT_FUNC
PyInit_benchmark(void) 		{
#else
#define INITERROR return
void initbenchmark(void) 		{
#endif
	PyObject *module;
	static void *PyBenchmark_API[PyBenchmark_API_pointers];
	PyObject *api_object;

	if(PyType_Ready(&BenchmarkType) < 0) INITERROR;

#if PY_MAJOR_VERSION >= 3
  module = PyModule_Create(&moduledef);
#else
  module = Py_InitModule("benchmark", module_methods);
#endif
	if(module == NULL) INITERROR;

	struct module_state *st = GETSTATE(module);
	st->error = PyErr_NewException("benchmark.Error", NULL, NULL);
	if(st->error == NULL) {
		Py_DECREF(module);
		INITERROR;
	}
	BenchmarkError = st->error;

	/* initialize the c api pointer array - this is what other modules call */
	PyBenchmark_API[PyBenchmark_Start]  = (void *)PyStartBenchmark;
	PyBenchmark_API[PyBenchmark_End]    = (void *)PyEndBenchmark;
	PyBenchmark_API[PyBenchmark_Update] = (void *)PyUpdateBenchmark;
	PyBenchmark_API[PyBenchmark_Clear]  = (void *)PyClearBenchmark;

	api_object = (PyObject *) PyCapsule_New((void *) PyBenchmark_API,BENCHMARK_MOD_NAME, NULL);
	if(api_object != NULL) {
	  PyModule_AddObject(module, "_C_API", api_object);
	}

	Py_INCREF(&BenchmarkType);
	PyModule_AddObject(module, "Benchmark", (PyObject *) &BenchmarkType);
	// add exception handler
#if PY_MAJOR_VERSION >= 3
	return module;
#endif

}
