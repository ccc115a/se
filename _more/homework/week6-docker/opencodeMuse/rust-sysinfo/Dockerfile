# ---- Rust sysinfo (multi-stage build) ----
# 第一階段：編譯 (直接複製全部原始碼編譯，避免假 main 快取陷阱)
FROM rust:bookworm AS builder
WORKDIR /app
COPY Cargo.toml Cargo.lock* ./
COPY src ./src
RUN cargo build --release

# 第二階段：最小執行環境
FROM debian:bookworm-slim
WORKDIR /app
COPY --from=builder /app/target/release/sysinfo /app/sysinfo
EXPOSE 9000
CMD ["/app/sysinfo"]
