# 採用 Ubuntu 24.04 作為基礎，相容性最高 (glibc)
FROM ubuntu:24.04

# 1. 設定非互動模式，避免安裝過程跳出時區設定等提示
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Taipei

# 2. 安裝基礎系統工具、C/C++ 編譯器、Python 3、Node.js、Tmux、Vim、Curl 等
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
    && rm -rf /var/lib/apt/lists/*

# 3. 安裝 Rust 官方工具鏈 (Rustup, Rustc, Cargo)
ENV RUSTUP_HOME=/usr/local/rustup \
    CARGO_HOME=/usr/local/cargo \
    PATH=/usr/local/cargo/bin:$PATH

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && rustup --version \
    && cargo --version \
    && rustc --version

# 4. 設定預設工作目錄
WORKDIR /ccc

# 5. 設定背景保活指令，確保 Container 啟動後不會自動退出
CMD ["sleep", "infinity"]