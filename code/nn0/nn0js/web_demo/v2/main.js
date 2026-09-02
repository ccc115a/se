// ============================================================
//  nn0.py 互動學習 — main.js
//  結構：
//    1. Value 引擎（自動微分）
//    2. 神經網路（Linear / MLP / AdamOpt）
//    3. 資料集
//    4. 訓練實驗室（Tab 1）
//    5. 反向傳播動畫（Tab 2）
//    6. 程式碼圖表（Tab 3）
//    7. 語言切換（Tab 3）
//    8. 應用展示（Tab 4）：MNIST / 函數逼近 / 邏輯電路 / 加法熱力圖
//    9. 工具函式 & 初始化
// ============================================================


// ════════════════════════════════════════════
//  1. VALUE ENGINE  — nn0.py 的純 JS 移植
// ════════════════════════════════════════════

class Value {
  constructor(data, children = [], localGrads = []) {
    this.data        = data;
    this.grad        = 0;
    this._children   = children;
    this._localGrads = localGrads;
    this._op         = '';
    this._label      = '';
  }

  add(other) {
    other = other instanceof Value ? other : new Value(other);
    const out = new Value(this.data + other.data, [this, other], [1, 1]);
    out._op = '+';
    return out;
  }

  mul(other) {
    other = other instanceof Value ? other : new Value(other);
    const out = new Value(
      this.data * other.data,
      [this, other],
      [other.data, this.data]
    );
    out._op = '×';
    return out;
  }

  pow(n) {
    const out = new Value(
      Math.pow(this.data, n),
      [this],
      [n * Math.pow(this.data, n - 1)]
    );
    out._op = `^${n}`;
    return out;
  }

  log() {
    const safe = Math.max(this.data, 1e-7);
    const out = new Value(Math.log(safe), [this], [1 / safe]);
    out._op = 'log';
    return out;
  }

  exp() {
    const e = Math.exp(Math.min(this.data, 20));
    const out = new Value(e, [this], [e]);
    out._op = 'exp';
    return out;
  }

  relu() {
    const out = new Value(
      Math.max(0, this.data),
      [this],
      [this.data > 0 ? 1 : 0]
    );
    out._op = 'ReLU';
    return out;
  }

  tanh() {
    const t = Math.tanh(this.data);
    const out = new Value(t, [this], [1 - t * t]);
    out._op = 'tanh';
    return out;
  }

  neg()        { return this.mul(-1); }
  sub(other)   { return this.add(other instanceof Value ? other.neg() : new Value(-other)); }
  div(other)   { return this.mul(other instanceof Value ? other.pow(-1) : new Value(1 / other)); }

  backward() {
    const topo = [], visited = new Set();
    const build = v => {
      if (!visited.has(v)) {
        visited.add(v);
        v._children.forEach(build);
        topo.push(v);
      }
    };
    build(this);
    this.grad = 1;
    for (const v of [...topo].reverse()) {
      v._children.forEach((child, i) => {
        child.grad += v._localGrads[i] * v.grad;
      });
    }
  }
}


// ════════════════════════════════════════════
//  2. NEURAL NETWORK
// ════════════════════════════════════════════

function randn() { return (Math.random() * 2 - 1) * 0.5; }

class Linear {
  constructor(nin, nout) {
    this.w = Array.from({ length: nout }, () =>
      Array.from({ length: nin }, () => new Value(randn()))
    );
    this.b = Array.from({ length: nout }, () => new Value(0));
  }

  forward(x) {
    return this.w.map((row, i) =>
      row.reduce((acc, wij, j) => acc.add(wij.mul(x[j])), this.b[i])
    );
  }

  params() { return [...this.w.flat(), ...this.b]; }
}

/** 3-layer MLP used by the training lab */
class MLP {
  constructor(nin, hidden, nout) {
    this.l1 = new Linear(nin, hidden);
    this.l2 = new Linear(hidden, hidden);
    this.l3 = new Linear(hidden, nout);
  }

  forward(x) {
    let h = this.l1.forward(x).map(v => v.relu());
    h     = this.l2.forward(h).map(v => v.relu());
    return this.l3.forward(h);
  }

  params()   { return [...this.l1.params(), ...this.l2.params(), ...this.l3.params()]; }
  zeroGrad() { this.params().forEach(p => (p.grad = 0)); }
}

/** Generic MLP factory used by app demos */
function makeMLP(sizes) {
  const layers = [];
  for (let i = 0; i < sizes.length - 1; i++) {
    layers.push(new Linear(sizes[i], sizes[i + 1]));
  }
  return {
    layers,
    forward(x, acts) {
      let h = x;
      for (let i = 0; i < layers.length - 1; i++) {
        h = layers[i].forward(h).map(v =>
          acts?.[i] === 'tanh' ? v.tanh() : v.relu()
        );
      }
      return layers[layers.length - 1].forward(h);
    },
    params()   { return layers.flatMap(l => l.params()); },
    zeroGrad() { this.params().forEach(p => (p.grad = 0)); },
  };
}

/** Adam optimizer */
class AdamOpt {
  constructor(params, lr = 0.01, b1 = 0.85, b2 = 0.99, eps = 1e-8) {
    this.params = params;
    this.lr     = lr;
    this.b1     = b1;
    this.b2     = b2;
    this.eps    = eps;
    this.m      = new Array(params.length).fill(0);
    this.v      = new Array(params.length).fill(0);
    this.t      = 0;
  }

  step(lrOvr) {
    this.t++;
    const lr = lrOvr ?? this.lr;
    this.params.forEach((p, i) => {
      this.m[i] = this.b1 * this.m[i] + (1 - this.b1) * p.grad;
      this.v[i] = this.b2 * this.v[i] + (1 - this.b2) * p.grad ** 2;
      const mh  = this.m[i] / (1 - this.b1 ** this.t);
      const vh  = this.v[i] / (1 - this.b2 ** this.t);
      p.data   -= lr * mh / (Math.sqrt(vh) + this.eps);
      p.grad    = 0;
    });
  }
}

function softmax(logits) {
  const max  = Math.max(...logits.map(v => v.data));
  const exps = logits.map(v => v.sub(max).exp());
  const tot  = exps.reduce((a, b) => a.add(b));
  return exps.map(e => e.div(tot));
}


// ════════════════════════════════════════════
//  3. DATASETS
// ════════════════════════════════════════════

function makeDataset(type, n = 120) {
  const data = [], labels = [];
  for (let i = 0; i < n; i++) {
    let x, y, c;
    if (type === 'xor') {
      x = Math.random() * 2 - 1;
      y = Math.random() * 2 - 1;
      c = (x * y > 0) ? 0 : 1;
    } else if (type === 'circle') {
      const a = Math.random() * Math.PI * 2;
      const r = Math.random() * 1.4;
      x = Math.cos(a) * r;
      y = Math.sin(a) * r;
      c = r < 0.8 ? 0 : 1;
    } else if (type === 'spiral') {
      const t     = i % 2;
      const k     = Math.floor(i / 2);
      const theta = k / 60 * 4 * Math.PI + t * Math.PI;
      const r     = k / 60;
      x = r * Math.cos(theta) + (Math.random() - 0.5) * 0.15;
      y = r * Math.sin(theta) + (Math.random() - 0.5) * 0.15;
      c = t;
    } else {                         // regression → sine
      x = (i / n) * 4 * Math.PI - 2 * Math.PI;
      y = Math.sin(x) + (Math.random() - 0.5) * 0.3;
      c = y > 0 ? 0 : 1;
      x = x / 6;
      y = y / 1.5;
    }
    data.push([x, y]);
    labels.push(c);
  }
  return { data, labels };
}


