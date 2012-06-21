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
	#define PyToLongObj(o) PyLong_FromLong(o)
#else
	#define _PyLong_Check(o) (PyInt_Check(o) || PyLong_Check(o))
	#define ConvertToInt(o) PyInt_AsLong(o)
	#define PyToLongObj(o) PyInt_FromSize_t(o)
#endif

//#define BENCHMARK_MOD_NAME "charm.core.benchmark._C_API"

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
double CalcUsecs(struct timeval *start, struct timeval *stop);

/* c api functions */
//#define PyBenchmark_Start 		  0
//#define PyBenchmark_End 		  1
//#define PyBenchmark_Update		  2
//#define PyBenchmark_StartT		  3
//#define PyBenchmark_StopT	      4
//#define PyBenchmark_Clear		  5

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


//#ifdef BENCHMARK_MODULE
///* This section is used when compiling benchmarkmodule.c */
//static int PyStartBenchmark(Benchmark *data, PyObject *opList, int opListSize);
//static int PyEndBenchmark(Benchmark *data);
//static int PyUpdateBenchmark(MeasureType option, Benchmark *data);
//static int PyStartTBenchmark(MeasureType option, Benchmark *data);
//static int PyStopTBenchmark(MeasureType option, Benchmark *data);
//static int PyClearBenchmark(Benchmark *data);
//
//#else

/* This section is used in modules that use benchmarkmodule's API
 * e.g. pairingmath, integermath, etc.
 */
//static void **PyBenchmark_API;
//
//#define PyStartBenchmark (*(int (*)(Benchmark *data, PyObject *opList, int opListSize)) PyBenchmark_API[PyBenchmark_Start])
//#define PyEndBenchmark (*(int (*)(Benchmark *data)) PyBenchmark_API[PyBenchmark_End])
//#define PyUpdateBenchmark (*(int (*)(MeasureType option, Benchmark *data)) PyBenchmark_API[PyBenchmark_Update])
//#define PyStartTBenchmark (*(int (*)(MeasureType option, Benchmark *data)) PyBenchmark_API[PyBenchmark_StartT])
//#define PyStopTBenchmark (*(int (*)(MeasureType option, Benchmark *data)) PyBenchmark_API[PyBenchmark_StopT])
//#define PyClearBenchmark (*(int (*)(Benchmark *data)) PyBenchmark_API[PyBenchmark_Clear])
static int PyStartBenchmark(Benchmark *data, PyObject *opList, int opListSize);
static int PyEndBenchmark(Benchmark *data);
static int PyUpdateBenchmark(MeasureType option, Benchmark *data);
static int PyStartTBenchmark(MeasureType option, Benchmark *data);
static int PyStopTBenchmark(MeasureType option, Benchmark *data);
static int PyClearBenchmark(Benchmark *data);


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
		if(option != NONE) return Retrieve_result(dBench, option); \
		else if(id == bench->identifier) return Benchmark_print(dBench); \
		Py_RETURN_FALSE;	}		\
	Py_RETURN_FALSE;	}

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


PyObject *Benchmark_print(Benchmark *self) {
	if(self != NULL) {
		PyObject *cpu = PyFloat_FromDouble(self->cpu_time_ms);
		PyObject *native = PyFloat_FromDouble(self->native_time_ms);
		PyObject *real = PyFloat_FromDouble(self->real_time_ms);
		PyObject *results = PyUnicode_FromFormat("<--- Results --->\nCPU Time:  %Sms\nReal Time: %Ss\nNative Time: %Ss\nAdd:\t%i\nSub:\t%i\nMul:\t%i\nDiv:\t%i\nExp:\t%i\nPair:\t%i\n",
								cpu, real, native, self->op_add, self->op_sub, self->op_mult, self->op_div, self->op_exp, self->op_pair);

		PyClearBenchmark(self);
		return results;
	}
	return PyUnicode_FromString("Benchmark object has not been initialized properly.");
}

