from src.utils.logger import get_logger
from sqlalchemy import create_engine
from src.config.paths import PROCESSED_DIR
from src.config.config import DB_CREATED

logger = get_logger(__name__)

def _copy_csv(raw_conn, table: str, csv_path):
    cursor = raw_conn.cursor()
    with open(csv_path, "r", encoding="utf-8") as f:
        cursor.execute(f"TRUNCATE TABLE {table}")
        cursor.copy_expert(
            f"COPY {table} FROM STDIN WITH CSV HEADER DELIMITER ','",
            f
        )
    logger.info(f"Loaded {table} from {csv_path.name}")

def load_base():
    engine = create_engine(DB_CREATED)
    logger.info("=== LOAD STARTED ===")
    logger.info("Loading CSVs into dim...")
    raw_conn = engine.raw_connection()
    try:
        _copy_csv(raw_conn, "dim.dim_base_retail", PROCESSED_DIR / "base_retail.csv")
        raw_conn.commit()
        logger.info("Base loaded.")
        logger.info("=== LOAD COMPLETED SUCCESSFULLY ===")
    except Exception as e:
        raw_conn.rollback()
        logger.exception(f"Base load failed: {e}")
        raise
    finally:
        raw_conn.close()