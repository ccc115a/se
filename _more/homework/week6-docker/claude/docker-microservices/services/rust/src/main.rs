// Rust 服務：CPU 密集運算（質數篩法），展示高效能後端
use axum::{extract::Query, routing::get, Json, Router};
use serde_json::{json, Value};
use std::{collections::HashMap, time::Instant};

fn count_primes(limit: usize) -> usize {
    if limit < 2 {
        return 0;
    }
    let mut sieve = vec![true; limit + 1];
    sieve[0] = false;
    sieve[1] = false;
    let mut i = 2;
    while i * i <= limit {
        if sieve[i] {
            let mut j = i * i;
            while j <= limit {
                sieve[j] = false;
                j += i;
            }
        }
        i += 1;
    }
    sieve.iter().filter(|&&p| p).count()
}

async fn health() -> Json<Value> {
    Json(json!({ "service": "rust", "runtime": "axum 0.7", "status": "ok" }))
}

async fn primes(Query(q): Query<HashMap<String, String>>) -> Json<Value> {
    let limit: usize = q
        .get("limit")
        .and_then(|v| v.parse().ok())
        .unwrap_or(1_000_000)
        .min(50_000_000);
    let start = Instant::now();
    let count = tokio::task::spawn_blocking(move || count_primes(limit))
        .await
        .unwrap();
    Json(json!({ "limit": limit, "primes": count, "elapsed_ms": start.elapsed().as_secs_f64() * 1000.0 }))
}

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/health", get(health))
        .route("/primes", get(primes));
    let listener = tokio::net::TcpListener::bind("0.0.0.0:8000").await.unwrap();
    println!("rust service on :8000");
    axum::serve(listener, app).await.unwrap();
}
