use axum::{extract::State, Json};
use sea_orm::{ColumnTrait, EntityTrait, QueryFilter};
use serde::{Deserialize, Serialize};

use crate::entities::users;
use crate::errors::AppError;
use crate::middleware::create_token;
use crate::AppState;

#[derive(Deserialize)]
pub struct LoginRequest {
    pub username: String,
    pub password: String,
}

#[derive(Serialize)]
pub struct LoginResponse {
    pub token: String,
    pub user_id: i32,
    pub username: String,
    pub full_name: String,
    pub role: String,
}

pub async fn login(
    State(state): State<AppState>,
    Json(payload): Json<LoginRequest>,
) -> Result<Json<LoginResponse>, AppError> {
    let user = users::Entity::find()
        .filter(users::Column::Username.eq(&payload.username))
        .one(&state.db)
        .await?
        .ok_or_else(|| AppError::unauthorized("帳號或密碼錯誤"))?;

    let password_valid = bcrypt::verify(&payload.password, &user.password_hash)
        .map_err(|_| AppError::internal("密碼驗證錯誤"))?;

    if !password_valid {
        return Err(AppError::unauthorized("帳號或密碼錯誤"));
    }

    let token = create_token(user.user_id, &user.username, &user.role, &state.jwt_secret)
        .map_err(|e| AppError::internal(format!("Token 產生失敗: {}", e)))?;

    Ok(Json(LoginResponse {
        token,
        user_id: user.user_id,
        username: user.username,
        full_name: user.full_name,
        role: user.role,
    }))
}
