ccc:
/start

CccBot:
✅ Bot 連線正常。
WORK_DIR=/Users/Shared/ccc/bot
直接傳一句話就會丟給 opencode 執行（例如：幫我寫 tsmc.py）。

ccc:
請幫我用 Python 寫一個抓取台股台積電 (2330) 今日股價的腳本，並存成 tsmc3.py

CccBot:
幫你抓 2330 今日股價，存成 tsmc3.py。
已建立，現在驗證執行。
已存成 `tsmc3.py` 並驗證可執行：

* 僅用標準函式庫（`urllib` + `json`），免安裝套件
* 先抓 TWSE MIS 即時 API（盤中/收盤價），失敗自動備援 `STOCK_DAY_ALL`
* 執行：`python3 tsmc3.py`

剛實測輸出：台積電 20260918 收盤 2460，開盤 2460，最高 2460，最低 2435（週末顯示上個交易日，正常）。

← Write tsmc3.py
Wrote file successfully.

