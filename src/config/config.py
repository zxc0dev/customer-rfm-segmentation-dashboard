import os
from dotenv import load_dotenv
from sqlalchemy.engine import URL

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 5432),
    "main_dbname": os.getenv("MAIN_DB_NAME"),
    "created_dbname": os.getenv("CREATED_DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

def make_url(database):
    return URL.create(
        drivername="postgresql+psycopg2",
        username=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        database=database,
    )

DB_MAIN = make_url(DB_CONFIG["main_dbname"])
DB_CREATED = make_url(DB_CONFIG["created_dbname"])

