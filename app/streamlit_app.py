import pandas as pd
import streamlit as st

st.set_page_config(page_title="Fraud Detection Dashboard", layout="wide")
st.title("Credit Card Fraud Detection Dashboard")


@st.cache_data
def load():
    cols = ["trans_time", "amt", "is_fraud", "category", "state", "trans_hour", "flag_count"]
    return pd.read_csv("data/flagged.csv", usecols=cols, parse_dates=["trans_time"])


df = load()

st.sidebar.header("Filters")
cats = st.sidebar.multiselect("Category", sorted(df["category"].unique()))
states = st.sidebar.multiselect("State", sorted(df["state"].unique()))
hours = st.sidebar.slider("Hour of day", 0, 23, (0, 23))
min_rules = st.sidebar.selectbox("Flag a transaction when at least this many rules fire", [1, 2, 3], index=1)

f = df[df["trans_hour"].between(*hours)]
if cats:
    f = f[f["category"].isin(cats)]
if states:
    f = f[f["state"].isin(states)]

total = len(f)
fraud = int(f["is_fraud"].sum())
flagged = f["flag_count"] >= min_rules
caught = int((flagged & (f["is_fraud"] == 1)).sum())
precision = caught / flagged.sum() * 100 if flagged.sum() else 0
recall = caught / fraud * 100 if fraud else 0

k1, k2, k3, k4 = st.columns(4)
k1.metric("Transactions", f"{total:,}")
k2.metric("Fraud cases", f"{fraud:,}", f"{fraud / total * 100:.2f}% of transactions" if total else None)
k3.metric("Precision", f"{precision:.1f}%")
k4.metric("Recall", f"{recall:.1f}%")

c1, c2 = st.columns(2)
with c1:
    st.subheader("Fraud rate by category (%)")
    if total:
        st.bar_chart(f.groupby("category")["is_fraud"].mean().mul(100).sort_values())
with c2:
    st.subheader("Fraud rate by hour (%)")
    if total:
        st.bar_chart(f.groupby("trans_hour")["is_fraud"].mean().mul(100))

st.subheader("Fraud transactions per month")
if total:
    st.line_chart(f.groupby(f["trans_time"].dt.to_period("M").astype(str))["is_fraud"].sum())

st.caption("Data source: 'Credit Card Transactions Fraud Detection Dataset' (Kaggle, kartik2112), "
           "simulated transactions; sample of 500 cards. Rules: amount > 600, 3 transactions in 30 min, night and amount > 300.")
