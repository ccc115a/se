use sea_orm::entity::prelude::*;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, DeriveEntityModel, Serialize, Deserialize)]
#[sea_orm(table_name = "grades")]
pub struct Model {
    #[sea_orm(primary_key, auto_increment = true)]
    pub grade_id: i32,
    #[sea_orm(unique)]
    pub enrollment_id: i32,
    pub midterm_score: Option<f64>,
    pub final_score: Option<f64>,
    pub total_score: Option<f64>,
    pub is_submitted: bool,
    pub updated_at: DateTimeUtc,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {
    #[sea_orm(
        belongs_to = "super::enrollments::Entity",
        from = "Column::EnrollmentId",
        to = "super::enrollments::Column::EnrollmentId"
    )]
    Enrollment,
}

impl Related<super::enrollments::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Enrollment.def()
    }
}

impl ActiveModelBehavior for ActiveModel {}
