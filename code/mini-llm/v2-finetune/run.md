# mini-llm v2 -- run.sh

## finetune

```
(.venv) cccuser@cccimacdeiMac v2-finetune % ./run.sh
=== 開始生成合成訓練資料 (智慧家庭助理) ===
-> 儲存純文字檔 (pretrain.txt, finetune.txt)...
✅ 機器人指令產生完成！
詞表大小: 89 字元
詞表已儲存為 vocab.json
Pretrain 資料已儲存，長度: 200697
使用硬體: cpu | 開始 Pre-training...
Pretrain Step    0 | Loss: 4.6894
Pretrain Step  100 | Loss: 0.2096
Pretrain Step  200 | Loss: 0.1540
Pretrain Step  300 | Loss: 0.1453
Pretrain Step  400 | Loss: 0.1559
Pretrain Step  499 | Loss: 0.1467
預訓練完成！模型已儲存為 pretrain.pt
Finetune 資料已建立，長度: 51168
成功載入 pretrain.pt 權重！
使用硬體: cpu | 開始 Fine-tuning...
Finetune Step    0 | Loss: 3.7132
Finetune Step  100 | Loss: 0.2097
Finetune Step  200 | Loss: 0.1833
Finetune Step  299 | Loss: 0.1832
微調完成！模型已儲存為 finetune.pt

==================================================
測試對話 (自動抓取訓練集第一句進行測試)
==================================================
📝 抽取到的題目: <Q>請幫我打開廚房的冷氣。<A>
🎯 預期的解答: 系統指令：打開廚房冷氣
--------------------------------------------------
🤖 AI 實際輸出:
<Q>請幫我打開廚房的冷氣。<A>系統指令：打開廚房冷氣
<Q>我在客廳，有點吵。<A>系統指令：關閉客廳電視
<Q請幫我打開臥室的電視。<A>系統指令：打開臥室電視
<Q>請幫我打開臥室的電視。<A>系統指令：打開臥室電視
<Q>我
==================================================
```
