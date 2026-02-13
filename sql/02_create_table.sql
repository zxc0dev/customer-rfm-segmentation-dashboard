CREATE TABLE IF NOT EXISTS public.retail_records (
        invoice      varchar(50) NOT NULL,
        stockcode    varchar(50),
        description  text,
        quantity     integer,
        invoicedate  timestamp without time zone,
        price        numeric(10,2),
        customer_id  integer,
        country      varchar(100)
    );