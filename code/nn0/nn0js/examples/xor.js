/**
 * xor_example.js — 使用 nn0.js 訓練多層感知器 (MLP) 解決 XOR 問題
 */
const { Value, Adam, linear, cross_entropy } = require('../nn0.js');

// 建立單層線性層 (包含權重與偏差)
class LinearLayer {
    constructor(nin, nout) {
        this.w =[];
        for (let i = 0; i < nout; i++) {
            let row =[];
            // 使用均勻分佈隨機初始化 (-0.5 ~ 0.5)
            for (let j = 0; j < nin; j++) {
                row.push(new Value((Math.random() - 0.5))); 
            }
            this.w.push(row);
        }
        this.b = Array.from({ length: nout }, () => new Value(0.0));
    }

    forward(x) {
        // y = Wx + b
        let out = linear(x, this.w);
        return out.map((val, i) => val.add(this.b[i]));
    }

    parameters() {
        let p =[];
        for (let row of this.w) p.push(...row);
        p.push(...this.b);
        return p;
    }
}

// 建立兩層 MLP: Input(2) -> Hidden(4) -> Output(2)
class MLP {
    constructor() {
        this.l1 = new LinearLayer(2, 4);
        this.l2 = new LinearLayer(4, 2); // 預測 2 個類別 (0 或是 1)
    }

    forward(x) {
        // 第一層 + ReLU 激活函數
        let h = this.l1.forward(x).map(v => v.relu());
        // 第二層 (輸出 Logits)
        return this.l2.forward(h);
    }

    parameters() {
        return[...this.l1.parameters(), ...this.l2.parameters()];
    }
}

// XOR 資料集
const X = [[new Value(0), new Value(0)],
    [new Value(0), new Value(1)],[new Value(1), new Value(0)],
    [new Value(1), new Value(1)]
];
const Y = [0, 1, 1, 0]; // XOR 邏輯正確答案

const model = new MLP();
const optimizer = new Adam(model.parameters(), 0.1); // lr = 0.1

console.log("=== 開始訓練 XOR MLP ===");
for (let epoch = 1; epoch <= 100; epoch++) {
    let total_loss = new Value(0);

    for (let i = 0; i < 4; i++) {
        let logits = model.forward(X[i]);
        let loss = cross_entropy(logits, Y[i]);
        total_loss = total_loss.add(loss);
    }

    // 計算平均 Loss 並反向傳播
    let avg_loss = total_loss.mul(1/4);
    avg_loss.backward();
    optimizer.step();

    if (epoch % 10 === 0) {
        console.log(`Epoch ${epoch} | Loss: ${avg_loss.data.toFixed(4)}`);
    }
}

console.log("\n=== 訓練結果預測 ===");
for (let i = 0; i < 4; i++) {
    let logits = model.forward(X[i]);
    // 判斷 logits[0] 和 logits[1] 誰比較大
    let pred = logits[1].data > logits[0].data ? 1 : 0; 
    console.log(`輸入: [${X[i][0].data}, ${X[i][1].data}] | 預測: ${pred} | 實際: ${Y[i]} | (Logits: [${logits[0].data.toFixed(2)}, ${logits[1].data.toFixed(2)}])`);
}