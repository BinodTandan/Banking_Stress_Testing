# 🧠 AI-Driven Stress Testing: Generative Models for Scenario Simulation in Banking  

> **A research-driven data science project exploring how Generative AI can enhance financial stress testing through synthetic macroeconomic scenario generation.**

---

## 📘 Overview  

Traditional banking stress tests rely on a few **regulator-defined scenarios** (Baseline, Adverse, Severely Adverse) published by the **Federal Reserve (Fed)** and **European Central Bank (ECB)**.  
These are static and backward-looking — they fail to anticipate new systemic risks like **pandemics, cyberattacks, or geopolitical shocks**.  

This project introduces an **AI-driven stress testing framework** that leverages **Generative Models (VAEs, GANs, Diffusion)** to simulate **novel and plausible macroeconomic scenarios**.  
These scenarios are then applied to a **loan portfolio model** (trained on LendingClub data) to assess portfolio-level credit losses under both historical and synthetic conditions.

---

## 🎯 Objectives  

- To design a **data-driven stress testing pipeline** integrating macroeconomic and loan-level data.  
- To train baseline **credit-risk models** (Logistic Regression, XGBoost, LSTM) predicting default probabilities.  
- To develop **Generative AI models** (VAE/GAN) that create diverse macroeconomic scenarios.  
- To use **LLMs (FinBERT, GPT-4)** for generating human-readable narratives for each scenario.  
- To evaluate realism, diversity, and interpretability of AI-generated stress scenarios compared to regulator scenarios.  

---

## 🧩 Project Workflow  

| Phase | Description | Output |
|:------|:-------------|:--------|
| 1️⃣ Data Ingestion | Load LendingClub loans (2007–2018) and FRED macroeconomic indicators. | `loans_slim.parquet`, `macro_q.parquet` |
| 2️⃣ Data Merging | Align loan issue dates with quarterly macro data. | `loans_merged.parquet` |
| 3️⃣ EDA & Cleaning | Remove nulls, handle outliers, and validate data distributions. | `loans_cleaned.parquet` |
| 4️⃣ Feature Engineering | Add macro deltas, income ratios, encoded borrower features. | `loans_fe.parquet` |
| 5️⃣ Credit Risk Modeling | Train Logistic / XGBoost / LSTM models on default prediction. | Model metrics |
| 6️⃣ Stress Scenario Simulation | Apply regulator and GenAI scenarios to evaluate portfolio loss. | `stress_results.parquet` |
| 7️⃣ LLM Narrative Generation | Use FinBERT/GPT to generate text summaries for synthetic scenarios. | Scenario narratives |

---

## 🧮 Repository Structure  
```bash
ai_stress_testing/
│
├── data_raw/ # Original CSV/GZ files (not committed to Git)
├── data_work/ # Intermediate Parquet datasets
├── results/ # Model outputs, metrics, and plots
├── notebooks/
│ ├── 01_data_cleaning.ipynb
│ ├── 02_feature_engineering.ipynb
│ ├── 03_model_training.ipynb
│ ├── 04_stress_testing.ipynb
  ├── 05_genAI_scenarios.ipynb
│ └── 06_prepare_llm_scenario.ipynb
│
├── src/
│ ├── ingest.py # Large-file ingestion in chunks
  ├── llm_narratives.py
│ ├── merge_macro.py # Macro data integration (FRED)
│ ├── train_model.py # Credit risk model training
│ └── stress_genai.py # Generative stress scenario generation
│
├── DATA_README.md # Data documentation and update logs
├── requirements.txt # Dependencies
└── README.md # Project overview (this file)
```


---

## ⚙️ Installation & Environment Setup  

### 1️⃣ Clone the repository  
```bash
git clone 
cd ai_stress_testing
```
### 2️⃣ Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate      # Mac / Linux
venv\Scripts\activate         # Windows
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Verify setup
```bash 
python src/ingest.py
python src/merge_macro.py
```
✅ You should see output confirming merged datasets.

### 🗂️ Data Sources

| Source | Description | Access |
|:--------|:-------------|:--------|
| **Kaggle: LendingClub Loan Data** | Historical accepted/rejected loan applications (2007–2018). | [https://www.kaggle.com/datasets/wordsforthewise/lending-club](https://www.kaggle.com/datasets/wordsforthewise/lending-club) |
| **FRED (Federal Reserve Economic Data)** | U.S. macroeconomic indicators used for stress testing. | [https://fred.stlouisfed.org/](https://fred.stlouisfed.org/) |
| **Variables Used** | UNRATE (unemployment rate), GDPC1 (real GDP), CPIAUCSL (inflation), FEDFUNDS (interest rate). | Public API via `pandas_datareader` |

---
All raw data files are stored in the shared Google Drive folder and are excluded from GitHub (see .gitignore).


### 🧠 Modeling Techniques

| Category | Algorithm / Model | Purpose |
|:-----------|:------------------|:----------|
| **Baseline Credit Risk** | Logistic Regression, XGBoost | Predict loan default (PD) |
| **Generative Modeling** | VAE | Generate synthetic macroeconomic scenarios |
| **LLM Narrative Generation** | OpenAI | Create textual stress-test narratives |
| **Evaluation Metrics** | AUC, cluster diversity | Compare realism and coverage |

---

### 🧩 Collaboration & Roles

| Member | Responsibility |
|:--------|:----------------|
| **Binod Tandan** | Team Lead, Pipeline Setup, Macro-Merge, GenAI Integration |
| **Karthikeya Reddy Bonuga** | Data Cleaning, EDA, Statistical Testing |
| **Rutuja Jadhav** | Feature Engineering, Model Training |
| **Karthikeya Reddy Bonuga** | Visualization, Reporting, Documentation |

