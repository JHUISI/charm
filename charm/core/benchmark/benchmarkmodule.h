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
//#define BENCHMARK_ENABLED 1vi bad
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
	/* check for both unicode and bytes objects */
	#define PyBytes_CharmCheck(obj) PyUnicode_Check(obj) || PyBytes_Check(obj)
	/* if unicode then add extra conversion step. two possibilities: unicode or bytes */
	#define PyBytes_ToString2(a, obj, tmp_obj)	\
if(PyBytes_Check(obj)) { a = PyBytes_AsString(obj); } \
else if(PyUnicode_Check(obj)) { tmp_obj = PyUnicode_AsUTF8String(obj); a = PyBytes_AsString(tmp_obj); }	\
else { tmp_obj = PyObject_Str(obj); a = PyBytes_AsString(tmp_obj); }

  #define _PyUnicode_FromFormat PyUnicode_FromFormat
  #define _PyUnicode_FromString PyUnicode_FromString
#else
	/* python 2.x definitions */
  #define _PyLong_Check(o) (PyInt_Check(o) || PyLong_Check(o))
  #define ConvertToInt(o) PyInt_AsLong(o)
  #define PyToLongObj(o) PyInt_FromSize_t(o)
  #define _PyUnicode_FromFormat PyString_FromFormat
  #define _PyUnicode_FromString PyString_FromString
  /* treat everything as string in 2.x */
  #define PyBytes_CharmCheck(obj)	PyUnicode_Check(obj) || PyString_Check(obj)
  #define PyBytes_ToString2(a, obj, tmpObj) a = PyString_AsString(obj);

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
#define _CPUTIME_OPT 	"CpuTime"
#define _REALTIME_OPT 	"RealTime"
#define _ADD_OPT		"Add"
#define _SUB_OPT		"Sub"
#define _MUL_OPT		"Mul"
#define _DIV_OPT		"Div"
#define _EXP_OPT		"Exp"
#define _PAIR_OPT		"Pair"
#define _GRAN_OPT		"Granular"

typedef struct {
	PyObject_HEAD
	struct timeval start_time, stop_time, native_time; // track real time
	clock_t start_clock, stop_clock; // track cpu time

	int op_add, op_sub, op_mult, op_div;
	int op_exp, op_pair;
	double cpu_time_ms, real_time_ms;
	int num_options; // track num options for a particular benchmark
	MeasureType options_selected[MAX_MEASURE+1]; // measurement options selected
	int cpu_option, real_option, granular_option;
	int identifier;
	int bench_initialized, bench_inprogress;
} Benchmark;

// PyMethodDef Benchmark_methods[];
PyObject *Benchmark_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
void Benchmark_dealloc(Benchmark *self);
int Benchmark_init(Benchmark *self, PyObject *args, PyObject *kwds);

PyObject *Benchmark_print(Benchmark *self);
PyObject *GetResults(Benchmark *self);
PyObject *GetResultsWithPair(Benchmark *self);
PyObject *Retrieve_result(Benchmark *self, char *option);

/* c api functions */
#define PyBenchmark_Start 		  0
#define PyBenchmark_End 		  1
#define PyBenchmark_Update		  2
#define PyBenchmark_Clear		  3

/* total number of C api pointers? */
#define PyBenchmark_API_pointers 4

#ifdef BENCHMARK_ENABLED
#define UPDATE_BENCHMARK(option, bench)   \
	if(bench != NULL && bench->bench_initialized == TRUE) {	   \
	PyUpdateBenchmark(option, bench); }

#else
#define UPDATE_BENCHMARK(option, bench) /* ... */
#endif

#ifdef BENCHMARK_MODULE
/* This section is used when compiling benchmarkmodule.c */
static int PyStartBenchmark(Benchmark *data, PyObject *opList, int opListSize);
static int PyEndBenchmark(Benchmark *data);
static int PyUpdateBenchmark(MeasureType option, Benchmark *data);
static int PyClearBenchmark(Benchmark *data);

#else

/* This section is used in modules that use benchmarkmodule's API
 * e.g. pairingmath, integermath, etc.
 */
static void **PyBenchmark_API;

#define PyStartBenchmark (*(int (*)(Benchmark *data, PyObject *opList, int opListSize)) PyBenchmark_API[PyBenchmark_Start])
#define PyEndBenchmark (*(int (*)(Benchmark *data)) PyBenchmark_API[PyBenchmark_End])
#define PyUpdateBenchmark (*(int (*)(MeasureType option, Benchmark *data)) PyBenchmark_API[PyBenchmark_Update])
#define PyClearBenchmark (*(int (*)(Benchmark *data)) PyBenchmark_API[PyBenchmark_Clear])

#define ADD_BENCHMARK_OPTIONS(m)		\
	PyModule_AddStringConstant(m, "CpuTime", "CpuTime");		\
	PyModule_AddStringConstant(m, "RealTime", "RealTime");		\
	PyModule_AddStringConstant(m, "Add", "Add");			\
	PyModule_AddStringConstant(m, "Sub", "Sub");		\
	PyModule_AddStringConstant(m, "Mul", "Mul");		\
	PyModule_AddStringConstant(m, "Div", "Div");			\
	PyModule_AddStringConstant(m, "Exp", "Exp");

/* end - api helper functions */

static int import_benchmark(void)
{
	// PyBenchmark_API = (void **) PyCapsule_Import(BENCHMARK_MOD_NAME, 1);
  PyBenchmark_API = (void **) PyCapsule_Import(BENCHMARK_MOD_NAME, 0); // 0 = enable tracing
  return (PyBenchmark_API != NULL) ? 0 : -1;
}

#endif

#ifdef __cplusplus
}
#endif

#endif /* PY_BENCHMARK_H_ */
