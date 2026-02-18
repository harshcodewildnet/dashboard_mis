
import pandas as pd

file_path = "data/MIS_Report_2020-04-01_2025-12-31 (76).xlsx"

try:
    # Read the first 20 rows to find the header row
    df_peek = pd.read_excel(file_path, nrows=20, header=None)
    header_row_index = -1
    for i, row in df_peek.iterrows():
        if any("Alloc Parent template" in str(cell) for cell in row):
            header_row_index = i
            print(f"Header row found at index: {header_row_index}")
            break
    
    if header_row_index != -1:
        # Re-read the file with the correct header
        df = pd.read_excel(file_path, header=header_row_index)
        target_col = "Alloc Parent template"
        if target_col in df.columns:
            unique_values = df[target_col].dropna().unique().tolist()
            print("\nUnique Cost Centers found:")
            for val in unique_values:
                print(f"- {val}")
        else:
            print(f"Target column '{target_col}' not found even after setting header.")
            print("Columns found at that row:", df.columns.tolist())
    else:
        print("Could not find 'Alloc Parent template' in the first 20 rows.")
        # Print the first few rows for debugging
        print("\nFirst 5 rows (no header):")
        print(df_peek.head(5).to_string())

except Exception as e:
    print(f"Error: {e}")
