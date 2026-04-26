SELECT
    customer_id,
    invoice,
    invoice_date,
    quantity,
    price,
    (quantity * price) AS revenue,
    description,
    stock_code,
    country,
    year,
    month
FROM {{ ref('stg_retail') }}
WHERE customer_id IS NOT NULL
