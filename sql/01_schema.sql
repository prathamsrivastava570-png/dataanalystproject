CREATE TABLE dim_card (
    card_key    NUMBER PRIMARY KEY,
    cc_num      NUMBER(19)   NOT NULL UNIQUE,
    first_name  VARCHAR2(50),
    last_name   VARCHAR2(50),
    gender      CHAR(1)      CHECK (gender IN ('M','F')),
    dob         DATE,
    job         VARCHAR2(100),
    street      VARCHAR2(150),
    city        VARCHAR2(80),
    state       CHAR(2),
    zip         NUMBER(5),
    latitude    NUMBER(9,6),
    longitude   NUMBER(9,6),
    city_pop    NUMBER(10)
);

CREATE TABLE dim_merchant (
    merchant_key  NUMBER PRIMARY KEY,
    merchant_name VARCHAR2(150) NOT NULL UNIQUE
);

CREATE TABLE dim_category (
    category_key  NUMBER PRIMARY KEY,
    category_name VARCHAR2(50) NOT NULL UNIQUE
);

CREATE TABLE dim_date (
    date_key    NUMBER(8) PRIMARY KEY,
    full_date   DATE NOT NULL UNIQUE,
    year_num    NUMBER(4),
    month_num   NUMBER(2) CHECK (month_num BETWEEN 1 AND 12),
    day_num     NUMBER(2) CHECK (day_num BETWEEN 1 AND 31),
    day_name    VARCHAR2(10),
    is_weekend  NUMBER(1) CHECK (is_weekend IN (0,1))
);

CREATE TABLE fact_transaction (
    trans_num        VARCHAR2(40) PRIMARY KEY,
    card_key         NUMBER NOT NULL REFERENCES dim_card(card_key),
    merchant_key     NUMBER NOT NULL REFERENCES dim_merchant(merchant_key),
    category_key     NUMBER NOT NULL REFERENCES dim_category(category_key),
    date_key         NUMBER(8) NOT NULL REFERENCES dim_date(date_key),
    trans_time       TIMESTAMP NOT NULL,
    trans_hour       NUMBER(2) CHECK (trans_hour BETWEEN 0 AND 23),
    amt              NUMBER(10,2) NOT NULL CHECK (amt > 0),
    merch_latitude   NUMBER(9,6),
    merch_longitude  NUMBER(9,6),
    is_fraud         NUMBER(1) NOT NULL CHECK (is_fraud IN (0,1)),
    py_rule_amount   NUMBER(1) CHECK (py_rule_amount IN (0,1)),
    py_rule_velocity NUMBER(1) CHECK (py_rule_velocity IN (0,1)),
    py_rule_night    NUMBER(1) CHECK (py_rule_night IN (0,1)),
    py_flag_count    NUMBER(1) CHECK (py_flag_count BETWEEN 0 AND 3)
);

CREATE INDEX idx_fact_card_time ON fact_transaction (card_key, trans_time);
