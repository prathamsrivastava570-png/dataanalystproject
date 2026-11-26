# Dataset description

**Source:** *Credit Card Transactions Fraud Detection Dataset*, Kaggle (author: kartik2112). Public dataset of **simulated** card transactions. File used: `fraudTrain.csv`.

| Item | Value |
|---|---|
| Original size | 1,296,675 rows, 23 columns, 983 cards |
| Sample used | All transactions of 500 randomly chosen cards (seed 42): 662,187 rows |
| Date range | 2019-01-01 to 2020-06-21 |
| Fraud rows | 3,771 (0.57%) |
| Missing values | None |
| Duplicates / invalid amounts | None found |

**Why sample by card:** the velocity rule needs every transaction of a card. A random sample of rows would break the 30-minute windows.

**Cleaning:** see `docs/data_quality_log.csv` (issue, rule applied, rows affected). No rows were removed.

**Limitations:** the data is simulated, so patterns are cleaner than in real fraud. Fraud is rare (0.57%), so precision and recall are used instead of accuracy.
