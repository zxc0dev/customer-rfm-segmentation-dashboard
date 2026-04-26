SELECT
    invoice,
    stock_code,
    description,
    quantity,
    invoice_date::TIMESTAMP AS invoice_date,
    price,
    customer_id,
    country,
    revenue,
    year,
    month
FROM {{ source('raw', 'raw_base_retail') }}
