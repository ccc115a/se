/**
 * nn0.js — 自動微分引擎 (Value) 與 Adam 優化器 (Node.js 版)
 */

class Value {
    /**
     * 純 JavaScript 的自動微分節點，支援反向傳播。
     */
    constructor(data, children = [], local_grads =[]) {
        this.data = data;
        this.grad = 0;
        this._children = children;
        this._local_grads = local_grads;
    }

    // 將純數字轉為 Value，若已是 Value 則直接回傳
    static asValue(other) {
        return other instanceof Value ? other : new Value(other);
    }

    add(other) {
        other = Value.asValue(other);
        return new Value(this.data + other.data, [this, other], [1, 1]);
    }

    mul(other) {
        other = Value.asValue(other);
        return new Value(this.data * other.data, [this, other], [other.data, this.data]);
    }

    pow(exponent) {
        const p = exponent instanceof Value ? exponent.data : exponent;
        return new Value(
            Math.pow(this.data, p), 
            [this], 
            [p * Math.pow(this.data, p - 1)]
        );
    }

    log() {
        return new Value(Math.log(this.data), [this],[1 / this.data]);
    }

    exp() {
        return new Value(Math.exp(this.data), [this], [Math.exp(this.data)]);
    }

    relu() {
        return new Value(Math.max(0, this.data), [this],[this.data > 0 ? 1 : 0]);
    }

    neg() {
        return this.mul(-1);
    }

    sub(other) {
        other = Value.asValue(other);
        return this.add(other.neg());
    }

    div(other) {
        other = Value.asValue(other);
        return this.mul(other.pow(-1));
    }

    backward() {
        /** 反向傳播：計算所有參數的梯度。 */
        const topo =[];
        const visited = new Set();

        const build_topo = (v) => {
            if (!visited.has(v)) {
                visited.add(v);
                for (let child of v._children) {
                    build_topo(child);
                }
                topo.push(v);
            }
        };

        build_topo(this);
        this.grad = 1;

        // 從計算圖的尾端倒序往前傳播梯度
        for (let i = topo.length - 1; i >= 0; i--) {
            let v = topo[i];
            for (let j = 0; j < v._children.length; j++) {
                let child = v._children[j];
                let local_grad = v._local_grads[j];
                child.grad += local_grad * v.grad;
            }
        }
    }

    toString() {
        return `Value(${this.data.toFixed(4)})`;
    }
}

class Adam {
    /** Adam optimizer，支援 learning rate 線性衰減。 */
    constructor(params, lr = 0.01, beta1 = 0.85, beta2 = 0.99, eps = 1e-8) {
        this.params = params;
        this.lr = lr;
        this.beta1 = beta1;
        this.beta2 = beta2;
        this.eps = eps;
        this.m = new Array(params.length).fill(0.0);
        this.v = new Array(params.length).fill(0.0);
        this.step_count = 0;
    }

    step(lr_override = null) {
        /** 執行一步參數更新，並清除梯度。 */
        this.step_count++;
        const lr = lr_override !== null ? lr_override : this.lr;
        
        for (let i = 0; i < this.params.length; i++) {
            let p = this.params[i];
            this.m[i] = this.beta1 * this.m[i] + (1 - this.beta1) * p.grad;
            this.v[i] = this.beta2 * this.v[i] + (1 - this.beta2) * Math.pow(p.grad, 2);
            
            let m_hat = this.m[i] / (1 - Math.pow(this.beta1, this.step_count));
            let v_hat = this.v[i] / (1 - Math.pow(this.beta2, this.step_count));
            
            p.data -= lr * m_hat / (Math.sqrt(v_hat) + this.eps);
            p.grad = 0; // 清空梯度
        }
    }
}

function linear(x, w) {
    /** 矩陣乘法：y = W @ x */
    return w.map(row => {
        let sum = new Value(0);
        for (let i = 0; i < row.length; i++) {
            sum = sum.add(row[i].mul(x[i]));
        }
        return sum;
    });
}

function softmax(logits) {
    /** 數值穩定的 softmax。 */
    const max_val = Math.max(...logits.map(val => val.data));
    const exps = logits.map(val => val.sub(max_val).exp());
    
    let total = new Value(0);
    for (let e of exps) total = total.add(e);
    
    return exps.map(e => e.div(total));
}

function rmsnorm(x) {
    /** RMS Normalization（取代 LayerNorm）。 */
    let ms = new Value(0);
    for (let xi of x) {
        ms = ms.add(xi.mul(xi));
    }
    ms = ms.div(x.length);
    
    const scale = ms.add(1e-5).pow(-0.5);
    return x.map(xi => xi.mul(scale));
}

function cross_entropy(logits, target_id) {
    /** 數值穩定的 Cross-Entropy Loss (Log-Sum-Exp 技巧) */
    const max_val = Math.max(...logits.map(val => val.data));
    
    const exps = logits.map(val => val.sub(max_val).exp());
    let total = new Value(0);
    for (let e of exps) total = total.add(e);
    
    return total.log().sub(logits[target_id].sub(max_val));
}

function gd(model, optimizer, tokens, step, num_steps) {
    /**
     * 一步梯度下降：forward → loss → backward → Adam update。
     * 支援 JavaScript 版本的呼叫方式。
     */
    const n = Math.min(model.block_size, tokens.length - 1);
    const keys = Array.from({length: model.n_layer}, () =>[]);
    const values = Array.from({length: model.n_layer}, () => []);

    let losses =[];
    for (let pos_id = 0; pos_id < n; pos_id++) {
        const token_id = tokens[pos_id];
        const target_id = tokens[pos_id + 1];
        
        // 假設 model 可直接被當作函數呼叫 (或是 model.forward)
        const logits = typeof model === 'function' 
            ? model(token_id, pos_id, keys, values)
            : model.forward(token_id, pos_id, keys, values);
            
        const loss_t = cross_entropy(logits, target_id);
        losses.push(loss_t);
    }
    
    // loss = (1 / n) * sum(losses)
    let loss_sum = new Value(0);
    for(let l of losses) loss_sum = loss_sum.add(l);
    let loss = loss_sum.mul(1 / n);

    loss.backward();

    const lr_t = optimizer.lr * (1 - step / num_steps);
    optimizer.step(lr_t);

    return loss.data;
}

// 匯出 Node.js 模組
module.exports = {
    Value,
    Adam,
    linear,
    softmax,
    rmsnorm,
    cross_entropy,
    gd
};