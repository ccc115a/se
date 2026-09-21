use axum::extract::{Path, State};
use axum::Json;
use sea_orm::{ActiveModelTrait, ColumnTrait, EntityTrait, QueryFilter, Set, TransactionTrait};
use serde::{Deserialize, Serialize};

use crate::entities::{courses, enrollments, grades, users};
use crate::errors::AppError;
use crate::middleware::AuthUser;
use crate::AppState;

#[derive(Deserialize)]
pub struct GradeEntry {
    pub enrollment_id: i32,
    pub midterm_score: Option<f64>,
    pub final_score: Option<f64>,
}

#[derive(Deserialize)]
pub struct BatchGradeRequest {
    pub course_id: i32,
    pub grades: Vec<GradeEntry>,
}

#[derive(Serialize)]
pub struct GradeResponse {
    pub success: bool,
    pub message: String,
}

#[derive(Deserialize)]
pub struct SubmitRequest {
    pub course_id: i32,
}

pub async fn batch_update_grades(
    State(state): State<AppState>,
    auth: AuthUser,
    Json(payload): Json<BatchGradeRequest>,
) -> Result<Json<GradeResponse>, AppError> {
    if !auth.is_teacher() {
        return Err(AppError::forbidden("只有教師可以登錄成績"));
    }

    let tx = state.db.begin().await?;

    for entry in &payload.grades {
        let enrollment = enrollments::Entity::find_by_id(entry.enrollment_id)
            .one(&tx)
            .await?
            .ok_or_else(|| AppError::not_found("選課紀錄不存在"))?;

        if enrollment.course_id != payload.course_id {
            return Err(AppError::bad_request("選課紀錄不屬於此課程"));
        }

        let existing_grade = grades::Entity::find()
            .filter(grades::Column::EnrollmentId.eq(entry.enrollment_id))
            .one(&tx)
            .await?;

        let midterm = entry.midterm_score.unwrap_or(0.0);
        let final_ = entry.final_score.unwrap_or(0.0);
        let total = midterm * 0.4 + final_ * 0.6;

        if let Some(g) = existing_grade {
            if g.is_submitted {
                return Err(AppError::forbidden("此課程成績已送交，無法修改"));
            }

            grades::Entity::update(grades::ActiveModel {
                grade_id: Set(g.grade_id),
                midterm_score: Set(Some(midterm)),
                final_score: Set(Some(final_)),
                total_score: Set(Some(total)),
                updated_at: Set(chrono::Utc::now()),
                ..Default::default()
            })
            .exec(&tx)
            .await?;
        } else {
            grades::ActiveModel {
                enrollment_id: Set(entry.enrollment_id),
                midterm_score: Set(Some(midterm)),
                final_score: Set(Some(final_)),
                total_score: Set(Some(total)),
                ..Default::default()
            }
            .insert(&tx)
            .await?;
        }
    }

    tx.commit().await?;

    Ok(Json(GradeResponse {
        success: true,
        message: "成績登錄成功".into(),
    }))
}

pub async fn submit_grades(
    State(state): State<AppState>,
    auth: AuthUser,
    Json(payload): Json<SubmitRequest>,
) -> Result<Json<GradeResponse>, AppError> {
    if !auth.is_teacher() {
        return Err(AppError::forbidden("只有教師可以送交成績"));
    }

    let enrollments = enrollments::Entity::find()
        .filter(enrollments::Column::CourseId.eq(payload.course_id))
        .all(&state.db)
        .await?;

    for e in &enrollments {
        let grade = grades::Entity::find()
            .filter(grades::Column::EnrollmentId.eq(e.enrollment_id))
            .one(&state.db)
            .await?;

        if let Some(g) = grade {
            grades::Entity::update(grades::ActiveModel {
                grade_id: Set(g.grade_id),
                is_submitted: Set(true),
                updated_at: Set(chrono::Utc::now()),
                ..Default::default()
            })
            .exec(&state.db)
            .await?;
        }
    }

    Ok(Json(GradeResponse {
        success: true,
        message: "成績已鎖定送交".into(),
    }))
}

