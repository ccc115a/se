use sea_orm::entity::prelude::*;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Eq, DeriveEntityModel, Serialize, Deserialize)]
#[sea_orm(table_name = "enrollments")]
pub struct Model {
    #[sea_orm(primary_key, auto_increment = true)]
    pub enrollment_id: i32,
    pub student_id: i32,
    pub course_id: i32,
    #[sea_orm(length = 15)]
    pub status: String,
    pub created_at: DateTimeUtc,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {
    #[sea_orm(
        belongs_to = "super::users::Entity",
        from = "Column::StudentId",
        to = "super::users::Column::UserId"
    )]
    Student,
    #[sea_orm(
        belongs_to = "super::courses::Entity",
        from = "Column::CourseId",
        to = "super::courses::Column::CourseId"
    )]
    Course,
    #[sea_orm(has_one = "super::grades::Entity")]
    Grade,
}

impl Related<super::users::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Student.def()
    }
}

impl Related<super::courses::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Course.def()
    }
}

impl Related<super::grades::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Grade.def()
    }
}

impl ActiveModelBehavior for ActiveModel {}
