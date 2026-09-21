use sea_orm::entity::prelude::*;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Eq, DeriveEntityModel, Serialize, Deserialize)]
#[sea_orm(table_name = "class_schedules")]
pub struct Model {
    #[sea_orm(primary_key, auto_increment = true)]
    pub schedule_id: i32,
    pub course_id: i32,
    pub day_of_week: i32,
    pub start_period: i32,
    pub end_period: i32,
    #[sea_orm(length = 50)]
    pub location: String,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {
    #[sea_orm(
        belongs_to = "super::courses::Entity",
        from = "Column::CourseId",
        to = "super::courses::Column::CourseId"
    )]
    Course,
}

impl Related<super::courses::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Course.def()
    }
}

impl ActiveModelBehavior for ActiveModel {}
