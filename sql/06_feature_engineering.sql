DROP TABLE IF EXISTS public.featured_retail;

    CREATE TABLE public.featured_retail AS
    WITH
    /* 1) Base data (UNFILTERED except customer_id not null) */
    base AS (
        SELECT
            customer_id,
            invoice,
            CAST(invoice_date AS timestamp) AS invoice_date,
            quantity,
            price,
            (quantity * price) AS revenue
        FROM public.base_retail
        WHERE customer_id IS NOT NULL
    ),

    /* 2) Global max invoice date */
    global_max AS (
        SELECT MAX(invoice_date) AS max_date
        FROM base
    ),

    /* 3) RFM core */
    rfm_core AS (
        SELECT
            b.customer_id,
            MAX(b.invoice_date) AS last_purchase_date,
            COUNT(DISTINCT b.invoice) AS frequency,
            SUM(b.revenue) AS monetary
        FROM base b
        GROUP BY b.customer_id
    ),

    rfm AS (
        SELECT
            r.customer_id,
            r.last_purchase_date,
            r.frequency,
            r.monetary,
            DATE_PART('day', (gm.max_date - r.last_purchase_date))::int AS recency
        FROM rfm_core r
        CROSS JOIN global_max gm
    ),

    /* 4) Scores */
    scored AS (
        SELECT
            r.*,
            (6 - NTILE(5) OVER (ORDER BY r.recency ASC, r.customer_id)) AS recency_score,
            NTILE(5) OVER (ORDER BY r.frequency ASC, r.customer_id) AS frequency_score,
            NTILE(5) OVER (ORDER BY r.monetary ASC, r.customer_id) AS monetary_score
        FROM rfm r
    ),

    /* 5) Segment mapping from R_F_Score */
    segmented AS (
        SELECT
            s.*,
            (s.recency_score::text || s.frequency_score::text) AS r_f_score,
            CASE
                WHEN (s.recency_score::text || s.frequency_score::text) ~ '^[1-2][1-2]$' THEN 'hibernating'
                WHEN (s.recency_score::text || s.frequency_score::text) ~ '^[1-2][3-4]$' THEN 'at_risk'
                WHEN (s.recency_score::text || s.frequency_score::text) ~ '^[1-2]5$'     THEN 'cant_lose'
                WHEN (s.recency_score::text || s.frequency_score::text) ~ '^3[1-2]$'      THEN 'about_to_sleep'
                WHEN (s.recency_score::text || s.frequency_score::text) = '33'            THEN 'need_attention'
                WHEN (s.recency_score::text || s.frequency_score::text) ~ '^[3-4][4-5]$'  THEN 'loyal_customers'
                WHEN (s.recency_score::text || s.frequency_score::text) = '41'            THEN 'promising'
                WHEN (s.recency_score::text || s.frequency_score::text) = '51'            THEN 'new_customers'
                WHEN (s.recency_score::text || s.frequency_score::text) ~ '^[4-5][2-3]$'  THEN 'potential_loyalists'
                WHEN (s.recency_score::text || s.frequency_score::text) ~ '^5[4-5]$'      THEN 'champions'
                ELSE NULL
            END AS segment
        FROM scored s
    ),

    /* 6) Return ratio */
    sales_returns AS (
        SELECT
            customer_id,
            SUM(CASE WHEN revenue > 0 THEN revenue ELSE 0 END) AS total_sales,
            SUM(CASE WHEN revenue < 0 THEN -revenue ELSE 0 END) AS total_returns
        FROM base
        GROUP BY customer_id
    ),

    return_ratio AS (
        SELECT
            customer_id,
            COALESCE(total_returns / NULLIF(total_sales, 0), 0) AS return_ratio
        FROM sales_returns
    ),

    /* 7) Average order value */
    aov AS (
        SELECT
            customer_id,
            SUM(revenue) AS total_revenue,
            COUNT(DISTINCT invoice) AS total_orders,
            (SUM(revenue) / NULLIF(COUNT(DISTINCT invoice), 0)) AS avg_order_value
        FROM base
        GROUP BY customer_id
    )

    SELECT
        seg.customer_id,
        seg.recency,
        seg.frequency,
        seg.monetary,
        seg.recency_score,
        seg.frequency_score,
        seg.monetary_score,
        seg.r_f_score,
        seg.segment,
        rr.return_ratio,
        a.avg_order_value
    FROM segmented seg
    LEFT JOIN return_ratio rr
        ON rr.customer_id = seg.customer_id
    LEFT JOIN aov a
        ON a.customer_id = seg.customer_id
    ;