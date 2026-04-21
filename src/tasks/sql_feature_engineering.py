
from src.config.sql import SQL_TASKS
from src.config.config import DB_CREATED

from sqlalchemy import text, create_engine
from src.utils.sql_execute import execute_sql_file
from src.utils.logger import get_logger

logger = get_logger(__name__)

def sql_feature_engineering():
    engine = create_engine(DB_CREATED)
    logger.info("=== SQL FEATURE ENGINEERING STARTED ===")
    with engine.connect() as conn:
        for script in ["feature_engineering.sql"]:
            logger.info(f"Running {script}...")
            execute_sql_file(conn, SQL_TASKS / script)

        conn.commit()
        logger.info("=== SQL FEATURE ENGINEERING COMPLETED SUCCESSFULLY ===")