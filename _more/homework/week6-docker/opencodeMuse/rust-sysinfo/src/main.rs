use axum::{routing::get, Json, Router};
use serde::Serialize;
use std::time::Instant;

static START: std::sync::OnceLock<Instant> = std::sync::OnceLock::new();

#[derive(Serialize)]
struct Info {
    service: &'static str,
    language: &'static str,
    hostname: String,
    os: String,
    uptime_sec: u64,
}

async fn info() -> Json<Info> {
    let start = START.get_or_init(Instant::now);
    Json(Info {
        service: "rust-sysinfo",
        language: "rust (axum)",
        hostname: hostname::get()
            .map(|h| h.to_string_lossy().into_owned())
            .unwrap_or_else(|_| "unknown".into()),
        os: std::env::consts::OS.to_string(),
        uptime_sec: start.elapsed().as_secs(),
    })
}

async fn health() -> Json<serde_json::Value> {
    Json(serde_json::json!({"status": "ok", "service": "rust-sysinfo"}))
}

#[tokio::main]
async fn main() {
    let app = Router::new().route("/sys/info", get(info)).route("/health", get(health));
    let listener = tokio::net::TcpListener::bind("0.0.0.0:9000").await.unwrap();
    println!("rust-sysinfo listening on :9000");
    axum::serve(listener, app).await.unwrap();
}
