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
#else
	#define _PyLong_Check(o) (PyInt_Check(o) || PyLong_Check(o))
	#define ConvertToInt(o) PyInt_AsLong(o)
#endif

// define new benchmark type for benchmark module
PyTypeObject BenchmarkType;
// define new benchmark error type (will be used for notifying errors)
PyObject *BenchmarkError;
// define a macro to help determine whether an object is of benchmark type
#define PyBenchmark_Check(obj) PyObject_TypeCheck(obj, &BenchmarkType)
/* header file for benchmark module */
#define MAX_MEASURE 10
enum Measure {CPU_TIME = 0, REAL_TIME, NATIVE_TIME, ADDITION, SUBTRACTION, MULTIPLICATION, DIVISION, EXPONENTIATION, PAIRINGS, NONE};
typedef enum Measure MeasureType;

// for recording native time
#define START_CLOCK(object) \
if(object->native_option) { \
	PyStartTBenchmark(NATIVE_TIME, object); \
}

#define STOP_CLOCK(object) \
if(object->native_option) { \
	PyStopTBenchmark(NATIVE_TIME, object); \
}

typedef struct {
	PyObject_HEAD
	int identifier;
//	time_t start_time, stop_time; // track real time
	struct timeval start_time, stop_time, native_time; // track real time
	clock_t start_clock, stop_clock; // track cpu time
	// Operations *op_ptr; // track various operations
	int op_add, op_sub, op_mult, op_div;
	int op_exp, op_pair;
	double native_time_ms, cpu_time_ms, real_time_ms;
	int num_options; // track num options for a particular benchmark
	MeasureType options_selected[MAX_MEASURE]; // measurement options selected
	int cpu_option, native_option, real_option;
	int bench_initialized;
} Benchmark;

// PyMethodDef Benchmark_methods[];
PyObject *Benchmark_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
void Benchmark_dealloc(Benchmark *self);
int Benchmark_init(Benchmark *self, PyObject *args, PyObject *kwds);
PyObject *Benchmark_print(Benchmark *self);
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

#define START_NATIVE(bench)  \
    if(bench->bench_initialized && bench->native_option) { \
	PyStartTBenchmark(NATIVE_TIME, bench); }

#define STOP_NATIVE(bench)  \
	if(bench->bench_initialized && bench->native_option) {  \
	PyStopTBenchmark(NATIVE_TIME, bench); }

#define UPDATE_BENCHMARK(option, bench)   \
	if(bench->bench_initialized) {	   \
	PyUpdateBenchmark(option, bench); }


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
#define InitBenchmark_CAPI(func_name, bench, id)   \
static PyObject *func_name(PyObject *self, PyObject *args) {  \
	if(bench->bench_initialized == FALSE) {   						\
		PyClearBenchmark(bench);									\
		bench->bench_initialized = TRUE;							\
		bench->identifier = id;										\
		debug("Initialized benchmark object.\n");					\
		return Py_BuildValue("i", bench->identifier);	}			\
	debug("Benchmark already initialized.\n");						\
	Py_RETURN_FALSE;				}

#define StartBenchmark_CAPI(func_name, bench) 	\
static PyObject *func_name(PyObject *self, PyObject *args) { \
	PyObject *list = NULL; int id = -1;								\
	if(PyArg_ParseTuple(args, "iO", &id, &list)) {					\
		if(bench->bench_initialized && id == bench->identifier) {	\
			size_t size = PyList_Size(list);						\
			PyStartBenchmark(bench, list, size);					\
			debug("list size => %zd\n", size);						\
			debug("benchmark enabled and initialized!!!\n");		\
			Py_RETURN_TRUE;  }										\
		Py_RETURN_FALSE; 	}										\
	return NULL;	}

#define EndBenchmark_CAPI(func_name, bench)		\
static PyObject *func_name(PyObject *self, PyObject *args) {		\
	int id = -1;													\
	if(PyArg_ParseTuple(args, "i", &id)) {							\
		if(id == bench->identifier) {								\
			PyEndBenchmark(bench);									\
			bench->bench_initialized = FALSE;						\
			Py_RETURN_TRUE;		}									\
		debug("Invalid benchmark idenifier.\n");		}			\
	Py_RETURN_FALSE;			}

#define GetBenchmark_CAPI(func_name, bench)		\
static PyObject *_get_benchmark(PyObject *self, PyObject *args) {	\
	int id = -1;													\
	MeasureType option = NONE;										\
	if(PyArg_ParseTuple(args, "i|i", &id, &option)) {					\
		if(option != NONE) return Retrieve_result(dBench, option);		\
		else if(id == bench->identifier) return Benchmark_print(dBench); \
		Py_RETURN_FALSE;	}										\
	Py_RETURN_FALSE;	}



/* end - api helper functions */

static int import_benchmark(void)
{
	PyBenchmark_API = (void **) PyCapsule_Import("benchmark._C_API", 1);
	return (PyBenchmark_API != NULL) ? 0 : -1;
}

#endif

#ifdef __cplusplus
}
#endif

#endif /* PY_BENCHMARK_H_ */
