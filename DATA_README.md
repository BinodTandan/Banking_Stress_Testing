## 📘 Project  
**AI-Driven Stress Testing: Generative Models for Scenario Simulation in Banking**

This document describes all datasets used in the project, their sources, processing stages, and key variables.  
All raw and processed data are stored in the shared Google Drive folder:  
📁 **UNT_AI_Stress_Testing_Data/**  

---

## 🔁 Data Lifecycle Overview

| Stage | Description | File |
|:------|:-------------|:-----|
| 1️⃣ Raw Data | Original LendingClub and FRED macroeconomic data. | `accepted_2007_to_2018Q4.csv.gz`, `macro_fred_raw.csv` |
| 2️⃣ Slim Dataset | Selected LendingClub variables cleaned and standardized. | `data_work/loans_slim.parquet` |
| 3️⃣ Merged Dataset | Lending data merged with quarterly FRED macro variables. | `data_work/loans_merged.parquet` |
| 4️⃣ Cleaned Dataset | Missing values handled, outliers reviewed, columns validated. | `data_work/loans_cleaned.parquet` |
| 5️⃣ Feature-Engineered Dataset | Added derived variables (ratios, macro deltas, encodings). | `data_work/loans_fe.parquet` |
| 6️⃣ Modeling Inputs | Train/test splits and scaled features for model training. | `data_work/train.parquet`, `data_work/test.parquet` |
| 7️⃣ Stress Scenario Data | Regulator and Generative-AI macro scenarios for stress tests. | `data_work/stress_scenarios.parquet` |
| 8️⃣ Results Data | Model metrics, stress outcomes, and visual summaries. | `results/model_metrics.csv`, `results/stress_results.parquet` |

---

## 🗂️ Data Sources

| Source | Description | Access |
|:--------|:-------------|:--------|
| **Kaggle: LendingClub Loan Data** | Historical accepted/rejected loan applications (2007–2018). | [https://www.kaggle.com/datasets/wordsforthewise/lending-club](https://www.kaggle.com/datasets/wordsforthewise/lending-club) |
| **FRED (Federal Reserve Economic Data)** | U.S. macroeconomic indicators used for stress testing. | [https://fred.stlouisfed.org/](https://fred.stlouisfed.org/) |
| **Variables Used** | UNRATE (unemployment rate), GDPC1 (real GDP), CPIAUCSL (inflation), FEDFUNDS (interest rate). | Public API via `pandas_datareader` |

---

## 🧮 Dataset Summary

| Dataset | Rows | Columns | Time Range | Key Variables | Notes |
|:---------|------:|------:|:------------|:---------------|:-------|
| `loans_slim.parquet` | 2,260,701 | 15 | 2007–2018 | loan_amnt, int_rate, term | Cleaned raw data |
| `macro_q.parquet` | 48 | 5 | 2007–2018 | GDP, CPI, UNRATE, FEDFUNDS | Quarterly averages |
| `loans_merged.parquet` | 2,260,668 | 20 | 2007–2018 | Combined borrower + macro data | Merged via issue quarter |
| `loans_cleaned.parquet` | 2,258,953 | 20 | 2007–2018 | EDA-verified dataset | Load and cleaned merged dataset along with EDA and hypothesis testing |
| `loans_fe.parquet` | TBD | TBD | 2007–2018 | Derived features | Member B will update |

---

## 🗂️ Folder Structure
```bash
ai_stress_testing/
│
├── data_raw/ # raw input files (not versioned)
├── data_work/ # intermediate parquet outputs
├── results/ # model metrics & plots
├── notebooks/ # EDA, modeling, GenAI scenarios
└── src/ # processing & modeling scripts
```

All large `.parquet`, `.csv`, and `.zip` files are **excluded from Git** (see `.gitignore`) and shared securely via Google Drive.

---

## 📊 Data Dictionary

### 🔹 LendingClub (Borrower & Loan Variables)

| Variable | Description | Type | Example |
|:----------|:-------------|:------|:---------|
| `id` | Unique loan identifier | Integer | 12437890 |
| `issue_d` | Loan issue date | Date | 2016-03-01 |
| `loan_amnt` | Amount funded by investors | Numeric | 12000 |
| `term` | Repayment term in months | Categorical | 36 / 60 |
| `int_rate` | Annual interest rate (%) | Numeric | 13.49 |
| `installment` | Monthly repayment amount | Numeric | 409.75 |
| `grade` | Credit risk grade (A–G) | Categorical | B |
| `emp_length` | Employment duration (years) | Categorical | 10+ years |
| `home_ownership` | Borrower’s home ownership status | Categorical | RENT / OWN / MORTGAGE |
| `annual_inc` | Annual reported income | Numeric | 65 000 |
| `purpose` | Reason for the loan | Categorical | debt_consolidation |
| `dti` | Debt-to-income ratio | Numeric | 17.2 |
| `fico_range_low` | Lower bound of borrower FICO score | Numeric | 690 |
| `loan_status` | Loan repayment status (target variable) | Categorical | Fully Paid / Charged Off |

### 🔹 FRED (Macroeconomic Variables)

| Variable | Description | Source | Frequency |
|:----------|:-------------|:---------|:------------|
| `UNRATE` | U.S. Unemployment Rate (%) | FRED | Monthly → Quarterly avg |
| `GDPC1` | Real GDP (Billions, chained 2017 USD) | FRED | Quarterly |
| `CPIAUCSL` | Consumer Price Index (Inflation) | FRED | Monthly → Quarterly avg |
| `FEDFUNDS` | Federal Funds Interest Rate (%) | FRED | Monthly → Quarterly avg |
| `quarter` | Quarter start date | Derived | 2007Q1–2018Q4 |

---

## 👥 Data Ownership Summary

| Stage | Responsible Member |
|:--------|:------------------|
| Raw ingestion & macro merge | **Binod** |
| Data cleaning & EDA | **Karthikeya & Binod** |
| Feature engineering & model prep | **Member B** |
| Visualization & documentation | **Member C** |

---

## 📚 Version Log

| Version | Date | Description |
|:----------|:------|:-------------|
| v1.0 | 2025-10-08 | Initial setup, ingestion & macro merge completed |
| v1.1 | 2025-10-19 | Cleaned dataset & EDA results added |
| v1.2 | — | Feature engineering completed |
| v1.3 | — | Modeling & stress-testing results added |

---

## 🪶 Update Log

Each team member must record updates here whenever new data files are created, cleaned, or enhanced.  
Only **textual summaries** (no screenshots or plots) should be added.

| Date | Member | File(s) Updated | Description of Change | Rows / Columns | Notes |
|:------|:--------|:----------------|:-----------------------|---------------:|:-------|
| 2025-10-08 | Binod | loans_merged.parquet | Completed macro merge and ingestion scripts | 2 260 668 / 18 | Added GDP, CPI, UNRATE, FEDFUNDS |
| 2025-10-27 | Binod & Karthikeya | loans_cleaned.parquet | Cleaned dataset and removed nulls | 2,258,953 / 24 | Added EDA summary |
| YYYY-MM-DD | Member B | loans_fe.parquet | Added engineered features (ratios, macro deltas) | 2 153 420 / 22 | Ready for model input |
| YYYY-MM-DD | Member C | model_metrics.csv | Added baseline model metrics and plots | — | Included ROC & PR curves |
| YYYY-MM-DD | Binod | stress_scenarios.parquet | Added synthetic macro scenarios from VAE model | — | Prepared for GenAI stress testing |
 
