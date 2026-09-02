#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "gpt0.h"

int n_layer = 1;
int n_embd = 16;
int block_size = 16;
int n_head = 4;
int head_dim = 0;

static Matrix wte, wpe, lm_head;
static Matrix attn_wq[10], attn_wk[10], attn_wv[10], attn_wo[10];
static Matrix mlp_fc1[10], mlp_fc2[10];

void init_gpt(int vocab_size) {
    head_dim = n_embd / n_head;
    wte = create_matrix(vocab_size, n_embd, 0.08);
    wpe = create_matrix(block_size, n_embd, 0.08);
    lm_head = create_matrix(vocab_size, n_embd, 0.08);
    for (int i = 0; i < n_layer; i++) {
        attn_wq[i] = create_matrix(n_embd, n_embd, 0.08);
        attn_wk[i] = create_matrix(n_embd, n_embd, 0.08);
        attn_wv[i] = create_matrix(n_embd, n_embd, 0.08);
        attn_wo[i] = create_matrix(n_embd, n_embd, 0.08);
        mlp_fc1[i] = create_matrix(4 * n_embd, n_embd, 0.08);
        mlp_fc2[i] = create_matrix(n_embd, 4 * n_embd, 0.08);
    }
}

Value** gpt_forward(int token_id, int pos_id, Value**** keys, Value**** values) {
    Value** x = arena_alloc(n_embd * sizeof(Value*));
    for (int i = 0; i < n_embd; i++) x[i] = add(wte.data[token_id][i], wpe.data[pos_id][i]);
    x = rmsnorm(x, n_embd);

    for (int li = 0; li < n_layer; li++) {
        Value** x_residual = x;
        x = rmsnorm(x, n_embd);
        Value** q = linear(x, n_embd, attn_wq[li]);
        Value** k = linear(x, n_embd, attn_wk[li]);
        Value** v = linear(x, n_embd, attn_wv[li]);
        
        keys[li][pos_id] = k;
        values[li][pos_id] = v;
        
        Value** x_attn = arena_alloc(n_embd * sizeof(Value*));
        int len_seq = pos_id + 1;
        
        for (int h = 0; h < n_head; h++) {
            int hs = h * head_dim;
            Value** attn_logits = arena_alloc(len_seq * sizeof(Value*));
            for (int t = 0; t < len_seq; t++) {
                Value* sum = new_value(0.0);
                for (int j = 0; j < head_dim; j++) sum = add(sum, mul(q[hs + j], keys[li][t][hs + j]));
                attn_logits[t] = div_v(sum, new_value(sqrt((double)head_dim)));
            }
            Value** attn_weights = softmax_v(attn_logits, len_seq);
            for (int j = 0; j < head_dim; j++) {
                Value* sum = new_value(0.0);
                for (int t = 0; t < len_seq; t++) sum = add(sum, mul(attn_weights[t], values[li][t][hs + j]));
                x_attn[hs + j] = sum;
            }
        }
        x = linear(x_attn, n_embd, attn_wo[li]);
        Value** x_res1 = arena_alloc(n_embd * sizeof(Value*));
        for (int i = 0; i < n_embd; i++) x_res1[i] = add(x[i], x_residual[i]);
        x = x_res1;
        
        Value** x_residual_mlp = x;
        x = rmsnorm(x, n_embd);
        x = linear(x, n_embd, mlp_fc1[li]);
        Value** x_relu = arena_alloc(4 * n_embd * sizeof(Value*));
        for (int i = 0; i < 4 * n_embd; i++) x_relu[i] = v_relu(x[i]);
        x = linear(x_relu, 4 * n_embd, mlp_fc2[li]);
        Value** x_res2 = arena_alloc(n_embd * sizeof(Value*));
        for (int i = 0; i < n_embd; i++) x_res2[i] = add(x[i], x_residual_mlp[i]);
        x = x_res2;
    }
    return linear(x, n_embd, lm_head);
}

void train_gpt(int num_steps, double learning_rate, char** docs, int num_docs, int vocab_size, int* (*tokenize_cb)(const char*, int*)) {
    init_optimizer();
    
    for (int step = 0; step < num_steps; step++) {
        int out_len;
        int* tokens = tokenize_cb(docs[step % num_docs], &out_len);
        int n = block_size < (out_len - 1) ? block_size : (out_len - 1);

        Value**** keys = arena_alloc(n_layer * sizeof(Value***));
        Value**** values = arena_alloc(n_layer * sizeof(Value***));
        for (int i = 0; i < n_layer; i++) {
            keys[i] = arena_alloc(block_size * sizeof(Value**));
            values[i] = arena_alloc(block_size * sizeof(Value**));
        }

        Value* loss = new_value(0.0);
        for (int pos_id = 0; pos_id < n; pos_id++) {
            Value** logits = gpt_forward(tokens[pos_id], pos_id, keys, values);
            Value** probs = softmax_v(logits, vocab_size);
            loss = add(loss, neg(v_log(probs[tokens[pos_id + 1]])));
        }
        loss = div_v(loss, new_value((double)n));

        zero_grad();
        backward(loss);
        step_adam(step, num_steps, learning_rate);

        printf("step %4d / %4d | loss %.4f\r", step + 1, num_steps, loss->data);
        fflush(stdout);
        
        arena_reset();
        free(tokens);
    }
    printf("\n");
}

void inference_gpt(int num_samples, double temperature, int vocab_size, int BOS, char vocab_str[][5]) {
    printf("\n--- inference (new, hallucinated names) ---\n");
    for (int sample_idx = 0; sample_idx < num_samples; sample_idx++) {
        Value**** keys = arena_alloc(n_layer * sizeof(Value***));
        Value**** values = arena_alloc(n_layer * sizeof(Value***));
        for (int i = 0; i < n_layer; i++) {
            keys[i] = arena_alloc(block_size * sizeof(Value**));
            values[i] = arena_alloc(block_size * sizeof(Value**));
        }

        int token_id = BOS;
        printf("sample %2d: ", sample_idx + 1);

        for (int pos_id = 0; pos_id < block_size; pos_id++) {
            Value** logits = gpt_forward(token_id, pos_id, keys, values);
            Value** scaled_logits = arena_alloc(vocab_size * sizeof(Value*));
            for (int i = 0; i < vocab_size; i++) {
                scaled_logits[i] = div_v(logits[i], new_value(temperature));
            }
            Value** probs = softmax_v(scaled_logits, vocab_size);
            
            double* probs_data = malloc(vocab_size * sizeof(double));
            for (int i = 0; i < vocab_size; i++) probs_data[i] = probs[i]->data;
            token_id = random_choice(probs_data, vocab_size);
            free(probs_data);

            if (token_id == BOS) break;
            printf("%s", vocab_str[token_id]);
        }
        printf("\n");
        arena_reset();
    }
}