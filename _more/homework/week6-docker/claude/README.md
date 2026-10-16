# Docker 學習記錄與微服務實作

## 一、Docker 學習筆記

### 1. 核心概念

| 名詞 | 說明 |
|------|------|
| Image（映像） | 唯讀的應用程式模板，由 Dockerfile 一層一層建出來 |
| Container（容器） | Image 執行起來的實例，彼此隔離，共用主機 kernel |
| Dockerfile | 描述如何建置 image 的腳本 |
| Volume | 讓資料脫離容器生命週期（刪掉容器資料仍在） |
| Network | 容器之間的虛擬網路，同一網路內可用「服務名稱」當主機名稱 |
| docker compose | 用一個 YAML 檔定義並同時管理多個容器 |

容器與虛擬機（VM）的差別：VM 有完整 guest OS，容器只隔離程序，啟動快、體積小。

### 2. 常用指令

```bash
# 映像
docker pull nginx:alpine          # 下載映像
docker images                     # 列出映像
docker build -t myapp:1.0 .       # 依 Dockerfile 建置
docker rmi myapp:1.0              # 刪除映像

# 容器
docker run -d --name web -p 8080:80 nginx:alpine   # 背景執行並對應埠
docker ps -a                      # 列出容器（含已停止）
docker logs -f web                # 追蹤日誌
docker exec -it web sh            # 進入容器
docker stop web && docker rm web  # 停止並刪除

# 資料與網路
docker volume ls
docker network ls
docker run -v mydata:/data ...    # 掛載 named volume

# Compose
docker compose up -d --build      # 建置並啟動全部服務
docker compose ps                 # 查看狀態
docker compose logs -f node       # 看單一服務日誌
docker compose down               # 停止並移除容器（保留 volume）
docker compose down -v            # 連 volume 一起刪除

# 清理
docker system prune -a            # 清掉未使用的映像/容器/網路
```

### 3. Dockerfile 重點

- `FROM` 選基底映像，優先選 `alpine` / `slim` 以縮小體積。
- 先 `COPY package.json` 再 `RUN npm install`，最後才 `COPY` 原始碼，
  這樣程式碼改動時能重複使用依賴層的 cache。
- Multi-stage build：Rust 服務用 `rust` 映像編譯，最後只把執行檔複製到
  `debian:slim`，映像從約 2 GB 降到約 100 MB。
- `USER node` 避免以 root 執行。
- `EXPOSE` 只是文件標註，真正對外開放要靠 `-p` 或 compose 的 `ports`。

### 4. 學習過程中的心得與踩雷

1. **`localhost` 在容器裡指的是自己**。服務之間要用 compose 的服務名稱
   （例如 `db`、`node`），不能寫 `localhost`。
2. **`depends_on` 只等容器啟動，不等資料庫就緒**。所以 db 加了
   `healthcheck`（`pg_isready`），再用 `condition: service_healthy` 等它。
3. `docker-entrypoint-initdb.d/` 裡的 SQL 只在 **資料目錄為空時**執行一次；
   要重跑需 `docker compose down -v`。
4. nginx 的 `proxy_pass http://node:3000/;` 結尾有 `/` 時，
   會把 location 前綴（`/api/node/`）去掉再轉發。
5. compose 檔中想寫 shell 變數 `$VAR` 要寫成 `$$VAR`。
6. 只有 nginx 對外開埠，資料庫與各服務都不暴露，減少攻擊面。

---

## 二、系統說明

### 架構

```
                        ┌──────────── backend network ─────────────┐
 瀏覽器 ──:8080──► nginx ─┬─ /api/node/   ─► Node.js (Express) ──┐   │
   (frontend network)    ├─ /api/python/ ─► Python  (Flask)  ───┼─► PostgreSQL
                         └─ /api/rust/   ─► Rust    (axum)       │   │  (volume: pgdata)
                        └──────────────────────────────────────────┘
```

| 容器 | 技術 | 職責 |
|------|------|------|
| nginx | nginx 1.27 | 提供靜態網頁、reverse proxy 轉發 `/api/*` |
| node | Node.js 20 + Express + pg | 留言板的新增與查詢 |
| python | Python 3.12 + Flask + psycopg2 | 讀取留言並做統計（字詞頻率、平均長度） |
| rust | Rust + axum（multi-stage build） | CPU 密集運算：質數篩法 |
| db | PostgreSQL 16 | 儲存留言，資料存在 named volume |

### 專案結構

```
.
├── docker-compose.yml
├── db/init.sql                 # 建表與初始資料
├── nginx/
│   ├── Dockerfile
│   ├── nginx.conf              # reverse proxy 設定
│   └── html/index.html         # 展示用 web 介面
└── services/
    ├── node/    (Dockerfile, package.json, server.js)
    ├── python/  (Dockerfile, requirements.txt, app.py)
    └── rust/    (Dockerfile, Cargo.toml, src/main.rs)
```

### 執行方式

```bash
docker compose up -d --build
```

第一次建置 Rust 需要下載並編譯依賴，約需數分鐘。完成後開啟
<http://localhost:8080>。

```bash
docker compose ps                 # 確認 5 個容器都在執行
curl localhost:8080/api/node/health
curl localhost:8080/api/python/stats
curl "localhost:8080/api/rust/primes?limit=1000000"
docker compose down               # 停止（資料保留）
```

可用 `.env` 覆寫資料庫帳密：`POSTGRES_USER`、`POSTGRES_PASSWORD`、`POSTGRES_DB`。

### Web 介面功能

- 頂端四個「貨櫃」顯示 Node.js、Python、Rust、PostgreSQL 的即時健康狀態。
- 留言板：送出留言 → Node.js 寫入 PostgreSQL → 重新讀取列表。
- 留言統計：Python 服務即時分析資料庫內容。
- 質數運算：Rust 服務計算並回報耗時。

### 驗證重點

- 刪除容器再重建（`docker compose down && docker compose up -d`），留言仍在 → volume 生效。
- `docker compose stop python` 後，頁面上 Python 變紅、其他功能不受影響 → 微服務彼此獨立。
