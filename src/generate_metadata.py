import pandas as pd
import json
import numpy as np
from datetime import datetime
from pathlib import Path

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (datetime, pd.Timestamp)):
            return obj.isoformat()
        return super(NpEncoder, self).default(obj)

def generate_metadata(df: pd.DataFrame, csv_path: str, description: str = "") -> str:
    output_path = Path(csv_path).with_name(f"{Path(csv_path).stem}_metadata.json")
    
    metadata = {
        "file_name": Path(csv_path).name,
        "generated_at": datetime.now().isoformat(),
        "shape": {"rows": df.shape[0], "columns": df.shape[1]},
        "description": description,
        "columns": {}
    }

    for col in df.columns:
        metadata["columns"][col] = {
            "dtype": str(df[col].dtype),
            "missing_values": int(df[col].isna().sum()), # Useful quality metric
            "sample_values": df[col].dropna().unique()[:5].tolist()
        }

    with open(output_path, "w") as f:
        json.dump(metadata, f, indent=4, cls=NpEncoder)

    print(f"Metadata saved: {output_path}")
    return str(output_path)