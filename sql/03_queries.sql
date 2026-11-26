-- 7 business queries (Oracle). Run: python python/09_run_sql.py sql/03_queries.sql
-- SQLite differences are marked "SQLITE:" in the comments.

-- Q1. Which merchant categories have the highest fraud rate?  (JOIN, GROUP BY)
SELECT c.category_name,
       COUNT(*) AS txns,
       SUM(f.is_fraud) AS fraud_txns,
       ROUND(SUM(f.is_fraud) / COUNT(*) * 100, 2) AS fraud_rate_pct
FROM fact_transaction f
JOIN dim_category c ON c.category_key = f.category_key
GROUP BY c.category_name
ORDER BY fraud_rate_pct DESC;

-- Q2. Is fraud more common at night?  (CASE, GROUP BY)
SELECT CASE WHEN f.trans_hour IN (22,23,0,1,2,3) THEN 'Night (22:00-03:59)'
            ELSE 'Day (04:00-21:59)' END AS time_band,
       COUNT(*) AS txns,
       SUM(f.is_fraud) AS fraud_txns,
       ROUND(SUM(f.is_fraud) / COUNT(*) * 100, 2) AS fraud_rate_pct
FROM fact_transaction f
GROUP BY CASE WHEN f.trans_hour IN (22,23,0,1,2,3) THEN 'Night (22:00-03:59)'
              ELSE 'Day (04:00-21:59)' END
ORDER BY fraud_rate_pct DESC;

-- Q3. How does monthly fraud change from the previous month?  (JOIN, GROUP BY, window function LAG)
WITH monthly AS (
    SELECT d.year_num, d.month_num, COUNT(*) AS txns, SUM(f.is_fraud) AS fraud_txns
    FROM fact_transaction f
    JOIN dim_date d ON d.date_key = f.date_key
    GROUP BY d.year_num, d.month_num
)
SELECT year_num, month_num, txns, fraud_txns,
       ROUND(fraud_txns / txns * 100, 2) AS fraud_rate_pct,
       LAG(fraud_txns) OVER (ORDER BY year_num, month_num) AS prev_month_fraud,
       fraud_txns - LAG(fraud_txns) OVER (ORDER BY year_num, month_num) AS change_vs_prev
FROM monthly
ORDER BY year_num, month_num;

-- Q4. Which 10 states have the highest fraud rate?  (JOIN, GROUP BY, HAVING)
-- SQLITE: replace FETCH FIRST 10 ROWS ONLY with LIMIT 10
SELECT k.state,
       COUNT(*) AS txns,
       SUM(f.is_fraud) AS fraud_txns,
       ROUND(SUM(f.is_fraud) / COUNT(*) * 100, 2) AS fraud_rate_pct
FROM fact_transaction f
JOIN dim_card k ON k.card_key = f.card_key
GROUP BY k.state
HAVING COUNT(*) >= 1000
ORDER BY fraud_rate_pct DESC
FETCH FIRST 10 ROWS ONLY;

-- Q5. How well does each rule perform against the labelled fraud?  (precision / recall)
SELECT 'amount > 600' AS rule_name,
       SUM(sql_rule_amount) AS flagged,
       SUM(sql_rule_amount * is_fraud) AS caught,
       ROUND(SUM(sql_rule_amount * is_fraud) / SUM(sql_rule_amount) * 100, 1) AS precision_pct,
       ROUND(SUM(sql_rule_amount * is_fraud) / SUM(is_fraud) * 100, 1) AS recall_pct
FROM vw_txn_flagged
UNION ALL
SELECT 'velocity (3 in 30 min)',
       SUM(sql_rule_velocity), SUM(sql_rule_velocity * is_fraud),
       ROUND(SUM(sql_rule_velocity * is_fraud) / SUM(sql_rule_velocity) * 100, 1),
       ROUND(SUM(sql_rule_velocity * is_fraud) / SUM(is_fraud) * 100, 1)
FROM vw_txn_flagged
UNION ALL
SELECT 'night and amt > 300',
       SUM(sql_rule_night), SUM(sql_rule_night * is_fraud),
       ROUND(SUM(sql_rule_night * is_fraud) / SUM(sql_rule_night) * 100, 1),
       ROUND(SUM(sql_rule_night * is_fraud) / SUM(is_fraud) * 100, 1)
FROM vw_txn_flagged
UNION ALL
SELECT '2 or more rules (final)',
       SUM(CASE WHEN sql_flag_count >= 2 THEN 1 ELSE 0 END),
       SUM(CASE WHEN sql_flag_count >= 2 THEN is_fraud ELSE 0 END),
       ROUND(SUM(CASE WHEN sql_flag_count >= 2 THEN is_fraud ELSE 0 END)
             / SUM(CASE WHEN sql_flag_count >= 2 THEN 1 ELSE 0 END) * 100, 1),
       ROUND(SUM(CASE WHEN sql_flag_count >= 2 THEN is_fraud ELSE 0 END) / SUM(is_fraud) * 100, 1)
FROM vw_txn_flagged;

-- Q6. Which 10 cards lost the most to fraud?  (JOIN, GROUP BY, CASE; card shown as last 4 digits)
-- SQLITE: replace FETCH FIRST 10 ROWS ONLY with LIMIT 10; SUBSTR(TO_CHAR(x), -4) works as SUBSTR(CAST(x AS TEXT), -4)
SELECT SUBSTR(TO_CHAR(k.cc_num), -4) AS card_last4,
       k.state,
       COUNT(*) AS txns,
       SUM(f.is_fraud) AS fraud_txns,
       ROUND(SUM(CASE WHEN f.is_fraud = 1 THEN f.amt ELSE 0 END), 2) AS fraud_amount
FROM fact_transaction f
JOIN dim_card k ON k.card_key = f.card_key
GROUP BY k.cc_num, k.state
ORDER BY fraud_txns DESC, fraud_amount DESC
FETCH FIRST 10 ROWS ONLY;

-- Q7. Does a short gap since the card's previous transaction signal fraud?  (window function LAG, CASE, GROUP BY)
-- SQLITE: gap in minutes = (julianday(trans_time) - julianday(LAG(trans_time) OVER (...))) * 1440
WITH gaps AS (
    SELECT f.is_fraud,
           (CAST(f.trans_time AS DATE)
            - CAST(LAG(f.trans_time) OVER (PARTITION BY f.card_key ORDER BY f.trans_time) AS DATE)) * 1440 AS gap_min
    FROM fact_transaction f
)
SELECT CASE WHEN gap_min IS NULL THEN '1) First transaction of card'
            WHEN gap_min < 10 THEN '2) Under 10 min'
            WHEN gap_min < 60 THEN '3) 10 to 60 min'
            ELSE '4) Over 60 min' END AS gap_band,
       COUNT(*) AS txns,
       SUM(is_fraud) AS fraud_txns,
       ROUND(SUM(is_fraud) / COUNT(*) * 100, 2) AS fraud_rate_pct
FROM gaps
GROUP BY CASE WHEN gap_min IS NULL THEN '1) First transaction of card'
              WHEN gap_min < 10 THEN '2) Under 10 min'
              WHEN gap_min < 60 THEN '3) 10 to 60 min'
              ELSE '4) Over 60 min' END
ORDER BY gap_band;
