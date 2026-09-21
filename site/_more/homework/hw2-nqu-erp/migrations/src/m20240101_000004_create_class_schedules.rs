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
                    .table(ClassSchedules::Table)
                    .if_not_exists()
                    .col(pk_auto(ClassSchedules::ScheduleId))
                    .col(ColumnDef::new(ClassSchedules::CourseId).integer().not_null())
                    .col(ColumnDef::new(ClassSchedules::DayOfWeek).integer().not_null())
                    .col(ColumnDef::new(ClassSchedules::StartPeriod).integer().not_null())
                    .col(ColumnDef::new(ClassSchedules::EndPeriod).integer().not_null())
                    .col(ColumnDef::new(ClassSchedules::Location).string().not_null())
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk_schedules_course")
                            .from(ClassSchedules::Table, ClassSchedules::CourseId)
                            .to(Courses::Table, Courses::CourseId)
                            .on_delete(ForeignKeyAction::Cascade),
                    )
                    .to_owned(),
            )
            .await?;

        manager
            .create_index(
                Index::create()
                    .name("idx_schedules_course")
                    .table(ClassSchedules::Table)
                    .col(ClassSchedules::CourseId)
                    .to_owned(),
            )
            .await
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .drop_index(Index::drop().name("idx_schedules_course").to_owned())
            .await?;
        manager
            .drop_table(Table::drop().table(ClassSchedules::Table).to_owned())
            .await
    }
}

#[derive(DeriveIden)]
enum ClassSchedules {
    Table,
    ScheduleId,
    CourseId,
    DayOfWeek,
    StartPeriod,
    EndPeriod,
    Location,
}

#[derive(DeriveIden)]
enum Courses {
    Table,
    CourseId,
}
