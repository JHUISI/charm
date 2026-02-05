#ifndef BENCHMARK_UTIL_H
#define BENCHMARK_UTIL_H

// for multiplicative notation
#define Op_MUL(op_var_type, op_group_type, group, bench_obj)  \
	if(op_var_type == MULTIPLICATION && op_group_type == group)      \
		((Operations *) bench_obj)->mul_ ##group += 1;

#define Op_DIV(op_var_type, op_group_type, group, bench_obj)  \
	if(op_var_type == DIVISION && op_group_type == group)      \
		((Operations *) bench_obj)->div_ ##group += 1;

// for additive notation
#define Op_ADD(op_var_type, op_group_type, group, bench_obj)  \
	if(op_var_type == ADDITION && op_group_type == group)      \
		((Operations *) bench_obj)->add_ ##group += 1;

#define Op_SUB(op_var_type, op_group_type, group, bench_obj)  \
	if(op_var_type == SUBTRACTION && op_group_type == group)      \
		((Operations *) bench_obj)->sub_ ##group += 1;

// exponentiation
#define Op_EXP(op_var_type, op_group_type, group, bench_obj)  \
	if(op_var_type == EXPONENTIATION && op_group_type == group)      \
		((Operations *) bench_obj)->exp_ ##group += 1;

#define UPDATE_BENCH(op_type, elem_type, gobj) \
	if(gobj->dBench != NULL && gobj->dBench->granular_option == TRUE && elem_type != NONE_G) {		\
		Update_Op(MUL, op_type, elem_type, gobj->gBench) \
		Update_Op(DIV, op_type, elem_type, gobj->gBench) \
		Update_Op(ADD, op_type, elem_type, gobj->gBench) \
		Update_Op(SUB, op_type, elem_type, gobj->gBench) \
		Update_Op(EXP, op_type, elem_type, gobj->gBench) \
	}		\
	UPDATE_BENCHMARK(op_type, gobj->dBench);

#define CLEAR_DBENCH(bench_obj, group)   \
	((Operations *) bench_obj)->mul_ ##group = 0;	\
	((Operations *) bench_obj)->exp_ ##group = 0;	\
	((Operations *) bench_obj)->div_ ##group = 0;	\
	((Operations *) bench_obj)->add_ ##group = 0;	\
	((Operations *) bench_obj)->sub_ ##group = 0;	\

#define GetField(count, type, group, bench_obj)  \
	if(type == MULTIPLICATION) count = (((Operations *) bench_obj)->mul_ ##group ); \
	else if(type == DIVISION) count = (((Operations *) bench_obj)->div_ ##group );	\
	else if(type == ADDITION) count = (((Operations *) bench_obj)->add_ ##group ); \
	else if(type == SUBTRACTION) count = (((Operations *) bench_obj)->sub_ ##group ); \
	else if(type == EXPONENTIATION) count = (((Operations *) bench_obj)->exp_ ##group );

#define ClearBenchmark(data) \
	data->op_add = data->op_sub = data->op_mult = 0; \
	data->op_div = data->op_exp = data->op_pair = 0; \
	data->cpu_time_ms = 0.0;	\
	data->real_time_ms = 0.0;	\
	data->cpu_option = FALSE;	\
	data->real_option = FALSE;	\
	data->granular_option = FALSE;


#endif
