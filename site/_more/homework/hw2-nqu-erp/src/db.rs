use sea_orm::{Database, DatabaseConnection};
use sea_orm_migration::prelude::*;

use crate::config::Config;

pub async fn establish_connection(config: &Config) -> Result<DatabaseConnection, sea_orm::DbErr> {
    let db = Database::connect(&config.database_url).await?;
    Ok(db)
}

pub async fn run_migrations(db: &DatabaseConnection) -> Result<(), sea_orm::DbErr> {
    use migrations::Migrator;
    Migrator::up(db, None).await?;
    Ok(())
}
