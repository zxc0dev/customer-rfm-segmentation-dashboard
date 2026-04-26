# Customer RFM Segmentation Dashboard

An end-to-end customer segmentation project that combines SQL-first RFM feature engineering (PostgreSQL + dbt), exploratory analysis, and KMeans clustering to produce analysis and customer segmentation.

## Table of Contents

1. Problem and Objective
2. Dataset
3. Project Structure
4. Workflow Overview
5. Key Insights
6. Segmentation Results
7. Run This Project Locally
8. Contact

## 1. Problem and Objective

Problem: no rfm segmentation pipeline that would help business to prioritize customers.

Objective: build a reproducible pipeline that cleans raw data, engineers customer features, and segments customers into interpretable behavioral groups for marketing and CRM activation.

## 2. Dataset

Source: Online Retail II (UCI) via Kaggle (`mashlyn/online-retail-ii-uci`)

Pipeline data layers:

- `data/01_raw/online_retail_II.csv` (raw transactions)
- `data/02_processed/base_retail.csv` (cleaned base dataset)
- `data/03_featured/featured_retail.csv` (RFM + scoring features)
- `data/04_segmented/customer_segments_kmeans.csv` (final KMeans segments)

From notebook analysis:

- Raw rows: 1,067,371
- Cleaned rows for segmentation: 797,815

## 3. Project Structure

```text
customer-rfm-segmentation-dashboard/
|
|-- notebooks/
|   |-- 01_ingestion_and_eda.ipynb
|   |-- 02_feature_engineering.ipynb
|   |-- 03_segmentation_modeling.ipynb
|
|-- src/
|   |-- pipelines/
|   |   |-- pipeline.py                  # Prefect flow: DB setup -> load -> dbt run/test
|   |   \-- dbt_run.py                   # dbt run / dbt test wrappers
|   |-- tasks/
|   |   |-- download.py                  # Kaggle download helper
|   |   |-- load.py                      # COPY CSV into PostgreSQL raw schema
|   |   |-- sql_feature_engineering.py   # SQL feature task runner
|   |   \-- pd_feature_engineering.py    # Pandas feature engineering
|   |-- db_init/
|   |   \-- db_setup.py                  # create/drop DB and schema objects
|   \-- config/
|       |-- config.py                    # env-driven DB connection URLs
|       |-- constants.py                 # dataset source constant
|       \-- paths.py                     # project/data paths
|
|-- dbt/
|   |-- models/staging/stg_retail.sql
|   |-- models/intermediate/int_retail_cleaned.sql
|   |-- models/dim/dim_customers.sql
|   \-- models/mart/mart_customer_rfm_features.sql
|
|-- sql/
|   |-- sql_create/schema.sql
|   \-- sql_indexes/
|
|-- data/
|-- pyproject.toml
\-- README.md
```

## 4. Workflow Overview

### Notebook 1: Ingestion and EDA

- Downloads raw dataset via `kagglehub`
- Cleans core fields, removes duplicates and zero-price rows
- Explores missing IDs, returns/cancellations, seasonality, country concentration
- Exports processed dataset to `data/02_processed/base_retail.csv`

### Notebook 2: Feature Engineering

- Runs canonical SQL feature engineering via Prefect + dbt
- Builds customer-level RFM and supporting features:
    - `recency`, `frequency`, `monetary`
    - `recency_score`, `frequency_score`, `monetary_score`
    - `r_f_score`, `segment`
    - `return_ratio`, `avg_order_value`
- Saves featured output to `data/03_featured/featured_retail.csv`

### Notebook 3: Segmentation Modeling

- Standardizes transformed RFM inputs
- Chooses K using inertia + silhouette diagnostics
- Trains KMeans and profiles clusters
- Adds human-readable segment names and exports final file to:
    `data/04_segmented/customer_segments_kmeans.csv`

## 5. Key Insights

- Missing customer IDs are substantial in raw data (about 22.8%), so customer-level modeling necessarily excludes guest transactions.
- Revenue is highly concentrated in the UK customer base.
- Returns are meaningful behavior and are preserved in engineered features through `return_ratio`.
- RFM distributions are skewed, so log transform + scaling are used before clustering.

## 6. Segmentation Results

Current modeling notebook output:

- Selected clusters: 3 (practical floor applied for interpretability)
- Cluster sizes:
    - Cluster 0: 1,714 customers
    - Cluster 1: 2,340 customers
    - Cluster 2: 1,804 customers
- PCA coverage: first 2 principal components explain about 94.27% variance

Auto-assigned business-friendly names include:

- Champions
- Loyal Customers
- Potential Loyalists

## 7. Run This Project Locally

### Prerequisites

- Python 3.11+
- PostgreSQL
- dbt (`dbt-core`, `dbt-postgres`)

### Setup

```bash
# 1) Clone
git clone https://github.com/zxc0dev/customer-rfm-segmentation-dashboard
cd customer-rfm-segmentation-dashboard

# 2) Create venv
python -m venv .venv

# Windows
.venv\Scripts\activate

# 3) Install project
pip install -e .
```

### Configure Environment

Create `.env` (or copy from `.env_example`) with:

- `DB_HOST`
- `DB_PORT`
- `DB_USER`
- `DB_PASSWORD`
- `MAIN_DB_NAME`
- `CREATED_DB_NAME`

### Execute

Notebook workflow

1. `notebooks/01_ingestion_and_eda.ipynb`
2. `notebooks/02_feature_engineering.ipynb`
3. `notebooks/03_segmentation_modeling.ipynb`

### Deactivate

```bash
deactivate
```

## 8. Contact

Author: zxc0.dev