#[derive(Serialize)]
pub struct StudentGradeItem {
    pub course_code: String,
    pub course_name: String,
    pub credits: i32,
    pub midterm_score: Option<f64>,
    pub final_score: Option<f64>,
    pub total_score: Option<f64>,
    pub is_submitted: bool,
}

pub async fn get_student_grades(
    State(state): State<AppState>,
    auth: AuthUser,
) -> Result<Json<Vec<StudentGradeItem>>, AppError> {
    if !auth.is_student() {
        return Err(AppError::forbidden("只有學生可以查看成績"));
    }

    let enrollments = enrollments::Entity::find()
        .filter(enrollments::Column::StudentId.eq(auth.user_id))
        .all(&state.db)
        .await?;

    let mut items = Vec::new();

    for e in &enrollments {
        let course = crate::entities::courses::Entity::find_by_id(e.course_id)
            .one(&state.db)
            .await?;

        let grade = grades::Entity::find()
            .filter(grades::Column::EnrollmentId.eq(e.enrollment_id))
            .one(&state.db)
            .await?;

        if let Some(c) = course {
            items.push(StudentGradeItem {
                course_code: c.course_code,
                course_name: c.course_name,
                credits: c.credits,
                midterm_score: grade.as_ref().and_then(|g| g.midterm_score),
                final_score: grade.as_ref().and_then(|g| g.final_score),
                total_score: grade.as_ref().and_then(|g| g.total_score),
                is_submitted: grade.as_ref().map(|g| g.is_submitted).unwrap_or(false),
            });
        }
    }

    Ok(Json(items))
}

#[derive(Serialize)]
pub struct RosterItem {
    pub enrollment_id: i32,
    pub student_id: i32,
    pub student_number: String,
    pub full_name: String,
    pub midterm_score: Option<f64>,
    pub final_score: Option<f64>,
    pub total_score: Option<f64>,
    pub is_submitted: bool,
}

pub async fn get_course_roster(
    State(state): State<AppState>,
    auth: AuthUser,
    Path(course_id): Path<i32>,
) -> Result<Json<Vec<RosterItem>>, AppError> {
    if !auth.is_teacher() {
        return Err(AppError::forbidden("只有教師可以查看學生名冊"));
    }

    let course = courses::Entity::find_by_id(course_id)
        .one(&state.db)
        .await?
        .ok_or_else(|| AppError::not_found("課程不存在"))?;

    if course.teacher_id != auth.user_id {
        return Err(AppError::forbidden("非您授課的課程"));
    }

    let enrollments = enrollments::Entity::find()
        .filter(enrollments::Column::CourseId.eq(course_id))
        .filter(enrollments::Column::Status.eq("ENROLLED"))
        .all(&state.db)
        .await?;

    let mut items = Vec::new();

    for e in &enrollments {
        let student = users::Entity::find_by_id(e.student_id)
            .one(&state.db)
            .await?;
        let grade = grades::Entity::find()
            .filter(grades::Column::EnrollmentId.eq(e.enrollment_id))
            .one(&state.db)
            .await?;

        items.push(RosterItem {
            enrollment_id: e.enrollment_id,
            student_id: e.student_id,
            student_number: student
                .as_ref()
                .map(|s| s.username.clone())
                .unwrap_or_default(),
            full_name: student.map(|s| s.full_name).unwrap_or_default(),
            midterm_score: grade.as_ref().and_then(|g| g.midterm_score),
            final_score: grade.as_ref().and_then(|g| g.final_score),
            total_score: grade.as_ref().and_then(|g| g.total_score),
            is_submitted: grade.as_ref().map(|g| g.is_submitted).unwrap_or(false),
        });
    }

    Ok(Json(items))
}
