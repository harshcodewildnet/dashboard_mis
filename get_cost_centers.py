
import pandas as pd
import sys

file_path = "data/MIS_Report_2020-04-01_2025-12-31 (76).xlsx"

try:
    df = pd.read_excel(file_path, nrows=10)
    print("Columns in file:")
    print(df.columns.tolist())
    
    # Check if 'Alloc Parent template' is in columns or if there's a typo
    target_col = "Alloc Parent template"
    if target_col in df.columns:
        # Get unique values from the whole file for this column
        full_df = pd.read_excel(file_path, usecols=[target_col])
        unique_values = full_df[target_col].dropna().unique().tolist()
        print("\nUnique values in 'Alloc Parent template':")
        for val in unique_values:
            print(f"- {val}")
    else:
        print(f"\nTarget column '{target_col}' not found.")
        # Try fuzzy match
        matches = [c for c in df.columns if 'alloc' in str(c).lower()]
        if matches:
            print(f"Similar columns found: {matches}")
except Exception as e:
    print(f"Error: {e}")