PyObject *GetResults(Benchmark *self) {
	if(self != NULL) {
		PyObject *resultDict = PyDict_New();
		PyDict_SetItem(resultDict, Py_BuildValue("i", CPU_TIME), PyFloat_FromDouble(self->cpu_time_ms));
		PyDict_SetItem(resultDict, Py_BuildValue("i", REAL_TIME), PyFloat_FromDouble(self->real_time_ms));
		PyDict_SetItem(resultDict, Py_BuildValue("i", NATIVE_TIME), PyFloat_FromDouble(self->native_time_ms));
		PyDict_SetItem(resultDict, Py_BuildValue("i", ADDITION), Py_BuildValue("i", self->op_add));
		PyDict_SetItem(resultDict, Py_BuildValue("i", SUBTRACTION), Py_BuildValue("i", self->op_sub));
		PyDict_SetItem(resultDict, Py_BuildValue("i", MULTIPLICATION), Py_BuildValue("i", self->op_mult));
		PyDict_SetItem(resultDict, Py_BuildValue("i", DIVISION), Py_BuildValue("i", self->op_div));
		PyDict_SetItem(resultDict, Py_BuildValue("i", EXPONENTIATION), Py_BuildValue("i", self->op_exp));
		PyDict_SetItem(resultDict, Py_BuildValue("i", PAIRINGS), Py_BuildValue("i", self->op_pair));

//		PyClearBenchmark(self); // wipe benchmark data
		return resultDict;
	}

	return PyUnicode_FromString("Benchmark object has not been initialized properly.");
}

PyObject *Retrieve_result(Benchmark *self, MeasureType option) {
	PyObject *result = NULL;
	if(self != NULL) {

		switch(option) {
			case REAL_TIME:	result = PyFloat_FromDouble(self->real_time_ms); break;
			case NATIVE_TIME: result = PyFloat_FromDouble(self->native_time_ms); break;
			case CPU_TIME: result = PyFloat_FromDouble(self->cpu_time_ms); break;

			case ADDITION: 	result = PyToLongObj(self->op_add); break;
			case SUBTRACTION:  	result = PyToLongObj(self->op_sub); break;
			case MULTIPLICATION: result = PyToLongObj(self->op_mult); break;
			case DIVISION:		 result = PyToLongObj(self->op_div); break;
			case EXPONENTIATION: result = PyToLongObj(self->op_exp); break;
			case PAIRINGS: 		 result = PyToLongObj(self->op_pair); break;

			default: debug("not a valid option.\n");
					 break;
		}
	}
	return result;
}

static int PyStartTBenchmark(MeasureType option, Benchmark *data)
{
	if(data->native_option) {
		if(option == NATIVE_TIME) // last thing we do before returning
			return gettimeofday(&data->native_time, NULL);
	}
	return FALSE;
}

static int PyStopTBenchmark(MeasureType option, Benchmark *data)
{
	struct timeval stop; gettimeofday(&stop, NULL);
	if(data->native_option) {
		if(option == NATIVE_TIME)
			data->native_time_ms += CalcUsecs(&data->native_time,  &stop);
			// data->aux_time_ms += ((double)(stop - data->aux_time))/CLOCKS_PER_SEC;
		return TRUE;
	}
	return FALSE;
}

static int PyStartBenchmark(Benchmark *data, PyObject *opList, int opListSize)
{
	int i;
	if(!PyList_Check(opList)) {
		PyErr_SetString(BenchmarkError, "did not provide a list.");
		return FALSE;
	}

	if(data != NULL) {
		int cnt = 0;
		for(i = 0; i < opListSize; i++) {
			PyObject *item = PyList_GetItem(opList, i);
			if(!_PyLong_Check(item)) continue;
			MeasureType option = ConvertToInt(item);
			if(option > 0 && option < NONE) {
				data->options_selected[cnt] = option;
				cnt++;
				debug("Option '%d' selected...\n", option);
				switch(option) {
					case CPU_TIME:  data->cpu_option = TRUE; break;
					case REAL_TIME:	data->real_option = TRUE; break;
					case NATIVE_TIME: data->native_option = TRUE; break;
					case ADDITION: 		data->op_add = 0; break;
					case SUBTRACTION:  data->op_sub = 0; break;
					case MULTIPLICATION:  data->op_mult = 0; break;
					case DIVISION:	data->op_div = 0; break;
					case EXPONENTIATION: data->op_exp = 0; break;
					case PAIRINGS: data->op_pair = 0; break;
					case GRANULAR: data->granular_option = TRUE; data->gran_init(); break; // data->gran_init();
					default: debug("not a valid option.\n");
							 break;
				}
			}
		}
		// set size of list
		data->num_options = cnt;
		debug("num_options set: %d\n", data->num_options);
		data->bench_initialized = TRUE;

		//set timers for time-based measures (reduces the overhead of timer)
		if(data->cpu_option) { data->start_clock = clock(); }
		if(data->native_option) { gettimeofday(&data->native_time, NULL); }
		if(data->real_option) { gettimeofday(&data->start_time, NULL); }
		return TRUE;
	}
	return FALSE;
}

