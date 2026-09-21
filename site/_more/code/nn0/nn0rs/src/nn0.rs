//! nn0.rs — 自動微分引擎 (Value) 與 Adam 優化器
//!
//! 純 Rust 實現的自動微分（Automatic Differentiation）引擎，是構建神經網路的基礎元件。
//!
//! 功能說明：
//!   Value      — 自動微分節點，支援反向傳播（backpropagation）
//!   Adam       — Adam 優化器，自適應學習率
//!   linear()   — 矩陣乘法（全連接層）
//!   softmax()  — 數值穩定的 Softmax 激活函數
//!   rmsnorm()  — RMS Normalization 正規化
//!   cross_entropy() — 數值穩定的交叉熵損失函數
//!   gd()       — 單步梯度下降訓練

use std::cell::RefCell;
use std::collections::HashSet;
use std::rc::Rc;

// ──────────────────────────────────────────────
// Value：自動微分節點
// ──────────────────────────────────────────────

/// 計算圖中一個節點的內部狀態（用 RefCell 包裝，允許內部可變性）
#[derive(Debug)]
struct ValueInner {
    pub data: f64,
    pub grad: f64,
    /// 依賴的子節點
    children: Vec<ValueRef>,
    /// 對每個子節點的局部梯度
    local_grads: Vec<f64>,
}

/// 引用計數 + 內部可變的 Value 節點
///
/// 使用 `Rc<RefCell<...>>` 模式：
///   - `Rc`：多個節點可以共享同一個子節點（計算圖中的 fan-out）
///   - `RefCell`：在不可變引用下仍可修改 grad（反向傳播時需要）
#[derive(Clone, Debug)]
pub struct ValueRef(Rc<RefCell<ValueInner>>);

impl ValueRef {
    // ── 建構子 ──────────────────────────────────

    /// 建立葉節點（無父節點）
    pub fn new(data: f64) -> Self {
        ValueRef(Rc::new(RefCell::new(ValueInner {
            data,
            grad: 0.0,
            children: vec![],
            local_grads: vec![],
        })))
    }

    /// 建立中間節點（有父節點和局部梯度）
    fn from_op(data: f64, children: Vec<ValueRef>, local_grads: Vec<f64>) -> Self {
        ValueRef(Rc::new(RefCell::new(ValueInner {
            data,
            grad: 0.0,
            children,
            local_grads,
        })))
    }

    // ── 讀寫資料 ─────────────────────────────────

    pub fn data(&self) -> f64 {
        self.0.borrow().data
    }

    pub fn set_data(&self, v: f64) {
        self.0.borrow_mut().data = v;
    }

    pub fn grad(&self) -> f64 {
        self.0.borrow().grad
    }

    pub fn set_grad(&self, v: f64) {
        self.0.borrow_mut().grad = v;
    }

    pub fn add_grad(&self, v: f64) {
        self.0.borrow_mut().grad += v;
    }

    // ── 算術運算 ─────────────────────────────────

    /// 加法：y = a + b，∂y/∂a = 1，∂y/∂b = 1
    pub fn add(&self, other: &ValueRef) -> ValueRef {
        ValueRef::from_op(
            self.data() + other.data(),
            vec![self.clone(), other.clone()],
            vec![1.0, 1.0],
        )
    }

    /// 加純量：y = a + c
    pub fn add_scalar(&self, c: f64) -> ValueRef {
        ValueRef::from_op(
            self.data() + c,
            vec![self.clone()],
            vec![1.0],
        )
    }

    /// 乘法：y = a * b，∂y/∂a = b，∂y/∂b = a
    pub fn mul(&self, other: &ValueRef) -> ValueRef {
        let (a, b) = (self.data(), other.data());
        ValueRef::from_op(
            a * b,
            vec![self.clone(), other.clone()],
            vec![b, a],
        )
    }

