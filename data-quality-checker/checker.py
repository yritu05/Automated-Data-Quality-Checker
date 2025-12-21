import pandas as pd
from db import load_table

def check_missing(df):
    missing = df.isnull().sum()
    return missing[missing > 0]

def check_duplicates(df):
    return df[df.duplicated()]

def check_schema(df, expected_columns):
    missing = [col for col in expected_columns if col not in df.columns]
    extra = [col for col in df.columns if col not in expected_columns]
    return missing, extra

def check_outliers(df, numeric_cols):
    outliers = {}
    for col in numeric_cols:
        q1, q3 = df[col].quantile([0.25, 0.75])
        iqr = q3 - q1
        lower, upper = q1 - 1.5*iqr, q3 + 1.5*iqr
        outliers[col] = df[(df[col] < lower) | (df[col] > upper)]
    return outliers

# MAIN
table = "assets"  # Example table
df = load_table(table)

print("\n=== Missing Values ===")
print(check_missing(df))

print("\n=== Duplicates ===")
print(check_duplicates(df))

print("\n=== Schema Check ===")
expected = ["asset_id", "asset_name", "asset_type", "status", "purchase_date", "warranty_expiry", "assigned_to", "cost"]
print(check_schema(df, expected))

print("\n=== Outliers ===")
numeric_cols = ["cost"]
print(check_outliers(df, numeric_cols))
