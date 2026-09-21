#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "nn0.h"

#define MAX_NODES 10000000

char* arena_mem;
size_t arena_offset = 0;
Value** topo;
Value* params[MAX_PARAMS];
int num_params = 0;

// Adam 狀態緩衝區
double* m_adam = NULL;
double* v_adam = NULL;

void init_nn(void) {
    arena_mem = malloc(ARENA_BYTES);
    topo = malloc(MAX_NODES * sizeof(Value*));
}

void arena_reset(void) { arena_offset = 0; }

void* arena_alloc(size_t size) {
    size = (size + 7) & ~7; // 8-byte alignment
    if (arena_offset + size > ARENA_BYTES) {
        fprintf(stderr, "Out of memory in arena\n"); exit(1);
    }
    void* ptr = arena_mem + arena_offset;
    arena_offset += size;
    return ptr;
}

Value* new_value(double data) {
    Value* v = arena_alloc(sizeof(Value));
    v->data = data; v->grad = 0.0;
    v->child1 = NULL; v->child2 = NULL;
    v->local_grad1 = 0.0; v->local_grad2 = 0.0;
    v->visited = 0;
    return v;
}

Value* new_param(double data) {
    Value* v = malloc(sizeof(Value));
    v->data = data; v->grad = 0.0;
    v->child1 = NULL; v->child2 = NULL;
    v->visited = 0;
    params[num_params++] = v;
    return v;
}

Value* add(Value* a, Value* b) {
    Value* out = new_value(a->data + b->data);
    out->child1 = a; out->child2 = b;
    out->local_grad1 = 1.0; out->local_grad2 = 1.0;
    return out;
}

Value* mul(Value* a, Value* b) {
    Value* out = new_value(a->data * b->data);
    out->child1 = a; out->child2 = b;
    out->local_grad1 = b->data; out->local_grad2 = a->data;
    return out;
}

Value* power(Value* a, double b) {
    Value* out = new_value(pow(a->data, b));
    out->child1 = a; out->local_grad1 = b * pow(a->data, b - 1.0);
    return out;
}

Value* v_log(Value* a) {
    Value* out = new_value(log(a->data));
    out->child1 = a; out->local_grad1 = 1.0 / a->data;
    return out;
}

Value* v_exp(Value* a) {
    Value* out = new_value(exp(a->data));
    out->child1 = a; out->local_grad1 = exp(a->data);
    return out;
}

Value* v_relu(Value* a) {
    Value* out = new_value(a->data > 0 ? a->data : 0);
    out->child1 = a; out->local_grad1 = a->data > 0 ? 1.0 : 0.0;
    return out;
}

Value* neg(Value* a) {
    Value* out = new_value(-a->data);
    out->child1 = a; out->local_grad1 = -1.0;
    return out;
}

Value* div_v(Value* a, Value* b) {
    Value* out = new_value(a->data / b->data);
    out->child1 = a; out->child2 = b;
    out->local_grad1 = 1.0 / b->data; out->local_grad2 = -a->data / (b->data * b->data);
    return out;
}

void build_topo(Value* v, int* topo_idx) {
    if (!v->visited) {
        v->visited = 1;
        if (v->child1) build_topo(v->child1, topo_idx);
        if (v->child2) build_topo(v->child2, topo_idx);
        if (*topo_idx >= MAX_NODES) {
            fprintf(stderr, "MAX_NODES exceeded in topological sort\n"); exit(1);
        }
        topo[(*topo_idx)++] = v;
    }
}

void zero_grad(void) {
    for (int i = 0; i < num_params; i++) params[i]->visited = 0;
}

void backward(Value* root) {
    int topo_idx = 0;
    build_topo(root, &topo_idx);
    root->grad = 1.0;
    for (int i = topo_idx - 1; i >= 0; i--) {
        Value* v = topo[i];
        if (v->child1) v->child1->grad += v->local_grad1 * v->grad;
        if (v->child2) v->child2->grad += v->local_grad2 * v->grad;
    }
}

