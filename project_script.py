# ============================================================
# Referral Reward Validation Project
# Data Engineering Take-Home Test
# Author: Phabian Otieno
# ============================================================

# ============================================================
# Import Required Libraries
# ============================================================
import pandas as pd

# ============================================================
# Load Input CSV Files
# ============================================================
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
# Convert Date Columns to Datetime
# ============================================================

# user_referrals timestamp columns conversion to datetime
tables["user_referrals"]["referral_at"] = pd.to_datetime(
    tables["user_referrals"]["referral_at"],
    utc=True
)

tables["user_referrals"]["updated_at"] = pd.to_datetime(
    tables["user_referrals"]["updated_at"],
    utc=True
)

# user_referral_statuses timestamp columns conversion to datetime
tables["user_referral_statuses"]["created_at"] = pd.to_datetime(
    tables["user_referral_statuses"]["created_at"],
    utc=True
)

# user_referral_logs timestamp columns conversion to datetime
tables["user_referral_logs"]["created_at"] = pd.to_datetime(
    tables["user_referral_logs"]["created_at"],
    utc=True
)

# paid_transactions timestamp columns conversion to datetime
tables["paid_transactions"]["transaction_at"] = pd.to_datetime(
    tables["paid_transactions"]["transaction_at"],
    utc=True
)

# referral_rewards timestamp columns conversion to datetime
tables["referral_rewards"]["created_at"] = pd.to_datetime(
    tables["referral_rewards"]["created_at"],
    utc=True
)

# lead_log timestamp columns conversion to datetime
tables["lead_log"]["created_at"] = pd.to_datetime(
    tables["lead_log"]["created_at"],
    utc=True
)

tables["user_logs"]["membership_expired_date"] = pd.to_datetime(
    tables["user_logs"]["membership_expired_date"]
)

# Checking on the Data Types
for name, df in tables.items():
    print(f"\n{name}")
    print(df.dtypes)


# Removing any leading and existing spaces
for df in tables.values():
    string_cols = df.select_dtypes(include=["object", "str"]).columns

    for col in string_cols:
        df[col] = df[col].str.strip()

# Checking on the duplicated values
for name, df in tables.items():

    print(name)

    print(df.duplicated().sum())


# Starndadizing text columns
def initcap(text):
    if pd.isna(text):
        return text
    return str(text).title()

# Checking for Nulls
for name, df in tables.items():

    print(f"\n{name}")

    print(df.isnull().sum())

# Only columns that have nulls
for table_name, df in tables.items():
    nulls = df.isnull().sum()

    if nulls.sum() > 0:
        print(f"\n{table_name}")
        print(nulls[nulls > 0])

"""
user_referrals	referee_id	3 nulls
The referee may not have completed registration yet.

user_referrals	referee_name 3 nulls
Missing because the referee has not become a user yet.

user_referrals	referral_reward_id	38 nulls
Most referrals haven't earned a reward yet.

user_referrals	referrer_id	13 nulls
Some referrals originated from leads rather than existing users. We'll verify this later.

user_referrals	transaction_id	13 nulls
Pending or failed referrals may not have transactions.

user_referral_logs	source_transaction_id	79 nulls
Only some log records are linked to transactions.

"""

for name, df in tables.items():

    print(f"\n{name}")

    print(df.info())

# ============================================================
# Join Tables
# Create the analytical reporting dataset
# ============================================================

df = tables["user_referrals"].copy()
print("Start:", df.shape)

# 1. Status
df = df.merge(
    tables["user_referral_statuses"],
    left_on="user_referral_status_id",
    right_on="id",
    how="left"
)
print("After Status:", df.shape)

# 2. Rewards
df = df.merge(
    tables["referral_rewards"],
    left_on="referral_reward_id",
    right_on="id",
    how="left",
    suffixes=("", "_reward")
)
print("After Rewards:", df.shape)

# 3. Transactions
df = df.merge(
    tables["paid_transactions"],
    on="transaction_id",
    how="left"
)
print("After Transactions:", df.shape)

# 4. User Logs
# solving one to many
user_logs = (
    tables["user_logs"]
    .sort_values("membership_expired_date")
    .drop_duplicates(
        subset="user_id",
        keep="last"
    )
)
print(user_logs.shape)
print(user_logs["user_id"].nunique())

referrer = (
    tables["user_logs"]
    .sort_values("membership_expired_date")
    .drop_duplicates(
        subset="user_id",
        keep="last"
    )
)

df = df.merge(
    referrer,
    left_on="referrer_id",
    right_on="user_id",
    how="left",
    suffixes=("", "_referrer")
)
print("After User Logs:", df.shape)

# 5. Lead Logs

