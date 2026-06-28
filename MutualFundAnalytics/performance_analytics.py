import pandas as pd

# Load cleaned NAV history
df = pd.read_csv("data/processed/nav_history_clean.csv")

# Convert date column to datetime
df["date"] = pd.to_datetime(df["date"])

# Sort by fund and date
df = df.sort_values(["amfi_code", "date"])

# Calculate Daily Return
df["daily_return"] = df.groupby("amfi_code")["nav"].pct_change()

# Save the output
df.to_csv("data/processed/daily_returns.csv", index=False)

# Display first 10 rows
print(df.head(10))

print("\nDaily Return calculation completed successfully!")
# =====================================
# STEP 2 : CAGR Calculation
# =====================================

print("\nCalculating CAGR...")

cagr_results = []

for fund, group in df.groupby("amfi_code"):

    group = group.sort_values("date")

    start_nav = group.iloc[0]["nav"]
    end_nav = group.iloc[-1]["nav"]

    years = (
        (group.iloc[-1]["date"] - group.iloc[0]["date"]).days
    ) / 365.25

    if years > 0:

        cagr = ((end_nav / start_nav) ** (1 / years) - 1) * 100

    else:

        cagr = None

    cagr_results.append([fund, start_nav, end_nav, years, cagr])

cagr_df = pd.DataFrame(
    cagr_results,
    columns=[
        "amfi_code",
        "start_nav",
        "end_nav",
        "years",
        "CAGR (%)"
    ]
)

print(cagr_df.head())

cagr_df.to_csv(
    "data/processed/cagr_results.csv",
    index=False
)

print("CAGR calculation completed successfully!")
# =====================================
# STEP 3 : Sharpe Ratio
# =====================================
print("\nCalculating Sharpe Ratio...")

risk_free_rate = 0.065  # 6.5% annual

sharpe_results = []

for fund, group in df.groupby("amfi_code"):

    returns = group["daily_return"].dropna()

    if len(returns) > 1:

        avg_return = returns.mean() * 252
        std_return = returns.std() * (252 ** 0.5)

        sharpe = (avg_return - risk_free_rate) / std_return

        sharpe_results.append([fund, sharpe])

sharpe_df = pd.DataFrame(
    sharpe_results,
    columns=["amfi_code", "Sharpe Ratio"]
)

print(sharpe_df.head())

sharpe_df.to_csv(
    "data/processed/sharpe_ratio.csv",
    index=False
)

print("Sharpe Ratio calculation completed successfully!")   
# =====================================
# STEP 4 : Sortino Ratio
# =====================================

print("\nCalculating Sortino Ratio...")

risk_free_rate = 0.065

sortino_results = []

for fund, group in df.groupby("amfi_code"):

    returns = group["daily_return"].dropna()

    downside_returns = returns[returns < 0]

    if len(downside_returns) > 1:

        avg_return = returns.mean() * 252

        downside_std = downside_returns.std() * (252 ** 0.5)

        sortino = (avg_return - risk_free_rate) / downside_std

        sortino_results.append([fund, sortino])

sortino_df = pd.DataFrame(
    sortino_results,
    columns=["amfi_code", "Sortino Ratio"]
)

print(sortino_df.head())

sortino_df.to_csv(
    "data/processed/sortino_ratio.csv",
    index=False
)

print("Sortino Ratio calculation completed successfully!")
# =====================================
# STEP 5 : Alpha & Beta
# =====================================

print("\nCalculating Alpha & Beta...")
from scipy.stats import linregress

benchmark = pd.read_csv("data/raw/10_benchmark_indices.csv")

benchmark = benchmark[benchmark["index_name"] == "NIFTY100"]

benchmark["date"] = pd.to_datetime(benchmark["date"])

benchmark = benchmark.sort_values("date")

benchmark["benchmark_return"] = benchmark["close_value"].pct_change()
alpha_beta_results = []
for fund in df["amfi_code"].unique():

    fund_df = df[df["amfi_code"] == fund].copy()

    merged = pd.merge(
        fund_df,
        benchmark[["date", "benchmark_return"]],
        on="date",
        how="inner"
    )

    merged = merged.dropna()

    if len(merged) < 30:
        continue

    slope, intercept, r, p, std = linregress(
        merged["benchmark_return"],
        merged["daily_return"]
    )

    beta = slope
    alpha = intercept * 252

    alpha_beta_results.append([fund, alpha, beta])
    alpha_beta_df = pd.DataFrame(
    alpha_beta_results,
    columns=["amfi_code", "Alpha", "Beta"]
)

print(alpha_beta_df.head())

alpha_beta_df.to_csv(
    "data/processed/alpha_beta.csv",
    index=False
)

print("Alpha & Beta calculation completed successfully!")
# =====================================
# STEP 6 : Maximum Drawdown
# =====================================

print("\nCalculating Maximum Drawdown...")

mdd_results = []

