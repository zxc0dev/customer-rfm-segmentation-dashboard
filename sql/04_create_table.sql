CREATE TABLE IF NOT EXISTS public.base_retail (
        invoice      varchar(50) NOT NULL,
        stock_code    varchar(50),
        description  text,
        quantity     integer,
        invoice_date  timestamp without time zone,
        price        numeric(10,2),
        customer_id  integer,
        country      varchar(100),
        revenue      numeric(20,2),
        year         integer,
        month        integer
    );