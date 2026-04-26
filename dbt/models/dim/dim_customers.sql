SELECT
    customer_id,
    invoice,
    invoice_date,
    quantity,
    price,
    revenue,
    description,
    stock_code,
    country,
    year,
    month
FROM {{ ref('int_retail_cleaned') }}
