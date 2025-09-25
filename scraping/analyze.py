# analyze.py
from pathlib import Path
import pandas as pd

csv_path = Path("data/signature-india.csv")

if not csv_path.exists():
    raise FileNotFoundError(f"Could not find CSV at {csv_path.resolve()}")

df = pd.read_csv(csv_path)

drop_cols = ["web-scraper-order", "web-scraper-start-url"]
df = df.drop(columns=[c for c in drop_cols if c in df.columns])

print("✅ Loaded CSV (cleaned)")
print(f"Rows: {len(df):,} | Columns: {list(df.columns)}\n")


pd.set_option("display.max_colwidth", 80)  
pd.set_option("display.width", 120)        

print("First 5 reviews:\n")
print(df.head(5))
