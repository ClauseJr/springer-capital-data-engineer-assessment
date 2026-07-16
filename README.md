# Referral Reward Validation Pipeline

## Overview

This project was completed as part of the Springer Capital Data Engineering Take-Home Assessment.

The objective was to build a data pipeline that profiles, cleans, integrates, and validates referral reward data using Python and Pandas. The solution implements business logic to determine whether each referral reward is valid or invalid and produces a final report containing 46 referral records.

The project also includes Docker containerization to ensure the pipeline can be executed consistently across different environments.

---

# Objectives

The project addresses the following requirements:

- Perform data profiling on all input datasets.
- Clean and standardize the data.
- Integrate multiple datasets into a single analytical dataset.
- Implement referral reward business rules.
- Identify invalid or potentially fraudulent referrals.
- Produce a final CSV report.
- Containerize the application using Docker.

---

# Dataset

Seven CSV files were provided.

| Dataset | Description |
|----------|-------------|
| user_referrals | Main referral information |
| user_referral_statuses | Lookup table for referral statuses |
| user_referral_logs | Reward processing logs |
| user_logs | User account information |
| referral_rewards | Reward definitions |
| paid_transactions | Payment transactions |
| lead_log | Marketing lead information |

---

# Project Structure

```
project/
│
├── data/
│   ├── user_referrals.csv
│   ├── user_referral_statuses.csv
│   ├── user_referral_logs.csv
│   ├── user_logs.csv
│   ├── referral_rewards.csv
│   ├── paid_transactions.csv
│   └── lead_log.csv
│
├── output/
│   ├── report.csv
│   └── report.csv
│
├── project_script.py
├── profiling.py
├── Dockerfile
├── requirements.txt
├── README.md
└── data_dictionary.xlsx
```

---

# Data Profiling

Before implementing any business logic, each dataset was profiled to understand its quality and structure.

The profiling included:

- Number of rows and columns
- Data types
- Missing values
- Duplicate records
- Distinct values
- Summary statistics
- Timestamp validation

Several timestamp columns were converted into UTC datetime format for accurate comparisons.

---

# Data Cleaning

The following preprocessing steps were performed.

## Datetime Conversion

Converted all timestamp columns using:

- referral_at
- updated_at
- transaction_at
- membership_expired_date
- created_at

---

## String Standardization

Leading and trailing spaces were removed from all string columns.

```
df[col] = df[col].str.strip()
```

This prevented mismatches during joins.

---

## Duplicate Check

Every dataset was checked for duplicate rows.
```
df[column].duplicated().sum()
```
No duplicate records were found.

---

## Missing Value Analysis

Missing values were investigated instead of automatically removed.

Examples include:

- Referral rewards not yet granted.
- Pending referrals without transactions.
- Lead referrals without referrer accounts.
- Reward logs without transaction IDs.

These missing values were treated as valid business scenarios where appropriate.

---

# Data Integration

The datasets were merged into a reporting table.

Relationships implemented:

1.

```
user_referrals
        ↓
user_referral_statuses
```

Status description lookup.

---

2.

```
user_referrals
        ↓
referral_rewards
```

Reward details.

---

3.

```
user_referrals
        ↓
paid_transactions
```

Payment information.

---

4.

```
user_referrals
        ↓
user_logs
```

Referrer details.

Initially this join produced:

```
248 rows
```

The issue was caused by duplicate user IDs in the user log table, creating a one-to-many relationship.

The solution was to deduplicate the user table before joining.

The final dataset correctly returned:

```
46 rows
```

---

5.

```
Lead referrals
        ↓
lead_log
```

Lead referrals were enriched with marketing source information.

The final implementation successfully matched:

```
8 out of 11
```

lead referrals.

---

6.

```
user_referrals
        ↓
user_referral_logs
```

Reward log information.

Only seven referrals had matching reward logs.

This was determined to be expected because the log table represents reward processing events rather than all referrals.

Therefore a LEFT JOIN was retained.

---

# Business Rules

The following business rules were implemented.

A reward is considered valid only if:

- Reward exists.
- Referral status is successful ("Berhasil").
- Transaction exists.
- Transaction status is PAID.
- Transaction type is NEW.
- Transaction occurred after referral.
- Transaction occurred within the same month.
- Membership was active.
- User account is active.
- Reward grant log exists.

Additional validation rules identify:

- Rewards issued without successful referrals.
- Rewards without transactions.
- Paid transactions without rewards.
- Successful referrals without rewards.
- Transactions occurring before referrals.

Each referral is assigned:

```
is_business_logic_valid
```

and where applicable:

```
validation_reason
```

---

# Output Report

The final report contains:

```
46 referral records
```

with the following information:

- Referral details
- Referrer details
- Referee details
- Transaction information
- Reward information
- Validation result

Output location:

```
output/report.csv
```

---

# Technologies

- Python 3.12
- Pandas
- NumPy
- PySpark
- Docker

---

# Docker

## Build

```bash
docker build -t referral-project .
```

---

## Run

```bash
docker run --rm -v "%cd%/output:/app/output" referral-project
```

The report is generated inside:

```
output/report.csv
```

outside the Docker container.

---

# Challenges Encountered

During implementation several issues were identified and resolved.

### String dtype migration

Pandas produced warnings regarding the new string dtype.

The script was updated to explicitly select both object and string columns.

---

### One-to-many joins

Joining `user_logs` initially expanded the dataset from 46 rows to 248 rows.

This was resolved by removing duplicate user IDs before performing the merge.

---

### Reward log mismatch

Only seven referrals matched reward logs.

Investigation showed that the reward log table stores reward events rather than every referral, making the LEFT JOIN the correct implementation.

---

### Lead mapping

Only eight of the eleven lead referrals matched entries in `lead_log`.

The remaining referrals had no corresponding lead record, which was treated as missing source information rather than invalid data.

---

### Business Rule Validation

No referral satisfied every business rule simultaneously because all reward log entries had:

```
is_reward_granted = False
```

This indicates that no reward had actually been granted in the supplied dataset.

---

# Assumptions

The following assumptions were made:

- Missing reward IDs indicate rewards have not yet been issued.
- Missing transaction IDs represent pending or failed referrals.
- Missing lead records indicate unavailable marketing information.
- LEFT JOINs preserve all referral records, even when related information is unavailable.

---

# Deliverables

The submission includes:

- project_script.py
- profiling.py
- Dockerfile
- requirements.txt
- README.md
- data_dictionary.xlsx
- output/profiling_report.csv
- output/report.csv
- data_dictionary.xlsx

---

# Credentials

This project does not require cloud storage.

No credentials, secrets, or API keys are stored within the source code.
