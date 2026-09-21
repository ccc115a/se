/**
 * gpt.js — GPT 模型與訓練 / 推理函式 (Node.js 版)
 */

const { Value, Adam, linear, softmax, rmsnorm, gd } = require('./nn0.js');

// 輔助函式：產生常態分佈的隨機數 (Box-Muller transform)
function randomGauss(mu = 0, std = 1) {
    let u = 1 - Math.random(); // (0, 1]
    let v = Math.random();
    let z = Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
    return z * std + mu;
}

// 輔助函式：加權隨機選擇 (取代 Python 的 random.choices)
function weightedChoices(weights) {
    let sum = weights.reduce((a, b) => a + b, 0);
    let r = Math.random() * sum;
    for (let i = 0; i < weights.length; i++) {
        r -= weights[i];
        if (r <= 0) return i;
    }
    return weights.length - 1;
}

class Gpt {
    /**
     * GPT 模型：embedding → transformer layers → lm_head。
     * 結構類似 GPT-2，但用 RMSNorm 取代 LayerNorm、ReLU 取代 GeLU、無 bias。
     */
    constructor(vocab_size, n_embd = 16, n_layer = 1, n_head = 4, block_size = 16) {
        this.vocab_size = vocab_size;
        this.n_embd = n_embd;
        this.n_layer = n_layer;
        this.n_head = n_head;
        this.block_size = block_size;
        this.head_dim = Math.floor(n_embd / n_head);

        this.state_dict = this._init_params();
        
        // 攤平所有參數到 this.params 陣列中供優化器使用
        this.params =[];
        for (const mat of Object.values(this.state_dict)) {
            for (const row of mat) {
                this.params.push(...row);
            }
        }
    }

    _init_params(std = 0.08) {
        /** 隨機初始化所有權重矩陣。 */
        const matrix = (nout, nin) => {
            return Array.from({ length: nout }, () => 
                Array.from({ length: nin }, () => new Value(randomGauss(0, std)))
            );
        };

        let sd = {
            'wte': matrix(this.vocab_size, this.n_embd),
            'wpe': matrix(this.block_size, this.n_embd),
            'lm_head': matrix(this.vocab_size, this.n_embd),
        };

        for (let i = 0; i < this.n_layer; i++) {
            sd[`layer${i}.attn_wq`] = matrix(this.n_embd, this.n_embd);
            sd[`layer${i}.attn_wk`] = matrix(this.n_embd, this.n_embd);
            sd[`layer${i}.attn_wv`] = matrix(this.n_embd, this.n_embd);
            sd[`layer${i}.attn_wo`] = matrix(this.n_embd, this.n_embd);
            sd[`layer${i}.mlp_fc1`] = matrix(4 * this.n_embd, this.n_embd);
            sd[`layer${i}.mlp_fc2`] = matrix(this.n_embd, 4 * this.n_embd);
        }
        return sd;
    }

    forward(token_id, pos_id, keys, values) {
        /** 單步前向傳播：給定一個 token 和位置，回傳 logits。 */
        const sd = this.state_dict;

        const tok_emb = sd['wte'][token_id];
        const pos_emb = sd['wpe'][pos_id];
        
        // x = tok_emb + pos_emb
        let x = tok_emb.map((t, i) => t.add(pos_emb[i]));
        x = rmsnorm(x);

        for (let li = 0; li < this.n_layer; li++) {
            // --- Multi-head Attention ---
            let x_residual = x;
            x = rmsnorm(x);
            
            let q = linear(x, sd[`layer${li}.attn_wq`]);
            let k = linear(x, sd[`layer${li}.attn_wk`]);
            let v = linear(x, sd[`layer${li}.attn_wv`]);
            keys[li].push(k);
            values[li].push(v);

            let x_attn =[];
            for (let h = 0; h < this.n_head; h++) {
                let hs = h * this.head_dim;
                let q_h = q.slice(hs, hs + this.head_dim);
                let k_h = keys[li].map(ki => ki.slice(hs, hs + this.head_dim));
                let v_h = values[li].map(vi => vi.slice(hs, hs + this.head_dim));
                
                let attn_logits =[];
                let scale = Math.pow(this.head_dim, -0.5);
                for (let t = 0; t < k_h.length; t++) {
                    let sumVal = new Value(0);
                    for (let j = 0; j < this.head_dim; j++) {
                        sumVal = sumVal.add(q_h[j].mul(k_h[t][j]));
                    }
                    attn_logits.push(sumVal.mul(scale));
                }
                
                let attn_weights = softmax(attn_logits);
                
                let head_out =[];
                for (let j = 0; j < this.head_dim; j++) {
                    let sumVal = new Value(0);
                    for (let t = 0; t < v_h.length; t++) {
                        sumVal = sumVal.add(attn_weights[t].mul(v_h[t][j]));
                    }
                    head_out.push(sumVal);
                }
                x_attn.push(...head_out);
            }

            x = linear(x_attn, sd[`layer${li}.attn_wo`]);
            x = x.map((a, i) => a.add(x_residual[i]));

            // --- MLP ---
            x_residual = x;
            x = rmsnorm(x);
            x = linear(x, sd[`layer${li}.mlp_fc1`]);
            x = x.map(xi => xi.relu());
            x = linear(x, sd[`layer${li}.mlp_fc2`]);
            x = x.map((a, i) => a.add(x_residual[i]));
        }

        let logits = linear(x, sd['lm_head']);
        return logits;
    }
}

function train(model, optimizer, docs, uchars, BOS, num_steps = 1000) {
    /** 訓練迴圈：對每個文件做一步梯度下降。 */
    console.log(`Training for ${num_steps} steps ...`);
    for (let step = 0; step < num_steps; step++) {
        let doc = docs[step % docs.length];
        // 將字元轉為 id，前後加上 BOS
        let tokens =[BOS, ...doc.split('').map(ch => uchars.indexOf(ch)), BOS];
        
        let loss_val = gd(model, optimizer, tokens, step, num_steps);
        
        // 模擬 end='\r' 動態覆蓋輸出的效果
        process.stdout.write(`step ${(step + 1).toString().padStart(4, ' ')} / ${num_steps.toString().padStart(4, ' ')} | loss ${loss_val.toFixed(4)}\r`);
    }
    console.log(); // 訓練結束後換行
}

function inference(model, uchars, BOS, num_samples = 20, temperature = 0.5) {
    /** 生成文字：從 BOS 開始，逐 token 取樣直到再次產生 BOS。 */
    let vocab_size = model.vocab_size;
    console.log(`--- inference (${num_samples} samples, temperature=${temperature}) ---`);
    
    for (let sample_idx = 0; sample_idx < num_samples; sample_idx++) {
        let keys = Array.from({ length: model.n_layer }, () =>[]);
        let values = Array.from({ length: model.n_layer }, () =>[]);
        let token_id = BOS;
        let sample =[];
        
        for (let pos_id = 0; pos_id < model.block_size; pos_id++) {
            let logits = model.forward(token_id, pos_id, keys, values);
            
            // 處理 temperature scaling
            let scaled_logits = logits.map(l => l.mul(1 / temperature));
            let probs = softmax(scaled_logits);
            
            // 將 Value 物件轉為純數值供隨機選取
            let weights = probs.map(p => p.data);
            token_id = weightedChoices(weights);
            
            if (token_id === BOS) {
                break;
            }
            sample.push(uchars[token_id]);
        }
        console.log(`sample ${(sample_idx + 1).toString().padStart(2, ' ')}: ${sample.join('')}`);
    }
}

module.exports = {
    Gpt,
    train,
    inference
};