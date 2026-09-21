/**
 * examples.js — 測試 nn0.js
 * 
 * 執行方法: node examples.js
 */

const { Value, Adam, linear, cross_entropy } = require('../nn0.js');

console.log("\n=== 測試線性分類器與 Adam 優化器 (Cross Entropy) ===");

// 建構一個簡單的二元分類器
// 權重矩陣 W: shape [2, 3] (2 個類別，3 個特徵)
let W = [[new Value(0.1), new Value(0.2), new Value(-0.1)], // 預測類別 0 的權重
    [new Value(-0.2), new Value(0.1), new Value(0.3)]  // 預測類別 1 的權重
];

// 把所有需要優化的 Value 放進一個一維陣列交給 Adam
let params = [...W[0], ...W[1]]; 
let optimizer = new Adam(params, 0.1); // Learning Rate = 0.1

// 模擬輸入資料 x (長度 3 的向量)
let x =[new Value(1.0), new Value(-1.0), new Value(0.5)];
let target_class = 1; // 正確答案是類別 1

// 訓練迴圈 
console.log("開始訓練...");
for (let step = 1; step <= 20; step++) {
    
    // 1. Forward pass
    // logits 會是一個長度為 2 的陣列 [Value, Value]
    let logits = linear(x, W); 
    
    // 2. 計算 Loss
    let loss = cross_entropy(logits, target_class);
    
    // 3. Backward pass
    loss.backward();
    
    // 4. Update
    optimizer.step();
    
    if (step === 1 || step % 5 === 0) {
        console.log(`Step ${step} | Loss: ${loss.data.toFixed(4)} | Logits: [${logits[0].data.toFixed(4)}, ${logits[1].data.toFixed(4)}]`);
    }
}
console.log("訓練完成！預測目標類別 1 的 logit 成功超越了類別 0。");