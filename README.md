# Customer RFM Segmentation Project

## Project Overview

This project implements an RFM (Recency, Frequency, Monetary) Analysis pipeline to segment customers based on their transaction history. By categorizing customers, businesses can create targeted marketing strategies, improve retention, and identify high-value "Champions."

## Repository Structure

    data/: Tiered data storage from raw ingestion to processed modeling sets.

    sql/: Database schema definitions and RFM calculation logic.

    notebooks/: Step-by-step workflow from ETL to Machine Learning clustering.

    requirements.txt: Python dependencies for reproducibility.

## Getting Started

1. Environment Setup

Clone the repository and install dependencies:
Bash

pip install -r requirements.txt

2. Data Pipeline Execution

Follow the numbered notebooks/scripts in order:

    Extract: Run 01_download_data.ipynb to fetch source transactions.

    Load: Execute sql/01_create_database.sql and 02_create_table.sql, then run 02_load_data_to_sql.ipynb.

    Transform: Run 03_calculate_rfm.sql to generate the scoring table.

    Analyze: Explore distributions in 04_eda_data.ipynb.

    Model: Train K-Means clustering in 05_train_segmentation_models.ipynb.

## RFM Scoring Logic

I used a quintile-based scoring system (1−5):

    Recency (R): Days since last purchase. (Lower days = Higher Score)

    Frequency (F): Total number of distinct transactions.

    Monetary (M): Total revenue generated per customer.