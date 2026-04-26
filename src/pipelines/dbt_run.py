import subprocess
from pathlib import Path

from src.config.paths import ROOT_DIR
from src.utils.logger import get_logger

logger = get_logger(__name__)

DBT_PROJECT_DIR = ROOT_DIR / "dbt"


def dbt_run(select: str | None = None, target: str = "dev") -> None:
    cmd = [
        "dbt", "run",
        "--project-dir", str(DBT_PROJECT_DIR),
        "--profiles-dir", str(DBT_PROJECT_DIR),
        "--target", target,
    ]
    if select:
        cmd += ["--select", select]

    logger.info(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT_DIR))

    if result.stdout:
        logger.info(result.stdout)
    if result.returncode != 0:
        logger.error(result.stderr)
        raise RuntimeError(f"dbt run failed:\n{result.stderr}")

    logger.info("dbt run completed successfully.")


def dbt_test(select: str | None = None, target: str = "dev") -> None:
    cmd = [
        "dbt", "test",
        "--project-dir", str(DBT_PROJECT_DIR),
        "--profiles-dir", str(DBT_PROJECT_DIR),
        "--target", target,
    ]
    if select:
        cmd += ["--select", select]

    logger.info(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT_DIR))

    if result.stdout:
        logger.info(result.stdout)
    if result.returncode != 0:
        logger.error(result.stderr)
        raise RuntimeError(f"dbt test failed:\n{result.stderr}")

    logger.info("dbt test completed successfully.")
