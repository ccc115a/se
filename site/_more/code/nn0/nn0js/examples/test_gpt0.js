/**
 * main.js — 載入資料、建立模型、訓練、推理
 *
 * 執行方式: node main.js
 */

const fs = require('fs');
const { Adam } = require('../nn0.js');
const { Gpt, train, inference } = require('../gpt0.js'); // 如果上一步的檔案叫 gpt0.js，請改為 './gpt0.js'

// --- 設定亂數種子 (模擬 Python 的 random.seed(42)) ---
let seed = 42;
Math.random = function() {
    let t = seed += 0x6D2B79F5;
    t = Math.imul(t ^ t >>> 15, t | 1);
    t ^= t + Math.imul(t ^ t >>> 7, t | 61);
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
};

// --- 載入資料集 ---
const data_file = process.argv[2] // '../_data/chinese.txt';

// 確保檔案存在，如果沒有的話給予提示
if (!fs.existsSync(data_file)) {
    console.error(`[錯誤] 找不到 ${data_file}！請在同目錄下建立一個包含文字的 input.txt 檔案。`);
    process.exit(1);
}

// 讀取檔案，去除每行頭尾空白，並過濾掉空白行
let docs = fs.readFileSync(data_file, 'utf-8')
    .split('\n')
    .map(line => line.trim())
    .filter(line => line.length > 0);

// 隨機打亂資料 (模擬 random.shuffle(docs))
// 使用 Fisher-Yates 洗牌演算法
for (let i = docs.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [docs[i], docs[j]] = [docs[j], docs[i]];
}
console.log(`num docs: ${docs.length}`);

// --- Tokenizer ---
// 提取所有不重複的字元並排序
let charSet = new Set(docs.join(''));
let uchars = Array.from(charSet).sort();
const BOS = uchars.length;
const vocab_size = uchars.length + 1;
console.log(`vocab size: ${vocab_size}`);

// --- 建立模型 ---
const model = new Gpt(vocab_size, 16, 1, 4, 16);
console.log(`num params: ${model.params.length}`);

// --- 建立優化器 ---
const optimizer = new Adam(model.params, 0.01);

// --- 訓練 ---
train(model, optimizer, docs, uchars, BOS, 1000);

// --- 推理 ---
inference(model, uchars, BOS, 20, 0.5);