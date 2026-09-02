//! gpt0demo.rs (main.rs) — GPT 模型訓練與推理演示程式
//!
//! 本程式展示如何：
//!   1. 載入文本資料集
//!   2. 建立字符級 Tokenizer
//!   3. 初始化 GPT 模型
//!   4. 訓練模型
//!   5. 生成文本
//!
//! 執行方式：
//!   cargo run <資料檔案>
//!
//! 範例：
//!   cargo run chinese.txt

use std::collections::HashSet;
use std::env;
use std::fs;
use std::process;

// 引入隨機數處理 (需要 rand 套件)
use rand::seq::SliceRandom;
use rand::{rngs::StdRng, SeedableRng};

// 宣告同目錄下的模組
mod nn0;
mod gpt0;

// 從 nn0 模組匯入 Adam 優化器
use nn0::Adam;

// 從 gpt0 模組匯入 GPT 模型和相關函式
use gpt0::{inference, train, Gpt};

fn main() {
    // ===================== 主程式開始 =====================

    // -------------------- 載入資料集 --------------------

    // 從命令列參數取得資料檔案路徑
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("使用方式: {} <資料檔案>", args[0]);
        eprintln!("範例: {} chinese.txt", args[0]);
        process::exit(1);
    }
    let data_file = &args[1];

    // 讀取檔案，每行視為一個文檔
    let content = fs::read_to_string(data_file).unwrap_or_else(|err| {
        eprintln!("無法讀取檔案 '{}': {}", data_file, err);
        process::exit(1);
    });

    // 去除空白行，只保留有內容的行
    let mut docs: Vec<&str> = content
        .lines()
        .map(|line| line.trim())
        .filter(|line| !line.is_empty())
        .collect();

    // 隨機打亂文檔順序
    // 訓練時每個 epoch 看到不同的順序，有助於泛化
    // 這裡設定固定的隨機種子 42，確保每次執行的打亂結果相同 (可重現性)
    let mut rng = StdRng::seed_from_u64(42);
    docs.shuffle(&mut rng);

    // 顯示文檔數量
    println!("num docs: {}", docs.len());


    // -------------------- Tokenizer（分詞器）--------------------

    // 收集所有出現的字元
    // 首先，使用 HashSet 去重複
    let mut char_set = HashSet::new();
    for doc in &docs {
        for ch in doc.chars() {
            char_set.insert(ch);
        }
    }

    // 將結果轉為 Vector 並排序確保順序固定
    let mut uchars: Vec<char> = char_set.into_iter().collect();
    uchars.sort_unstable();

    // 定義 BOS（Begin Of String）標記的 ID
    // 我們使用 vocab_size 作為 BOS 的 ID
    // 這樣確保它不會與實際字元衝突
    let bos = uchars.len();

    // 計算詞彙表大小
    // 等於字元數量 + 1（BOS 標記）
    let vocab_size = uchars.len() + 1;

    // 顯示詞彙表大小
    println!("vocab size: {}", vocab_size);

    // Tokenizer 說明：
    // 我們使用字符級Tokenizer（Character-level Tokenizer）
    // 每個字元對應一個 ID
    // 例如：['你', '好'] -> [0, 1]
    // 加上 BOS：['你', '好'] -> [2, 0, 1, 2]（BOS 在頭尾）


    // -------------------- 建立模型 --------------------

    // 建立 GPT 模型實例
    // 參數說明：
    //   vocab_size: 詞彙表大小
    //   n_embd: Embedding 維度（每個 token 的向量維度）
    //   n_layer: Transformer 層數
    //   n_head: Attention 頭數
    //   block_size: 最大上下文長度
    //
    // 這是一個小型模型：
    //   - 16 維 embedding
    //   - 1 層 Transformer
    //   - 4 個 Attention 頭
    //   - 16 個 token 的上下文
    let model = Gpt::new(vocab_size, 16, 1, 4, 16);

    // 顯示模型參數數量
    println!("num params: {}", model.params.len());

    // 參數數量計算：
    //   wte: vocab_size × n_embd = 96 × 16 = 1536
    //   wpe: block_size × n_embd = 16 × 16 = 256
    //   lm_head: vocab_size × n_embd = 96 × 16 = 1536
    //   每層 attention: 4 × n_embd × n_embd = 4 × 16 × 16 = 1024
    //   每層 MLP: 2 × n_embd × 4n_embd = 2 × 16 × 64 = 2048
    //   總計約：6400


    // -------------------- 建立優化器 --------------------

    // 建立 Adam 優化器實例
    // 參數說明：
    //   model.params: 模型的所有參數列表。
    //                 在 Rust 中我們 clone() 指標陣列，因為 ValueRef 是 Rc<RefCell<..>>
    //   lr: 學習率，nn0 的 Adam::default 預設會配置 lr=0.01
    //
    // Adam 優化器的特點：
    //   - 自適應學習率：不同參數有不同的 learning rate
    //   - 動量：加速收斂
    //   - 通常比 SGD 更容易訓練
    let mut optimizer = Adam::default(model.params.clone());


    // -------------------- 訓練 --------------------

    // 執行訓練
    // 参数说明：
    //   model: GPT 模型
    //   optimizer: Adam 優化器
    //   docs: 文檔列表
    //   uchars: 字元集
    //   bos: Begin Of String 標記的 ID
    //   num_steps: 訓練步驟數
    //
    // 訓練流程（train 函式內部）：
    //   1. 對每個文檔 tokenize
    //   2. 反復執行梯度下降
    //   3. 輸出 loss 監控訓練進度
    train(&model, &mut optimizer, &docs, &uchars, bos, 1000);

    // 訓練目標：
    //   输入：token t0, t1, ..., t(n-1)
    //   目标：t1, t2, ..., tn
    //   Loss = -1/n * Σ log(P(t(i+1) | t0,...,ti))

    // 學習率衰減：
    //   lr_t = lr_0 * (1 - step / num_steps)
    //   開始時較大（快速收斂）
    //   結束時較小（fine-tune）


    // -------------------- 推理 --------------------

    // 執行文字生成
    // 參數說明：
    //   model: 已訓練的模型
    //   uchars: 字元集（用於將 ID 轉回字元）
    //   bos: Begin Of String 標記的 ID
    //   num_samples: 生成樣本數
    //   temperature: 溫度參數，控制多樣性
    //
    // temperature 說明：
    //   - T = 0：總是選擇最可能的 token（貪心解碼）
    //   - T = 1：原始分布
    //   - T > 1：更多樣性，可能不太流暢
    //   預設 T = 0.5 是一個平衡值
    inference(&model, &uchars, bos, 20, 0.5);

    // 生成流程：
    //   1. 從 BOS 開始
    //   2. 每一步：前向傳播得到 logits
    //   3. 應用 temperature：logits / T
    //   4. Softmax 得到機率分布
    //   5. 按機率加權隨機選擇下一個 token
    //   6. 重複直到遇到 BOS 或達到 block_size
    //   7. 輸出生成的文本
}