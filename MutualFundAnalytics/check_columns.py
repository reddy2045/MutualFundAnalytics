import pandas as pd

files = [
    "data/raw/02_nav_history.csv",
    "data/raw/07_scheme_performance.csv",
    "data/raw/08_investor_transactions.csv"
]

for file in files:
    print("\n", file)
    df = pd.read_csv(file)
    print(df.columns)