for fund, group in df.groupby("amfi_code"):

    group = group.sort_values("date").copy()

    # Running Maximum NAV
    group["running_max"] = group["nav"].cummax()

    # Drawdown
    group["drawdown"] = (
        group["nav"] / group["running_max"]
    ) - 1

    # Maximum Drawdown
    max_drawdown = group["drawdown"].min()

    mdd_results.append([fund, max_drawdown])

mdd_df = pd.DataFrame(
    mdd_results,
    columns=[
        "amfi_code",
        "Maximum Drawdown"
    ]
)

print(mdd_df.head())

mdd_df.to_csv(
    "data/processed/maximum_drawdown.csv",
    index=False
)

print("Maximum Drawdown calculation completed successfully!")
# =====================================
# STEP 7 : Fund Scorecard
# =====================================

print("\nCalculating Fund Scorecard...")

# Load required files
performance = pd.read_csv("data/processed/scheme_performance_clean.csv")
sharpe = pd.read_csv("data/processed/sharpe_ratio.csv")
alpha = pd.read_csv("data/processed/alpha_beta.csv")
mdd = pd.read_csv("data/processed/maximum_drawdown.csv")

# Merge all datasets
scorecard = performance.merge(sharpe, on="amfi_code")
scorecard = scorecard.merge(alpha, on="amfi_code")
scorecard = scorecard.merge(mdd, on="amfi_code")

# Ranking
scorecard["return_rank"] = scorecard["return_3yr_pct"].rank(ascending=False)
scorecard["sharpe_rank"] = scorecard["Sharpe Ratio"].rank(ascending=False)
scorecard["alpha_rank"] = scorecard["Alpha"].rank(ascending=False)
scorecard["expense_rank"] = scorecard["expense_ratio_pct"].rank(ascending=True)
scorecard["mdd_rank"] = scorecard["Maximum Drawdown"].rank(ascending=False)

# Final Score
scorecard["Fund Score"] = (
    scorecard["return_rank"] * 0.30 +
    scorecard["sharpe_rank"] * 0.25 +
    scorecard["alpha_rank"] * 0.20 +
    scorecard["expense_rank"] * 0.15 +
    scorecard["mdd_rank"] * 0.10
)

# Sort
scorecard = scorecard.sort_values("Fund Score")

# Save
scorecard.to_csv(
    "data/processed/fund_scorecard.csv",
    index=False
)

print(scorecard[
    ["scheme_name", "Fund Score"]
].head())

print("Fund Scorecard completed successfully!")

import matplotlib.pyplot as plt
# =====================================
# STEP 8 : Benchmark Comparison
# =====================================

print("\nCreating Benchmark Comparison Chart...")

# Load Benchmark Data
benchmark = pd.read_csv("data/raw/10_benchmark_indices.csv")

benchmark["date"] = pd.to_datetime(benchmark["date"])

# Separate NIFTY50 and NIFTY100
nifty50 = benchmark[benchmark["index_name"] == "NIFTY50"]
nifty100 = benchmark[benchmark["index_name"] == "NIFTY100"]

# Load Fund Scorecard
scorecard = pd.read_csv("data/processed/fund_scorecard.csv")

# Top 5 Funds
top5 = scorecard.nsmallest(5, "Fund Score")

plt.figure(figsize=(12,6))

# Plot Top 5 Funds
for fund in top5["amfi_code"]:

    fund_data = df[df["amfi_code"] == fund]

    plt.plot(
        fund_data["date"],
        fund_data["nav"],
        label=f"Fund {fund}"
    )

# Plot Benchmarks
plt.plot(
    nifty50["date"],
    nifty50["close_value"],
    label="NIFTY50",
    linewidth=2
)

plt.plot(
    nifty100["date"],
    nifty100["close_value"],
    label="NIFTY100",
    linewidth=2
)

plt.title("Top 5 Funds vs NIFTY50 & NIFTY100")
plt.xlabel("Date")
plt.ylabel("NAV / Index Value")
plt.legend()

plt.savefig("reports/benchmark_comparison.png")

plt.close()

print("Benchmark Comparison Chart Saved Successfully!")

print("\nCalculating Tracking Error...")

benchmark_returns = nifty100.copy()

benchmark_returns["benchmark_return"] = (
    benchmark_returns["close_value"].pct_change()
)

tracking = []

for fund in top5["amfi_code"]:

    fund = df[df["amfi_code"] == fund].copy()

    merged = pd.merge(
        fund,
        benchmark_returns[["date", "benchmark_return"]],
        on="date",
        how="inner"
    )

    merged = merged.dropna()

    tracking_error = (
        (merged["daily_return"] - merged["benchmark_return"]).std()
        * (252 ** 0.5)
    )

    tracking.append([fund["amfi_code"].iloc[0], tracking_error])

tracking_df = pd.DataFrame(
    tracking,
    columns=["amfi_code", "Tracking Error"]
)

tracking_df.to_csv(
    "data/processed/tracking_error.csv",
    index=False
)

print(tracking_df)

print("Tracking Error calculation completed successfully!")

