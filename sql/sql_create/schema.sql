CREATE SCHEMA IF NOT EXISTS dim;


CREATE TABLE IF NOT EXISTS dim.dim_base_retail (
        invoice      VARCHAR(50) NOT NULL,
        stock_code    VARCHAR(50),
        description  TEXT,
        quantity     INTEGER,
        invoice_date  TIMESTAMP WITHOUT TIME ZONE,
        price        NUMERIC(10,2),
        customer_id  INTEGER,
        country      VARCHAR(100),
        revenue      NUMERIC(20,2),
        year         INTEGER,
        month        INTEGER
    );