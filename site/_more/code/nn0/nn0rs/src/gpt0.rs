//! gpt0.rs — GPT 模型實現
//!
//! 本模組實現簡化版的 GPT-2（Generative Pre-trained Transformer 2）語言模型，
//! 使用純 Rust 和自定義自動微分引擎（nn0.rs）。
//!
//! 需要將 nn0.rs 放在同個 crate 中，或者作為模組引入。

use std::collections::HashMap;
use std::io::Write;
use rand::prelude::*;
use rand_distr::Normal;

// 引入 nn0.rs 中的元件
// 假設 nn0.rs 在同一個專案中定義為模組 `nn0`
use crate::nn0::{gd, linear, rmsnorm, softmax, Adam, LanguageModel, ValueRef};

/// GPT 語言模型
pub struct Gpt {
    pub vocab_size: usize,
    pub n_embd: usize,
    pub n_layer: usize,
    pub n_head: usize,
    pub block_size: usize,
    pub head_dim: usize,
    
    /// 儲存所有權重矩陣
    pub state_dict: HashMap<String, Vec<Vec<ValueRef>>>,
    /// 攤平後的所有參數，供優化器使用
    pub params: Vec<ValueRef>,
}

impl Gpt {
    /// 建構函數
    pub fn new(vocab_size: usize, n_embd: usize, n_layer: usize, n_head: usize, block_size: usize) -> Self {
        let head_dim = n_embd / n_head;
        assert_eq!(n_embd % n_head, 0, "n_embd 必須能被 n_head 整除");

        let mut rng = rand::thread_rng();
        let mut state_dict = Self::init_params(vocab_size, n_embd, n_layer, block_size, &mut rng, 0.08);

        // 將所有參數展平為列表，方便 Adam 優化器使用
        let mut params = Vec::new();
        for mat in state_dict.values() {
            for row in mat {
                for p in row {
                    params.push(p.clone());
                }
            }
        }

        Self {
            vocab_size,
            n_embd,
            n_layer,
            n_head,
            block_size,
            head_dim,
            state_dict,
            params,
        }
    }

    /// 初始化所有模型參數
    fn init_params(
        vocab_size: usize,
        n_embd: usize,
        n_layer: usize,
        block_size: usize,
        rng: &mut impl Rng,
        std: f64,
    ) -> HashMap<String, Vec<Vec<ValueRef>>> {
        let mut sd = HashMap::new();
        let normal = Normal::new(0.0, std).unwrap();

        // 建立 nout × nin 的權重矩陣
        let mut matrix = |nout: usize, nin: usize| -> Vec<Vec<ValueRef>> {
            (0..nout)
                .map(|_| {
                    (0..nin)
                        .map(|_| ValueRef::new(normal.sample(rng)))
                        .collect()
                })
                .collect()
        };

        // 1. Embedding 層
        sd.insert("wte".to_string(), matrix(vocab_size, n_embd));
        sd.insert("wpe".to_string(), matrix(block_size, n_embd));
        sd.insert("lm_head".to_string(), matrix(vocab_size, n_embd));

        // 2. Transformer 層
        for i in 0..n_layer {
            sd.insert(format!("layer{}.attn_wq", i), matrix(n_embd, n_embd));
            sd.insert(format!("layer{}.attn_wk", i), matrix(n_embd, n_embd));
            sd.insert(format!("layer{}.attn_wv", i), matrix(n_embd, n_embd));
            sd.insert(format!("layer{}.attn_wo", i), matrix(n_embd, n_embd));

            // MLP：先擴展到 4 倍維度，再壓回來
            sd.insert(format!("layer{}.mlp_fc1", i), matrix(4 * n_embd, n_embd));
            sd.insert(format!("layer{}.mlp_fc2", i), matrix(n_embd, 4 * n_embd));
        }

        sd
    }
}

/// 實作 nn0.rs 要求的 LanguageModel Trait
impl LanguageModel for Gpt {
    fn block_size(&self) -> usize {
        self.block_size
    }

    fn n_layer(&self) -> usize {
        self.n_layer
    }

