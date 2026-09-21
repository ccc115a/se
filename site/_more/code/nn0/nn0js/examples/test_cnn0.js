/**
 * mnist_example.js — 使用 nn0.js 進行 MNIST 手寫數字訓練
 */
const fs = require('fs');
const { Value, Adam, linear, cross_entropy } = require('../nn0.js');

// === 定義 MLP 網路架構 (與 XOR 類似，但支援動態維度) ===
class LinearLayer {
    constructor(nin, nout) {
        this.w =[];
        // 初始化使用更小的權重以幫助 MNIST 收斂
        for (let i = 0; i < nout; i++) {
            let row =[];
            for (let j = 0; j < nin; j++) {
                row.push(new Value((Math.random() - 0.5) * 0.1)); 
            }
            this.w.push(row);
        }
        this.b = Array.from({ length: nout }, () => new Value(0.0));
    }
    forward(x) {
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

class MNISTModel {
    constructor() {
        // 輸入層 784(28x28) -> 隱藏層 16 -> 輸出層 10
        // 為了確保純 JS 不會跑到當機，我們隱藏層設很小 (16)
        this.l1 = new LinearLayer(784, 16); 
        this.l2 = new LinearLayer(16, 10);
    }
    forward(x) {
        let h = this.l1.forward(x).map(v => v.relu());
        return this.l2.forward(h);
    }
    parameters() {
        return [...this.l1.parameters(), ...this.l2.parameters()];
    }
}

// === 讀取 MNIST 二進位檔案 ===
function loadMNIST(imageFile, labelFile, maxItems = 50) {
    if (!fs.existsSync(imageFile) || !fs.existsSync(labelFile)) {
        console.warn("\n[警告] 找不到 MNIST 檔案！將使用隨機產生的假資料測試引擎運作...");
        let dummy =[];
        for(let i=0; i<maxItems; i++) {
            let pixels = Array.from({length: 784}, () => new Value(Math.random()));
            dummy.push({ x: pixels, y: Math.floor(Math.random() * 10) });
        }
        return dummy;
    }

    console.log("正在讀取 MNIST 檔案...");
    const imgBuffer = fs.readFileSync(imageFile);
    const lblBuffer = fs.readFileSync(labelFile);

    let dataset =[];
    // 圖片檔資料從 byte 16 開始；標籤檔從 byte 8 開始
    for (let i = 0; i < maxItems; i++) {
        let pixels =[];
        for (let j = 0; j < 784; j++) {
            let p = imgBuffer[16 + (i * 784) + j];
            pixels.push(new Value(p / 255.0)); // 轉為 Value 且正規化到 0~1
        }
        let label = lblBuffer[8 + i];
        dataset.push({ x: pixels, y: label });
    }
    return dataset;
}

// === 主程式 ===
const data_path = "../../_data/MNIST/"
const max_samples = 1000; // 只取前 20 筆 (因為純 JS Value 物件極慢)
const dataset = loadMNIST(data_path+'train-images-idx3-ubyte', data_path+'train-labels-idx1-ubyte', max_samples);

console.log(`載入完成，共 ${dataset.length} 筆資料。模型建立中...`);
const model = new MNISTModel();
const optimizer = new Adam(model.parameters(), 0.05);

console.log(`\n=== 開始 MNIST 微型訓練 (純 JS Autograd 效能警告) ===`);
console.log(`由於這是教育用的純量級別引擎，訓練 ${max_samples} 筆圖片會花費數秒到數十秒，請耐心等待。\n`);

for (let epoch = 1; epoch <= 5; epoch++) { // 跑 5 個 Epoch
    let epoch_loss = 0.0;
    let correct = 0;

    for (let i = 0; i < dataset.length; i++) {
        const { x, y } = dataset[i];

        let logits = model.forward(x);
        let loss = cross_entropy(logits, y);
        
        // 計算準確率 (找最大的 logit 的 index)
        let max_logit = -Infinity;
        let pred = -1;
        for (let j=0; j<10; j++) {
            if (logits[j].data > max_logit) { max_logit = logits[j].data; pred = j; }
        }
        if (pred === y) correct++;

        // 反向傳播與優化
        loss.backward();
        optimizer.step();

        epoch_loss += loss.data;
    }

    console.log(`Epoch ${epoch} | 平均 Loss: ${(epoch_loss / dataset.length).toFixed(4)} | 準確率: ${correct}/${dataset.length} (${((correct/dataset.length)*100).toFixed(1)}%)`);
}
console.log("訓練結束！");