    /// 乘純量：y = a * c，∂y/∂a = c
    pub fn mul_scalar(&self, c: f64) -> ValueRef {
        ValueRef::from_op(
            self.data() * c,
            vec![self.clone()],
            vec![c],
        )
    }

    /// 冪次：y = a^n，∂y/∂a = n * a^(n-1)
    pub fn powf(&self, n: f64) -> ValueRef {
        let a = self.data();
        ValueRef::from_op(
            a.powf(n),
            vec![self.clone()],
            vec![n * a.powf(n - 1.0)],
        )
    }

    /// 自然對數：y = ln(a)，∂y/∂a = 1/a
    pub fn log(&self) -> ValueRef {
        let a = self.data();
        ValueRef::from_op(a.ln(), vec![self.clone()], vec![1.0 / a])
    }

    /// 指數：y = e^a，∂y/∂a = e^a
    pub fn exp(&self) -> ValueRef {
        let ea = self.data().exp();
        ValueRef::from_op(ea, vec![self.clone()], vec![ea])
    }

    /// ReLU：y = max(0, a)，∂y/∂a = 1 if a > 0 else 0
    pub fn relu(&self) -> ValueRef {
        let a = self.data();
        ValueRef::from_op(
            a.max(0.0),
            vec![self.clone()],
            vec![if a > 0.0 { 1.0 } else { 0.0 }],
        )
    }

    /// 取負：y = -a，等價於 a * (-1)
    pub fn neg(&self) -> ValueRef {
        self.mul_scalar(-1.0)
    }

    /// 減法：a - b
    pub fn sub(&self, other: &ValueRef) -> ValueRef {
        self.add(&other.neg())
    }

    /// 除法：a / b = a * b^(-1)
    pub fn div(&self, other: &ValueRef) -> ValueRef {
        self.mul(&other.powf(-1.0))
    }

    // ── 反向傳播 ─────────────────────────────────

    /// 反向傳播（Backpropagation）
    ///
    /// 使用拓撲排序 + 鏈式法則，從輸出節點逆向計算所有葉節點的梯度。
    ///
    /// 算法步驟：
    ///   1. DFS 建立拓撲排序（子節點先於父節點）
    ///   2. 設定輸出梯度 = 1（∂L/∂L = 1）
    ///   3. 逆序遍歷，對每個節點傳遞梯度給其子節點
    ///      child.grad += local_grad * node.grad  （鏈式法則）
    pub fn backward(&self) {
        // 第一步：建立拓撲排序（DFS）
        let mut topo: Vec<ValueRef> = Vec::new();
        let mut visited: HashSet<*const RefCell<ValueInner>> = HashSet::new();

        fn build_topo(
            v: &ValueRef,
            topo: &mut Vec<ValueRef>,
            visited: &mut HashSet<*const RefCell<ValueInner>>,
        ) {
            let ptr = Rc::as_ptr(&v.0);
            if visited.insert(ptr) {
                // 先遞迴處理所有子節點
                let children: Vec<ValueRef> = v.0.borrow().children.clone();
                for child in &children {
                    build_topo(child, topo, visited);
                }
                // 再把自己加入列表
                topo.push(v.clone());
            }
        }

        build_topo(self, &mut topo, &mut visited);

        // 第二步：初始化輸出梯度
        self.set_grad(1.0);

        // 第三步：逆序傳播梯度
        for v in topo.iter().rev() {
            // 先把需要的資料一次取出，釋放借用後再修改子節點
            // 這樣可以避免「持有 borrow 的同時修改子節點」的衝突
            let (v_grad, pairs): (f64, Vec<(ValueRef, f64)>) = {
                let inner = v.0.borrow();
                let grad = inner.grad;
                let pairs = inner
                    .children
                    .iter()
                    .zip(inner.local_grads.iter())
                    .map(|(c, &lg)| (c.clone(), lg))
                    .collect();
                (grad, pairs)
            }; // borrow 在此釋放

            // 鏈式法則：child.grad += local_grad * v.grad
            for (child, lg) in &pairs {
                child.add_grad(lg * v_grad);
            }
        }
    }
}