lead = tables["lead_log"].copy()

lead = (
    lead.sort_values("created_at")
        .drop_duplicates(subset="lead_id", keep="last")
)

df = df.merge(
    lead[["lead_id", "source_category"]],
    left_on="referee_id",
    right_on="lead_id",
    how="left"
)

print(df.shape)

df["referral_source_category"] = None

df.loc[
    df["referral_source"] == "User Sign Up",
    "referral_source_category"
] = "Online"

df.loc[
    df["referral_source"] == "Draft Transaction",
    "referral_source_category"
] = "Offline"

df.loc[
    df["referral_source"] == "Lead",
    "referral_source_category"
] = df["source_category"]

print(df[[
    "referral_source",
    "source_category",
    "referral_source_category"
]].head(15))

# 6. User Referral Logs
logs = (
    tables["user_referral_logs"]
    .sort_values("created_at")
    .drop_duplicates(
        subset="user_referral_id",
        keep="last"
    )
)
print(logs.shape)

# matches = set(logs["user_referral_id"]) & set(tables["user_referrals"]["referral_id"])
# Only 7 referrals have corresponding log records.

df = df.merge(
    logs,
    left_on="referral_id",
    right_on="user_referral_id",
    how="left",
    suffixes=("", "_log")
)

print(df.shape)


# ============================================================
#BUSINESS LOGIC VALIDATION
# ============================================================
# Business Rule 1
#
# A referral is valid only if:
# - reward exists
# - referral succeeded
# - payment exists
# - payment is PAID
# - payment is NEW
# - payment occurred after referral
# - payment happened in the same month
# - membership was active
# - account is active
# - reward grant was recorded
# ============================================================

df["is_business_logic_valid"] = None

# (Condition 1) 
reward_exists = (
    df["reward_value"]
    .str.extract(r"(\d+)")[0]
    .astype(float)
    .fillna(0)
    > 0
)



# (Condition 2)
status_success = df["description"] == "Berhasil"



# (Condition 3)
has_transaction = df["transaction_id"].notna()


# (Condition 4)
transaction_paid = df["transaction_status"] == "PAID"



# (Condition 5)
transaction_new = df["transaction_type"] == "NEW"


# (Condition 6)
transaction_after_referral = (
    df["transaction_at"] >= df["referral_at"]
)

# (Condition 7)
same_month = (
    (df["transaction_at"].dt.year == df["referral_at"].dt.year)
    &
    (df["transaction_at"].dt.month == df["referral_at"].dt.month)
)

# (Condition 8)
membership_valid = (
    df["membership_expired_date"] >= df["referral_at"].dt.tz_localize(None)
)

# (Condition 9)

account_active = (
    df["is_deleted"]
    .fillna(False)
    .eq(False)
)

# (Condition 10)
reward_granted = (
    df["is_reward_granted"]
    .fillna(False)
)


# combining & assigning values to condition
valid_condition_1 = (
    reward_exists
    & status_success
    & has_transaction
    & transaction_paid
    & transaction_new
    & transaction_after_referral
    & same_month
    & membership_valid
    & account_active
    & reward_granted
)

df.loc[valid_condition_1, "is_business_logic_valid"] = True

conditions = {
    "reward_exists": reward_exists,
    "status_success": status_success,
    "has_transaction": has_transaction,
    "transaction_paid": transaction_paid,
    "transaction_new": transaction_new,
    "transaction_after_referral": transaction_after_referral,
    "same_month": same_month,
    "membership_valid": membership_valid,
    "account_active": account_active,
    "reward_granted": reward_granted,
}

for name, cond in conditions.items():
    print(f"{name}:")
    print("Type:", type(cond))
    print("Shape:", getattr(cond, "shape", "No shape"))
    print("-" * 50)


print(type(valid_condition_1))
print(valid_condition_1.shape)
print(valid_condition_1.dtype)



# Rule 2 — Valid Reward (Pending or Failed)
valid_condition_2 = (
    df["description"].isin(["Menunggu", "Tidak Berhasil"])
    &
    df["reward_value"].isna()
)

df.loc[valid_condition_2, "is_business_logic_valid"] = True

# Invalid Rule 1
invalid_condition_1 = (
    reward_exists
    &
    (df["description"] != "Berhasil")
)

df.loc[invalid_condition_1, "is_business_logic_valid"] = False

# Invalid Rule 2
invalid_condition_2 = (
    reward_exists
    &
    df["transaction_id"].isna()
)

df.loc[invalid_condition_2, "is_business_logic_valid"] = False

# Invalid Rule 3
invalid_condition_3 = (
    (~reward_exists)
    &
    has_transaction
    &
    transaction_paid
    &
    transaction_after_referral
)

