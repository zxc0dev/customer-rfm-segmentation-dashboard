import pandas as pd
from src.utils.logger import get_logger

logger = get_logger(__name__)

def pd_feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("=== PANDAS FEATURE ENGINEERING STARTED ===")
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

    # Sort by customer_id as tiebreaker to match SQL's NTILE(...ORDER BY ..., customer_id)
    df_rfm = df_rfm.sort_values(["recency", "customer_id"], ascending=[True, True])
    df_rfm["recency_score"] = pd.qcut(
        df_rfm["recency"].rank(method="first", ascending=True),
        5,
        labels=[5, 4, 3, 2, 1]
    )

    df_rfm = df_rfm.sort_values(["frequency", "customer_id"], ascending=[True, True])
    df_rfm["frequency_score"] = pd.qcut(
        df_rfm["frequency"].rank(method="first", ascending=True),
        5,
        labels=[1, 2, 3, 4, 5]
    )

    df_rfm = df_rfm.sort_values(["monetary", "customer_id"], ascending=[True, True])
    df_rfm["monetary_score"] = pd.qcut(
        df_rfm["monetary"].rank(method="first", ascending=True),
        5,
        labels=[1, 2, 3, 4, 5]
    )

    df_rfm["recency_score"] = df_rfm["recency_score"].astype(int)
    df_rfm["frequency_score"] = df_rfm["frequency_score"].astype(int)
    df_rfm["monetary_score"] = df_rfm["monetary_score"].astype(int)

    df_rfm["r_f_score"] = df_rfm["recency_score"].astype(str) + df_rfm["frequency_score"].astype(str)

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

    df_rfm["segment"] = df_rfm["r_f_score"].replace(seg_map, regex = True)

    df['sales_only'] = df['revenue'].clip(lower=0)
    df['returns_only'] = df['revenue'].clip(upper=0).abs()

    ratios = df.groupby('customer_id').agg(
        total_sales=('sales_only', 'sum'),
        total_returns=('returns_only', 'sum')
    )

    ratios['return_ratio'] = ratios['total_returns'] / ratios['total_sales']
    ratios['return_ratio'] = ratios['return_ratio'].fillna(0)
    ratios.reset_index(inplace=True)
    df_rfm = df_rfm.set_index('customer_id')
    df_rfm = df_rfm.merge(ratios[['return_ratio']], left_index=True, right_index=True, how='left')

    inv = (df.dropna(subset=["customer_id"])
            .drop_duplicates(subset=["customer_id", "invoice"])
            .sort_values(["customer_id", "invoice_date"]))
    '''
    Unused features

    avg_interpurchase = (inv.groupby("customer_id")["invoice_date"]
                        .diff()
                        .dt.total_seconds().div(86400)
                        .groupby(inv["customer_id"])
                        .mean()
                        .rename("avg_interpurchase_days"))
    
    df_rfm = df_rfm.merge(avg_interpurchase, left_index=True, right_index=True, how="left")

    purchase_date = df.groupby("customer_id")["invoice_date"].min() 

    customer_tenure = (
        (max_date - purchase_date)
        .dt.total_seconds().div(86400)
        .rename("customer_tenure_days")
        .round()
        .astype("Int64")  
    )

    df_rfm = df_rfm.merge(customer_tenure, left_index=True, right_index=True, how="left")
    '''
    avg_order_value = (
        df.groupby("customer_id")
        .agg(total_revenue=("revenue", "sum"),
            total_orders=("invoice", "nunique"))
    )

    avg_order_value["avg_order_value"] = avg_order_value["total_revenue"] / avg_order_value["total_orders"]

    df_rfm = df_rfm.merge(avg_order_value[["avg_order_value"]],
                        left_index=True, right_index=True, how="left")
    
    logger.info("=== PANDAS FEATURE ENGINEERING COMPLETED SUCCESSFULLY ===")

    return df_rfm