// ════════════════════════════════════════════
//  4. 訓練實驗室 (Tab 1)
// ════════════════════════════════════════════

const TOTAL_EPOCHS = 200;
let trainState    = null;
let trainInterval = null;

function initTrain() {
  const hidden   = parseInt(document.getElementById('hiddenSize').value);
  const lr       = parseInt(document.getElementById('lrSlider').value) * 0.001;
  const task     = document.getElementById('taskSel').value;
  const model    = new MLP(2, hidden, 2);
  const dataset  = makeDataset(task);
  const optimizer = new AdamOpt(model.params(), lr);
  trainState = { model, dataset, optimizer, lr, epoch: 0, losses: [], accs: [], gradNorms: [] };
  drawDecision();
  drawLossChart();
}

function startTrain() {
  if (!trainState) initTrain();
  document.getElementById('btnTrain').disabled = true;
  document.getElementById('btnStop').disabled  = false;
  log('<span class="ok">// 開始訓練...</span>');

  trainInterval = setInterval(() => {
    if (trainState.epoch >= TOTAL_EPOCHS) { stopTrain(); return; }
    trainStep();
    if (trainState.epoch % 5 === 0) { drawDecision(); drawLossChart(); }
  }, 30);
}

function stopTrain() {
  clearInterval(trainInterval);
  document.getElementById('btnTrain').disabled = false;
  document.getElementById('btnStop').disabled  = true;
  log('<span class="info">// 訓練停止</span>');
}

function resetTrain() {
  stopTrain();
  trainState = null;
  document.getElementById('statEpoch').textContent = '—';
  document.getElementById('statLoss').textContent  = '—';
  document.getElementById('statAcc').textContent   = '—';
  document.getElementById('statGrad').textContent  = '—';
  document.getElementById('progBar').style.width   = '0%';
  clearCanvas('decCanvas');
  clearCanvas('lossCanvas');
  initTrain();
}

function trainStep() {
  const { model, dataset, optimizer, epoch } = trainState;
  const { data, labels } = dataset;
  const batchSize = parseInt(document.getElementById('batchSlider').value);
  const useAdam   = document.getElementById('optSel').value === 'adam';
  const idx       = Array.from({ length: batchSize }, () =>
    Math.floor(Math.random() * data.length)
  );

  model.zeroGrad();
  let totalLoss = new Value(0), correct = 0;

  idx.forEach(i => {
    const x      = data[i].map(v => new Value(v));
    const logits = model.forward(x);
    const probs  = softmax(logits);
    const loss   = probs[labels[i]].log().mul(-1);
    totalLoss    = totalLoss.add(loss);
    if ((logits[0].data > logits[1].data ? 0 : 1) === labels[i]) correct++;
  });

  const avgLoss = totalLoss.div(batchSize);
  avgLoss.backward();

  const params   = model.params();
  const gradNorm = Math.sqrt(params.reduce((s, p) => s + p.grad ** 2, 0));
  const lrDecay  = trainState.lr * (1 - epoch / TOTAL_EPOCHS);

  if (useAdam) optimizer.step(lrDecay);
  else params.forEach(p => { p.data -= lrDecay * p.grad; p.grad = 0; });

  const lossVal = avgLoss.data;
  const acc     = correct / batchSize;
  trainState.losses.push(lossVal);
  trainState.accs.push(acc);
  trainState.gradNorms.push(gradNorm);
  trainState.epoch++;

  document.getElementById('statEpoch').textContent = trainState.epoch;
  document.getElementById('statLoss').textContent  = lossVal.toFixed(4);
  document.getElementById('statAcc').textContent   = (acc * 100).toFixed(1) + '%';
  document.getElementById('statGrad').textContent  = gradNorm.toFixed(3);
  document.getElementById('progBar').style.width   = (trainState.epoch / TOTAL_EPOCHS * 100) + '%';

  if (trainState.epoch % 20 === 0) {
    log(`<span class="ok">epoch ${trainState.epoch}</span>  ` +
        `loss: ${lossVal.toFixed(4)}  acc: ${(acc * 100).toFixed(0)}%`);
  }
}

function drawDecision() {
  const canvas = document.getElementById('decCanvas');
  const W = canvas.offsetWidth, H = 300;
  canvas.width = W; canvas.height = H;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, W, H);
  if (!trainState) return;

  const { model, dataset } = trainState;
  const RES = 40, cell = W / RES;

  for (let r = 0; r < RES; r++) {
    for (let c = 0; c < RES; c++) {
      const x    = (c / RES) * 2.6 - 1.3;
      const y    = -(r / RES) * 2.6 + 1.3;
      const out  = model.forward([new Value(x), new Value(y)]);
      const p0   = Math.exp(out[0].data);
      const p1   = Math.exp(out[1].data);
      const conf = p0 / (p0 + p1);
      ctx.fillStyle = conf > 0.5
        ? `rgba(107,203,255,${(conf - 0.5) * 0.7})`
        : `rgba(255,107,107,${(0.5 - conf) * 0.7})`;
      ctx.fillRect(c * cell, r * cell, cell + 1, cell + 1);
    }
  }

  const toX = v => (v + 1.3) / 2.6 * W;
  const toY = v => (1 - (v + 1.3) / 2.6) * H;
  dataset.data.forEach(([x, y], i) => {
    ctx.beginPath();
    ctx.arc(toX(x), toY(y), 4, 0, Math.PI * 2);
    ctx.fillStyle   = dataset.labels[i] === 0 ? '#6bcbff' : '#ff6b6b';
    ctx.strokeStyle = '#0a0a0f';
    ctx.lineWidth   = 1;
    ctx.fill();
    ctx.stroke();
  });
}

function drawLossChart() {
  const canvas = document.getElementById('lossCanvas');
  const W = canvas.offsetWidth, H = 300;
  canvas.width = W; canvas.height = H;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, W, H);
  if (!trainState || trainState.losses.length < 2) return;

  const { losses, accs } = trainState;
  const pad  = 32;
  const maxL = Math.max(...losses) * 1.1;
  const tx   = i => pad + i / Math.max(losses.length - 1, 1) * (W - pad * 2);
  const tyL  = v => H - pad - (v / maxL) * (H - pad * 2);
  const tyA  = v => H - pad - v * (H - pad * 2);

  // grid
  ctx.strokeStyle = '#1a1a28'; ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const y = pad + i * (H - pad * 2) / 4;
    ctx.beginPath(); ctx.moveTo(pad, y); ctx.lineTo(W - pad, y); ctx.stroke();
  }

  // loss
  ctx.strokeStyle = '#ff6b6b'; ctx.lineWidth = 2;
  ctx.beginPath();
  losses.forEach((v, i) => (i === 0 ? ctx.moveTo(tx(i), tyL(v)) : ctx.lineTo(tx(i), tyL(v))));
  ctx.stroke();

  // accuracy
  ctx.strokeStyle = '#6bcbff'; ctx.lineWidth = 2;
  ctx.beginPath();
  accs.forEach((v, i) => (i === 0 ? ctx.moveTo(tx(i), tyA(v)) : ctx.lineTo(tx(i), tyA(v))));
  ctx.stroke();

  ctx.font = '10px Syne Mono'; ctx.textAlign = 'left';
  ctx.fillStyle = '#ff6b6b'; ctx.fillText('LOSS', pad + 4, 20);
  ctx.fillStyle = '#6bcbff'; ctx.fillText('ACC',  pad + 48, 20);
  ctx.fillStyle = '#666680'; ctx.fillText('0', pad - 18, H - pad + 4);
  ctx.fillText(losses.length, W - pad - 10, H - pad + 14);
}


