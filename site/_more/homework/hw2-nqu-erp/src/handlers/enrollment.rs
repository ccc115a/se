use axum::{extract::State, Json};
use sea_orm::{
    ActiveModelTrait, ColumnTrait, EntityTrait, ModelTrait, QueryFilter, Set, TransactionTrait,
};
use serde::{Deserialize, Serialize};

use crate::entities::{class_schedules, courses, enrollments, grades};
use crate::errors::AppError;
use crate::middleware::AuthUser;
use crate::AppState;

#[derive(Deserialize)]
pub struct EnrollRequest {
    pub course_id: i32,
}

#[derive(Serialize)]
pub struct EnrollResponse {
    pub success: bool,
    pub message: String,
}

#[derive(Deserialize)]
pub struct DropRequest {
    pub course_id: i32,
}

pub async fn enroll_course(
    State(state): State<AppState>,
    auth: AuthUser,
    Json(payload): Json<EnrollRequest>,
) -> Result<Json<EnrollResponse>, AppError> {
    if !auth.is_student() {
        return Err(AppError::forbidden("只有學生可以選課"));
    }

    let tx = state.db.begin().await?;

    let already_enrolled = enrollments::Entity::find()
        .filter(enrollments::Column::StudentId.eq(auth.user_id))
        .filter(enrollments::Column::CourseId.eq(payload.course_id))
        .one(&tx)
        .await?;

    if let Some(e) = already_enrolled {
        if e.status == "ENROLLED" {
            return Ok(Json(EnrollResponse {
                success: false,
                message: "您已選修過此課程".into(),
            }));
        }
        if e.status == "DROPPED" {
            return Ok(Json(EnrollResponse {
                success: false,
                message: "已退選課程，請聯繫教務處重新選課".into(),
            }));
        }
    }

    let target_schedules = class_schedules::Entity::find()
        .filter(class_schedules::Column::CourseId.eq(payload.course_id))
        .all(&tx)
        .await?;

    let current_enrollments = enrollments::Entity::find()
        .filter(enrollments::Column::StudentId.eq(auth.user_id))
        .filter(enrollments::Column::Status.eq("ENROLLED"))
        .all(&tx)
        .await?;

    for current in &current_enrollments {
        let current_schedules = class_schedules::Entity::find()
            .filter(class_schedules::Column::CourseId.eq(current.course_id))
            .all(&tx)
            .await?;

        for cs in &current_schedules {
            for ts in &target_schedules {
                if cs.day_of_week == ts.day_of_week
                    && cs.start_period <= ts.end_period
                    && ts.start_period <= cs.end_period
                {
                    return Ok(Json(EnrollResponse {
                        success: false,
                        message: format!(
                            "課程時間衝突！與已選課程在星期 {} 第 {}~{} 節重疊",
                            cs.day_of_week, cs.start_period, cs.end_period
                        ),
                    }));
                }
            }
        }
    }

    let course = courses::Entity::find_by_id(payload.course_id)
        .one(&tx)
        .await?
        .ok_or_else(|| AppError::not_found("課程不存在"))?;

    if course.enrolled_count >= course.capacity {
        return Ok(Json(EnrollResponse {
            success: false,
            message: "選課失敗：課程名額已滿".into(),
        }));
    }

    courses::Entity::update(courses::ActiveModel {
        course_id: Set(course.course_id),
        enrolled_count: Set(course.enrolled_count + 1),
        ..Default::default()
    })
    .exec(&tx)
    .await?;

    let enrollment = enrollments::ActiveModel {
        student_id: Set(auth.user_id),
        course_id: Set(payload.course_id),
        status: Set("ENROLLED".into()),
        ..Default::default()
    }
    .insert(&tx)
    .await?;

    grades::ActiveModel {
        enrollment_id: Set(enrollment.enrollment_id),
        ..Default::default()
    }
    .insert(&tx)
    .await?;

    tx.commit().await?;

    Ok(Json(EnrollResponse {
        success: true,
        message: "加選成功！".into(),
    }))
}