impl std::fmt::Display for ValueRef {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Value({:.4})", self.data())
    }
}

// ──────────────────────────────────────────────
// Adam 優化器
// ──────────────────────────────────────────────

/// Adam 優化器（Adaptive Moment Estimation）
///
/// 更新規則：
///   m = β1 * m + (1-β1) * grad           （一階矩，動量）
///   v = β2 * v + (1-β2) * grad²          （二階矩，RMSProp）
///   m̂ = m / (1 - β1^t)                  （偏差修正）
///   v̂ = v / (1 - β2^t)
///   p = p - lr * m̂ / (√v̂ + ε)          （參數更新）
pub struct Adam {
    params: Vec<ValueRef>,
    pub lr: f64,
    beta1: f64,
    beta2: f64,
    eps: f64,
    m: Vec<f64>,
    v: Vec<f64>,
    step_count: u64,
}

impl Adam {
    /// 建立 Adam 優化器
    ///
    /// 參數說明：
    ///   params — 要優化的參數列表
    ///   lr     — 初始學習率（預設 0.01）
    ///   beta1  — 一階矩衰減率（預設 0.85）
    ///   beta2  — 二階矩衰減率（預設 0.99）
    ///   eps    — 數值穩定項（預設 1e-8）
    pub fn new(params: Vec<ValueRef>, lr: f64, beta1: f64, beta2: f64, eps: f64) -> Self {
        let n = params.len();
        Adam {
            params,
            lr,
            beta1,
            beta2,
            eps,
            m: vec![0.0; n],
            v: vec![0.0; n],
            step_count: 0,
        }
    }

    /// 使用預設超參數建立優化器
    pub fn default(params: Vec<ValueRef>) -> Self {
        Self::new(params, 0.01, 0.85, 0.99, 1e-8)
    }

    /// 執行一步參數更新
    ///
    /// `lr_override`：可選的學習率覆蓋值（用於學習率衰減）
    pub fn step(&mut self, lr_override: Option<f64>) {
        self.step_count += 1;
        let lr = lr_override.unwrap_or(self.lr);
        let t = self.step_count as f64;

        for (i, p) in self.params.iter().enumerate() {
            let g = p.grad();

            // 一階矩（動量）
            self.m[i] = self.beta1 * self.m[i] + (1.0 - self.beta1) * g;

            // 二階矩（梯度平方）
            self.v[i] = self.beta2 * self.v[i] + (1.0 - self.beta2) * g * g;

            // 偏差修正
            let m_hat = self.m[i] / (1.0 - self.beta1.powf(t));
            let v_hat = self.v[i] / (1.0 - self.beta2.powf(t));

            // 參數更新
            let new_data = p.data() - lr * m_hat / (v_hat.sqrt() + self.eps);
            p.set_data(new_data);

            // 清除梯度
            p.set_grad(0.0);
        }
    }
}

// ──────────────────────────────────────────────
// 神經網路運算函數
// ──────────────────────────────────────────────

/// 矩陣乘法（全連接層）：y = W @ x
///
/// y[i] = Σ_j W[i][j] * x[j]
///
/// 參數說明：
///   x — 輸入向量，長度 nin
///   w — 權重矩陣，形狀 (nout, nin)
///
/// 返回：輸出向量，長度 nout
pub fn linear(x: &[ValueRef], w: &[Vec<ValueRef>]) -> Vec<ValueRef> {
    w.iter()
        .map(|row| {
            // 計算一行的點積
            row.iter()
                .zip(x.iter())
                .map(|(wi, xi)| wi.mul(xi))
                .reduce(|acc, v| acc.add(&v))
                .expect("linear: 權重矩陣列不能為空")
        })
        .collect()
}

