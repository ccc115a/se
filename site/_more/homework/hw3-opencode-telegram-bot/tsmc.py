#!/usr/bin/env python3
"""抓取台股台積電 (2330) 今日股價.

資料來源: 臺灣證券交易所 (TWSE) 官方 API, 僅用 Python 標準函式庫, 不需安裝套件.
執行: python3 tsmc.py
"""

import json
import urllib.request
import urllib.error
from datetime import datetime

STOCK_ID = "2330"
MIS_URL = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_{STOCK_ID}.tw&json=1&delay=0"
DAY_ALL_URL = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"

HEADERS = {"User-Agent": "Mozilla/5.0"}


def fetch_json(url: str, timeout: int = 10) -> dict | list:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return json.loads(resp.read().decode(charset))


def get_from_mis() -> dict | None:
    """從 MIS 即時 API 抓今日盤中/收盤價, 最即時."""
    try:
        data = fetch_json(MIS_URL)
        rows = data.get("msgArray", []) if isinstance(data, dict) else []
        if not rows:
            return None
        s = rows[0]
        # z: 現價/收盤價, o: 開盤, h: 最高, l: 最低, y: 昨收, v: 累積成交量(張已除千?), d: 日期
        return {
            "source": "TWSE MIS 即時API",
            "stock_id": s.get("c", STOCK_ID),
            "name": s.get("n", "台積電"),
            "date": f"{s.get('d', '')} {s.get('t', '')}".strip(),
            "current": s.get("z", "-"),
            "open": s.get("o", "-"),
            "high": s.get("h", "-"),
            "low": s.get("l", "-"),
            "prev_close": s.get("y", "-"),
            "volume_lots": s.get("v", "-"),
        }
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError) as e:
        print(f"[MIS API 失敗] {e}")
        return None


def get_from_day_all() -> dict | None:
    """備援: 從 STOCK_DAY_ALL 抓最近一筆 2330 收盤資料."""
    try:
        data = fetch_json(DAY_ALL_URL)
        if not isinstance(data, list):
            return None
        for row in data:
            if row.get("Code") == STOCK_ID:
                return {
                    "source": "TWSE STOCK_DAY_ALL",
                    "stock_id": STOCK_ID,
                    "name": row.get("Name", "台積電"),
                    "date": row.get("Date", ""),
                    "current": row.get("ClosingPrice", "-"),
                    "open": row.get("OpeningPrice", "-"),
                    "high": row.get("HighestPrice", "-"),
                    "low": row.get("LowestPrice", "-"),
                    "prev_close": "",
                    "volume_lots": row.get("TradeVolume", "-"),
                }
        return None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        print(f"[DAY_ALL API 失敗] {e}")
        return None


def get_tsmc_price() -> dict | None:
    return get_from_mis() or get_from_day_all()


def main() -> None:
    print(f"台積電 ({STOCK_ID}) 今日股價查詢中... ({datetime.now():%Y-%m-%d %H:%M})")
    info = get_tsmc_price()
    if not info:
        print("抓取失敗, 請檢查網路連線後再試。")
        raise SystemExit(1)
    print(f"資料來源: {info['source']}")
    print(f"股票: {info['name']} ({info['stock_id']})")
    print(f"時間/日期: {info['date']}")
    print(f"現價/收盤: {info['current']}")
    print(f"開盤: {info['open']}  最高: {info['high']}  最低: {info['low']}")
    if info.get("prev_close") and info["prev_close"] != "-":
        print(f"昨收: {info['prev_close']}")
    print(f"成交量: {info['volume_lots']}")


if __name__ == "__main__":
    main()
