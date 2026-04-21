from sqlalchemy import text
from src.utils.logger import get_logger
import re

logger = get_logger(__name__)

def _strip_comments(sql: str) -> str:
    sql = re.sub(r'--[^\n]*', '', sql)
    sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
    return sql

def execute_sql_file(conn, path, params=None):
    with open(path, "r", encoding="utf-8") as f:
        sql = f.read()

    sql = _strip_comments(sql)

    if "$$" in sql:
        conn.execute(text(sql), params or {})
    else:
        statements = [s.strip() for s in sql.split(";") if s.strip()]
        for statement in statements:
            conn.execute(text(statement), params or {})

    logger.info(f"Executed: {path}")

def execute_sql(conn, sql: str, params=None):
    conn.execute(text(sql), params or {})