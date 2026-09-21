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
                    .table(Enrollments::Table)
                    .if_not_exists()
                    .col(pk_auto(Enrollments::EnrollmentId))
                    .col(ColumnDef::new(Enrollments::StudentId).integer().not_null())
                    .col(ColumnDef::new(Enrollments::CourseId).integer().not_null())
                    .col(ColumnDef::new(Enrollments::Status).string().not_null().default("ENROLLED"))
                    .col(ColumnDef::new(Enrollments::CreatedAt).timestamp().default(Expr::current_timestamp()))
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk_enrollments_student")
                            .from(Enrollments::Table, Enrollments::StudentId)
                            .to(Users::Table, Users::UserId),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk_enrollments_course")
                            .from(Enrollments::Table, Enrollments::CourseId)
                            .to(Courses::Table, Courses::CourseId),
                    )
                    .to_owned(),
            )
            .await?;

        manager
            .create_index(
                Index::create()
                    .name("uniq_student_course")
                    .table(Enrollments::Table)
                    .col(Enrollments::StudentId)
                    .col(Enrollments::CourseId)
                    .unique()
                    .to_owned(),
            )
            .await?;

        manager
            .create_index(
                Index::create()
                    .name("idx_enrollments_student")
                    .table(Enrollments::Table)
                    .col(Enrollments::StudentId)
                    .col(Enrollments::Status)
                    .to_owned(),
            )
            .await
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .drop_index(Index::drop().name("uniq_student_course").to_owned())
            .await?;
        manager
            .drop_index(Index::drop().name("idx_enrollments_student").to_owned())
            .await?;
        manager
            .drop_table(Table::drop().table(Enrollments::Table).to_owned())
            .await
    }
}

#[derive(DeriveIden)]
enum Enrollments {
    Table,
    EnrollmentId,
    StudentId,
    CourseId,
    Status,
    CreatedAt,
}

#[derive(DeriveIden)]
enum Users {
    Table,
    UserId,
}

#[derive(DeriveIden)]
enum Courses {
    Table,
    CourseId,
}
