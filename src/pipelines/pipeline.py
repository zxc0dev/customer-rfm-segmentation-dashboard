from prefect import flow, task
from prefect.logging import get_run_logger

from src.db_init.db_setup import drop_database, create_database, create_tables
from src.tasks.load import load_base
from src.pipelines.dbt_run import dbt_run, dbt_test


@task(name="db-drop", retries=0)
def task_drop_database() -> None:
    log = get_run_logger()
    log.info("Dropping database if it exists...")
    drop_database()


@task(name="db-create", retries=0)
def task_create_database() -> None:
    log = get_run_logger()
    log.info("Creating database...")
    create_database()


@task(name="db-create-tables", retries=0)
def task_create_tables() -> None:
    log = get_run_logger()
    log.info("Creating schemas and tables...")
    create_tables()


@task(name="load-base-data", retries=1, retry_delay_seconds=5)
def task_load_base() -> None:
    log = get_run_logger()
    log.info("Loading base CSV into dim.dim_base_retail...")
    load_base()


@task(name="dbt-run", retries=0)
def task_dbt_run() -> None:
    log = get_run_logger()
    log.info("Running dbt models (stg -> int -> dim + mart)...")
    dbt_run()
    log.info("dbt run finished.")


@task(name="dbt-test", retries=0)
def task_dbt_test() -> None:
    log = get_run_logger()
    log.info("Running dbt tests...")
    dbt_test()
    log.info("dbt test finished.")


@flow(name="feature-engineering-pipeline", log_prints=True)
def feature_engineering_pipeline(run_tests: bool = True) -> None:
    task_drop_database()
    task_create_database()
    task_create_tables()
    task_load_base()
    task_dbt_run()
    if run_tests:
        task_dbt_test()


if __name__ == "__main__":
    feature_engineering_pipeline()