pub async fn drop_course(
    State(state): State<AppState>,
    auth: AuthUser,
    Json(payload): Json<DropRequest>,
) -> Result<Json<EnrollResponse>, AppError> {
    if !auth.is_student() {
        return Err(AppError::forbidden("只有學生可以退選"));
    }

    let tx = state.db.begin().await?;

    let enrollment = enrollments::Entity::find()
        .filter(enrollments::Column::StudentId.eq(auth.user_id))
        .filter(enrollments::Column::CourseId.eq(payload.course_id))
        .filter(enrollments::Column::Status.eq("ENROLLED"))
        .one(&tx)
        .await?
        .ok_or_else(|| AppError::not_found("未找到選課紀錄"))?;

    enrollments::ActiveModel {
        enrollment_id: Set(enrollment.enrollment_id),
        status: Set("DROPPED".into()),
        ..Default::default()
    }
    .update(&tx)
    .await?;

    let course = courses::Entity::find_by_id(payload.course_id)
        .one(&tx)
        .await?
        .ok_or_else(|| AppError::not_found("課程不存在"))?;

    if course.enrolled_count > 0 {
        courses::Entity::update(courses::ActiveModel {
            course_id: Set(course.course_id),
            enrolled_count: Set(course.enrolled_count - 1),
            ..Default::default()
        })
        .exec(&tx)
        .await?;
    }

    if let Some(g) = grades::Entity::find()
        .filter(grades::Column::EnrollmentId.eq(enrollment.enrollment_id))
        .one(&tx)
        .await?
    {
        g.delete(&tx).await?;
    }

    tx.commit().await?;

    Ok(Json(EnrollResponse {
        success: true,
        message: "退選成功！".into(),
    }))
}

#[derive(Serialize)]
pub struct ScheduleItem {
    pub course_code: String,
    pub course_name: String,
    pub teacher_name: String,
    pub day_of_week: i32,
    pub start_period: i32,
    pub end_period: i32,
    pub location: String,
}

pub async fn get_student_schedule(
    State(state): State<AppState>,
    auth: AuthUser,
    axum::extract::Query(params): axum::extract::Query<std::collections::HashMap<String, String>>,
) -> Result<Json<Vec<ScheduleItem>>, AppError> {
    if !auth.is_student() {
        return Err(AppError::forbidden("只有學生可以查看課表"));
    }

    let year: i32 = params
        .get("year")
        .and_then(|v| v.parse().ok())
        .unwrap_or(113);
    let semester: i32 = params
        .get("semester")
        .and_then(|v| v.parse().ok())
        .unwrap_or(1);

    let enrollments = enrollments::Entity::find()
        .filter(enrollments::Column::StudentId.eq(auth.user_id))
        .filter(enrollments::Column::Status.eq("ENROLLED"))
        .all(&state.db)
        .await?;

    let mut items = Vec::new();

    for e in &enrollments {
        let course = courses::Entity::find_by_id(e.course_id)
            .one(&state.db)
            .await?;

        if let Some(c) = course {
            if c.academic_year != year || c.semester != semester {
                continue;
            }

            let teacher = crate::entities::users::Entity::find_by_id(c.teacher_id)
                .one(&state.db)
                .await?;

            let schedules = class_schedules::Entity::find()
                .filter(class_schedules::Column::CourseId.eq(c.course_id))
                .all(&state.db)
                .await?;

            for s in schedules {
                items.push(ScheduleItem {
                    course_code: c.course_code.clone(),
                    course_name: c.course_name.clone(),
                    teacher_name: teacher
                        .as_ref()
                        .map(|t| t.full_name.clone())
                        .unwrap_or_default(),
                    day_of_week: s.day_of_week,
                    start_period: s.start_period,
                    end_period: s.end_period,
                    location: s.location.clone(),
                });
            }
        }
    }

    items.sort_by(|a, b| {
        a.day_of_week
            .cmp(&b.day_of_week)
            .then(a.start_period.cmp(&b.start_period))
    });

    Ok(Json(items))
}
