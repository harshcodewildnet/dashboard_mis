
import pandas as pd

file_path = "data/MIS_Report_2020-04-01_2025-12-31 (76).xlsx"

try:
    # Read the header row directly (row 1 based on previous findings)
    df = pd.read_excel(file_path, sheet_name='Transaction Dump', header=1, nrows=0)
    print("All columns in 'Transaction Dump':")
    for col in df.columns:
        print(f"- {col}")
        
except Exception as e:
    print(f"Error: {e}")
