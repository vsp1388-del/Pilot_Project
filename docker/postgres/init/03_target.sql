-- Target (migrated) system: same data with renamed columns and decoded status values.
\connect pilot_target

CREATE TABLE customer (
    customer_id    integer PRIMARY KEY,
    first_name     varchar(50) NOT NULL,
    last_name      varchar(50) NOT NULL,
    date_of_birth  date,
    email          varchar(120),
    status         varchar(10) NOT NULL
);

CREATE TABLE deposit_account (
    account_number  integer PRIMARY KEY,
    customer_id     integer NOT NULL REFERENCES customer (customer_id),
    product_code    varchar(3) NOT NULL,
    open_date       date NOT NULL,
    balance         numeric(14, 2) NOT NULL,
    currency        char(3) NOT NULL
);

CREATE TABLE loan (
    loan_number    varchar(10) PRIMARY KEY,
    customer_id    integer NOT NULL REFERENCES customer (customer_id),
    principal      numeric(14, 2) NOT NULL,
    interest_rate  numeric(5, 3) NOT NULL,
    start_date     date NOT NULL,
    maturity_date  date NOT NULL,
    status         varchar(10) NOT NULL
);

INSERT INTO customer
SELECT i, 'First' || i, 'Last' || i, DATE '1970-01-01' + i * 97,
       'customer' || i || '@example.com', CASE WHEN i % 10 = 0 THEN 'INACTIVE' ELSE 'ACTIVE' END
FROM generate_series(1, 50) AS i;

INSERT INTO deposit_account
SELECT 100000 + i, ((i - 1) % 50) + 1, (ARRAY['SAV', 'CHK', 'CD'])[i % 3 + 1],
       DATE '2015-01-01' + i * 11, round(((i * 1234.56) % 50000)::numeric, 2), 'USD'
FROM generate_series(1, 80) AS i;

INSERT INTO loan
SELECT 'LN' || lpad(i::text, 5, '0'), ((i * 7 - 1) % 50) + 1, i * 5000, 3.5 + (i % 5) * 0.25,
       DATE '2018-01-01' + i * 30, (DATE '2018-01-01' + i * 30 + INTERVAL '5 years')::date,
       CASE WHEN i % 8 = 0 THEN 'CLOSED' ELSE 'OPEN' END
FROM generate_series(1, 40) AS i;