// ════════════════════════════════════════════
//  5. 反向傳播動畫 (Tab 2)
// ════════════════════════════════════════════

const EXPRS = [
  () => {
    const x = new Value(2.0);  x._label = 'x=2';
    const w = new Value(-0.5); w._label = 'w=-0.5';
    const b = new Value(1.0);  b._label = 'b=1';
    const z = x.mul(w).add(b).relu(); z._label = 'ReLU(x·w+b)';
    return { root: z, inputs: { x, w, b } };
  },
  () => {
    const y = new Value(1.0); y._label = 'y=1';
    const p = new Value(0.7); p._label = 'p=0.7';
    const loss = y.mul(p.log()).neg(); loss._label = '-y·log(p)';
    return { root: loss, inputs: { y, p } };
  },
  () => {
    const x = new Value(1.5); x._label = 'x=1.5';
    const z = x.pow(2).add(x).relu(); z._label = 'ReLU(x²+x)';
    return { root: z, inputs: { x } };
  },
  () => {
    const a = new Value(2);  a._label = 'a=2';
    const b = new Value(3);  b._label = 'b=3';
    const c = new Value(-1); c._label = 'c=-1';
    const d = new Value(4);  d._label = 'd=4';
    const z = a.mul(b).add(c.mul(d)); z._label = 'a·b + c·d';
    return { root: z, inputs: { a, b, c, d } };
  },
];

let bpExpr = null, bpNodes = [], bpDone = false;

function buildTopo(root) {
  const topo = [], visited = new Set();
  const build = v => {
    if (!visited.has(v)) {
      visited.add(v);
      v._children.forEach(build);
      topo.push(v);
    }
  };
  build(root);
  return topo;
}

function layoutNodes(topo) {
  const depth = new Map();
  topo.forEach(v => {
    const d = v._children.length === 0
      ? 0
      : Math.max(...v._children.map(c => depth.get(c) || 0)) + 1;
    depth.set(v, d);
  });
  const maxD   = Math.max(...depth.values());
  const byDepth = new Map();
  topo.forEach(v => {
    const d = maxD - depth.get(v);
    if (!byDepth.has(d)) byDepth.set(d, []);
    byDepth.get(d).push(v);
  });

  const canvas = document.getElementById('bpCanvas');
  const W = canvas.offsetWidth || 800, H = 420;
  const cols = byDepth.size;
  byDepth.forEach((nodes, col) => {
    const x = (col + 0.5) * W / cols;
    nodes.forEach((node, row) => {
      node._px = x;
      node._py = (row + 0.5) * H / nodes.length;
    });
  });
}

function loadExpr() {
  bpDone  = false;
  const i = parseInt(document.getElementById('exprSel').value);
  bpExpr  = EXPRS[i]();
  bpNodes = buildTopo(bpExpr.root);
  layoutNodes(bpNodes);
  drawBP(false);
}

function runBackprop() {
  if (!bpExpr) loadExpr();
  bpExpr.root.backward();
  bpDone = true;
  drawBP(true);
}

function resetBackprop() {
  bpDone = false;
  loadExpr();
  document.getElementById('nodeInfo').textContent = '點擊畫布上的節點查看詳細資訊...';
}

function drawBP(showGrad) {
  const canvas = document.getElementById('bpCanvas');
  const W = canvas.offsetWidth, H = 420;
  canvas.width = W; canvas.height = H;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, W, H);
  if (!bpNodes.length) return;

  const R = 32;

  // edges
  bpNodes.forEach(v => {
    v._children.forEach(child => {
      ctx.beginPath();
      ctx.moveTo(v._px, v._py);
      ctx.lineTo(child._px, child._py);
      ctx.strokeStyle = showGrad ? 'rgba(255,107,107,0.4)' : 'rgba(100,100,130,0.4)';
      ctx.lineWidth   = showGrad ? 2 : 1;
      ctx.stroke();

      if (showGrad) {
        const mx = (v._px + child._px) / 2;
        const my = (v._py + child._py) / 2;
        ctx.fillStyle = '#ff6b6b';
        ctx.font      = '9px Syne Mono';
        ctx.textAlign = 'center';
        ctx.fillText(`∂=${child.grad.toFixed(3)}`, mx, my - 5);
      }
    });
  });

  // nodes
  bpNodes.forEach(v => {
    const isLeaf = v._children.length === 0;
    ctx.beginPath();
    ctx.arc(v._px, v._py, R, 0, Math.PI * 2);
    ctx.fillStyle   = isLeaf ? '#0d1a0f' : '#0d0d1a';
    ctx.fill();
    ctx.strokeStyle = isLeaf ? '#7fffb2' : (showGrad ? '#ff6b6b' : '#6bcbff');
    ctx.lineWidth   = 2;
    ctx.stroke();

    ctx.fillStyle = isLeaf ? '#7fffb2' : '#e8e8f0';
    ctx.font      = 'bold 11px Syne Mono';
    ctx.textAlign = 'center';
    ctx.fillText(v._op || 'in', v._px, v._py - 4);
    ctx.font      = '10px Syne Mono';
    ctx.fillStyle = '#aaa';
    ctx.fillText(v.data.toFixed(2), v._px, v._py + 10);

    if (showGrad && v.grad !== 0) {
      ctx.fillStyle = '#ff6b6b';
      ctx.font      = '9px Syne Mono';
      ctx.fillText(`g:${v.grad.toFixed(2)}`, v._px, v._py + R + 11);
    }
    if (v._label) {
      ctx.fillStyle = '#55557a';
      ctx.font      = '9px Syne Mono';
      ctx.fillText(v._label, v._px, v._py - R - 5);
    }
  });
}

document.getElementById('bpCanvas').addEventListener('click', e => {
  if (!bpNodes.length) return;
  const rect  = e.target.getBoundingClientRect();
  const scaleX = e.target.width / rect.width;
  const scaleY = e.target.height / rect.height;
  const sx = (e.clientX - rect.left) * scaleX;
  const sy = (e.clientY - rect.top)  * scaleY;
  const hit = bpNodes.find(v => Math.hypot(v._px - sx, v._py - sy) < 34);
  if (hit) {
    document.getElementById('nodeInfo').innerHTML =
      `<span style="color:var(--accent)">${hit._label || hit._op || 'leaf'}</span><br>` +
      `data = <span style="color:var(--accent3)">${hit.data.toFixed(6)}</span><br>` +
      `grad = <span style="color:var(--accent2)">${hit.grad.toFixed(6)}</span><br>` +
      `children = <span style="color:var(--muted)">${hit._children.length}</span>  ` +
      `op = <span style="color:var(--muted)">${hit._op || '—'}</span>`;
  }
});


// ════════════════════════════════════════════
//  6. 程式碼 Tab 圖表 (Tab 3)
// ════════════════════════════════════════════

