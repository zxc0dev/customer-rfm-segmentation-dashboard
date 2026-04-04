COPY public.base_retail(invoice,stock_code,description,quantity,invoice_date,price,customer_id,country,revenue,year,month)
    FROM STDIN WITH (FORMAT CSV, HEADER, DELIMITER ',');
    