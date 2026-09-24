import os
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1] / "data" / "FinSight_synthetic_ERP_dataset_v1"
RAW_SALES = os.path.join(BASE_DIR, "raw", "sales")
PROCESSED_SALES = os.path.join(BASE_DIR, "processed", "sales")

os.makedirs(PROCESSED_SALES, exist_ok=True)

# -----------------------------
# 1. Clean sales.csv
# -----------------------------
sales_path = os.path.join(RAW_SALES, "sales.csv")
sales = pd.read_csv(sales_path)

# Keep the first occurrence of a duplicated invoice number.
sales_clean = sales.drop_duplicates(subset=["invoice_number"], keep="first").copy()

# Normalize status for PostgreSQL constraint.
sales_clean["status"] = sales_clean["status"].str.upper()

sales_clean.to_csv(
    os.path.join(PROCESSED_SALES, "sales.csv"),
    index=False
)

# -----------------------------
# 2. Clean sale_items.csv
# -----------------------------
items_path = os.path.join(RAW_SALES, "sale_items.csv")
items = pd.read_csv(items_path)

valid_sale_ids = set(sales_clean["sale_id"])
items_clean = items[items["sale_id"].isin(valid_sale_ids)].copy()

items_clean.to_csv(
    os.path.join(PROCESSED_SALES, "sale_items.csv"),
    index=False
)

print("Cleaning completed.")
print(f"Original sales rows : {len(sales)}")
print(f"Clean sales rows    : {len(sales_clean)}")
print(f"Removed sales       : {len(sales) - len(sales_clean)}")
print()
print(f"Original item rows  : {len(items)}")
print(f"Clean item rows     : {len(items_clean)}")
print(f"Removed item rows   : {len(items) - len(items_clean)}")
print()
print("Clean files created in:")
print(PROCESSED_SALES)
