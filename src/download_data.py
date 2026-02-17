import shutil
import zipfile
import kagglehub

from pathlib import Path

def download_data():
    cache_path = Path(
        kagglehub.dataset_download(
            "mashlyn/online-retail-ii-uci",
            force_download=True
        )
    )

    project_dir = Path("../data/01_raw")
    project_dir.mkdir(parents=True, exist_ok=True)

    if cache_path.suffix == ".zip":
        with zipfile.ZipFile(cache_path, "r") as z:
            z.extractall(project_dir)
        print("Extracted to:", project_dir)

    elif cache_path.is_dir():
        for file in cache_path.iterdir():
            if file.is_file():
                shutil.copy(file, project_dir)
        print("Copied to:", project_dir)

    else:
        raise ValueError(f"Unexpected cache_path: {cache_path}")
