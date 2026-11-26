# ER diagram: how to draw it in draw.io (star schema)

1. Open draw.io and choose **Entity Relation** shapes (More Shapes > Entity Relation).
2. Put **fact_transaction** in the centre. Place the four dimensions around it: **dim_card** (top), **dim_merchant** (left), **dim_category** (right), **dim_date** (bottom).
3. List the columns inside each box and mark keys:
   - **dim_card**: card_key (PK), cc_num (unique), first_name, last_name, gender, dob, job, street, city, state, zip, latitude, longitude, city_pop
   - **dim_merchant**: merchant_key (PK), merchant_name (unique)
   - **dim_category**: category_key (PK), category_name (unique)
   - **dim_date**: date_key (PK, YYYYMMDD), full_date, year_num, month_num, day_num, day_name, is_weekend
   - **fact_transaction**: trans_num (PK), card_key (FK), merchant_key (FK), category_key (FK), date_key (FK), trans_time, trans_hour, amt, merch_latitude, merch_longitude, is_fraud, py_rule_amount, py_rule_velocity, py_rule_night, py_flag_count
4. Draw four relationship lines from the fact table to each dimension, with crow's foot (many) at the fact end and a single bar (one) at the dimension end.
5. Add a note: "CHECK constraints: amt > 0, is_fraud in (0,1), trans_hour 0-23."
6. Export as PNG (File > Export as > PNG) and add it to the report.

Oracle-specific notes: LONG is a reserved word (columns renamed to longitude); NUMBER and VARCHAR2 types; TO_DATE / TO_TIMESTAMP used when loading dates.
