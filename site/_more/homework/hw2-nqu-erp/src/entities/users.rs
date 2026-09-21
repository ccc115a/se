use sea_orm::entity::prelude::*;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Eq, DeriveEntityModel, Serialize, Deserialize)]
#[sea_orm(table_name = "users")]
pub struct Model {
    #[sea_orm(primary_key, auto_increment = true)]
    pub user_id: i32,
    #[sea_orm(unique, length = 20)]
    pub username: String,
    #[sea_orm(length = 255)]
    pub password_hash: String,
    #[sea_orm(length = 50)]
    pub full_name: String,
    #[sea_orm(length = 10)]
    pub role: String,
    pub dept_id: i32,
    #[sea_orm(unique, length = 100)]
    pub email: String,
    pub created_at: DateTimeUtc,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {
    #[sea_orm(
        belongs_to = "super::departments::Entity",
        from = "Column::DeptId",
        to = "super::departments::Column::DeptId"
    )]
    Department,
    #[sea_orm(has_many = "super::courses::Entity")]
    CoursesAsTeacher,
    #[sea_orm(has_many = "super::enrollments::Entity")]
    Enrollments,
}

impl Related<super::departments::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Department.def()
    }
}

impl Related<super::courses::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::CoursesAsTeacher.def()
    }
}

impl Related<super::enrollments::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Enrollments.def()
    }
}

impl ActiveModelBehavior for ActiveModel {}
