import os
import pandas as pd
import duckdb
from pandas_datareader import data as web

os.makedirs("data_work", exist_ok=True)

# ---- 1) Fetch macro from FRED and build a quarterly table ----
fred = web.DataReader(
    ['GDPC1', 'UNRATE', 'CPIAUCSL', 'FEDFUNDS'],
    'fred', start='2007-01-01', end='2018-12-31'
)

# Quarterly average using the non-deprecated alias 'QE-DEC'
macro_q = fred.resample('QE-DEC').mean().reset_index(names='date')

# Create quarter Period and explicit quarter-start timestamp for clean joins
macro_q['quarter'] = macro_q['date'].dt.to_period('Q-DEC')
macro_q['quarter_start'] = macro_q['quarter'].dt.to_timestamp(how='start')  # start of quarter (Timestamp)

macro_q = macro_q[['quarter', 'quarter_start', 'GDPC1', 'UNRATE', 'CPIAUCSL', 'FEDFUNDS']]
macro_q.to_parquet('data_work/macro_q.parquet', index=False)
print(f"Macro rows: {len(macro_q)}  (quarters 2007–2018)")

# ---- 2) Merge loans with macro by quarter start date ----
con = duckdb.connect()
con.execute("CREATE TABLE loans AS SELECT * FROM 'data_work/loans_slim.parquet';")
con.execute("CREATE TABLE macro AS SELECT * FROM 'data_work/macro_q.parquet';")

merged = con.execute("""
WITH L AS (
  SELECT
    id,
    issue_d,
    DATE_TRUNC('quarter', issue_d) AS issue_q_start,    -- quarter start (Timestamp)
    CAST(loan_amnt AS INTEGER)      AS loan_amnt,
    CAST(term_m    AS SMALLINT)     AS term_m,
    CAST(int_rate  AS DOUBLE)       AS int_rate,
    CAST(installment AS DOUBLE)     AS installment,
    grade, sub_grade, emp_length, home_ownership,
    CAST(annual_inc AS DOUBLE)      AS annual_inc,
    purpose,
    CAST(dti AS DOUBLE)             AS dti,
    CAST(fico_range_low AS INTEGER) AS fico,
    CAST(target AS INTEGER)         AS target
  FROM loans
  WHERE issue_d BETWEEN '2007-01-01' AND '2018-12-31'
)
SELECT
  L.*,
  M.GDPC1, M.UNRATE, M.CPIAUCSL, M.FEDFUNDS
FROM L
LEFT JOIN macro M
  ON L.issue_q_start = M.quarter_start
""").df()

out_path = "data_work/loans_merged.parquet"
merged.to_parquet(out_path, index=False)
print(f"Merged rows: {len(merged):,} → {out_path}")
