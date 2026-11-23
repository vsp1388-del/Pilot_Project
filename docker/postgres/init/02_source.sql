-- Legacy source system: sample data generated deterministically.
\connect pilot_source

CREATE TABLE cust_master (
    cust_id     integer PRIMARY KEY,
    first_nm    varchar(50) NOT NULL,
    last_nm     varchar(50) NOT NULL,
    dob         date,
    email_addr  varchar(120),
    status_cd   char(1) NOT NULL
);

CREATE TABLE dep_acct (
    acct_no      integer PRIMARY KEY,
    cust_id      integer NOT NULL REFERENCES cust_master (cust_id),
    product_cd   varchar(3) NOT NULL,
    open_dt      date NOT NULL,
    balance_amt  numeric(14, 2) NOT NULL,
    currency_cd  char(3) NOT NULL
);

CREATE TABLE loan_acct (
    loan_no        varchar(10) PRIMARY KEY,
    cust_id        integer NOT NULL REFERENCES cust_master (cust_id),
    principal_amt  numeric(14, 2) NOT NULL,
    rate_pct       numeric(5, 3) NOT NULL,
    start_dt       date NOT NULL,
    maturity_dt    date NOT NULL,
    status_cd      char(1) NOT NULL
);

INSERT INTO cust_master
SELECT i, 'First' || i, 'Last' || i, DATE '1970-01-01' + i * 97,
       'customer' || i || '@example.com', CASE WHEN i % 10 = 0 THEN 'I' ELSE 'A' END
FROM generate_series(1, 50) AS i;

INSERT INTO dep_acct
SELECT 100000 + i, ((i - 1) % 50) + 1, (ARRAY['SAV', 'CHK', 'CD'])[i % 3 + 1],
       DATE '2015-01-01' + i * 11, round(((i * 1234.56) % 50000)::numeric, 2), 'USD'
FROM generate_series(1, 80) AS i;

INSERT INTO loan_acct
SELECT 'LN' || lpad(i::text, 5, '0'), ((i * 7 - 1) % 50) + 1, i * 5000, 3.5 + (i % 5) * 0.25,
       DATE '2018-01-01' + i * 30, (DATE '2018-01-01' + i * 30 + INTERVAL '5 years')::date,
       CASE WHEN i % 8 = 0 THEN 'C' ELSE 'O' END
FROM generate_series(1, 40) AS i;
