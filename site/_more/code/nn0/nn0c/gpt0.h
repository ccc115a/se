#ifndef GPT_H
#define GPT_H

#include "nn0.h"

extern int n_layer;
extern int n_embd;
extern int block_size;
extern int n_head;
extern int head_dim;

// 初始化 GPT 模型
void init_gpt(int vocab_size);

// 高階 API：訓練與推論
void train_gpt(int num_steps, double learning_rate, char** docs, int num_docs, int vocab_size, int* (*tokenize_cb)(const char*, int*));
void inference_gpt(int num_samples, double temperature, int vocab_size, int BOS, char vocab_str[][5]);

#endif // GPT_H