static int PyEndBenchmark(Benchmark *data)
{
	struct timeval stop_t; gettimeofday(&stop_t, NULL); // stop real time clock
	int i, stop_c = clock();
	if(data != NULL && data->bench_initialized) {
		debug("Results....\n");
		for(i = 0; i < data->num_options; i++) {
			MeasureType option = data->options_selected[i];
			debug("option => %d\n", option);
			switch(option) {
				case CPU_TIME:  data->stop_clock = stop_c;
								// compute processor time or clocks per sec
								data->cpu_time_ms = ((double)(data->stop_clock - data->start_clock))/CLOCKS_PER_SEC;
								debug("CPU Time:\t%f\n", data->cpu_time_ms);
								break;
				case NATIVE_TIME: debug("Native time in C:\t%f\n", data->native_time_ms); break;
				case REAL_TIME:	// time(&data->stop_time);
								// data->real_time_ms = difftime(stop_t, data->start_time);
								data->real_time_ms = CalcUsecs(&data->start_time, &stop_t);
								debug("Real Time:\t%f\n", data->real_time_ms);
								break;
				case ADDITION: 		debug("add operations:\t\t%d\n", data->op_add); break;
				case SUBTRACTION:  debug("sub operations:\t\t%d\n", data->op_sub); break;
				case MULTIPLICATION:  debug("mult operations:\t\t%d\n", data->op_mult); break;
				case DIVISION:	debug("div operations:\t\t%d\n", data->op_div); break;
				case EXPONENTIATION: debug("exp operations:\t\t%d\n", data->op_exp); break;
				case PAIRINGS: debug("pairing operations:\t\t%d\n", data->op_pair); break;
				case GRANULAR: debug("disabling granular measurement option.\n"); break;
				default: debug("not a valid option.\n"); break;
			}
		}
		data->bench_initialized = FALSE;
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
	data->native_time_ms = data->cpu_time_ms = data->real_time_ms = 0.0;
	if(data->granular_option == TRUE) data->gran_init();
	data->native_option = data->cpu_option = data->real_option = data->granular_option = FALSE;
	debug("Initialized benchmark object.\n");
	return TRUE;
}

double CalcUsecs(struct timeval *start, struct timeval *stop) {
	double usec_per_second = 1000000;
	double result = usec_per_second * (stop->tv_sec - start->tv_sec);

	if(stop->tv_usec >= stop->tv_usec) {
		result += (stop->tv_usec - start->tv_usec);
	}
	else {
		result -= (start->tv_usec - stop->tv_usec);
	}

//	if(result < 0) {
//		printf("start secs => '%ld' and usecs => '%d'\n", start->tv_sec, start->tv_usec);
//		printf("stop secs => '%ld' and usecs => '%d'\n", stop->tv_sec, stop->tv_usec);
//	}

	return result / usec_per_second;
}

//int check_option(MeasureType o, Benchmark *d)  {
//	int i;
//	if(d != NULL && d->bench_initialized) {
//		for(i = 0; i < d->num_options; i++) {
//			MeasureType tmp = d->options_selected[i];
//			if(tmp == o) { return TRUE; }
//		}
//	}
//	return FALSE;
//}

#define ADD_BENCHMARK_OPTIONS(module)	\
	PyModule_AddIntConstant(module, "CpuTime", CPU_TIME);		\
	PyModule_AddIntConstant(module, "RealTime", REAL_TIME);		\
	PyModule_AddIntConstant(module, "NativeTime", NATIVE_TIME);	\
	PyModule_AddIntConstant(module, "Add", ADDITION);			\
	PyModule_AddIntConstant(module, "Sub", SUBTRACTION);		\
	PyModule_AddIntConstant(module, "Mul", MULTIPLICATION);		\
	PyModule_AddIntConstant(module, "Div", DIVISION);			\
	PyModule_AddIntConstant(module, "Exp", EXPONENTIATION);


/* end - api helper functions */

/*
static int import_benchmark(void)
{
	PyBenchmark_API = (void **) PyCapsule_Import(BENCHMARK_MOD_NAME, 1);
	return (PyBenchmark_API != NULL) ? 0 : -1;
}
*/
//#endif

#ifdef __cplusplus
}
#endif

#endif /* PY_BENCHMARK_H_ */