function drawOptimizerCompare() {
  const canvas = document.getElementById('optimCanvas');
  if (!canvas) return;
  const W = canvas.offsetWidth, H = 220;
  canvas.width = W; canvas.height = H;
  const ctx = canvas.getContext('2d');

  const adam = [], sgd = [];
  let la = 2, ls = 2, ma = 0, va = 0;
  for (let i = 1; i <= 80; i++) {
    const g = 2 - i * 0.025 + (Math.random() - 0.5) * 0.3;
    ma = 0.85 * ma + 0.15 * g;
    va = 0.99 * va + 0.01 * g * g;
    const mh = ma / (1 - 0.85 ** i);
    const vh = va / (1 - 0.99 ** i);
    la = Math.max(0.05, la - 0.015 * mh / (Math.sqrt(vh) + 1e-8) + (Math.random() - 0.5) * 0.05);
    ls = Math.max(0.05, ls - 0.018 * g + (Math.random() - 0.5) * 0.12);
    adam.push(la); sgd.push(ls);
  }

  const pad  = 28;
  const maxV = 2.1;
  const tx   = i => pad + i / 79 * (W - pad * 2);
  const ty   = v => H - pad - (v / maxV) * (H - pad * 2);

  ctx.strokeStyle = '#1a1a28'; ctx.lineWidth = 1;
  [0, 0.5, 1, 1.5, 2].forEach(v => {
    ctx.beginPath(); ctx.moveTo(pad, ty(v)); ctx.lineTo(W - pad, ty(v)); ctx.stroke();
    ctx.fillStyle = '#444'; ctx.font = '8px Syne Mono'; ctx.textAlign = 'right';
    ctx.fillText(v.toFixed(1), pad - 3, ty(v) + 3);
  });

  const draw = (arr, color) => {
    ctx.strokeStyle = color; ctx.lineWidth = 2;
    ctx.beginPath();
    arr.forEach((v, i) => (i === 0 ? ctx.moveTo(tx(i), ty(v)) : ctx.lineTo(tx(i), ty(v))));
    ctx.stroke();
  };
  draw(adam, '#7fffb2');
  draw(sgd,  '#ff6b6b');

  ctx.font = '10px Syne Mono'; ctx.textAlign = 'left';
  ctx.fillStyle = '#7fffb2'; ctx.fillText('Adam', pad + 4,  18);
  ctx.fillStyle = '#ff6b6b'; ctx.fillText('SGD',  pad + 52, 18);
}

function drawGradVanish() {
  const canvas = document.getElementById('gradCanvas');
  if (!canvas) return;
  const W = canvas.offsetWidth, H = 220;
  canvas.width = W; canvas.height = H;
  const ctx = canvas.getContext('2d');

  const layers = 8, pad = 28;
  const barW   = (W - pad * 2) / layers - 6;
  const sig    = Array.from({ length: layers }, (_, i) => Math.pow(0.25, layers - i));
  const rel    = Array.from({ length: layers }, (_, i) => Math.pow(0.85, layers - i));
  const maxV   = Math.max(...rel);
  const ty     = v => H - pad - (v / maxV) * (H - pad * 2);

  [0, 0.25, 0.5, 0.75, 1].forEach(v => {
    ctx.strokeStyle = '#1a1a28'; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(pad, ty(v * maxV)); ctx.lineTo(W - pad, ty(v * maxV)); ctx.stroke();
  });

  sig.forEach((v, i) => {
    const x = pad + i * (barW + 6);
    ctx.fillStyle = 'rgba(255,107,107,0.7)';
    ctx.fillRect(x, ty(v), barW / 2, H - pad - ty(v));
    ctx.fillStyle = 'rgba(127,255,178,0.7)';
    ctx.fillRect(x + barW / 2, ty(rel[i]), barW / 2, H - pad - ty(rel[i]));
  });

  ctx.font = '9px Syne Mono'; ctx.textAlign = 'center';
  ctx.fillStyle = '#666';
  ctx.fillText('Layer 1',   pad + barW / 2,     H - 10);
  ctx.fillText(`Layer ${layers}`, W - pad - barW / 2, H - 10);

  ctx.font = '10px Syne Mono'; ctx.textAlign = 'left';
  ctx.fillStyle = '#ff6b6b'; ctx.fillText('Sigmoid (消失)', pad + 4,   18);
  ctx.fillStyle = '#7fffb2'; ctx.fillText('ReLU (穩定)',    pad + 100,  18);
}


// ════════════════════════════════════════════
//  7. 語言切換 (Tab 3)
// ════════════════════════════════════════════

function switchLang(group, lang, btn) {
  document.getElementById(`${group}-py`).classList.toggle('active', lang === 'py');
  document.getElementById(`${group}-js`).classList.toggle('active', lang === 'js');
  btn.closest('.lang-toggle').querySelectorAll('.lang-btn')
     .forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
}


// ════════════════════════════════════════════
//  8a. MNIST 手寫數字辨識 (Tab 4)
// ════════════════════════════════════════════

const MNIST_W       = 28;
let mnistModel      = null;
let mnistIsDrawing  = false;
let mnistTrainData  = { allX: [], allY: [] };
let mnistTimer      = null;
let mnistEp         = 0;
let mnistTotalEp    = 0;
let mnistAccHistory = [];
let mnistOpt        = null;

// ── 合成筆畫 ──────────────────────────────────

function mnistSyntheticDigit(digit, n = 12) {
  const samples = [];
  for (let s = 0; s < n; s++) {
    const px = new Array(MNIST_W * MNIST_W).fill(0);

    const setLine = (x0, y0, x1, y1, w = 2) => {
      const dx = x1 - x0, dy = y1 - y0, len = Math.hypot(dx, dy);
      for (let t = 0; t < len; t += 0.5) {
        const x = Math.round(x0 + dx * t / len);
        const y = Math.round(y0 + dy * t / len);
        for (let ddy = -w; ddy <= w; ddy++)
          for (let ddx = -w; ddx <= w; ddx++) {
            const pi = (y + ddy) * MNIST_W + (x + ddx);
            if (pi >= 0 && pi < px.length)
              px[pi] = Math.min(1, Math.random() * 0.4 + 0.7);
          }
      }
    };
    const setArc = (cx, cy, r, a0, a1, w = 2) => {
      for (let a = a0; a < a1; a += 0.04) {
        const x = Math.round(cx + r * Math.cos(a));
        const y = Math.round(cy + r * Math.sin(a));
        for (let ddy = -w; ddy <= w; ddy++)
          for (let ddx = -w; ddx <= w; ddx++) {
            const pi = (y + ddy) * MNIST_W + (x + ddx);
            if (pi >= 0 && pi < px.length)
              px[pi] = Math.min(1, Math.random() * 0.3 + 0.7);
          }
      }
    };

    // 每個樣本加入隨機位移，增加多樣性
    const ox = (Math.random() - 0.5) * 3;
    const oy = (Math.random() - 0.5) * 3;
    const c  = 14 + ox, cy2 = 14 + oy;

    if      (digit === 0) setArc(c, cy2, 7 + Math.random(), 0, Math.PI * 2);
    else if (digit === 1) { setLine(c, 5+oy, c, 23+oy); setLine(c-3, 8+oy, c, 5+oy, 1); }
    else if (digit === 2) { setArc(c, 10+oy, 5, Math.PI, 0); setLine(c+5, 10+oy, c-5, 23+oy); setLine(c-5, 23+oy, c+5, 23+oy); }
    else if (digit === 3) { setArc(c, 10+oy, 5, -0.3, Math.PI+0.3); setArc(c, 18+oy, 5, -0.3, Math.PI+0.3); }
    else if (digit === 4) { setLine(c+2, 5+oy, c-6, 16+oy); setLine(c-6, 16+oy, c+6, 16+oy); setLine(c+2, 5+oy, c+2, 23+oy); }
    else if (digit === 5) { setLine(c+4, 5+oy, c-4, 5+oy); setLine(c-4, 5+oy, c-4, 14+oy); setArc(c, 18+oy, 5, Math.PI, Math.PI*2); setLine(c-4, 18+oy, c-4, 14+oy); }
    else if (digit === 6) { setArc(c, cy2, 8, 0.4, Math.PI*1.75); setArc(c, 18+oy, 5, 0, Math.PI*2); }
    else if (digit === 7) { setLine(c-6, 5+oy, c+6, 5+oy); setLine(c+6, 5+oy, c-2, 23+oy); }
    else if (digit === 8) { setArc(c, 10+oy, 5, 0, Math.PI*2); setArc(c, 18+oy, 5, 0, Math.PI*2); }
    else if (digit === 9) { setArc(c, 10+oy, 5, 0, Math.PI*2); setArc(c, cy2, 8, Math.PI*1.2, Math.PI*2.3); }

    // 雜訊
    for (let i = 0; i < px.length; i++)
      if (Math.random() < 0.04) px[i] = Math.random() * 0.25;

    samples.push(px);
  }
  return samples;
}

