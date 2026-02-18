
import pandas as pd
import sys

# Path to the data file inside the container
file_path = "data/MIS_Report_2020-04-01_2025-12-31 (76).xlsx"

print(f"Reading file: {file_path}")

try:
    # Read the first 20 rows without header to find where the column names are
    df_raw = pd.read_excel(file_path, sheet_name='Transaction Dump', header=None, nrows=20)
    
    header_row_idx = -1
    target_col_idx = -1
    target_col_name = "Alloc Parent template"
    
    print("\nScanning first 20 rows for header...")
    for i, row in df_raw.iterrows():
        # Convert row to string to search
        row_str = row.astype(str).tolist()
        # Check if target column is loosely in this row
        matches = [idx for idx, val in enumerate(row_str) if 'alloc' in val.lower() and 'parent' in val.lower()]
        
        if matches:
            header_row_idx = i
            target_col_idx = matches[0]
            print(f"Found header at row {i}")
            print(f"Target column found at index {target_col_idx}: {row_str[target_col_idx]}")
            # Print the whole row to see other columns
            print(f"Row {i} content: {row_str}")
            break
    
    if header_row_idx != -1:
        # Re-read with correct header
        print(f"\nRe-reading file with header at row {header_row_idx}...")
        df = pd.read_excel(file_path, sheet_name='Transaction Dump', header=header_row_idx)
        
        # Identify the column name from the dataframe columns
        cols = df.columns.tolist()
        possible_cols = [c for c in cols if 'alloc' in str(c).lower() and 'parent' in str(c).lower()]
        
        if possible_cols:
            col_name = possible_cols[0]
            print(f"\nUsing column: '{col_name}'")
            
            # Get unique values
            unique_vals = df[col_name].dropna().unique().tolist()
            print(f"\nFound {len(unique_vals)} unique cost centers:")
            for val in sorted(unique_vals):
                print(f"- {val}")
        else:
            print("\nCould not find column in DataFrame columns after re-reading.")
            print(f"Columns: {cols}")
            
    else:
        print("\nCould not find 'Alloc Parent template' in the first 20 rows.")
        print("First 5 rows for inspection:")
        print(df_raw.head().to_string())

except Exception as e:
    print(f"\nError: {e}")
    # Print traceback if needed
    import traceback
    traceback.print_exc()
