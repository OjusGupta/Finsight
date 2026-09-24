import pandas as pd
import glob
import os
from pathlib import Path

root = Path(__file__).resolve().parent / "data" / "FinSight_synthetic_ERP_dataset_v1" / "raw"

files = glob.glob(str(root / "**" / "*.csv"), recursive=True)

for file in files:
    print("=" * 80)

    relative_path = os.path.relpath(file, root)
    print("FILE:", relative_path)

    df = pd.read_csv(file)

    print("ROWS:", len(df))
    print("COLUMNS:", df.columns.tolist())

print("=" * 80)
print("Dataset inspection complete.")