// ── 把一個樣本畫到小 canvas 上（展示用）────────

function mnistRenderSampleCanvas(canvas, px) {
  const size = canvas.width;
  const ctx  = canvas.getContext('2d');
  ctx.clearRect(0, 0, size, size);
  const img = ctx.createImageData(MNIST_W, MNIST_W);
  for (let i = 0; i < MNIST_W * MNIST_W; i++) {
    const v = Math.round(px[i] * 255);
    img.data[i * 4]     = v;
    img.data[i * 4 + 1] = v;
    img.data[i * 4 + 2] = v;
    img.data[i * 4 + 3] = 255;
  }
  // 畫到臨時 canvas 再縮放
  const tmp = document.createElement('canvas');
  tmp.width = tmp.height = MNIST_W;
  tmp.getContext('2d').putImageData(img, 0, 0);
  ctx.imageSmoothingEnabled = false;
  ctx.drawImage(tmp, 0, 0, size, size);
}

// ── 即時辨識結果展示（類 ConvNetJS 風格）────────

/**
 * 從訓練集隨機抽取 SHOW_N 個樣本，
 * 把每張圖 + 正確標籤 + 預測標籤 + 信心分數畫成小卡片。
 */
function mnistUpdateLiveGrid() {
  const grid = document.getElementById('mnistLiveGrid');
  if (!grid || !mnistModel) return;

  const SHOW_N  = 40;
  const { allX, allY } = mnistTrainData;
  if (allX.length === 0) return;

  // 隨機抽樣
  const picks = Array.from({ length: SHOW_N }, () =>
    Math.floor(Math.random() * allX.length)
  );

  grid.innerHTML = '';

  picks.forEach(idx => {
    const px     = allX[idx];
    const truth  = allY[idx];
    const inp    = px.map(v => new Value(v));
    const logits = mnistModel.forward(inp, ['relu', 'relu']);
    const maxL   = Math.max(...logits.map(v => v.data));
    const exps   = logits.map(v => Math.exp(v.data - maxL));
    const sum    = exps.reduce((a, b) => a + b, 0);
    const probs  = exps.map(v => v / sum);
    const pred   = probs.indexOf(Math.max(...probs));
    const conf   = probs[pred];
    const ok     = pred === truth;

    // 外層 cell
    const cell = document.createElement('div');
    cell.className = `mnist-cell ${ok ? 'correct' : 'wrong'}`;

    // 縮圖 canvas (28×28 → 40×40)
    const canv = document.createElement('canvas');
    canv.width = canv.height = MNIST_W;
    const ctx = canv.getContext('2d');
    const img = ctx.createImageData(MNIST_W, MNIST_W);
    for (let i = 0; i < MNIST_W * MNIST_W; i++) {
      const v = Math.round(px[i] * 255);
      img.data[i * 4]     = v;
      img.data[i * 4 + 1] = v;
      img.data[i * 4 + 2] = v;
      img.data[i * 4 + 3] = 255;
    }
    ctx.putImageData(img, 0, 0);
    cell.appendChild(canv);

    // 標籤列：真實 / 預測
    const lbl = document.createElement('div');
    lbl.className = 'mnist-cell-label';
    lbl.innerHTML =
      `<span class="truth">${truth}</span>` +
      ` → ` +
      `<span class="${ok ? 'pred-ok' : 'pred-err'}">${pred}</span>`;
    cell.appendChild(lbl);

    // 信心分數條
    const bar = document.createElement('div');
    bar.className = 'mnist-conf-bar';
    const fill = document.createElement('div');
    fill.className = `mnist-conf-fill ${ok ? '' : 'wrong'}`;
    fill.style.width = (conf * 100).toFixed(1) + '%';
    bar.appendChild(fill);
    cell.appendChild(bar);

    // 信心數字
    const confLbl = document.createElement('div');
    confLbl.className = 'mnist-cell-label';
    confLbl.textContent = (conf * 100).toFixed(0) + '%';
    cell.appendChild(confLbl);

    grid.appendChild(cell);
  });
}

// ── 準確率曲線 ───────────────────────────────

function mnistDrawAccCurve() {
  const canvas = document.getElementById('mnistAccCanvas');
  if (!canvas) return;
  const W = canvas.offsetWidth || 600, H = 100;
  canvas.width = W; canvas.height = H;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, W, H);

  // grid lines at 25%, 50%, 75%, 100%
  ctx.strokeStyle = '#1a1a28'; ctx.lineWidth = 1;
  [0.25, 0.5, 0.75, 1.0].forEach(v => {
    const y = H - v * (H - 10) - 2;
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
    ctx.fillStyle = '#333'; ctx.font = '8px Syne Mono'; ctx.textAlign = 'left';
    ctx.fillText((v * 100).toFixed(0) + '%', 2, y - 2);
  });

  if (mnistAccHistory.length < 2) return;
  const tx = i => i / (mnistAccHistory.length - 1) * W;
  const ty = v => H - v * (H - 10) - 2;

  ctx.strokeStyle = '#7fffb2'; ctx.lineWidth = 2;
  ctx.beginPath();
  mnistAccHistory.forEach((v, i) =>
    i === 0 ? ctx.moveTo(tx(i), ty(v)) : ctx.lineTo(tx(i), ty(v))
  );
  ctx.stroke();

  // current acc dot
  const last = mnistAccHistory[mnistAccHistory.length - 1];
  ctx.beginPath();
  ctx.arc(tx(mnistAccHistory.length - 1), ty(last), 4, 0, Math.PI * 2);
  ctx.fillStyle = '#7fffb2'; ctx.fill();

  // label
  ctx.fillStyle = '#7fffb2'; ctx.font = 'bold 10px Syne Mono'; ctx.textAlign = 'right';
  ctx.fillText(`acc ${(last * 100).toFixed(1)}%`, W - 4, 14);
}

// ── 訓練啟動 ──────────────────────────────────

