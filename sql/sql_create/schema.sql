CREATE SCHEMA IF NOT EXISTS dim;
CREATE SCHEMA IF NOT EXISTS stg;
CREATE SCHEMA IF NOT EXISTS mart;
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS int;


CREATE TABLE IF NOT EXISTS raw.raw_base_retail (
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