#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "nn0.h"
#include "gpt0.h"

#define MAX_DOCS 100000
#define MAX_VOCAB 10000

// 資料庫與字典
char* docs[MAX_DOCS];
int num_docs = 0;
char vocab_str[MAX_VOCAB][5];
int vocab_size = 0;
int BOS = 0;

int get_utf8_len(unsigned char c) {
    if ((c & 0x80) == 0x00) return 1; 
    if ((c & 0xE0) == 0xC0) return 2; 
    if ((c & 0xF0) == 0xE0) return 3; 
    if ((c & 0xF8) == 0xF0) return 4; 
    return 1;
}

int get_token_id(const char* str) {
    for (int i = 0; i < vocab_size; i++) {
        if (strcmp(vocab_str[i], str) == 0) return i;
    }
    if (vocab_size >= MAX_VOCAB) {
        fprintf(stderr, "MAX_VOCAB exceeded\n"); exit(1);
    }
    strcpy(vocab_str[vocab_size], str);
    return vocab_size++;
}

void load_data(char *inputFile) {
    FILE* f = fopen(inputFile, "r");
    if (!f) {
        printf("Downloading input.txt...\n");
        int ret = system("wget -qO input.txt https://raw.githubusercontent.com/karpathy/makemore/988aa59/names.txt || curl -so input.txt https://raw.githubusercontent.com/karpathy/makemore/988aa59/names.txt");
        if (ret != 0) { printf("Failed to download\n"); exit(1); }
        f = fopen("input.txt", "r");
    }
    char line[256];
    while (fgets(line, sizeof(line), f)) {
        int len = strlen(line);
        while (len > 0 && (line[len-1] == '\n' || line[len-1] == '\r')) line[--len] = '\0';
        if (len > 0) docs[num_docs++] = strdup(line);
    }
    fclose(f);
}

void build_vocab() {
    vocab_size = 0;
    for (int i = 0; i < num_docs; i++) {
        int j = 0, len = strlen(docs[i]);
        while (j < len) {
            int char_len = get_utf8_len((unsigned char)docs[i][j]);
            char temp[5] = {0};
            strncpy(temp, &docs[i][j], char_len);
            get_token_id(temp);
            j += char_len;
        }
    }
    BOS = vocab_size;
    strcpy(vocab_str[BOS], "<BOS>");
    vocab_size++; 
    printf("vocab size: %d\n", vocab_size);
}

int* tokenize(const char* doc, int* out_len) {
    int* tokens = malloc((strlen(doc) + 2) * sizeof(int));
    int count = 0, j = 0, len = strlen(doc);
    tokens[count++] = BOS;
    while (j < len) {
        int char_len = get_utf8_len((unsigned char)doc[j]);
        char temp[5] = {0};
        strncpy(temp, &doc[j], char_len);
        tokens[count++] = get_token_id(temp);
        j += char_len;
    }
    tokens[count++] = BOS;
    *out_len = count;
    return tokens;
}

int main(int argc, char *argv[]) {
    srand(42);
    
    // 1. 初始化神經網路引擎
    init_nn();

    if (argc < 2) {
        printf("%s <path_to_input.txt>", argv[0]);
        exit(1);
    }
    // 2. 準備文字資料與字典
    load_data(argv[1]);
    for (int i = num_docs - 1; i > 0; i--) {
        int j = rand() % (i + 1);
        char* temp = docs[i]; docs[i] = docs[j]; docs[j] = temp;
    }
    printf("num docs: %d\n", num_docs);
    build_vocab();

    // 3. 初始化 GPT 模型
    init_gpt(vocab_size);
    printf("num params: %d\n", num_params);

    // 4. 開始訓練 (1000 steps, learning_rate = 0.01)
    train_gpt(1000, 0.01, docs, num_docs, vocab_size, tokenize);

    // 5. 模型推論 (20 筆樣本, temperature = 0.5)
    inference_gpt(20, 0.5, vocab_size, BOS, vocab_str);

    return 0;
}