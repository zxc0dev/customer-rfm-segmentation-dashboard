import re
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.engine import Engine


# --- Helper to get SQL file path relative to this script ---
def get_sql_path(filename: str) -> Path:
    """
    Returns the path to a SQL file located in the 'sql' folder next to 'src/'.
    Structure expected:
        project/
        ├── sql/
        │   └── *.sql
        └── src/
            └── db_setup.py  ← this file
    """
    base_path = Path(__file__).parent.parent  # go up from src/ to project root
    file_path = base_path / "sql" / filename
    if not file_path.exists():
        raise FileNotFoundError(f"SQL file not found: {file_path}")
    return file_path


def _read_sql_statements(path: Path) -> list[str]:
    """
    Reads a SQL file and splits it into individual statements,
    stripping comments and empty entries.
    Handles both single-statement and multi-statement files.
    """
    raw = path.read_text(encoding="utf-8")

    # Remove single-line comments (-- ...)
    raw = re.sub(r"--[^\n]*", "", raw)
    # Remove block comments (/* ... */)
    raw = re.sub(r"/\*.*?\*/", "", raw, flags=re.DOTALL)

    statements = [s.strip() for s in raw.split(";") if s.strip()]
    return statements


# --- Database creation (runs with AUTOCOMMIT — required for CREATE/DROP DATABASE) ---
def create_database(engine: Engine) -> None:
    files = [
        "01_terminate_backend_sessions.sql",
        "02_drop_database.sql",
        "03_create_database.sql",
    ]

    for filename in files:
        path = get_sql_path(filename)
        statements = _read_sql_statements(path)

        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            for stmt in statements:
                conn.execute(text(stmt))

        print(f"  ✓ Executed: {filename}")

    print("Database 'retail' created successfully.")


# --- Table creation ---
def create_table(engine: Engine) -> None:
    path = get_sql_path("04_create_table.sql")
    statements = _read_sql_statements(path)

    with engine.connect() as conn:
        for stmt in statements:
            conn.execute(text(stmt))
        conn.commit()

    print("Table 'base_retail' created in schema 'public'.")


# --- Data loading via COPY (psycopg2 only) ---
def load_data(data_path: str, engine: Engine) -> None:
    copy_sql_path = get_sql_path("05_load_data.sql")
    # COPY expects a single statement — read as-is
    copy_sql = copy_sql_path.read_text(encoding="utf-8").strip()

    raw_conn = engine.raw_connection()
    try:
        with raw_conn.cursor() as cursor:
            with open(data_path, "r", encoding="utf-8") as f:
                cursor.copy_expert(copy_sql, f)
        raw_conn.commit()
        print("Data loaded into 'base_retail'.")
    except Exception as e:
        raw_conn.rollback()
        raise RuntimeError(f"Data load failed: {e}") from e
    finally:
        raw_conn.close()


# --- Feature engineering ---
def feature_engineering_sql(engine: Engine) -> None:
    path = get_sql_path("06_feature_engineering.sql")
    statements = _read_sql_statements(path)
 
    with engine.connect() as conn:
        for stmt in statements:
            conn.execute(text(stmt))
        conn.commit()
 
    print("Featured table 'public.featured_retail' created successfully.")

# --- Run everything in order ---
def run_all(engine: Engine, data_path: str) -> None:
    print("=== Step 1: Creating database ===")
    create_database(engine)
 
    print("\n=== Step 2: Creating table ===")
    create_table(engine)
 
    print("\n=== Step 3: Loading data ===")
    load_data(data_path, engine)
 
    print("\n=== Step 4: Feature engineering ===")
    feature_engineering_sql(engine)
 
    print("\n✅ Setup complete.")