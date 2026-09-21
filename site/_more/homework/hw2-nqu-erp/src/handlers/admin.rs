use axum::{extract::Path, extract::State, Json};
use sea_orm::{ActiveModelTrait, ColumnTrait, EntityTrait, QueryFilter, Set, TransactionTrait};
use serde::{Deserialize, Serialize};

use crate::entities::{class_schedules, courses, departments, enrollments, grades, users};
use crate::errors::AppError;
use crate::middleware::AuthUser;
use crate::AppState;

#[derive(Deserialize)]
pub struct CreateCourseRequest {
    pub course_code: String,
    pub academic_year: i32,
    pub semester: i32,
    pub course_name: String,
    pub teacher_id: i32,
    pub credits: i32,
    pub capacity: i32,
    pub dept_id: i32,
}

#[derive(Serialize)]
pub struct AdminResponse {
    pub success: bool,
    pub message: String,
}

pub async fn create_course(
    State(state): State<AppState>,
    auth: AuthUser,
    Json(payload): Json<CreateCourseRequest>,
) -> Result<Json<AdminResponse>, AppError> {
    if !auth.is_admin() {
        return Err(AppError::forbidden("只有管理員可以開課"));
    }

    let course = courses::ActiveModel {
        course_code: Set(payload.course_code),
        academic_year: Set(payload.academic_year),
        semester: Set(payload.semester),
        course_name: Set(payload.course_name),
        teacher_id: Set(payload.teacher_id),
        credits: Set(payload.credits),
        capacity: Set(payload.capacity),
        enrolled_count: Set(0),
        dept_id: Set(payload.dept_id),
        ..Default::default()
    }
    .insert(&state.db)
    .await?;

    Ok(Json(AdminResponse {
        success: true,
        message: format!("課程建立成功，ID: {}", course.course_id),
    }))
}

#[derive(Deserialize)]
pub struct CreateUserRequest {
    pub username: String,
    pub password: String,
    pub full_name: String,
    pub role: String,
    pub dept_id: i32,
    pub email: String,
}

pub async fn create_user(
    State(state): State<AppState>,
    auth: AuthUser,
    Json(payload): Json<CreateUserRequest>,
) -> Result<Json<AdminResponse>, AppError> {
    if !auth.is_admin() {
        return Err(AppError::forbidden("只有管理員可以建立帳號"));
    }

    let password_hash =
        bcrypt::hash(&payload.password, 10).map_err(|_| AppError::internal("密碼雜湊失敗"))?;

    let user = users::ActiveModel {
        username: Set(payload.username),
        password_hash: Set(password_hash),
        full_name: Set(payload.full_name),
        role: Set(payload.role),
        dept_id: Set(payload.dept_id),
        email: Set(payload.email),
        ..Default::default()
    }
    .insert(&state.db)
    .await?;

    Ok(Json(AdminResponse {
        success: true,
        message: format!("帳號建立成功，ID: {}", user.user_id),
    }))
}

#[derive(Serialize)]
pub struct UserListItem {
    pub user_id: i32,
    pub username: String,
    pub full_name: String,
    pub role: String,
    pub dept_id: i32,
    pub dept_name: String,
    pub email: String,
}

pub async fn list_users(
    State(state): State<AppState>,
    auth: AuthUser,
) -> Result<Json<Vec<UserListItem>>, AppError> {
    if !auth.is_admin() {
        return Err(AppError::forbidden("只有管理員可以查看帳號"));
    }

    let all_users = users::Entity::find().all(&state.db).await?;
    let mut items = Vec::new();

    for u in &all_users {
        let dept = departments::Entity::find_by_id(u.dept_id)
            .one(&state.db)
            .await?;
        items.push(UserListItem {
            user_id: u.user_id,
            username: u.username.clone(),
            full_name: u.full_name.clone(),
            role: u.role.clone(),
            dept_id: u.dept_id,
            dept_name: dept.map(|d| d.dept_name).unwrap_or_default(),
            email: u.email.clone(),
        });
    }

    Ok(Json(items))
}

#[derive(Serialize)]
pub struct TeacherListItem {
    pub user_id: i32,
    pub username: String,
    pub full_name: String,
    pub dept_name: String,
}

pub async fn list_teachers(
    State(state): State<AppState>,
    auth: AuthUser,
) -> Result<Json<Vec<TeacherListItem>>, AppError> {
    if !auth.is_admin() {
        return Err(AppError::forbidden("只有管理員可以查看教師清單"));
    }

    let all_users = users::Entity::find()
        .filter(users::Column::Role.eq("TEACHER"))
        .all(&state.db)
        .await?;
    let mut items = Vec::new();

    for u in &all_users {
        let dept = departments::Entity::find_by_id(u.dept_id)
            .one(&state.db)
            .await?;
        items.push(TeacherListItem {
            user_id: u.user_id,
            username: u.username.clone(),
            full_name: u.full_name.clone(),
            dept_name: dept.map(|d| d.dept_name).unwrap_or_default(),
        });
    }

    Ok(Json(items))
}

#[derive(Serialize)]
pub struct DepartmentItem {
    pub dept_id: i32,
    pub dept_code: String,
    pub dept_name: String,
}

pub async fn list_departments(
    State(state): State<AppState>,
    auth: AuthUser,
) -> Result<Json<Vec<DepartmentItem>>, AppError> {
    if !auth.is_admin() {
        return Err(AppError::forbidden("只有管理員可以查看科系清單"));
    }

    let depts = departments::Entity::find().all(&state.db).await?;
    Ok(Json(
        depts
            .into_iter()
            .map(|d| DepartmentItem {
                dept_id: d.dept_id,
                dept_code: d.dept_code,
                dept_name: d.dept_name,
            })
            .collect(),
    ))
}

