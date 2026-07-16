import pandas as pd

# Load the CSV files into DataFrames
tables = {
    "user_referrals": pd.read_csv("data/user_referrals.csv"),
    "user_referral_statuses": pd.read_csv("data/user_referral_statuses.csv"),
    "user_referral_logs": pd.read_csv("data/user_referral_logs.csv"),
    "user_logs": pd.read_csv("data/user_logs.csv"),
    "referral_rewards": pd.read_csv("data/referral_rewards.csv"),
    "paid_transactions": pd.read_csv("data/paid_transactions.csv"),
    "lead_log": pd.read_csv("data/lead_log.csv"),
}

# ============================================================
# Data Profiling
# - Check data types
# - Check duplicates
# - Check missing values
# ============================================================
"""
# Perform profiling for each table

for table_name, df in tables.items():

    print("=" * 80)
    print(f"TABLE: {table_name.upper()}")
    print("=" * 80)

    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")

    print("\nColumn Names")
    print(df.columns.tolist())

    print("\nData Types")
    print(df.dtypes)

    print("\nInfo")
    df.info()

    print("\nNull Count")
    print(df.isnull().sum())

    print("\nNull Percentage")
    print((df.isnull().sum() / len(df) * 100).round(2))

    print("\nDistinct Values")
    print(df.nunique())

    print("\nDuplicate Rows")
    print(df.duplicated().sum())

    print("\nSummary Statistics")
    print(df.describe(include="all"))

    print("\nFirst Five Rows")
    print(df.head())

    print("\n")
"""

profile_report = []

for table_name, df in tables.items():

    for column in df.columns:

        profile_report.append({
            "Table": table_name,
            "Column": column,
            "Data Type": str(df[column].dtype),
            "Null Count": df[column].isnull().sum(),
            "Percent Populated": round((1 - df[column].isnull().mean()) * 100, 2),
            "Distinct Values": df[column].nunique(),
            "Duplicate Values": df[column].duplicated().sum(),
            "Minimum Value" : df[column].dropna().min(),
            "Maximum Value" : df[column].dropna().max(),
            "Max String Length" : df[column].astype(str).str.len().max(),
            "Sample Value": (
                df[column].dropna().iloc[0]
                if not df[column].dropna().empty
                else None
            )
        })

profile_df = pd.DataFrame(profile_report)

profile_df.to_csv(
    "output/profiling_report.csv",
    index=False
)
print("Profiling report created successfully.")
print("Saved to: output/profiling_report.csv")
