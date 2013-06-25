#ifndef BENCHMARK_UTIL_H
#define BENCHMARK_UTIL_H

// for multiplicative notation
#define Op_MUL(op_var_type, op_group_type, group, bench_obj)  \
	if(op_var_type == MULTIPLICATION && op_group_type == group)      \
		((Operations *) bench_obj->data_ptr)->mul_ ##group += 1;

#define Op_DIV(op_var_type, op_group_type, group, bench_obj)  \
	if(op_var_type == DIVISION && op_group_type == group)      \
		((Operations *) bench_obj->data_ptr)->div_ ##group += 1;

// for additive notation
#define Op_ADD(op_var_type, op_group_type, group, bench_obj)  \
	if(op_var_type == ADDITION && op_group_type == group)      \
		((Operations *) bench_obj->data_ptr)->add_ ##group += 1;

#define Op_SUB(op_var_type, op_group_type, group, bench_obj)  \
	if(op_var_type == SUBTRACTION && op_group_type == group)      \
		((Operations *) bench_obj->data_ptr)->sub_ ##group += 1;

// exponentiation
#define Op_EXP(op_var_type, op_group_type, group, bench_obj)  \
	if(op_var_type == EXPONENTIATION && op_group_type == group)      \
		((Operations *) bench_obj->data_ptr)->exp_ ##group += 1;

#define UPDATE_BENCH(op_type, elem_type, bench_obj) \
	if(bench_obj != NULL && bench_obj->granular_option == TRUE && elem_type != NONE_G) {		\
		Update_Op(MUL, op_type, elem_type, bench_obj) \
		Update_Op(DIV, op_type, elem_type, bench_obj) \
		Update_Op(ADD, op_type, elem_type, bench_obj) \
		Update_Op(SUB, op_type, elem_type, bench_obj) \
		Update_Op(EXP, op_type, elem_type, bench_obj) \
	}		\
	UPDATE_BENCHMARK(op_type, bench_obj);

#define CLEAR_DBENCH(bench_obj, group)   \
	((Operations *) bench_obj->data_ptr)->mul_ ##group = 0;	\
	((Operations *) bench_obj->data_ptr)->exp_ ##group = 0;	\
	((Operations *) bench_obj->data_ptr)->div_ ##group = 0;	\
	((Operations *) bench_obj->data_ptr)->add_ ##group = 0;	\
	((Operations *) bench_obj->data_ptr)->sub_ ##group = 0;	\

#define GetField(count, type, group, bench_obj)  \
	if(type == MULTIPLICATION) count = (((Operations *) bench_obj->data_ptr)->mul_ ##group ); \
	else if(type == DIVISION) count = (((Operations *) bench_obj->data_ptr)->div_ ##group );	\
	else if(type == ADDITION) count = (((Operations *) bench_obj->data_ptr)->add_ ##group ); \
	else if(type == SUBTRACTION) count = (((Operations *) bench_obj->data_ptr)->sub_ ##group ); \
	else if(type == EXPONENTIATION) count = (((Operations *) bench_obj->data_ptr)->exp_ ##group );


#endif
