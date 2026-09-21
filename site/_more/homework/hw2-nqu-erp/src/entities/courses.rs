use sea_orm::entity::prelude::*;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Eq, DeriveEntityModel, Serialize, Deserialize)]
#[sea_orm(table_name = "courses")]
pub struct Model {
    #[sea_orm(primary_key, auto_increment = true)]
    pub course_id: i32,
    #[sea_orm(length = 20)]
    pub course_code: String,
    pub academic_year: i32,
    pub semester: i32,
    #[sea_orm(length = 100)]
    pub course_name: String,
    pub teacher_id: i32,
    pub credits: i32,
    pub capacity: i32,
    pub enrolled_count: i32,
    pub dept_id: i32,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {
    #[sea_orm(
        belongs_to = "super::users::Entity",
        from = "Column::TeacherId",
        to = "super::users::Column::UserId"
    )]
    Teacher,
    #[sea_orm(
        belongs_to = "super::departments::Entity",
        from = "Column::DeptId",
        to = "super::departments::Column::DeptId"
    )]
    Department,
    #[sea_orm(has_many = "super::class_schedules::Entity")]
    Schedules,
    #[sea_orm(has_many = "super::enrollments::Entity")]
    Enrollments,
}

impl Related<super::users::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Teacher.def()
    }
}

impl Related<super::departments::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Department.def()
    }
}

impl Related<super::class_schedules::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Schedules.def()
    }
}

impl Related<super::enrollments::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Enrollments.def()
    }
}

impl ActiveModelBehavior for ActiveModel {}
