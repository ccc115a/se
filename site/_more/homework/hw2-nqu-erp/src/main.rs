mod config;
mod db;
mod entities;
mod errors;
mod handlers;
mod middleware;

use axum::{
    http::HeaderValue,
    routing::{get, post, put},
    Router,
};
use std::net::SocketAddr;
use tower_http::cors::{Any, CorsLayer};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

#[derive(Clone)]
pub struct AppState {
    pub db: sea_orm::DatabaseConnection,
    pub jwt_secret: String,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    tracing_subscriber::registry()
        .with(tracing_subscriber::fmt::layer())
        .init();

    let config = config::Config::from_env();

    let db = db::establish_connection(&config).await?;
    db::run_migrations(&db).await?;

    tracing::info!("Database migrations completed");

    let state = AppState {
        db,
        jwt_secret: config.jwt_secret.clone(),
    };

    let cors = CorsLayer::new()
        .allow_origin(HeaderValue::from_static("http://localhost:5173"))
        .allow_methods(Any)
        .allow_headers(Any);

    let app = Router::new()
        .route("/health", get(|| async { "OK" }))
        .route("/api/v1/auth/login", post(handlers::auth::login))
        .route("/api/v1/courses", get(handlers::course::list_courses))
        .route(
            "/api/v1/enrollments",
            post(handlers::enrollment::enroll_course).delete(handlers::enrollment::drop_course),
        )
        .route(
            "/api/v1/students/me/schedule",
            get(handlers::enrollment::get_student_schedule),
        )
        .route(
            "/api/v1/students/me/grades",
            get(handlers::grade::get_student_grades),
        )
        .route(
            "/api/v1/teachers/me/courses",
            get(handlers::course::get_teacher_courses),
        )
        .route(
            "/api/v1/teachers/me/courses/{course_id}/students",
            get(handlers::grade::get_course_roster),
        )
        .route(
            "/api/v1/grades/batch",
            put(handlers::grade::batch_update_grades),
        )
        .route(
            "/api/v1/grades/submit",
            post(handlers::grade::submit_grades),
        )
        .route(
            "/api/v1/admin/courses",
            post(handlers::admin::create_course),
        )
        .route(
            "/api/v1/admin/courses/{course_id}",
            put(handlers::admin::update_course).delete(handlers::admin::delete_course),
        )
        .route(
            "/api/v1/admin/users",
            get(handlers::admin::list_users).post(handlers::admin::create_user),
        )
        .route(
            "/api/v1/admin/users/{user_id}",
            put(handlers::admin::update_user).delete(handlers::admin::delete_user),
        )
        .route(
            "/api/v1/admin/teachers",
            get(handlers::admin::list_teachers),
        )
        .route(
            "/api/v1/admin/departments",
            get(handlers::admin::list_departments),
        )
        .with_state(state)
        .layer(cors);

    let addr: SocketAddr = config.server_addr.parse()?;
    tracing::info!("Server starting on http://{}", addr);

    let listener = tokio::net::TcpListener::bind(addr).await?;
    axum::serve(listener, app).await?;

    Ok(())
}
