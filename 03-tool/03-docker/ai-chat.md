https://gemini.google.com/app/9534a09c71a4bab5

這是一套基於 **Ubuntu 24.04** 的全功能開發環境建置流程，採用相容性最高的 `glibc` 環境，內建 **Python, Rust, Node.js, GCC/Make, Vim, Tmux, Curl** 等完整工具鏈，並掛載 Mac 的共享資料夾 `/Users/Shared/ccc`。

---

## 📁 第一步：建立專案配置檔案

請在 Mac 的終端機中選擇一個目錄（例如建立一個 `my-dev-env` 檔案夾）並進去：

```bash
mkdir -p ~/my-dev-env && cd ~/my-dev-env

```

在該目錄下建立以下 **兩個檔案**：

### 1. 建立 `Dockerfile`

建立名為 `Dockerfile` 的檔案，貼入以下內容：

```dockerfile
# 採用 Ubuntu 24.04 LTS 作為基礎鏡像 (glibc 環境，相容性最高)
FROM ubuntu:24.04

# 設定非互動模式與時區，避免安裝時跳出互動詢問
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Taipei

# 1. 更新系統並安裝基礎開發工具：GCC, Make, Python3, Node.js, Vim, Tmux, Curl 等
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    make \
    curl \
    git \
    vim \
    tmux \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    ca-certificates \
    sudo \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# 2. 安裝官方 Rust 工具鏈 (rustup, rustc, cargo)
ENV RUSTUP_HOME=/usr/local/rustup \
    CARGO_HOME=/usr/local/cargo \
    PATH=/usr/local/cargo/bin:$PATH

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && rustup --version \
    && cargo --version \
    && rustc --version

# 3. 設定啟動預設目錄
WORKDIR /ccc

# 4. 保留背景執行指令
CMD ["sleep", "infinity"]

```

---

### 2. 建立 `docker-compose.yml`

在同一個目錄下建立名為 `docker-compose.yml` 的檔案，貼入以下內容：

```yaml
services:
  ubuntu-dev:
    build: .
    container_name: my-ubuntu-vm
    restart: always
    volumes:
      # 將 Mac 的共享資料夾 /Users/Shared/ccc 掛載至容器內的 /ccc
      - /Users/Shared/ccc:/ccc
    working_dir: /ccc

```

> ⚠️ **提示**：請確保 Mac 本地已先建立 `/Users/Shared/ccc` 資料夾（若不存在可先在 Mac 執行 `mkdir -p /Users/Shared/ccc`）。

---

## 🚀 第二步：一鍵構建與啟動容器

在包含上述兩個檔案的目錄下，於 Mac 終端機依序執行：

1. **1. 構建 Image:** docker compose build.
執行鏡像打包指令：

```bash
docker compose build

```

*說明：* 初次構建需要下載 Ubuntu 基礎層與各項開發工具包，耗時約 1~3 分鐘。


2. **2. 啟動背景容器:** docker compose up -d.
啟動名為 `my-ubuntu-vm` 的容器：

```bash
docker compose up -d

```

*驗證步驟：* 執行 `docker ps`，確認列表中名為 `my-ubuntu-vm` 的容器狀態為 `Up`。


3. **3. 進入開發虛擬機:** docker exec.
連入容器內部的 Bash Shell：

```bash
docker exec -it my-ubuntu-vm bash

```

*驗證步驟：* 進入容器後，逐一執行以下指令確認工具皆已準備就緒：

```bash
python3 --version
rustc --version
cargo --version
node -v
gcc --version
vim --version
tmux -V

```


---

## ⚡ 第三步：設定 Mac 快捷鍵（Alias）

為了讓你在 Mac 上隨時輸入一個短指令就能一秒進入這台「Linux 虛擬機」，請在 Mac 的終端機執行：

```bash
echo 'alias vm="docker exec -it my-ubuntu-vm bash"' >> ~/.zshrc
source ~/.zshrc

```

**今後的使用習慣：**

* **隨時連入**：打開 Mac 終端機，直接輸入 **`vm`** 即可直通虛擬機！
* **離開**：輸入 `exit` 退出 Shell。容器依然會持續在背景運作，隨時等待你再次進入。
* **檔案同步**：你在容器內部的 `/ccc` 目錄下建立或修改的任何檔案，都會即時同步儲存在 Mac 的 `/Users/Shared/ccc` 中！