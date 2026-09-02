# mini-llm v3 -- run.sh

## distill

```
(.venv) cccuser@cccimacdeiMac v3-distill % ./run.sh
詞表大小: 210 字元
詞表已儲存為 vocab.json
Pretrain 資料已儲存，長度: 100500
使用硬體: cpu | 開始 Pre-training...
Pretrain Step    0 | Loss: 5.5207
Pretrain Step  100 | Loss: 0.4385
Pretrain Step  200 | Loss: 0.3225
Pretrain Step  300 | Loss: 0.3103
Pretrain Step  400 | Loss: 0.3038
Pretrain Step  499 | Loss: 0.2945
預訓練完成！模型已儲存為 pretrain.pt
Finetune 資料已建立，長度: 30726
成功載入 pretrain.pt 權重！
使用硬體: cpu | 開始 Fine-tuning...
Finetune Step    0 | Loss: 5.0307
Finetune Step  100 | Loss: 0.3926
Finetune Step  200 | Loss: 0.2456
Finetune Step  299 | Loss: 0.2222
微調完成！模型已儲存為 finetune.pt

==================================================
測試對話 (自動抓取訓練集第一句進行測試)
==================================================
📝 抽取到的題目: <Q>火星的大氣層怎樣？<A>
🎯 預期的解答: 很稀薄
--------------------------------------------------
🤖 AI 實際輸出:
<Q>火星的大氣層怎樣？<A>很稀薄
<Q>行星的公轉軌道大致呈什麼形狀？<A>橢圓形
<Q>地球的直徑約為多少？<A>一萬二千七百公里
<Q>水星的表面有什麼？<A>八百公里
<Q>行星的自轉速度影響什麼？<A「大紅斑
<Q>水
==================================================
```