#[derive(Deserialize)]
pub struct UpdateUserRequest {
    pub password: Option<String>,
    pub full_name: String,
    pub role: String,
    pub dept_id: i32,
    pub email: String,
}

pub async fn update_user(
    State(state): State<AppState>,
    auth: AuthUser,
    Path(user_id): Path<i32>,
    Json(payload): Json<UpdateUserRequest>,
) -> Result<Json<AdminResponse>, AppError> {
    if !auth.is_admin() {
        return Err(AppError::forbidden("只有管理員可以修改帳號"));
    }

    let user = users::Entity::find_by_id(user_id)
        .one(&state.db)
        .await?
        .ok_or_else(|| AppError::not_found("帳號不存在"))?;

    let mut model: users::ActiveModel = user.into();
    if let Some(password) = payload.password {
        if !password.is_empty() {
            let hash =
                bcrypt::hash(&password, 10).map_err(|_| AppError::internal("密碼雜湊失敗"))?;
            model.password_hash = Set(hash);
        }
    }
    model.full_name = Set(payload.full_name);
    model.role = Set(payload.role);
    model.dept_id = Set(payload.dept_id);
    model.email = Set(payload.email);
    model.update(&state.db).await?;

    Ok(Json(AdminResponse {
        success: true,
        message: "帳號更新成功".to_string(),
    }))
}

pub async fn delete_user(
    State(state): State<AppState>,
    auth: AuthUser,
    Path(user_id): Path<i32>,
) -> Result<Json<AdminResponse>, AppError> {
    if !auth.is_admin() {
        return Err(AppError::forbidden("只有管理員可以刪除帳號"));
    }
    if user_id == auth.user_id {
        return Err(AppError::bad_request("不能刪除自己"));
    }

    let user = users::Entity::find_by_id(user_id)
        .one(&state.db)
        .await?
        .ok_or_else(|| AppError::not_found("帳號不存在"))?;

    let has_courses = !courses::Entity::find()
        .filter(courses::Column::TeacherId.eq(user_id))
        .all(&state.db)
        .await?
        .is_empty();
    if has_courses {
        return Err(AppError::bad_request("該教師尚有授課課程，無法刪除"));
    }

    let has_enrollments = !enrollments::Entity::find()
        .filter(enrollments::Column::StudentId.eq(user_id))
        .all(&state.db)
        .await?
        .is_empty();
    if has_enrollments {
        return Err(AppError::bad_request("該學生尚有選課紀錄，無法刪除"));
    }

    users::Entity::delete_by_id(user_id).exec(&state.db).await?;

    Ok(Json(AdminResponse {
        success: true,
        message: format!("帳號 {} 刪除成功", user.username),
    }))
}

#[derive(Deserialize)]
pub struct UpdateCourseRequest {
    pub course_code: String,
    pub academic_year: i32,
    pub semester: i32,
    pub course_name: String,
    pub teacher_id: i32,
    pub credits: i32,
    pub capacity: i32,
    pub dept_id: i32,
}

pub async fn update_course(
    State(state): State<AppState>,
    auth: AuthUser,
    Path(course_id): Path<i32>,
    Json(payload): Json<UpdateCourseRequest>,
) -> Result<Json<AdminResponse>, AppError> {
    if !auth.is_admin() {
        return Err(AppError::forbidden("只有管理員可以修改課程"));
    }

    let course = courses::Entity::find_by_id(course_id)
        .one(&state.db)
        .await?
        .ok_or_else(|| AppError::not_found("課程不存在"))?;

    let mut model: courses::ActiveModel = course.into();
    model.course_code = Set(payload.course_code);
    model.academic_year = Set(payload.academic_year);
    model.semester = Set(payload.semester);
    model.course_name = Set(payload.course_name);
    model.teacher_id = Set(payload.teacher_id);
    model.credits = Set(payload.credits);
    model.capacity = Set(payload.capacity);
    model.dept_id = Set(payload.dept_id);
    model.update(&state.db).await?;

    Ok(Json(AdminResponse {
        success: true,
        message: "課程更新成功".to_string(),
    }))
}

pub async fn delete_course(
    State(state): State<AppState>,
    auth: AuthUser,
    Path(course_id): Path<i32>,
) -> Result<Json<AdminResponse>, AppError> {
    if !auth.is_admin() {
        return Err(AppError::forbidden("只有管理員可以刪除課程"));
    }

    let course = courses::Entity::find_by_id(course_id)
        .one(&state.db)
        .await?
        .ok_or_else(|| AppError::not_found("課程不存在"))?;

    let tx = state.db.begin().await?;
    let enrollments = enrollments::Entity::find()
        .filter(enrollments::Column::CourseId.eq(course_id))
        .all(&tx)
        .await?;
    let enrollment_ids: Vec<i32> = enrollments.iter().map(|e| e.enrollment_id).collect();
    if !enrollment_ids.is_empty() {
        grades::Entity::delete_many()
            .filter(grades::Column::EnrollmentId.is_in(enrollment_ids))
            .exec(&tx)
            .await?;
    }
    enrollments::Entity::delete_many()
        .filter(enrollments::Column::CourseId.eq(course_id))
        .exec(&tx)
        .await?;
    class_schedules::Entity::delete_many()
        .filter(class_schedules::Column::CourseId.eq(course_id))
        .exec(&tx)
        .await?;
    courses::Entity::delete_by_id(course_id).exec(&tx).await?;
    tx.commit().await?;

    Ok(Json(AdminResponse {
        success: true,
        message: format!("課程 {} 刪除成功", course.course_name),
    }))
}