function mnistStartTrain() {
  clearInterval(mnistTimer);

  const hiddenSize = parseInt(document.getElementById('mnistHidden').value);
  const lr         = parseFloat(document.getElementById('mnistLR').value);
  const samplesN   = parseInt(document.getElementById('mnistSamples').value);

  // 重建模型
  mnistModel      = makeMLP([MNIST_W * MNIST_W, hiddenSize, hiddenSize / 2, 10]);
  mnistOpt        = new AdamOpt(mnistModel.params(), lr);
  mnistEp         = 0;
  mnistTotalEp    = 100;
  mnistAccHistory = [];

  // 建立訓練集
  mnistTrainData.allX = [];
  mnistTrainData.allY = [];
  for (let d = 0; d < 10; d++) {
    const samples = mnistSyntheticDigit(d, samplesN);
    samples.forEach(px => {
      mnistTrainData.allX.push(px);
      mnistTrainData.allY.push(d);
    });
  }

  document.getElementById('mnistProgWrap').style.display = 'block';
  document.getElementById('mnistTrainBtn').disabled = true;
  document.getElementById('mnistStatus').textContent = '訓練中…';

  const { allX, allY } = mnistTrainData;

  const runEpoch = () => {
    if (mnistEp >= mnistTotalEp) {
      clearInterval(mnistTimer);
      document.getElementById('mnistTrainBtn').disabled = false;
      document.getElementById('mnistStatus').textContent =
        `✓ 完成  最終準確率 ${(mnistAccHistory[mnistAccHistory.length - 1] * 100).toFixed(1)}%`;
      mnistUpdateLiveGrid();
      return;
    }

    // 一個 epoch：打亂順序、全量跑一遍（分批）
    const order = allX.map((_, i) => i).sort(() => Math.random() - 0.5);
    const BS    = 16;
    for (let bi = 0; bi < order.length; bi += BS) {
      mnistModel.zeroGrad();
      let loss = new Value(0);
      const batch = order.slice(bi, bi + BS);
      batch.forEach(i => {
        const inp    = allX[i].map(v => new Value(v));
        const logits = mnistModel.forward(inp, ['relu', 'relu']);
        const maxL   = Math.max(...logits.map(v => v.data));
        const exps   = logits.map(v => v.sub(maxL).exp());
        const sum    = exps.reduce((a, b) => a.add(b));
        loss = loss.add(exps[allY[i]].div(sum).log().mul(-1));
      });
      loss.div(batch.length).backward();
      mnistOpt.step();
    }

    // 測試集準確率（用訓練集本身當快速評估）
    let correct = 0;
    allX.forEach((px, i) => {
      const inp    = px.map(v => new Value(v));
      const logits = mnistModel.forward(inp, ['relu', 'relu']);
      const best   = logits.reduce((bi2, v, j) => v.data > logits[bi2].data ? j : bi2, 0);
      if (best === allY[i]) correct++;
    });
    const acc = correct / allX.length;
    mnistAccHistory.push(acc);
    mnistEp++;

    const pct = mnistEp / mnistTotalEp * 100;
    document.getElementById('mnistProgBar').style.width = pct + '%';
    document.getElementById('mnistStatus').textContent =
      `epoch ${mnistEp}/${mnistTotalEp}  acc ${(acc * 100).toFixed(1)}%`;

    mnistDrawAccCurve();
    mnistUpdateLiveGrid();   // ← 每 epoch 更新即時辨識展示
    setTimeout(runEpoch, 0);
  };

  setTimeout(runEpoch, 0);
}

// ── 重置 ──────────────────────────────────────

function mnistReset() {
  clearInterval(mnistTimer);
  mnistModel      = null;
  mnistAccHistory = [];
  mnistEp         = 0;
  document.getElementById('mnistTrainBtn').disabled      = false;
  document.getElementById('mnistStatus').textContent     = '尚未訓練';
  document.getElementById('mnistProgWrap').style.display = 'none';
  document.getElementById('mnistProgBar').style.width    = '0%';
  const grid = document.getElementById('mnistLiveGrid');
  if (grid) grid.innerHTML = '';
  mnistDrawAccCurve();
  mnistClear();
}

// ── 繪圖 canvas 事件 ──────────────────────────

function mnistInitCanvas() {
  const canvas = document.getElementById('mnistDraw');
  if (!canvas) return;
  canvas.addEventListener('mousedown',  e => { mnistIsDrawing = true;  mnistDrawAt(e); });
  canvas.addEventListener('mousemove',  e => { if (mnistIsDrawing) mnistDrawAt(e); });
  canvas.addEventListener('mouseup',    () => (mnistIsDrawing = false));
  canvas.addEventListener('mouseleave', () => (mnistIsDrawing = false));
  canvas.addEventListener('touchstart', e => { e.preventDefault(); mnistIsDrawing = true;  mnistDrawAt(e.touches[0]); }, { passive: false });
  canvas.addEventListener('touchmove',  e => { e.preventDefault(); if (mnistIsDrawing) mnistDrawAt(e.touches[0]); },   { passive: false });
  canvas.addEventListener('touchend',   () => (mnistIsDrawing = false));
}

function mnistDrawAt(e) {
  const canvas = document.getElementById('mnistDraw');
  const rect   = canvas.getBoundingClientRect();
  const cx     = (e.clientX - rect.left) * (180 / rect.width);
  const cy     = (e.clientY - rect.top)  * (180 / rect.height);
  const ctx    = canvas.getContext('2d');
  ctx.fillStyle = '#fff';
  ctx.beginPath();
  ctx.arc(cx, cy, 11, 0, Math.PI * 2);
  ctx.fill();
}

function mnistClear() {
  const canvas = document.getElementById('mnistDraw');
  if (canvas) canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
  document.getElementById('mnistResult').textContent = '—';
  for (let i = 0; i < 10; i++) {
    const pb = document.getElementById(`pbar${i}`);
    const pp = document.getElementById(`ppct${i}`);
    if (pb) { pb.style.width = '0%'; pb.classList.remove('top'); }
    if (pp)   pp.textContent = '0%';
  }
}

function mnistGetPixels() {
  const src = document.getElementById('mnistDraw');
  const tmp = document.createElement('canvas');
  tmp.width = tmp.height = MNIST_W;
  const ctx = tmp.getContext('2d');
  ctx.drawImage(src, 0, 0, MNIST_W, MNIST_W);
  const data = ctx.getImageData(0, 0, MNIST_W, MNIST_W).data;
  return Array.from({ length: MNIST_W * MNIST_W }, (_, i) => data[i * 4] / 255);
}

function mnistPredict() {
  if (!mnistModel) {
    document.getElementById('mnistStatus').textContent = '請先點「開始訓練」！';
    return;
  }
  const inp    = mnistGetPixels().map(v => new Value(v));
  const logits = mnistModel.forward(inp, ['relu', 'relu']);
  const maxL   = Math.max(...logits.map(v => v.data));
  const exps   = logits.map(v => Math.exp(v.data - maxL));
  const sum    = exps.reduce((a, b) => a + b, 0);
  const probs  = exps.map(v => v / sum);
  const best   = probs.indexOf(Math.max(...probs));

  document.getElementById('mnistResult').textContent = best;
  for (let i = 0; i < 10; i++) {
    const pct = (probs[i] * 100).toFixed(1);
    const pb  = document.getElementById(`pbar${i}`);
    const pp  = document.getElementById(`ppct${i}`);
    if (pb) { pb.style.width = pct + '%'; pb.classList.toggle('top', i === best); }
    if (pp)   pp.textContent = pct + '%';
  }
}

// ── 初始化：建立預測列 + 綁 canvas 事件 ────────

function mnistInit() {
  // 建立預測 bar (0–9)
  const bars = document.getElementById('predBars');
  if (bars) {
    bars.innerHTML = Array.from({ length: 10 }, (_, i) => `
      <div class="pred-row">
        <span class="pred-digit">${i}</span>
        <div class="pred-bar-wrap">
          <div class="pred-bar-fill" id="pbar${i}" style="width:0%"></div>
        </div>
        <span class="pred-pct" id="ppct${i}">0%</span>
      </div>`).join('');
  }

  mnistInitCanvas();
  mnistDrawAccCurve();
}


