use sea_orm_migration::prelude::*;

mod m20240101_000001_create_departments;
mod m20240101_000002_create_users;
mod m20240101_000003_create_courses;
mod m20240101_000004_create_class_schedules;
mod m20240101_000005_create_enrollments;
mod m20240101_000006_create_grades;

pub struct Migrator;

#[async_trait::async_trait]
impl MigratorTrait for Migrator {
    fn migrations() -> Vec<Box<dyn MigrationTrait>> {
        vec![
            Box::new(m20240101_000001_create_departments::Migration),
            Box::new(m20240101_000002_create_users::Migration),
            Box::new(m20240101_000003_create_courses::Migration),
            Box::new(m20240101_000004_create_class_schedules::Migration),
            Box::new(m20240101_000005_create_enrollments::Migration),
            Box::new(m20240101_000006_create_grades::Migration),
        ]
    }
}
