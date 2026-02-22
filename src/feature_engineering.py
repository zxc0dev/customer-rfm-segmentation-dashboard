import pandas as pd
import re
from sqlalchemy import text
from sqlalchemy.engine import URL

def feature_engineering_sql(engine: URL, table_name: str, table_name_rfm: str):
    feature_engineering_query = f"""
    WITH cleaned AS (
    SELECT 
        customer_id,
        invoice,
        CAST(invoice_date AS TIMESTAMP) as invoice_date,
        quantity,
        price
    FROM public.{table_name}
    WHERE quantity > 0
      AND price > 0
      AND customer_id IS NOT NULL
    ),
    rfm_base AS (
        SELECT
            customer_id,
            MAX(invoice_date) AS last_purchase_date,
            COUNT(DISTINCT invoice) AS frequency,
            SUM(quantity * price) AS monetary
        FROM cleaned
        GROUP BY customer_id
    )
    SELECT
        customer_id,
        last_purchase_date,
        frequency,
        monetary,
        DATE_PART('day', (SELECT MAX(last_purchase_date) FROM rfm_base) - last_purchase_date) AS recency,
        NTILE(5) OVER (ORDER BY DATE_PART('day', (SELECT MAX(last_purchase_date) FROM rfm_base) - last_purchase_date) DESC) AS R_score,
        NTILE(5) OVER (ORDER BY frequency ASC) AS F_score,
        NTILE(5) OVER (ORDER BY monetary ASC) AS M_score
    FROM rfm_base;
    """
    with engine.connect() as conn:
        conn.execute(text(feature_engineering_query))
        print(f"Feature engineering query executed successfully.")
    

def feature_engineering_pandas(df: pd.DataFrame) -> pd.DataFrame:
    max_date = df['invoice_date'].max()

    df_rfm = df.groupby('customer_id').agg({
        'invoice_date': lambda x: (max_date - x.max()).days,
        'invoice': 'nunique',
        'revenue': 'sum'
    }).reset_index()

    df_rfm.rename(columns={
        'invoice_date': 'recency',
        'invoice': 'frequency',
        'revenue': 'monetary'
    }, inplace=True)

    df_rfm["recency_score"] = pd.qcut(
        df_rfm["recency"], 
        5, 
        labels=[5,4,3,2,1]
    )

    df_rfm["frequency_score"] = pd.qcut(
        df_rfm["frequency"].rank(method="first"), 
        5, 
        labels=[1,2,3,4,5]
    )

    df_rfm["monetary_score"] = pd.qcut(
        df_rfm["monetary"], 
        5, 
        labels=[1,2,3,4,5]
    )

    df_rfm["recency_score"] = df_rfm["recency_score"].astype(int)
    df_rfm["frequency_score"] = df_rfm["frequency_score"].astype(int)
    df_rfm["monetary_score"] = df_rfm["monetary_score"].astype(int)

    df_rfm["R_F_Score"] = df_rfm["recency_score"].astype(str) + df_rfm["frequency_score"].astype(str)

    seg_map = {
        r'[1-2][1-2]': 'hibernating',
        r'[1-2][3-4]': 'at_risk',
        r'[1-2]5': 'cant_lose',
        r'3[1-2]': 'about_to_sleep',
        r'33': 'need_attention',
        r'[3-4][4-5]': 'loyal_customers',
        r'41': 'promising',
        r'51': 'new_customers',
        r'[4-5][2-3]': 'potential_loyalists',
        r'5[4-5]': 'champions'
    }

    df_rfm["segment"] = df_rfm["R_F_Score"].replace(seg_map, regex = True)

    df['sales_only'] = df['revenue'].clip(lower=0)
    df['returns_only'] = df['revenue'].clip(upper=0).abs()

    ratios = df.groupby('customer_id').agg(
        total_sales=('sales_only', 'sum'),
        total_returns=('returns_only', 'sum')
    )

    ratios['return_ratio'] = ratios['total_returns'] / ratios['total_sales']
    ratios['return_ratio'] = ratios['return_ratio'].fillna(0)
    ratios.reset_index()
    ratios
    df_rfm = df_rfm.set_index('customer_id')
    df_rfm = df_rfm.merge(ratios[['return_ratio']], left_index=True, right_index=True, how='left')

    #avg_interpurchase_time
    #customer_age_days
    #avg_order_value
    
    return df_rfm