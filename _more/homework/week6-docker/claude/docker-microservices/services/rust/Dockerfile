# Multi-stage build：編譯階段很大，最終映像只留執行檔
FROM rust:1-bookworm AS builder
WORKDIR /app
COPY Cargo.toml ./
COPY src ./src
RUN cargo build --release

FROM debian:bookworm-slim
COPY --from=builder /app/target/release/rust-service /usr/local/bin/rust-service
EXPOSE 8000
CMD ["rust-service"]