    fn forward(
        &self,
        token_id: usize,
        pos_id: usize,
        keys: &mut Vec<Vec<ValueRef>>,
        values: &mut Vec<Vec<ValueRef>>,
    ) -> Vec<ValueRef> {
        let sd = &self.state_dict;

        // -------------------- 1. Embedding 層 --------------------
        let tok_emb = &sd["wte"][token_id];
        let pos_emb = &sd["wpe"][pos_id];

        // 兩者相加
        let mut x: Vec<ValueRef> = tok_emb
            .iter()
            .zip(pos_emb.iter())
            .map(|(t, p)| t.add(p))
            .collect();

        // RMS Norm（Pre-LN 結構）
        x = rmsnorm(&x);

        // -------------------- 2. Transformer 層 --------------------
        for li in 0..self.n_layer {
            // ==================== Multi-Head Attention ====================
            let x_residual = x.clone();

            // Pre-LN
            x = rmsnorm(&x);

            // 計算 Q, K, V
            let q = linear(&x, &sd[&format!("layer{}.attn_wq", li)]);
            let k = linear(&x, &sd[&format!("layer{}.attn_wk", li)]);
            let v = linear(&x, &sd[&format!("layer{}.attn_wv", li)]);

            // 將 Key 和 Value 加入 Cache 中
            // 由於 nn0.rs 定義 keys 為 Vec<Vec<ValueRef>>，
            // 這裡將目前時間點的 Vector "攤平" (extend) 追加到該層的一維 Cache 陣列末端。
            keys[li].extend(k);
            values[li].extend(v);

            let mut x_attn = Vec::with_capacity(self.n_embd);
            let seq_len = keys[li].len() / self.n_embd; // 當前歷史長度

            for h in 0..self.n_head {
                let hs = h * self.head_dim;
                let q_h = &q[hs..hs + self.head_dim];

                // Scaled Dot-Product Attention
                let mut attn_logits = Vec::with_capacity(seq_len);
                
                for t in 0..seq_len {
                    // 取出 Cache 中第 t 個時間點，第 h 個 Head 的 Key
                    let k_h_t = &keys[li][t * self.n_embd + hs .. t * self.n_embd + hs + self.head_dim];
                    
                    // 點積 (Q @ K^T)
                    let dot = q_h.iter().zip(k_h_t.iter())
                        .map(|(q_val, k_val)| q_val.mul(k_val))
                        .reduce(|a, b| a.add(&b))
                        .unwrap();
                    
                    // 除以 sqrt(head_dim)
                    let scale = 1.0 / (self.head_dim as f64).sqrt();
                    attn_logits.push(dot.mul_scalar(scale));
                }

                // Softmax 獲得注意力權重
                let attn_weights = softmax(&attn_logits);

                // 加權求和得到輸出 (attention_weights @ V)
                for j in 0..self.head_dim {
                    let sum_v = (0..seq_len)
                        .map(|t| {
                            let v_h_t_j = &values[li][t * self.n_embd + hs + j];
                            attn_weights[t].mul(v_h_t_j)
                        })
                        .reduce(|a, b| a.add(&b))
                        .unwrap();
                    x_attn.push(sum_v);
                }
            }

            // 線性變換 + 殘差連接
            let attn_out = linear(&x_attn, &sd[&format!("layer{}.attn_wo", li)]);
            x = attn_out.iter().zip(x_residual.iter()).map(|(a, b)| a.add(b)).collect();

            // ==================== MLP ====================
            let x_residual = x.clone();

            // Pre-LN
            x = rmsnorm(&x);

            // 第一層：維度擴展
            x = linear(&x, &sd[&format!("layer{}.mlp_fc1", li)]);

            // 激活函數 ReLU
            x = x.into_iter().map(|xi| xi.relu()).collect();

            // 第二層：維度壓縮
            x = linear(&x, &sd[&format!("layer{}.mlp_fc2", li)]);

            // 殘差連接
            x = x.iter().zip(x_residual.iter()).map(|(a, b)| a.add(b)).collect();
        }

        // -------------------- 3. LM Head --------------------
        // 回傳 logits
        linear(&x, &sd["lm_head"])
    }
}


/// 訓練 GPT 模型
///
/// 參數說明：
///   model: GPT 模型實例
///   optimizer: Adam 優化器
///   docs: 文檔列表（字串陣列）
///   uchars: 字符集（char 陣列）
///   bos: Begin Of String 標記的 ID
///   num_steps: 訓練步驟數
pub fn train(
    model: &Gpt,
    optimizer: &mut Adam,
    docs: &[&str],
    uchars: &[char],
    bos: usize,
    num_steps: usize,
) {
    println!("Training for {} steps ...", num_steps);
    for step in 0..num_steps {
        // 循環選取文檔
        let doc = docs[step % docs.len()];

        // Tokenize：將字符轉為 ID
        let mut tokens = vec![bos];
        for ch in doc.chars() {
            let id = uchars.iter().position(|&c| c == ch).expect("Char not in uchars");
            tokens.push(id);
        }
        tokens.push(bos);

        // 執行一步梯度下降
        let loss_val = gd(model, optimizer, &tokens, step, num_steps);

        // 打印進度 (使用 \r 覆寫同一行)
        print!("\rstep {:4} / {:4} | loss {:.4}", step + 1, num_steps, loss_val);
        std::io::stdout().flush().unwrap();
    }
    println!();
}


/// 文字生成（推理）
///
/// 使用自回歸方式生成文字。
///
/// 參數說明：
///   model: GPT 模型實例
///   uchars: 字符集
///   bos: Begin Of String 標記的 ID
///   num_samples: 生成樣本數
///   temperature: 溫度參數，控制多樣性
pub fn inference(
    model: &Gpt,
    uchars: &[char],
    bos: usize,
    num_samples: usize,
    temperature: f64,
) {
    let vocab_size = model.vocab_size;
    println!("--- inference ({} samples, temperature={}) ---", num_samples, temperature);

    let mut rng = rand::thread_rng();

    for sample_idx in 0..num_samples {
        // 初始化 KV Cache
        let mut keys: Vec<Vec<ValueRef>> = vec![Vec::new(); model.n_layer()];
        let mut values: Vec<Vec<ValueRef>> = vec![Vec::new(); model.n_layer()];

        let mut token_id = bos;
        let mut sample = String::new();

        for pos_id in 0..model.block_size {
            // 前向傳播，獲取 logits
            let logits = model.forward(token_id, pos_id, &mut keys, &mut values);

            // 應用 Temperature：logits / T
            let scaled_logits: Vec<ValueRef> = logits
                .into_iter()
                .map(|l| l.mul_scalar(1.0 / temperature))
                .collect();

            let probs = softmax(&scaled_logits);

            // 轉為 f64 以供隨機抽樣
            let p_data: Vec<f64> = probs.iter().map(|p| p.data()).collect();

            // 按概率加權隨機選擇下一個 token
            let dist = rand::distributions::WeightedIndex::new(&p_data)
                .expect("Failed to create weighted index for sampling");
            token_id = dist.sample(&mut rng);

            // 遇到 BOS 停止
            if token_id == bos {
                break;
            }

            // 添加到樣本
            sample.push(uchars[token_id]);
        }

        println!("sample {:2}: {}", sample_idx + 1, sample);
    }
}