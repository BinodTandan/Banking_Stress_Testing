import os
import pandas as pd
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

RAW = "data_raw/accepted_2007_to_2018Q4.csv.gz"
OUT = "data_work/loans_slim.parquet"
os.makedirs("data_work", exist_ok=True)

USECOLS = [
    "id","issue_d","loan_amnt","term","int_rate","installment",
    "grade","sub_grade","emp_length","home_ownership","annual_inc",
    "purpose","dti","fico_range_low","loan_status"
]

def parse_emp_length(x):
    if pd.isna(x):
        return np.nan
    s = str(x).strip().lower()
    if s.startswith("10"):    # "10+ years"
        return 10.0
    if s.startswith("<"):     # "< 1 year"
        return 0.5
    if "year" in s:           # "7 years" / "1 year"
        try:
            return float(s.split()[0])
        except Exception:
            return np.nan
    return np.nan

writer = None
rows = 0

for chunk in pd.read_csv(RAW, usecols=USECOLS, chunksize=500_000, low_memory=False):
    # --- parse & clean ---
    # dates
    chunk["issue_d"] = pd.to_datetime(chunk["issue_d"], format="%b-%Y", errors="coerce")

    # interest rate: "13.56%" -> 0.1356
    chunk["int_rate"] = (
        chunk["int_rate"]
        .astype(str)
        .str.replace("%", "", regex=False)
        .astype(float) / 100.0
    )

    # emp_length -> float years
    chunk["emp_length"] = chunk["emp_length"].apply(parse_emp_length).astype("float32")

    # term -> months (36/60)
    chunk["term_m"] = np.where(chunk["term"].astype(str).str.contains("60"), 60, 36).astype("int16")

    # target: default/charged off = 1 else 0
    chunk["target"] = chunk["loan_status"].astype(str).str.contains(
        "Charged Off|Default", case=False, na=False
    ).astype("int8")

    # dtypes / categories to reduce size
    chunk["loan_amnt"]   = pd.to_numeric(chunk["loan_amnt"], errors="coerce").astype("Int32")
    chunk["installment"] = pd.to_numeric(chunk["installment"], errors="coerce").astype("float32")
    chunk["annual_inc"]  = pd.to_numeric(chunk["annual_inc"], errors="coerce").astype("float32")
    chunk["dti"]         = pd.to_numeric(chunk["dti"], errors="coerce").astype("float32")
    chunk["fico_range_low"] = pd.to_numeric(chunk["fico_range_low"], errors="coerce").astype("Int16")

    # categoricals
    for c in ["purpose","home_ownership","grade","sub_grade","term"]:
        if c in chunk.columns:
            chunk[c] = chunk[c].astype("category")

    # select & order final columns
    final_cols = [
        "id","issue_d","loan_amnt","term_m","int_rate","installment",
        "grade","sub_grade","emp_length","home_ownership","annual_inc",
        "purpose","dti","fico_range_low","target"
    ]
    chunk = chunk[final_cols]

    # --- write parquet (snappy) ---
    table = pa.Table.from_pandas(chunk, preserve_index=False)
    if writer is None:
        writer = pq.ParquetWriter(OUT, table.schema, compression="snappy")
    writer.write_table(table)

    rows += len(chunk)

if writer:
    writer.close()

print(f"Wrote {OUT} with ~{rows:,} rows")