// ════════════════════════════════════════════
//  8b. 函數逼近器 (Tab 4)
// ════════════════════════════════════════════

let funcPoints = [];
let funcModel2 = null;
let funcOpt    = null;
let funcTimer  = null;

function funcInit() {
  const canvas = document.getElementById('funcCanvas');
  if (!canvas) return;
  canvas.addEventListener('click', e => {
    const rect = canvas.getBoundingClientRect();
    const x    =  (e.clientX - rect.left) / rect.width  * 2 - 1;
    const y    = -((e.clientY - rect.top)  / rect.height * 2 - 1);
    funcPoints.push([x, y]);
    funcDraw();
    document.getElementById('funcStatus').textContent = `${funcPoints.length} 個點`;
  });
  funcDraw();
}

function funcReset() {
  clearInterval(funcTimer);
  funcPoints = [];
  funcModel2 = null;
  funcOpt    = null;
  document.getElementById('funcStatus').textContent = '點擊畫布加入點…';
  funcDraw();
}

function funcTrain() {
  if (funcPoints.length < 2) {
    document.getElementById('funcStatus').textContent = '請先加入至少 2 個點';
    return;
  }
  clearInterval(funcTimer);
  funcModel2 = makeMLP([1, 32, 32, 1]);
  funcOpt    = new AdamOpt(funcModel2.params(), 0.01);
  let step   = 0;

  funcTimer = setInterval(() => {
    funcModel2.zeroGrad();
    let loss = new Value(0);
    funcPoints.forEach(([x, y]) => {
      const pred = funcModel2.forward([new Value(x)], ['tanh', 'tanh'])[0];
      const diff = pred.sub(y);
      loss = loss.add(diff.mul(diff));
    });
    const avg = loss.div(funcPoints.length);
    avg.backward();
    funcOpt.step();
    step++;

    if (step % 20 === 0) funcDraw(step);
    if (step >= 600) {
      clearInterval(funcTimer);
      document.getElementById('funcStatus').textContent = '訓練完成！';
    } else {
      document.getElementById('funcStatus').textContent =
        `step ${step}  loss: ${avg.data.toFixed(4)}`;
    }
  }, 15);
}

function funcDraw() {
  const canvas = document.getElementById('funcCanvas');
  if (!canvas) return;
  const W = canvas.offsetWidth || 400, H = 200;
  canvas.width = W; canvas.height = H;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, W, H);

  const toSX = x =>  (x + 1) / 2 * W;
  const toSY = y => (1 - (y + 1) / 2) * H;

  // axes
  ctx.strokeStyle = '#1a1a28'; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(0, H / 2); ctx.lineTo(W, H / 2); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(W / 2, 0); ctx.lineTo(W / 2, H); ctx.stroke();

  // fitted curve
  if (funcModel2) {
    ctx.strokeStyle = 'rgba(127,255,178,0.8)'; ctx.lineWidth = 2;
    ctx.beginPath();
    for (let i = 0; i <= W; i++) {
      const x  = i / W * 2 - 1;
      const sy = toSY(funcModel2.forward([new Value(x)], ['tanh', 'tanh'])[0].data);
      i === 0 ? ctx.moveTo(i, sy) : ctx.lineTo(i, sy);
    }
    ctx.stroke();
  }

  // data points
  funcPoints.forEach(([x, y]) => {
    ctx.beginPath();
    ctx.arc(toSX(x), toSY(y), 5, 0, Math.PI * 2);
    ctx.fillStyle   = '#ff6b6b';
    ctx.strokeStyle = '#0a0a0f';
    ctx.lineWidth   = 1;
    ctx.fill();
    ctx.stroke();
  });
}


// ════════════════════════════════════════════
//  8c. 邏輯電路學習 (Tab 4)
// ════════════════════════════════════════════

const GATE_INPUTS = [[0, 0], [0, 1], [1, 0], [1, 1]];
let gateTargets      = [0, 1, 1, 0];   // XOR default
let gateModel        = null;
let gateOpt          = null;
let gateTimer        = null;
let gateLossHistory  = [];

function gateInit() { gatePreset('xor'); }

function gatePreset(name) {
  clearInterval(gateTimer);
  if      (name === 'xor') gateTargets = [0, 1, 1, 0];
  else if (name === 'and') gateTargets = [0, 0, 0, 1];
  else if (name === 'or')  gateTargets = [0, 1, 1, 1];
  gateModel = null;
  gateOpt   = null;
  gateRenderTable();
  document.getElementById('gateStatus').textContent = '就緒';
  drawGateLoss([]);
}

function gateRenderTable() {
  document.getElementById('truthBody').innerHTML =
    GATE_INPUTS.map((inp, i) => `
      <tr>
        <td>${inp[0]}</td>
        <td>${inp[1]}</td>
        <td class="target-cell" onclick="gateToggle(${i})" title="點擊切換">
          ${gateTargets[i]}
        </td>
        <td class="pred-cell" id="gatePred${i}">—</td>
      </tr>`).join('');
}

function gateToggle(i) {
  gateTargets[i] = 1 - gateTargets[i];
  gateRenderTable();
  if (gateModel) gateTrain();
}

function gateTrain() {
  clearInterval(gateTimer);
  gateModel        = makeMLP([2, 8, 8, 1]);
  gateOpt          = new AdamOpt(gateModel.params(), 0.02);
  gateLossHistory  = [];
  let step         = 0;

  gateTimer = setInterval(() => {
    for (let k = 0; k < 5; k++) {
      gateModel.zeroGrad();
      let loss = new Value(0);
      GATE_INPUTS.forEach((inp, i) => {
        const x      = inp.map(v => new Value(v));
        const pred   = gateModel.forward(x, ['relu', 'relu'])[0].tanh();
        const target = gateTargets[i] * 2 - 1;     // map {0,1} → {-1,1}
        const diff   = pred.sub(target);
        loss         = loss.add(diff.mul(diff));
      });
      loss.div(4).backward();
      gateOpt.step();
      step++;
      gateLossHistory.push(loss.data / 4);
    }

    GATE_INPUTS.forEach((inp, i) => {
      const x    = inp.map(v => new Value(v));
      const raw  = gateModel.forward(x, ['relu', 'relu'])[0].tanh().data;
      const pred = raw > 0 ? 1 : 0;
      const el   = document.getElementById(`gatePred${i}`);
      if (el) {
        el.textContent  = pred;
        el.style.color  = pred === gateTargets[i] ? 'var(--accent)' : 'var(--accent2)';
      }
    });

    drawGateLoss(gateLossHistory);
    const lastLoss = gateLossHistory[gateLossHistory.length - 1];
    document.getElementById('gateStatus').textContent =
      `step ${step * 5}  loss: ${lastLoss.toFixed(4)}`;

    if (step * 5 >= 1000 || lastLoss < 0.01) {
      clearInterval(gateTimer);
      document.getElementById('gateStatus').textContent =
        `✓ 收斂  loss: ${lastLoss.toFixed(4)}`;
    }
  }, 30);
}

function drawGateLoss(history) {
  const canvas = document.getElementById('gateCanvas');
  if (!canvas) return;
  const W = canvas.offsetWidth || 400, H = 80;
  canvas.width = W; canvas.height = H;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, W, H);
  if (history.length < 2) return;

  const maxV = Math.max(...history.slice(0, 5), 0.1);
  ctx.strokeStyle = '#7fffb2'; ctx.lineWidth = 1.5;
  ctx.beginPath();
  history.forEach((v, i) => {
    const x = i / (history.length - 1) * W;
    const y = H - (v / maxV) * (H - 8) - 4;
    i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
  });
  ctx.stroke();
  ctx.fillStyle = '#333'; ctx.font = '9px Syne Mono'; ctx.textAlign = 'left';
  ctx.fillText('LOSS', 4, 12);
}


