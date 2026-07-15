# 🛒 Walmart Store Sales Forecasting

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue)
![XGBoost](https://img.shields.io/badge/XGBoost-R²%3D0.974-green)
![Streamlit](https://img.shields.io/badge/Streamlit-Deployed-red)

---

## 📌 Business Problem Statement

Walmart operates **45 stores across multiple regions**, each containing
up to 99 departments. Every week, store managers must decide:

- How much **inventory to stock** per department
- How many **staff to schedule**
- Which departments need **promotional markdowns**
- How to **allocate budget** across stores

Making these decisions without accurate sales forecasts leads to:

| Problem | Business Impact |
|---|---|
| Overstocking | Wasted inventory costs, storage expenses |
| Understocking | Lost revenue, dissatisfied customers |
| Wrong staffing | Either idle staff costs or poor customer service |
| Misallocated markdowns | Promotions on wrong weeks = zero ROI |

**The Goal:** Build a Machine Learning model that accurately forecasts
weekly sales for each store-department combination — enabling data-driven
inventory, staffing, and promotional decisions across all 45 Walmart stores.

---

## 📊 Dataset Overview

| File | Rows | Description |
|---|---|---|
| `train.csv` | 421,570 | Weekly sales per store per department |
| `stores.csv` | 45 | Store type (A/B/C) and size in sq ft |
| `features.csv` | 8,190 | Economic indicators and promotional markdowns |

**Date Range:** February 2010 — October 2012

**Scale:** 45 stores × ~75 departments × 143 weeks

---

## 🏗️ Project Architecture

```
walmart-forecasting/
│
├── data/
│   ├── train.csv                    ← Raw sales data
│   ├── stores.csv                   ← Store metadata
│   ├── features.csv                 ← Economic + markdown data
│   ├── walmart_clean.csv            ← After cleaning
│   └── walmart_features.csv         ← After feature engineering
│
├── sql/
│   ├── create_tables.sql            ← PostgreSQL table schemas
│   └── eda_queries.sql              ← Business insight queries
│
├── scripts/
│   ├── load_data.py                 ← Load CSVs into PostgreSQL
│   ├── eda.py                       ← Run EDA queries
│   ├── data_understanding.py        ← Deep data analysis
│   ├── data_cleaning.py             ← Clean and transform data
│   ├── feature_engineering.py       ← Create new features
│   ├── linear_regression.py         ← Baseline model
│   └── xgboost_random_forest.py     ← Primary models
│
├── models/
│   ├── xgboost.pkl                  ← Production model
│   ├── random_forest.pkl            ← Comparison model
│   ├── linear_regression.pkl        ← Baseline model
│   └── scaler.pkl                   ← StandardScaler for Linear Reg
│
├── dashboard/                       ← All visualizations and charts
├── app/
│   └── app.py                       ← Streamlit web application
└── requirements.txt
```

---

## 🔍 Key Business Insights From EDA

**1. Store Type Drives Sales Significantly**
> Type A stores (largest) generate on average **2x more weekly sales**
> than Type C stores — store size is the single strongest predictor
> of sales.

**2. Holiday Weeks Are Not Always Higher**
> Surprisingly, not all holiday weeks show higher sales.
> Thanksgiving week is the single highest sales event while
> Super Bowl week shows minimal impact — promotional strategy
> should treat each holiday differently.

**3. Markdowns Signal Promotional Periods**
> Markdown columns are NULL before November 2011 — Walmart launched
> these promotional programs mid-dataset. Weeks with active markdowns
> show consistently higher sales, confirming promotions drive revenue.

**4. December and November Are Peak Months**
> Q4 (October-December) accounts for the highest weekly sales
> across all stores — inventory and staffing should scale up
> significantly for this period.

**5. Department-Level Variance is High**
> Top performing departments generate **10x more revenue** than
> bottom departments within the same store — department-level
> forecasting is essential, store-level aggregation is insufficient.

---

## ⚙️ Technical Approach

### Step 1 — Data Ingestion
- Loaded all 3 CSV files into **PostgreSQL** using `psycopg2`
- Created `walmart_master` view joining all 3 tables
- Used `NULL 'NA'` flag in COPY command to handle Kaggle-style nulls

### Step 2 — EDA with SQL
- 8 targeted business queries + 1 CTE for store performance tiering
- Identified NULL patterns in markdown columns
- Validated join keys across all 3 tables

### Step 3 — Data Cleaning
- Filled markdown NULLs with 0 (absence of promotion = zero discount)
- Label encoded store_type: A→0, B→1, C→2
- Applied `log1p` transform on `weekly_sales` and `unemployment`
- Retained negative sales — valid return-week data

### Step 4 — Feature Engineering
Created 7 new features from existing columns:

| Feature | Source | Business Meaning |
|---|---|---|
| `month` | date | Captures seasonal patterns |
| `year` | date | Captures yearly growth |
| `week_of_year` | date | Identifies Christmas/Thanksgiving weeks |
| `quarter` | date | Q4 = peak retail period |
| `is_quarter_end` | date | Budget spend patterns |
| `has_markdown` | markdown1-5 | Was any promotion active |
| `total_markdown` | markdown1-5 | Total promotional spend that week |

### Step 5 — Linear Regression (Baseline)

- Split data first → then applied StandardScaler on train only
- Applied `fit_transform` on train, `transform` on test only
  to prevent data leakage
- Dropped 6 multicollinear features using Correlation + VIF analysis:

| Dropped Feature | Reason |
|---|---|
| `week_of_year` | 0.996 correlation with month |
| `quarter` | 0.967 correlation with month |
| `year` | 0.820 correlation with has_markdown |
| `markdown4` | 0.839 correlation with markdown1 |
| `total_markdown` | 0.805 correlation with markdown1 |
| `store_type` | 0.812 correlation with store_size |

- Residual analysis confirmed violations of homoscedasticity
  and normality — validating that Linear Regression is
  insufficient for non-linear retail sales data

### Step 6 — Random Forest + XGBoost

- No scaling required — tree based models
- No VIF check required — handles correlated features naturally
- Used RandomizedSearchCV for hyperparameter tuning
- Applied early stopping on XGBoost to prevent overfitting

---

## 📈 Model Performance

| Model | Train R² | Test R² | MAE | RMSE |
|---|---|---|---|---|
| Linear Regression | — | 0.10 | $13,024 | $22,856 |
| Random Forest | 0.9923 | 0.9729 | $1,504 | $3,758 |
| **XGBoost** ✅ | **0.9831** | **0.9741** | **$1,919** | **$3,673** |

### Why Linear Regression Failed

> Residual analysis confirmed violations of homoscedasticity and
> normality assumptions — particularly for high-sales holiday weeks.
> Sales data is driven by complex non-linear interactions between
> store type, department, seasonality and promotions that a linear
> equation cannot capture.

### Why XGBoost Was Selected as Production Model

- Higher R² (0.9741 vs 0.9729) than Random Forest
- Lower RMSE ($3,673 vs $3,758) — fewer large prediction errors
- Smaller train-test gap (0.009 vs 0.019) — better generalization
- Industry standard for tabular forecasting problems

### Business Interpretation of Results

> **MAE of $1,919** means on average the model predicts weekly sales
> within $1,919 of actual — across all 45 stores and 75 departments.
> Given weekly sales range from $0 to $693,000 this represents
> exceptional accuracy for retail forecasting.

---

## 🌐 Streamlit Application

The trained XGBoost model is deployed as an interactive web app
where users can:

- Select any store (1-45) and department
- Pick any week date — month/year/week extracted automatically
- Adjust economic conditions (CPI, unemployment, fuel price)
- Enter promotional markdown amounts
- Switch between XGBoost and Random Forest models
- Compare prediction against historical average for that store/dept

```bash
streamlit run app/app.py
```

---

## 🔑 Data Quality Notes

The following issues were identified and retained intentionally:

- **Negative Weekly Sales** — weeks where returns exceeded purchases.
  Valid business signal, not data errors.
- **CPI Scale Inconsistency** — two CPI scales exist across stores
  due to regional measurement differences. Model learns per-store patterns.
- **Temperature Extremes** — real weather events in certain regions.
- **Zero Weekly Sales** — departments temporarily closed.
- **High Markdown Values** — genuine large-scale promotional events.

> None of these were removed — real-world retail data contains
> anomalies that carry business meaning.

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.9+ | Core programming language |
| PostgreSQL | Data storage and SQL EDA |
| psycopg2 | Python-PostgreSQL connection |
| pandas + numpy | Data manipulation |
| scikit-learn | Preprocessing + Linear Regression + Random Forest |
| XGBoost | Primary forecasting model |
| statsmodels | VIF calculation for Linear Regression |
| matplotlib + seaborn | Dashboard visualizations |
| joblib | Model serialization |
| Streamlit | Web app deployment |

---

## ▶️ How to Run

```bash
# 1. Clone the repository
git clone https://github.com/dhruvahuja-tech/walmart-sales-forecasting.git
cd walmart-sales-forecasting

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create PostgreSQL database
psql -U postgres -c "CREATE DATABASE walmart_db;"

# 4. Load data
python scripts/load_data.py

# 5. Run feature engineering
python scripts/feature_engineering.py

# 6. Train baseline model
python scripts/linear_regression.py

# 7. Train primary models
python scripts/xgboost_random_forest.py

# 8. Launch Streamlit app
streamlit run app/app.py
```

---

## 👤 Author

**Dhruv Ahuja**
- GitHub  : [dhruvahuja-tech](https://github.com/dhruvahuja-tech)
- LinkedIn: [linkedin.com/in/dhruv-ahuja-0b298a297](https://linkedin.com/in/dhruv-ahuja-0b298a297)
