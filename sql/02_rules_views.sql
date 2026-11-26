-- Rules in SQL (velocity uses a window function over the same card)
CREATE OR REPLACE VIEW vw_txn_rules AS
SELECT f.trans_num, f.card_key, f.trans_time, f.trans_hour, f.amt, f.is_fraud,
       f.py_rule_amount, f.py_rule_velocity, f.py_rule_night, f.py_flag_count,
       CASE WHEN f.amt > 600 THEN 1 ELSE 0 END AS sql_rule_amount,
       CASE WHEN COUNT(*) OVER (PARTITION BY f.card_key ORDER BY f.trans_time
                RANGE BETWEEN NUMTODSINTERVAL(1799, 'SECOND') PRECEDING AND CURRENT ROW) >= 3
            THEN 1 ELSE 0 END AS sql_rule_velocity,
       CASE WHEN f.trans_hour IN (22,23,0,1,2,3) AND f.amt > 300
            THEN 1 ELSE 0 END AS sql_rule_night
FROM fact_transaction f;

CREATE OR REPLACE VIEW vw_txn_flagged AS
SELECT r.*,
       (r.sql_rule_amount + r.sql_rule_velocity + r.sql_rule_night) AS sql_flag_count,
       CASE r.sql_rule_amount + r.sql_rule_velocity + r.sql_rule_night
            WHEN 0 THEN 'Clear' WHEN 1 THEN 'Low' WHEN 2 THEN 'Medium' ELSE 'High'
       END AS risk_tier
FROM vw_txn_rules r;

-- View for Power BI: fact + dimensions + flags
CREATE OR REPLACE VIEW vw_powerbi_txn AS
SELECT t.trans_num, t.trans_time, d.full_date, d.year_num, d.month_num, d.day_name,
       t.trans_hour, t.amt, t.is_fraud,
       c.category_name, m.merchant_name,
       k.state, k.city, k.gender, k.job,
       t.sql_rule_amount, t.sql_rule_velocity, t.sql_rule_night,
       t.sql_flag_count, t.risk_tier
FROM vw_txn_flagged t
JOIN fact_transaction f ON f.trans_num = t.trans_num
JOIN dim_date d     ON d.date_key = f.date_key
JOIN dim_category c ON c.category_key = f.category_key
JOIN dim_merchant m ON m.merchant_key = f.merchant_key
JOIN dim_card k     ON k.card_key = f.card_key;

-- RECONCILIATION: SQL vs Python counts (mismatches should be 0)
SELECT 'amount > 600' AS rule_name, SUM(sql_rule_amount) AS sql_count,
       SUM(py_rule_amount) AS py_count,
       SUM(ABS(sql_rule_amount - py_rule_amount)) AS mismatches
FROM vw_txn_rules
UNION ALL
SELECT 'velocity', SUM(sql_rule_velocity), SUM(py_rule_velocity),
       SUM(ABS(sql_rule_velocity - py_rule_velocity)) FROM vw_txn_rules
UNION ALL
SELECT 'night & amt > 300', SUM(sql_rule_night), SUM(py_rule_night),
       SUM(ABS(sql_rule_night - py_rule_night)) FROM vw_txn_rules
UNION ALL
SELECT '2 or more rules',
       SUM(CASE WHEN sql_flag_count >= 2 THEN 1 ELSE 0 END),
       SUM(CASE WHEN py_flag_count >= 2 THEN 1 ELSE 0 END),
       SUM(ABS(CASE WHEN sql_flag_count >= 2 THEN 1 ELSE 0 END
             - CASE WHEN py_flag_count >= 2 THEN 1 ELSE 0 END))
FROM vw_txn_flagged;

-- Precision and recall of the final rule (2 or more rules) in SQL
SELECT f.flagged, f.caught,
       ROUND(f.caught / f.flagged * 100, 1) AS precision_pct,
       ROUND(f.caught / t.total_fraud * 100, 1) AS recall_pct
FROM (SELECT COUNT(*) AS flagged, SUM(is_fraud) AS caught
      FROM vw_txn_flagged
      WHERE sql_flag_count >= 2) f,
     (SELECT SUM(is_fraud) AS total_fraud FROM fact_transaction) t;
-- Risk tiers
SELECT risk_tier, COUNT(*) AS txns, SUM(is_fraud) AS fraud,
       ROUND(SUM(is_fraud) / COUNT(*) * 100, 1) AS fraud_rate_pct
FROM vw_txn_flagged
GROUP BY risk_tier
ORDER BY fraud_rate_pct;