// ════════════════════════════════════════════
//  8d. 加法規律學習 — 熱力圖 (Tab 4)
// ════════════════════════════════════════════

const ARITH_N    = 10;
let arithModel   = null;
let arithOpt     = null;
let arithTimer   = null;
let arithTrainSet = [];

function arithReset() {
  clearInterval(arithTimer);
  arithModel = null;
  const cover = parseInt(document.getElementById('coverSlider').value) / 100;
  arithTrainSet = [];
  for (let i = 0; i < ARITH_N; i++)
    for (let j = 0; j < ARITH_N; j++)
      if (Math.random() < cover) arithTrainSet.push([i, j]);

  document.getElementById('arithStatus').textContent =
    `訓練集 ${arithTrainSet.length}/${ARITH_N * ARITH_N} 格`;
  drawArithTrain();
  drawArithHeatmap(null);
}

function arithTrain() {
  clearInterval(arithTimer);
  if (arithTrainSet.length === 0) arithReset();
  arithModel = makeMLP([2, 32, 32, 1]);
  arithOpt   = new AdamOpt(arithModel.params(), 0.005);
  let step   = 0;

  arithTimer = setInterval(() => {
    for (let k = 0; k < 10; k++) {
      arithModel.zeroGrad();
      let loss  = new Value(0);
      const batch = [...arithTrainSet].sort(() => Math.random() - 0.5).slice(0, 16);
      batch.forEach(([i, j]) => {
        const x      = i / (ARITH_N - 1);
        const y      = j / (ARITH_N - 1);
        const target = (x + y) / 2;
        const pred   = arithModel.forward([new Value(x), new Value(y)], ['relu', 'relu'])[0];
        const d      = pred.sub(target);
        loss         = loss.add(d.mul(d));
      });
      loss.div(batch.length).backward();
      arithOpt.step();
      step++;
    }
    drawArithHeatmap(arithModel);
    document.getElementById('arithStatus').textContent = `step ${step * 10}`;
    if (step * 10 >= 3000) {
      clearInterval(arithTimer);
      document.getElementById('arithStatus').textContent = `✓ 訓練完成 step ${step * 10}`;
    }
  }, 20);
}

function drawArithTrain() {
  const canvas = document.getElementById('arithTrain');
  if (!canvas) return;
  const W = canvas.offsetWidth || 300, H = 200;
  canvas.width = W; canvas.height = H;
  const ctx  = canvas.getContext('2d');
  ctx.clearRect(0, 0, W, H);
  const cellW = W / ARITH_N, cellH = H / ARITH_N;
  const trainSet = new Set(arithTrainSet.map(([i, j]) => `${i},${j}`));

  for (let i = 0; i < ARITH_N; i++) {
    for (let j = 0; j < ARITH_N; j++) {
      ctx.fillStyle = trainSet.has(`${i},${j}`)
        ? 'rgba(127,255,178,0.5)'
        : 'rgba(255,107,107,0.15)';
      ctx.fillRect(i * cellW, j * cellH, cellW - 1, cellH - 1);
    }
  }
  ctx.fillStyle = '#444'; ctx.font = '8px Syne Mono'; ctx.textAlign = 'center';
  ctx.fillText('x →', W / 2, H - 2);
  ctx.save();
  ctx.translate(6, H / 2);
  ctx.rotate(-Math.PI / 2);
  ctx.fillText('y →', 0, 0);
  ctx.restore();
}

function drawArithHeatmap(model) {
  const canvas = document.getElementById('arithCanvas');
  if (!canvas) return;
  const W = canvas.offsetWidth || 300, H = 200;
  canvas.width = W; canvas.height = H;
  const ctx  = canvas.getContext('2d');
  ctx.clearRect(0, 0, W, H);
  const cellW = W / ARITH_N, cellH = H / ARITH_N;

  for (let i = 0; i < ARITH_N; i++) {
    for (let j = 0; j < ARITH_N; j++) {
      const x      = i / (ARITH_N - 1);
      const y      = j / (ARITH_N - 1);
      const target = (x + y) / 2;
      let err      = 0.5;
      if (model) {
        const pred = model.forward([new Value(x), new Value(y)], ['relu', 'relu'])[0].data;
        err = Math.min(1, Math.abs(pred - target) * 4);
      }
      const r = Math.round(err * 255);
      const g = Math.round((1 - err) * 200);
      ctx.fillStyle = `rgba(${r},${g},60,0.85)`;
      ctx.fillRect(i * cellW, j * cellH, cellW - 1, cellH - 1);

      if (!model && cellW > 20) {
        ctx.fillStyle = '#555'; ctx.font = '8px Syne Mono'; ctx.textAlign = 'center';
        ctx.fillText((x + y).toFixed(1), i * cellW + cellW / 2, j * cellH + cellH / 2 + 3);
      }
    }
  }

  // legend
  const grd = ctx.createLinearGradient(W - 50, 0, W, 0);
  grd.addColorStop(0, 'rgba(0,200,60,0.8)');
  grd.addColorStop(1, 'rgba(255,0,60,0.8)');
  ctx.fillStyle = grd;
  ctx.fillRect(W - 50, 4, 46, 8);
  ctx.fillStyle = '#666'; ctx.font = '7px Syne Mono';
  ctx.textAlign = 'left';  ctx.fillText('準', W - 50, 20);
  ctx.textAlign = 'right'; ctx.fillText('誤', W - 4,  20);
}


// ════════════════════════════════════════════
//  9. 工具函式 & Tab 路由 & 初始化
// ════════════════════════════════════════════

function switchTab(name) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  event.target.classList.add('active');
  document.getElementById('panel-' + name).classList.add('active');

  if (name === 'code')     setTimeout(() => { drawOptimizerCompare(); drawGradVanish(); }, 50);
  if (name === 'backprop') setTimeout(() => { loadExpr(); }, 50);
  if (name === 'train')    setTimeout(() => { if (trainState) { drawDecision(); drawLossChart(); } }, 50);
  if (name === 'apps')     setTimeout(() => {
    funcDraw();
    drawArithTrain();
    drawArithHeatmap(null);
    drawGateLoss([]);
  }, 50);
}

function updateSlider(el, labelId, scale = 1) {
  const v   = parseFloat(el.value) * (scale || 1);
  const el2 = document.getElementById(labelId);
  el2.textContent = scale < 1 ? v.toFixed(3) : v;
}

function clearCanvas(id) {
  const c = document.getElementById(id);
  c.width = c.offsetWidth;
  c.height = 300;
  c.getContext('2d').clearRect(0, 0, c.width, c.height);
}

function log(msg) {
  const el = document.getElementById('trainLog');
  el.innerHTML += '<br>' + msg;
  el.scrollTop  = el.scrollHeight;
}

// ── 啟動 ──
window.addEventListener('load', () => {
  initTrain();
  loadExpr();
  mnistInit();
  funcInit();
  gateInit();
  arithReset();

  window.addEventListener('resize', () => {
    if (trainState)      { drawDecision(); drawLossChart(); }
    if (bpNodes.length)  { layoutNodes(bpNodes); drawBP(bpDone); }
  });
});
