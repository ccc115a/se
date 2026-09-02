#ifndef NN_H
#define NN_H

#include <stddef.h>

#define MAX_PARAMS 1000000
#define MAX_NODES 10000000
#define ARENA_BYTES (size_t)(1024 * 1024 * 1024) // 1 GB Arena

// ----------------------------------------------------------------------------
// Autograd Engine (Value)
// ----------------------------------------------------------------------------
typedef struct Value {
    double data;
    double grad;
    struct Value* child1;
    struct Value* child2;
    double local_grad1;
    double local_grad2;
    int visited;
} Value;

extern Value* params[MAX_PARAMS];
extern int num_params;

// 系統初始化
void init_nn(void);

// 記憶體池 (Arena Allocator)
void arena_reset(void);
void* arena_alloc(size_t size);

// Value 節點運算
Value* new_value(double data);
Value* new_param(double data);
Value* add(Value* a, Value* b);
Value* mul(Value* a, Value* b);
Value* power(Value* a, double b);
Value* v_log(Value* a);
Value* v_exp(Value* a);
Value* v_relu(Value* a);
Value* neg(Value* a);
Value* div_v(Value* a, Value* b);

// 反向傳播
void zero_grad(void);
void backward(Value* root);

// ----------------------------------------------------------------------------
// Optimizer (Adam)
// ----------------------------------------------------------------------------
void init_optimizer(void);
void step_adam(int step, int num_steps, double learning_rate);

// ----------------------------------------------------------------------------
// Matrix, Layers & Utils
// ----------------------------------------------------------------------------
typedef struct {
    int rows;
    int cols;
    Value*** data; // data[row][col]
} Matrix;

Matrix create_matrix(int rows, int cols, double std);
Value** linear(Value** x, int x_len, Matrix w);
Value** softmax_v(Value** logits, int len);
Value** rmsnorm(Value** x, int len);

double gauss(double mean, double std);
int random_choice(double* weights, int size);

#endif // NN_H