/// 數值穩定的 Softmax
///
/// softmax(x)[i] = e^(x[i]-M) / Σ_j e^(x[j]-M)，M = max(x)
///
/// 使用最大值平移避免 e^x 溢位。
pub fn softmax(logits: &[ValueRef]) -> Vec<ValueRef> {
    let max_val = logits.iter().map(|v| v.data()).fold(f64::NEG_INFINITY, f64::max);

    let exps: Vec<ValueRef> = logits
        .iter()
        .map(|v| v.add_scalar(-max_val).exp())
        .collect();

    // 計算總和
    let total = exps
        .iter()
        .cloned()
        .reduce(|a, b| a.add(&b))
        .expect("softmax: logits 不能為空");

    // 歸一化
    exps.iter().map(|e| e.div(&total)).collect()
}

/// RMS Normalization
///
/// rms  = sqrt(Σ x[i]² / n + ε)
/// out  = x / rms  =  x * (Σ x[i]² / n + ε)^(-0.5)
///
/// 比 Layer Norm 更簡單（無需計算均值）。
pub fn rmsnorm(x: &[ValueRef]) -> Vec<ValueRef> {
    let n = x.len() as f64;

    // 均方值：Σ x[i]² / n
    let ms = x
        .iter()
        .map(|xi| xi.mul(xi))
        .reduce(|a, b| a.add(&b))
        .expect("rmsnorm: 輸入不能為空")
        .mul_scalar(1.0 / n);

    // scale = (ms + ε)^(-0.5)
    let scale = ms.add_scalar(1e-5).powf(-0.5);

    x.iter().map(|xi| xi.mul(&scale)).collect()
}

/// 數值穩定的交叉熵損失
///
/// 使用 Log-Sum-Exp 技巧：
///   Loss = log(Σ e^(x[j]-M)) - (x[target] - M)
///        = log(total) - (logits[target] - max)
///
/// 參數說明：
///   logits    — 模型輸出的 logits
///   target_id — 正確類別的索引
pub fn cross_entropy(logits: &[ValueRef], target_id: usize) -> ValueRef {
    let max_val = logits.iter().map(|v| v.data()).fold(f64::NEG_INFINITY, f64::max);

    let exps: Vec<ValueRef> = logits.iter().map(|v| v.add_scalar(-max_val).exp()).collect();

    let total = exps
        .iter()
        .cloned()
        .reduce(|a, b| a.add(&b))
        .expect("cross_entropy: logits 不能為空");

    // Loss = log(total) - (logits[target] - max)
    total.log().sub(&logits[target_id].add_scalar(-max_val))
}

// ──────────────────────────────────────────────
// 梯度下降（訓練步驟）
// ──────────────────────────────────────────────

/// 語言模型訓練介面（由呼叫端實作）
///
/// 對應 Python 版本的 `model(token_id, pos_id, keys, values)` 呼叫。
pub trait LanguageModel {
    fn block_size(&self) -> usize;
    fn n_layer(&self) -> usize;

    /// 前向傳播，回傳 logits
    fn forward(
        &self,
        token_id: usize,
        pos_id: usize,
        keys: &mut Vec<Vec<ValueRef>>,
        values: &mut Vec<Vec<ValueRef>>,
    ) -> Vec<ValueRef>;
}

