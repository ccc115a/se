use sea_orm_migration::prelude::*;
use sea_orm_migration::schema::pk_auto;

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .create_table(
                Table::create()
                    .table(Grades::Table)
                    .if_not_exists()
                    .col(pk_auto(Grades::GradeId))
                    .col(ColumnDef::new(Grades::EnrollmentId).integer().not_null().unique_key())
                    .col(ColumnDef::new(Grades::MidtermScore).float())
                    .col(ColumnDef::new(Grades::FinalScore).float())
                    .col(ColumnDef::new(Grades::TotalScore).float())
                    .col(ColumnDef::new(Grades::IsSubmitted).boolean().default(false))
                    .col(ColumnDef::new(Grades::UpdatedAt).timestamp().default(Expr::current_timestamp()))
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk_grades_enrollment")
                            .from(Grades::Table, Grades::EnrollmentId)
                            .to(Enrollments::Table, Enrollments::EnrollmentId)
                            .on_delete(ForeignKeyAction::Cascade),
                    )
                    .to_owned(),
            )
            .await
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .drop_table(Table::drop().table(Grades::Table).to_owned())
            .await
    }
}

#[derive(DeriveIden)]
enum Grades {
    Table,
    GradeId,
    EnrollmentId,
    MidtermScore,
    FinalScore,
    TotalScore,
    IsSubmitted,
    UpdatedAt,
}

#[derive(DeriveIden)]
enum Enrollments {
    Table,
    EnrollmentId,
}
