from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(os.getenv("APP_RUNTIME_DIR", Path(__file__).resolve().parents[2]))

RAW_DIR = ROOT_DIR / "data" / "01_raw"
PROCESSED_DIR = ROOT_DIR / "data" / "02_processed"
LOG_FILE = ROOT_DIR / "logs" / f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"