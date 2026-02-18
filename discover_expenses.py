import pandas as pd
import os

file_path = 'd:/Dashboard-MIS/dashboard_mis/data/MIS_Report_2020-04-01_2025-12-31 (76).xlsx'
if not os.path.exists(file_path):
    print("File not found")
    exit()

df = pd.read_excel(file_path, sheet_name='Transaction Dump', skiprows=1)

print("--- Column Search for 'Salary' and Synonyms ---")
synonyms = ['salary', 'wage', 'remun', 'staff', 'stipend', 'payout', 'employee']
for col in df.columns:
    unique_vals = df[col].dropna().unique()
    matches = [str(v) for v in unique_vals if any(s in str(v).lower() for s in synonyms)]
    if matches:
        print(f"Column '{col}' matches: {matches}")

print("\n--- Column Search for 'Direct Expenses' ---")
for col in df.columns:
    unique_vals = df[col].dropna().unique()
    matches = [str(v) for v in unique_vals if 'direct expense' in str(v).lower()]
    if matches:
        print(f"Column '{col}' matches: {matches}")

print("\n--- Top 10 Ledger Groups ---")
print(df.groupby('Expenses Ledger Group')['Amount'].sum().sort_values().head(10))

print("\n--- Top 10 Primary Groups ---")
print(df.groupby('Primary Group')['Amount'].sum().sort_values().head(10))