void init_optimizer(void) {
    if (m_adam) free(m_adam);
    if (v_adam) free(v_adam);
    m_adam = calloc(num_params, sizeof(double));
    v_adam = calloc(num_params, sizeof(double));
}

void step_adam(int step, int num_steps, double learning_rate) {
    double beta1 = 0.85, beta2 = 0.99, eps_adam = 1e-8;
    double lr_t = learning_rate * (1.0 - (double)step / num_steps);
    for (int i = 0; i < num_params; i++) {
        m_adam[i] = beta1 * m_adam[i] + (1.0 - beta1) * params[i]->grad;
        v_adam[i] = beta2 * v_adam[i] + (1.0 - beta2) * params[i]->grad * params[i]->grad;
        double m_hat = m_adam[i] / (1.0 - pow(beta1, step + 1));
        double v_hat = v_adam[i] / (1.0 - pow(beta2, step + 1));
        params[i]->data -= lr_t * m_hat / (sqrt(v_hat) + eps_adam);
        params[i]->grad = 0.0; // 更新後清空梯度
    }
}

double gauss(double mean, double std) {
    static int has_spare = 0; static double spare;
    if (has_spare) { has_spare = 0; return mean + std * spare; }
    has_spare = 1; double u, v, s;
    do {
        u = ((double)rand() / RAND_MAX) * 2.0 - 1.0;
        v = ((double)rand() / RAND_MAX) * 2.0 - 1.0;
        s = u * u + v * v;
    } while (s >= 1.0 || s == 0.0);
    s = sqrt(-2.0 * log(s) / s);
    spare = v * s;
    return mean + std * (u * s);
}

int random_choice(double* weights, int size) {
    double sum = 0;
    for (int i = 0; i < size; i++) sum += weights[i];
    double r = ((double)rand() / RAND_MAX) * sum;
    double acc = 0;
    for (int i = 0; i < size; i++) {
        acc += weights[i];
        if (r <= acc) return i;
    }
    return size - 1;
}

Matrix create_matrix(int rows, int cols, double std) {
    Matrix m; m.rows = rows; m.cols = cols;
    m.data = malloc(rows * sizeof(Value**));
    for (int i = 0; i < rows; i++) {
        m.data[i] = malloc(cols * sizeof(Value*));
        for (int j = 0; j < cols; j++) m.data[i][j] = new_param(gauss(0, std));
    }
    return m;
}

Value** linear(Value** x, int x_len, Matrix w) {
    Value** out = arena_alloc(w.rows * sizeof(Value*));
    for (int i = 0; i < w.rows; i++) {
        Value* sum = new_value(0.0);
        for (int j = 0; j < x_len; j++) sum = add(sum, mul(w.data[i][j], x[j]));
        out[i] = sum;
    }
    return out;
}

Value** softmax_v(Value** logits, int len) {
    double max_val = logits[0]->data;
    for (int i = 1; i < len; i++) if (logits[i]->data > max_val) max_val = logits[i]->data;
    Value** exps = arena_alloc(len * sizeof(Value*));
    Value* total = new_value(0.0);
    for (int i = 0; i < len; i++) {
        exps[i] = v_exp(add(logits[i], new_value(-max_val)));
        total = add(total, exps[i]);
    }
    Value** out = arena_alloc(len * sizeof(Value*));
    for (int i = 0; i < len; i++) out[i] = div_v(exps[i], total);
    return out;
}

Value** rmsnorm(Value** x, int len) {
    Value* ms = new_value(0.0);
    for (int i = 0; i < len; i++) ms = add(ms, mul(x[i], x[i]));
    ms = div_v(ms, new_value((double)len));
    Value* scale = power(add(ms, new_value(1e-5)), -0.5);
    Value** out = arena_alloc(len * sizeof(Value*));
    for (int i = 0; i < len; i++) out[i] = mul(x[i], scale);
    return out;
}