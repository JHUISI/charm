/*
 * benchmarkmodule.h
 */
#ifndef Py_BENCHMARKMODULE_H_
#define Py_BENCHMARKMODULE_H_
#ifdef __cplusplus
extern "C" {
#endif

#include <Python.h>
#include <structmember.h>
#include <sys/time.h>

// set default if not passed in by compiler
//#ifndef BENCHMARK_ENABLED
//#define BENCHMARK_ENABLED 1
//#endif
//#define DEBUG   1
#define TRUE	1
#define FALSE	0

#ifdef DEBUG
#define debug(...)	printf("DEBUG: "__VA_ARGS__)
#else
#define debug(...)
#endif

#if PY_MAJOR_VERSION >= 3
	#define _PyLong_Check(o1) PyLong_Check(o1)
	#define ConvertToInt(o) PyLong_AsLong(o)
	#define PyToLongObj(o) PyLong_FromLong(o)
#else
	#define _PyLong_Check(o) (PyInt_Check(o) || PyLong_Check(o))
	#define ConvertToInt(o) PyInt_AsLong(o)
	#define PyToLongObj(o) PyInt_FromSize_t(o)
#endif

#define BENCHMARK_MOD_NAME "charm.core.benchmark._C_API"

// define new benchmark type for benchmark module
PyTypeObject BenchmarkType;
// define new benchmark error type (will be used for notifying errors)
PyObject *BenchmarkError;
// define a macro to help determine whether an object is of benchmark type
#define PyBenchmark_Check(obj) PyObject_TypeCheck(obj, &BenchmarkType)
/* header file for benchmark module */
#define MAX_MEASURE 10
enum Measure {CPU_TIME = 0, REAL_TIME, NATIVE_TIME, ADDITION, SUBTRACTION, MULTIPLICATION, DIVISION, EXPONENTIATION, PAIRINGS, GRANULAR, NONE};
typedef enum Measure MeasureType;

// for recording native time
#ifdef BENCHMARK_ENABLED
#define START_CLOCK(object) \
if(object->native_option) { \
	PyStartTBenchmark(NATIVE_TIME, object); \
}

#define STOP_CLOCK(object) \
if(object->native_option) { \
	PyStopTBenchmark(NATIVE_TIME, object); \
}
#else

#define START_CLOCK(object) /* ... */
#define STOP_CLOCK(object) /* ... */

#endif

typedef struct {
	PyObject_HEAD
	int identifier;

	struct timeval start_time, stop_time, native_time; // track real time
	clock_t start_clock, stop_clock; // track cpu time
	// Operations *op_ptr; // track various operations
	int op_add, op_sub, op_mult, op_div;
	int op_exp, op_pair;
	double native_time_ms, cpu_time_ms, real_time_ms;
	int num_options; // track num options for a particular benchmark
	MeasureType options_selected[MAX_MEASURE]; // measurement options selected
	int cpu_option, native_option, real_option, granular_option;
	int bench_initialized;
	void *data_ptr;
	void (*gran_init)(void);
} Benchmark;

// PyMethodDef Benchmark_methods[];
PyObject *Benchmark_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
void Benchmark_dealloc(Benchmark *self);
int Benchmark_init(Benchmark *self, PyObject *args, PyObject *kwds);
PyObject *Benchmark_print(Benchmark *self);
PyObject *GetResults(Benchmark *self);
PyObject *Retrieve_result(Benchmark *self, MeasureType option);

/* c api functions */
#define PyBenchmark_Start 		  0
#define PyBenchmark_End 		  1
#define PyBenchmark_Update		  2
#define PyBenchmark_StartT		  3
#define PyBenchmark_StopT	      4
#define PyBenchmark_Clear		  5

/* total number of C api pointers? */
#define PyBenchmark_API_pointers 6

#ifdef BENCHMARK_ENABLED
#define START_NATIVE(bench)  \
    if(bench->bench_initialized && bench->native_option) { \
	PyStartTBenchmark(NATIVE_TIME, bench); }

#define STOP_NATIVE(bench)  \
	if(bench->bench_initialized && bench->native_option) {  \
	PyStopTBenchmark(NATIVE_TIME, bench); }

#define UPDATE_BENCHMARK(option, bench)   \
	if(bench->bench_initialized) {	   \
	PyUpdateBenchmark(option, bench); }

#else

#define START_NATIVE(bench)  /* ... */
#define STOP_NATIVE(bench) /* ... */
#define UPDATE_BENCHMARK(option, bench) /* ... */

#endif

#ifdef BENCHMARK_MODULE
/* This section is used when compiling benchmarkmodule.c */
static int PyStartBenchmark(Benchmark *data, PyObject *opList, int opListSize);
static int PyEndBenchmark(Benchmark *data);
static int PyUpdateBenchmark(MeasureType option, Benchmark *data);
static int PyStartTBenchmark(MeasureType option, Benchmark *data);
static int PyStopTBenchmark(MeasureType option, Benchmark *data);
static int PyClearBenchmark(Benchmark *data);

#else

/* This section is used in modules that use benchmarkmodule's API
 * e.g. pairingmath, integermath, etc.
 */
static void **PyBenchmark_API;

#define PyStartBenchmark (*(int (*)(Benchmark *data, PyObject *opList, int opListSize)) PyBenchmark_API[PyBenchmark_Start])
#define PyEndBenchmark (*(int (*)(Benchmark *data)) PyBenchmark_API[PyBenchmark_End])
#define PyUpdateBenchmark (*(int (*)(MeasureType option, Benchmark *data)) PyBenchmark_API[PyBenchmark_Update])
#define PyStartTBenchmark (*(int (*)(MeasureType option, Benchmark *data)) PyBenchmark_API[PyBenchmark_StartT])
#define PyStopTBenchmark (*(int (*)(MeasureType option, Benchmark *data)) PyBenchmark_API[PyBenchmark_StopT])
#define PyClearBenchmark (*(int (*)(Benchmark *data)) PyBenchmark_API[PyBenchmark_Clear])

/* start - api helper functions */
#define InitBenchmark_CAPI(func_name, bench, id) \
static PyObject *func_name(PyObject *self, PyObject *args) { 	\
	if(bench->bench_initialized == FALSE) {   		\
		bench->bench_initialized = TRUE;		\
		bench->identifier = id;				\
		debug("Initialized benchmark object.\n");	\
		return Py_BuildValue("i", bench->identifier); }	\
	debug("Benchmark already initialized.\n");	\
	Py_RETURN_FALSE;				}

#define StartBenchmark_CAPI(func_name, bench) 	\
static PyObject *func_name(PyObject *self, PyObject *args) { \
	PyObject *list = NULL; int id = -1;			\
	if(PyArg_ParseTuple(args, "iO", &id, &list)) {		\
		if(bench->bench_initialized && id == bench->identifier) { \
			size_t size = PyList_Size(list);	\
			PyStartBenchmark(bench, list, size);	\
		debug("list size => %zd\n", size);		\
		debug("benchmark enabled and initialized!!!\n");\
		Py_RETURN_TRUE;  }				\
		Py_RETURN_FALSE; 	}			\
	return NULL;	}

#define EndBenchmark_CAPI(func_name, bench)		\
static PyObject *func_name(PyObject *self, PyObject *args) { \
	int id = -1;					\
	if(PyArg_ParseTuple(args, "i", &id)) {		\
		if(id == bench->identifier) {		\
			PyEndBenchmark(bench);		\
			bench->bench_initialized = FALSE; \
			Py_RETURN_TRUE;		}	\
	debug("Invalid benchmark idenifier.\n"); } 	\
	Py_RETURN_FALSE;			}

#define GetBenchmark_CAPI(func_name, bench) \
static PyObject *func_name(PyObject *self, PyObject *args) { \
	int id = -1;					\
	MeasureType option = NONE;			\
	if(PyArg_ParseTuple(args, "i|i", &id, &option)) { \
		return Retrieve_result(dBench, option); \
		Py_RETURN_FALSE;	}		\
	Py_RETURN_FALSE;	}

// 		else if(id == bench->identifier) return Benchmark_print(dBench);

#define GetAllBenchmarks_CAPI(func_name, bench)	\
static PyObject *func_name(PyObject *self, PyObject *args) { \
	int id = -1;					\
	if(PyArg_ParseTuple(args, "i", &id)) {		\
		if(id == bench->identifier)		\
			return GetResults(bench);	\
	debug("Invalid benchmark idenifier.\n"); }	\
	Py_RETURN_FALSE;	}

#define ClearBenchmarks_CAPI(func_name, bench) \
static PyObject *func_name(PyObject *self, PyObject *args) { \
	int id = -1;					\
	if(PyArg_ParseTuple(args, "i", &id)) {		\
		if(id == bench->identifier)	{	\
			PyClearBenchmark(bench);	\
			Py_RETURN_TRUE;    } 		\
	debug("Invalid benchmark idenifier.\n"); }	\
	Py_RETURN_FALSE;	}


#define InitClear(bench)  \
	bench->bench_initialized = bench->granular_option = FALSE; \
	bench->op_add = bench->op_sub = bench->op_mult = 0;	\
	bench->op_div = bench->op_exp = bench->op_pair = 0; \
	bench->native_time_ms = bench->cpu_time_ms = bench->real_time_ms = 0.0;

#define ADD_BENCHMARK_OPTIONS(m)		\
	PyModule_AddIntConstant(m, "CpuTime", CPU_TIME);		\
	PyModule_AddIntConstant(m, "RealTime", REAL_TIME);		\
	PyModule_AddIntConstant(m, "NativeTime", NATIVE_TIME);	\
	PyModule_AddIntConstant(m, "Add", ADDITION);			\
	PyModule_AddIntConstant(m, "Sub", SUBTRACTION);		\
	PyModule_AddIntConstant(m, "Mul", MULTIPLICATION);		\
	PyModule_AddIntConstant(m, "Div", DIVISION);			\
	PyModule_AddIntConstant(m, "Exp", EXPONENTIATION);


/* end - api helper functions */

static int import_benchmark(void)
{
	PyBenchmark_API = (void **) PyCapsule_Import(BENCHMARK_MOD_NAME, 1);
	return (PyBenchmark_API != NULL) ? 0 : -1;
}

#endif

#ifdef __cplusplus
}
#endif

#endif /* PY_BENCHMARK_H_ */
