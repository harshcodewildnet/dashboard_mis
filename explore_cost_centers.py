import pandas as pd

# Read the Excel file
file_path = "data/MIS_Report_2020-04-01_2025-12-31 (76).xlsx"

try:
    # Try reading with header at row 3
    df = pd.read_excel(file_path, sheet_name='Transaction Dump', header=3)
    
    # Find the Alloc Parent template column
    alloc_cols = [c for c in df.columns if 'alloc' in str(c).lower() and 'parent' in str(c).lower()]
    
    if alloc_cols:
        col_name = alloc_cols[0]
        print(f"Column found: '{col_name}'")
        print(f"\nTotal unique cost centers: {df[col_name].nunique()}")
        print(f"\nTop 20 Cost Centers by transaction count:")
        print("=" * 60)
        value_counts = df[col_name].value_counts()
        for idx, (cost_center, count) in enumerate(value_counts.head(20).items(), 1):
            print(f"{idx:2}. {cost_center:40} ({count:,} transactions)")
        
        print(f"\n\nAll unique cost centers:")
        print("=" * 60)
        for idx, cc in enumerate(sorted(df[col_name].dropna().unique()), 1):
            print(f"{idx:2}. {cc}")
    else:
        print("Column 'Alloc Parent template' not found!")
        print(f"Available columns: {df.columns.tolist()}")
        
except Exception as e:
    print(f"Error: {e}")
