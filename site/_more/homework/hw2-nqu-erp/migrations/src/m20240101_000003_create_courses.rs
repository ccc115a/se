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
                    .table(Courses::Table)
                    .if_not_exists()
                    .col(pk_auto(Courses::CourseId))
                    .col(ColumnDef::new(Courses::CourseCode).string().not_null())
                    .col(ColumnDef::new(Courses::AcademicYear).integer().not_null())
                    .col(ColumnDef::new(Courses::Semester).integer().not_null())
                    .col(ColumnDef::new(Courses::CourseName).string().not_null())
                    .col(ColumnDef::new(Courses::TeacherId).integer())
                    .col(ColumnDef::new(Courses::Credits).integer().not_null())
                    .col(ColumnDef::new(Courses::Capacity).integer().not_null())
                    .col(ColumnDef::new(Courses::EnrolledCount).integer().default(0))
                    .col(ColumnDef::new(Courses::DeptId).integer())
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk_courses_teacher")
                            .from(Courses::Table, Courses::TeacherId)
                            .to(Users::Table, Users::UserId),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk_courses_dept")
                            .from(Courses::Table, Courses::DeptId)
                            .to(Departments::Table, Departments::DeptId),
                    )
                    .to_owned(),
            )
            .await?;

        manager
            .create_index(
                Index::create()
                    .name("idx_courses_year_sem")
                    .table(Courses::Table)
                    .col(Courses::AcademicYear)
                    .col(Courses::Semester)
                    .to_owned(),
            )
            .await
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .drop_index(Index::drop().name("idx_courses_year_sem").to_owned())
            .await?;
        manager
            .drop_table(Table::drop().table(Courses::Table).to_owned())
            .await
    }
}

#[derive(DeriveIden)]
enum Courses {
    Table,
    CourseId,
    CourseCode,
    AcademicYear,
    Semester,
    CourseName,
    TeacherId,
    Credits,
    Capacity,
    EnrolledCount,
    DeptId,
}

#[derive(DeriveIden)]
enum Users {
    Table,
    UserId,
}

#[derive(DeriveIden)]
enum Departments {
    Table,
    DeptId,
}
