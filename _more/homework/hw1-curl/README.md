# rurl — 用 Rust 實作的 curl 替代工具

`rurl` 是一個以 Rust 實作的輕量、非同步 HTTP/HTTPS 客戶端，
提供類似 `curl` 的命令列介面。目前為 **Phase 1（v0.1.0）**：
基礎 CLI 解析 + HTTP 請求。

## 功能

- **HTTP 方法**：`GET / POST / PUT / DELETE / HEAD / PATCH`，以 `-X` 指定（大小寫不敏感）
- **自訂 Header**：`-H "Name: Value"`，可重複使用
- **Request Body**：`-d` / `--data`；提供 `-d` 且未指定方法時自動由 `GET` 升級為 `POST`（仿 curl）
- **重新導向**：`-L` 跟隨重導向（最多 20 次）；預設不跟隨
- **逾時**：`-m` / `--max-time`（秒）
- **回應標頭**：`-i` 在 body 前印出 HTTP 狀態行與標頭
- **詳細日誌**：`-v` 將請求資訊輸出至 stderr（不污染 stdout）
- **輸出至檔案**：`-o` / `--output` 將 response body 存檔

設計原則：**stdout 只輸出 response body**，日誌與診斷訊息一律到 **stderr**，
方便管線（pipe）處理。

## 快速開始

### 需求

- Rust toolchain（`cargo`，2021 edition）

### 建置與執行

```bash
cargo build                        # 編譯，產出 ./target/debug/rurl
cargo run -- <url>                 # 直接執行
cargo run -- -i https://example.com

cargo clippy                       # lint（維持 0 warning）
cargo fmt                          # 格式化（提交前執行）
```

### 測試

```bash
./test.sh                            # 完整自動化測試（需網路，預設 httpbin.org）
BASE=http://localhost:8080 ./test.sh # 覆寫測試伺服器（離線 / CI 用）
```

`test.sh` 涵蓋 11 個步驟、22 項斷言：clippy / build、版本輸出、
方法正確性、Header / Body、轉址、逾時、標頭顯示、verbose、檔案輸出。

## 用法

```
rurl [OPTIONS] <URL>

Options:
  -X, --request <METHOD>    HTTP method（預設 GET）
  -H, --header <HEADERS>    自訂 header（-H "Name: Value"，可重複）
  -d, --data <DATA>         request body 資料
  -L, --location            跟隨重新導向
  -m, --max-time <TIMEOUT>  請求逾時（秒）
  -i, --include             輸出包含 response headers
  -v, --verbose             詳細輸出（至 stderr）
  -o, --output <OUTPUT>     將 body 寫入檔案
  -h, --help                顯示說明
  -V, --version             顯示版本
```

### 範例

```bash
# 基本 GET
./target/debug/rurl https://api.github.com/users/octocat

# POST JSON
./target/debug/rurl -X POST https://httpbin.org/post \
  -H "Content-Type: application/json" -d '{"name": "rust"}'

# -d 未指定方法時自動升級為 POST（仿 curl）
./target/debug/rurl -d 'foo=bar' https://httpbin.org/post

# 自訂 header
./target/debug/rurl -H "X-Custom: rurl-unit" https://httpbin.org/headers

# 跟隨重導向 + 逾時 10 秒 + 顯示回應標頭
./target/debug/rurl -L -m 10 -i https://example.com

# 存檔 + 詳細訊息（診斷訊息走 stderr，body 寫入檔案）
./target/debug/rurl -v -o page.html https://example.com

# 其他方法
./target/debug/rurl -X PUT -d 'x=1' https://httpbin.org/put
./target/debug/rurl -X PATCH -d 'x=1' https://httpbin.org/patch
./target/debug/rurl -X DELETE -d 'x=1' https://httpbin.org/delete
```

### 錯誤處理

- Header 格式錯誤（缺少 `:`）會回報錯誤並以非零 exit code 結束：
  ```bash
  ./target/debug/rurl -H "NoColonHere" https://httpbin.org/get  # 失敗
  ```
- 無效網域 / 逾時會輸出 `Error` 至 stderr：
  ```bash
  ./target/debug/rurl http://nonexistent-domain-abc123.invalid/
  ./target/debug/rurl -m 1 https://httpbin.org/delay/3
  ```

## 專案結構

```
hw1-curl/
├── Cargo.toml          # 依賴：clap, reqwest, tokio, anyhow
├── src/
│   ├── main.rs         # 入口：parse CLI → execute → output
│   ├── cli.rs          # clap 參數定義、HttpMethod、header 解析、infer_method()
│   ├── client.rs       # Response struct、client::execute() 核心請求邏輯
│   └── output.rs       # print_response / write_to_file
├── _doc/               # 版本文件（如 v0.1.md）
├── test.sh             # bash 整合測試
└── README.md
```

## 技術選型

| 套件 | 用途 |
|------|------|
| `clap` (derive) | CLI 參數解析 |
| `reqwest` | 非同步 HTTP 客戶端（TLS + 內建 redirect 策略） |
| `tokio` | 非同步執行環境 |
| `anyhow` | 錯誤處理（`main` 回傳 `anyhow::Result<()>`） |

實作重點：

- `cli::Cli::infer_method()`：提供 `-d` 且方法為 `GET` 時自動升級為 `POST`。
- `cli::parse_headers()`：自訂 header 一律以 `"Name: Value"` 格式解析，非法格式回報錯誤。
- `HttpMethod::from_str` 大小寫不敏感（`-X GET` 與 `-X get` 皆可）。
- `client::execute()` 以 `Client::builder()` 統一處理 timeout 與 redirect 策略。

## 開發慣例

- 每次修改後依序執行：`cargo fmt` → `cargo clippy` → `cargo build` → 相關測試。
- 維持 `cargo clippy` 與 `cargo build` **零警告**。
- 新增 CLI 旗標須同步更新 `test.sh` 與 `_doc/`。
- 詳細設計與版本紀錄見 [`_doc/v0.1.md`](_doc/v0.1.md)。

## 後續規劃

Phase 1 已完成 Header / Body / Timeout / 轉址 / 檔案輸出；
後續階段預計加入 JSON / 標頭色彩高亮、檔案下載進度條（見 `_doc/v0.1.md`）。
