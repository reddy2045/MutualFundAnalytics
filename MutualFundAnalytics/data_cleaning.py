import pandas as pd

# ==========================
# 1. Clean nav_history.csv
# ==========================

nav = pd.read_csv("data/raw/02_nav_history.csv")

nav["date"] = pd.to_datetime(nav["date"])

nav = nav.sort_values(["amfi_code", "date"])

nav["nav"] = nav.groupby("amfi_code")["nav"].ffill()

nav = nav.drop_duplicates()

nav = nav[nav["nav"] > 0]

nav.to_csv(
    "data/processed/nav_history_clean.csv",
    index=False
)

print("nav_history cleaned")


# ==================================
# 2. Clean investor_transactions.csv
# ==================================

txn = pd.read_csv(
    "data/raw/08_investor_transactions.csv"
)

txn["transaction_type"] = (
    txn["transaction_type"]
    .str.strip()
    .str.upper()
)

txn["transaction_type"] = txn[
    "transaction_type"
].replace({
    "LUMP SUM": "LUMPSUM",
    "SIP": "SIP",
    "REDEMPTION": "REDEMPTION"
})

txn = txn[txn["amount_inr"] > 0]

txn["transaction_date"] = pd.to_datetime(
    txn["transaction_date"]
)

txn.to_csv(
    "data/processed/investor_transactions_clean.csv",
    index=False
)

print("investor_transactions cleaned")


# ==================================
# 3. Clean scheme_performance.csv
# ==================================

perf = pd.read_csv(
    "data/raw/07_scheme_performance.csv"
)

perf["return_1yr_pct"] = pd.to_numeric(
    perf["return_1yr_pct"],
    errors="coerce"
)

perf["return_3yr_pct"] = pd.to_numeric(
    perf["return_3yr_pct"],
    errors="coerce"
)

perf["return_5yr_pct"] = pd.to_numeric(
    perf["return_5yr_pct"],
    errors="coerce"
)

anomalies = perf[
    (perf["expense_ratio_pct"] < 0.1)
    |
    (perf["expense_ratio_pct"] > 2.5)
]

print("\nExpense Ratio Anomalies")
print(anomalies.shape)

perf.to_csv(
    "data/processed/scheme_performance_clean.csv",
    index=False
)

print("scheme_performance cleaned")