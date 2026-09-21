use axum::{extract::State, Json};
use sea_orm::{ColumnTrait, EntityTrait, QueryFilter};
use serde::Serialize;

use crate::entities::{class_schedules, courses, users};
use crate::errors::AppError;
use crate::middleware::AuthUser;
use crate::AppState;

#[derive(Serialize)]
pub struct CourseItem {
    pub course_id: i32,
    pub course_code: String,
    pub course_name: String,
    pub teacher_id: i32,
    pub teacher_name: String,
    pub credits: i32,
    pub capacity: i32,
    pub enrolled_count: i32,
    pub dept_id: i32,
    pub dept_name: String,
    pub schedules: Vec<ScheduleInfo>,
}

#[derive(Serialize)]
pub struct ScheduleInfo {
    pub day_of_week: i32,
    pub start_period: i32,
    pub end_period: i32,
    pub location: String,
}

pub async fn list_courses(
    State(state): State<AppState>,
    _auth: AuthUser,
    axum::extract::Query(params): axum::extract::Query<std::collections::HashMap<String, String>>,
) -> Result<Json<Vec<CourseItem>>, AppError> {
    let year: i32 = params
        .get("year")
        .and_then(|v| v.parse().ok())
        .unwrap_or(113);
    let semester: i32 = params
        .get("semester")
        .and_then(|v| v.parse().ok())
        .unwrap_or(1);

    let courses = courses::Entity::find()
        .filter(courses::Column::AcademicYear.eq(year))
        .filter(courses::Column::Semester.eq(semester))
        .all(&state.db)
        .await?;

    let mut items = Vec::new();

    for c in &courses {
        let teacher = users::Entity::find_by_id(c.teacher_id)
            .one(&state.db)
            .await?;

        let dept = crate::entities::departments::Entity::find_by_id(c.dept_id)
            .one(&state.db)
            .await?;

        let schedules = class_schedules::Entity::find()
            .filter(class_schedules::Column::CourseId.eq(c.course_id))
            .all(&state.db)
            .await?;

        items.push(CourseItem {
            course_id: c.course_id,
            course_code: c.course_code.clone(),
            course_name: c.course_name.clone(),
            teacher_id: c.teacher_id,
            teacher_name: teacher.map(|t| t.full_name).unwrap_or_default(),
            credits: c.credits,
            capacity: c.capacity,
            enrolled_count: c.enrolled_count,
            dept_id: c.dept_id,
            dept_name: dept.map(|d| d.dept_name).unwrap_or_default(),
            schedules: schedules
                .into_iter()
                .map(|s| ScheduleInfo {
                    day_of_week: s.day_of_week,
                    start_period: s.start_period,
                    end_period: s.end_period,
                    location: s.location,
                })
                .collect(),
        });
    }

    Ok(Json(items))
}

pub async fn get_teacher_courses(
    State(state): State<AppState>,
    auth: AuthUser,
) -> Result<Json<Vec<CourseItem>>, AppError> {
    if !auth.is_teacher() {
        return Err(AppError::forbidden("只有教師可以查看授課清單"));
    }

    let courses = courses::Entity::find()
        .filter(courses::Column::TeacherId.eq(auth.user_id))
        .all(&state.db)
        .await?;

    let mut items = Vec::new();

    for c in &courses {
        let schedules = class_schedules::Entity::find()
            .filter(class_schedules::Column::CourseId.eq(c.course_id))
            .all(&state.db)
            .await?;

        items.push(CourseItem {
            course_id: c.course_id,
            course_code: c.course_code.clone(),
            course_name: c.course_name.clone(),
            teacher_id: c.teacher_id,
            teacher_name: auth.username.clone(),
            credits: c.credits,
            capacity: c.capacity,
            enrolled_count: c.enrolled_count,
            dept_id: c.dept_id,
            dept_name: String::new(),
            schedules: schedules
                .into_iter()
                .map(|s| ScheduleInfo {
                    day_of_week: s.day_of_week,
                    start_period: s.start_period,
                    end_period: s.end_period,
                    location: s.location,
                })
                .collect(),
        });
    }

    Ok(Json(items))
}