/// 單步梯度下降（Gradient Descent）
///
/// 步驟：
///   1. 前向傳播，計算每個位置的 logits
///   2. Softmax → 機率
///   3. Cross-Entropy Loss
///   4. 平均 Loss 的反向傳播
///   5. 學習率線性衰減 + Adam 更新
///
/// 返回：平均 loss 的數值（f64）
pub fn gd<M: LanguageModel>(
    model: &M,
    optimizer: &mut Adam,
    tokens: &[usize],
    step: usize,
    num_steps: usize,
) -> f64 {
    // 序列長度：block_size 和 tokens-1 取較小值
    let n = model.block_size().min(tokens.len() - 1);

    // KV Cache：keys[layer] / values[layer] 存各位置的向量
    let mut keys: Vec<Vec<ValueRef>> = vec![Vec::new(); model.n_layer()];
    let mut values: Vec<Vec<ValueRef>> = vec![Vec::new(); model.n_layer()];

    // 收集各位置的 loss
    let mut losses: Vec<ValueRef> = Vec::with_capacity(n);

    for pos_id in 0..n {
        let token_id = tokens[pos_id];
        let target_id = tokens[pos_id + 1];

        // 前向傳播
        let logits = model.forward(token_id, pos_id, &mut keys, &mut values);

        // Softmax → 機率
        let probs = softmax(&logits);

        // Cross-Entropy Loss：-log(P[target])
        let loss_t = probs[target_id].log().neg();
        losses.push(loss_t);
    }

    // 平均 Loss：(1/n) * Σ losses
    let sum_loss = losses
        .iter()
        .cloned()
        .reduce(|a, b| a.add(&b))
        .expect("gd: tokens 不能為空");

    let loss = sum_loss.mul_scalar(1.0 / n as f64);

    // 反向傳播
    loss.backward();

    // 學習率線性衰減：lr_t = lr_0 * (1 - step / num_steps)
    let lr_t = optimizer.lr * (1.0 - step as f64 / num_steps as f64);

    // Adam 更新
    optimizer.step(Some(lr_t));

    loss.data()
}

// ──────────────────────────────────────────────
// 測試
// ──────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    /// 測試基本算術與反向傳播
    #[test]
    fn test_basic_ops() {
        let a = ValueRef::new(2.0);
        let b = ValueRef::new(3.0);
        let c = a.mul(&b); // c = a * b = 6

        c.backward();

        // ∂c/∂a = b = 3，∂c/∂b = a = 2
        assert!((a.grad() - 3.0).abs() < 1e-9, "∂c/∂a should be 3");
        assert!((b.grad() - 2.0).abs() < 1e-9, "∂c/∂b should be 2");
    }

    /// 測試加法
    #[test]
    fn test_add_backward() {
        let a = ValueRef::new(1.0);
        let b = ValueRef::new(4.0);
        let c = a.add(&b); // c = a + b = 5
        c.backward();

        assert!((a.grad() - 1.0).abs() < 1e-9);
        assert!((b.grad() - 1.0).abs() < 1e-9);
    }

    /// 測試 softmax 輸出總和為 1
    #[test]
    fn test_softmax_sum() {
        let logits: Vec<ValueRef> = vec![1.0, 2.0, 3.0]
            .into_iter()
            .map(ValueRef::new)
            .collect();

        let probs = softmax(&logits);
        let sum: f64 = probs.iter().map(|p| p.data()).sum();
        assert!((sum - 1.0).abs() < 1e-9, "softmax sum should be 1");
    }

    /// 測試 RMSNorm 輸出的 RMS 約為 1
    #[test]
    fn test_rmsnorm() {
        let x: Vec<ValueRef> = vec![1.0, 2.0, 3.0, 4.0]
            .into_iter()
            .map(ValueRef::new)
            .collect();

        let y = rmsnorm(&x);
        let rms_sq: f64 = y.iter().map(|v| v.data().powi(2)).sum::<f64>() / y.len() as f64;
        assert!((rms_sq - 1.0).abs() < 1e-4, "rmsnorm rms should be ~1");
    }

    /// 測試 Adam 一步更新後梯度清零
    #[test]
    fn test_adam_zero_grad() {
        let p = ValueRef::new(1.0);
        p.set_grad(0.5);

        let mut opt = Adam::default(vec![p.clone()]);
        opt.step(None);

        assert_eq!(p.grad(), 0.0, "grad should be zeroed after step");
    }

    /// 測試 cross_entropy 損失為正數
    #[test]
    fn test_cross_entropy_positive() {
        let logits: Vec<ValueRef> = vec![1.0, 2.0, 0.5]
            .into_iter()
            .map(ValueRef::new)
            .collect();

        let loss = cross_entropy(&logits, 1);
        assert!(loss.data() >= 0.0, "cross_entropy loss should be non-negative");
    }
}