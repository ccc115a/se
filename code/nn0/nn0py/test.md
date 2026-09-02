
```sh
(venv) cccuser@cccimacdeiMac nn0py % ./test.sh
+ python examples/ex1-grad.py
=== 1. 基礎自動微分運算 ===
前向計算結果 y.data = 50.0000
dy/da = 16.0000 (理論值 x^2 = 16)
dy/db = 1.0000 (理論值 1)
dy/dx = 24.0000 (理論值 2ax = 2*3*4 = 24)
+ python examples/ex2-linear.py

=== 2. 線性回歸訓練 ===
Epoch  0 | Loss: 41.0000 | w: 0.1000, b: 0.1000
Epoch 10 | Loss: 8.3166 | w: 1.0469, b: 1.0453
Epoch 20 | Loss: 0.1920 | w: 1.7021, b: 1.6866
Epoch 30 | Loss: 0.3412 | w: 1.8924, b: 1.8399
Epoch 40 | Loss: 0.1206 | w: 1.8143, b: 1.7098
Epoch 50 | Loss: 0.0717 | w: 1.7598, b: 1.5991
+ python examples/ex3-xor.py

=== 3. 多層感知器 (XOR) ===
Epoch   0 | Loss: 3.9844
Epoch  20 | Loss: 0.2863
Epoch  40 | Loss: 0.2557
Epoch  60 | Loss: 0.2514
Epoch  80 | Loss: 0.2504
Epoch 100 | Loss: 0.2501
預測結果:
輸入 [0, 0] -> 預測: 0.4888 (目標: 0)
輸入 [0, 1] -> 預測: 0.5034 (目標: 1)
輸入 [1, 0] -> 預測: 0.4957 (目標: 1)
輸入 [1, 1] -> 預測: 0.5102 (目標: 0)
+ python examples/ex4-classify.py

=== 4. Softmax 與 Cross-Entropy Loss ===
Logits    : [2.0, 1.0, 0.1]
Probs     : [0.659, 0.2424, 0.0986]
Loss      : 0.4170
Logits 梯度: [-0.341, 0.2424, 0.0986]
+ python examples/ex5-charpredicate.py

=== 5. 迷你字元預測器 ===
Epoch   0 | Loss: 1.4074
Epoch  20 | Loss: 0.3630
Epoch  40 | Loss: 0.3523
Epoch  60 | Loss: 0.3505
Epoch  80 | Loss: 0.3495
Epoch 100 | Loss: 0.3488
測試輸入 'a' -> 預測下一個字元: 'p'
+ python examples/gpt0demo.py ../_data/corpus/tw.txt
num docs: 147
vocab size: 96
num params: 6400
Training for 1000 steps ...
step 1000 / 1000 | loss 0.8818
--- inference (20 samples, temperature=0.5) ---
sample  1: 你看到一隻大貓
sample  2: 你會看書
sample  3: 我們都是好朋友
sample  4: 他在家裡看書
sample  5: 她很開心
sample  6: 我喜歡小魚
sample  7: 山上有小花
sample  8: 小狗跑在地上
sample  9: 大貓吃了肉
sample 10: 大鳥在路上
sample 11: 她會唱歌
sample 12: 小貓吃了蟲
sample 13: 小鳥很可愛
sample 14: 你喜歡小狗
sample 15: 小貓飛在地上
sample 16: 你喜歡大鳥
sample 17: 我在家裡看書
sample 18: 你看到一隻大狗
sample 19: 他在家裡看書
sample 20: 山上有大樹
```