df.loc[invalid_condition_3, "is_business_logic_valid"] = False

# Invalid Rule 4
invalid_condition_4 = (
    status_success
    &
    (~reward_exists)
)

df.loc[invalid_condition_4, "is_business_logic_valid"] = False

# Invalid Rule 5
invalid_condition_5 = (
    df["transaction_at"] < df["referral_at"]
)

df.loc[invalid_condition_5, "is_business_logic_valid"] = False

# 
df["is_business_logic_valid"] = (
    df["is_business_logic_valid"]
    .fillna(False)
    .astype(bool)
)
print(df.shape)
print(df["is_business_logic_valid"].value_counts(dropna=False))


reward_log_missing = (
    reward_exists
    &
    df["is_reward_granted"].fillna(False).eq(False)
)

df["validation_reason"] = ""

df.loc[
    reward_log_missing,
    "validation_reason"
] = "Reward grant log missing or reward not granted."


# 1. Business rule summary
print("\nBusiness Rule Summary")
print("-" * 40)

print("Valid Rule 1 :", valid_condition_1.sum())
print("Valid Rule 2 :", valid_condition_2.sum())
print("Invalid Rule 1:", invalid_condition_1.sum())
print("Invalid Rule 2:", invalid_condition_2.sum())
print("Invalid Rule 3:", invalid_condition_3.sum())
print("Invalid Rule 4:", invalid_condition_4.sum())
print("Invalid Rule 5:", invalid_condition_5.sum())

# 2. Validation reasons
df["validation_reason"] = ""

df.loc[
    invalid_condition_1 & (df["validation_reason"] == ""),
    "validation_reason"
] = "Reward exists but referral status is not Berhasil."

df.loc[
    invalid_condition_2 & (df["validation_reason"] == ""),
    "validation_reason"
] = "Reward exists but transaction ID is missing."

df.loc[
    invalid_condition_3 & (df["validation_reason"] == ""),
    "validation_reason"
] = "Paid transaction exists but reward is missing."

df.loc[
    invalid_condition_4 & (df["validation_reason"] == ""),
    "validation_reason"
] = "Referral marked Berhasil without reward."

df.loc[
    invalid_condition_5 & (df["validation_reason"] == ""),
    "validation_reason"
] = "Transaction occurred before referral."

df.loc[
    reward_log_missing & (df["validation_reason"] == ""),
    "validation_reason"
] = "Reward grant log missing or reward not granted."

# 3. Final validation
print("\nFinal Validation")
print(df["is_business_logic_valid"].value_counts())

# 4. Preview
print("\nValidation Preview")
print(df[[
    "referral_id",
    "description",
    "reward_value",
    "transaction_id",
    "is_business_logic_valid",
    "validation_reason"
]].head(10))


# OUTPUT

df["num_reward_days"] = (
    df["reward_value"]
    .str.extract(r"(\d+)")[0]
    .astype("Int64")
)

report = df.rename(columns={
    "description": "referral_status",
    "name": "referrer_name",
    "phone_number": "referrer_phone_number",
    "homeclub": "referrer_homeclub",
    "created_at_log": "reward_granted_at"
})

print(report.columns.tolist())

report.insert(
    0,
    "referral_details_id",
    range(1, len(report) + 1)
)

# selecting the required columns
report = report[
[
    "referral_details_id",
    "referral_id",
    "referral_source",
    "referral_source_category",
    "referral_at",
    "referrer_id",
    "referrer_name",
    "referrer_phone_number",
    "referrer_homeclub",
    "referee_id",
    "referee_name",
    "referee_phone",
    "referral_status",
    "num_reward_days",
    "transaction_id",
    "transaction_status",
    "transaction_at",
    "transaction_location",
    "transaction_type",
    "updated_at",
    "reward_granted_at",
    "is_business_logic_valid"
]
]

print(report.shape)

df.loc[
    df["referral_source"] == "Lead",
    [
        "referral_id",
        "referee_id",
        "lead_id",
        "source_category",
        "referral_source_category"
    ]
]
report = report.fillna({
    "referral_source_category": "Unknown",
    "referrer_name": "N/A",
    "referrer_phone_number": "N/A",
    "referrer_homeclub": "N/A",
    "transaction_status": "N/A",
    "transaction_location": "N/A",
    "transaction_type": "N/A",
    "num_reward_days": 0,
    "reward_granted_at": pd.NaT
})

print(report.shape)

print(report["referral_source"].value_counts())

print(report["referral_status"].value_counts())

print(report["is_business_logic_valid"].value_counts())

print(report.duplicated().sum())

report.to_csv(
    "output/report.csv",
    index=False
)
print("Report generated successfully!")