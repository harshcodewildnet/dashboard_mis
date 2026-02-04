import pandas as pd
import os

filename = "Book1.xlsx"
file_path = os.path.join("data", filename)

try:
    # Use Header=1 (Row index 1, which corresponds to the 2nd row visually)
    df = pd.read_excel(file_path, sheet_name="Sheet1", header=1)
    
    print(f"--- FULL COLUMN LIST ({len(df.columns)} Columns) ---")
    for i, col in enumerate(df.columns):
        # Print index and name
        print(f"{i+1}. {col}")

except Exception as e:
    print(f"Error: {e}")
