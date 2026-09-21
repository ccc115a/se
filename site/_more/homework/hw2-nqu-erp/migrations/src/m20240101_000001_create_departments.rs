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
                    .table(Departments::Table)
                    .if_not_exists()
                    .col(pk_auto(Departments::DeptId))
                    .col(ColumnDef::new(Departments::DeptCode).string().not_null().unique_key())
                    .col(ColumnDef::new(Departments::DeptName).string().not_null())
                    .to_owned(),
            )
            .await
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .drop_table(Table::drop().table(Departments::Table).to_owned())
            .await
    }
}

#[derive(DeriveIden)]
enum Departments {
    Table,
    DeptId,
    DeptCode,
    DeptName,
}
