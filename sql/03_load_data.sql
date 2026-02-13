COPY public.retail_records(invoice, stockcode, description, quantity, invoicedate, price, customer_id, country)
    FROM STDIN WITH (FORMAT CSV, HEADER, DELIMITER ',');