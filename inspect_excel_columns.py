
import pandas as pd
import json

file_path = r"d:\Dashboard-MIS\dashboard_mis\data\MIS_Report_2020-04-01_2025-12-31 (76).xlsx"

try:
    # Read the first few rows to understand the structure
    df = pd.read_excel(file_path, nrows=5)
    columns = df.columns.tolist()
    
    # Also check unique values for potential cost center columns if we can identify them
    # Common names: Cost Center, Cost Centre, Department, CC, etc.
    
    info = {
        "columns": columns,
        "sample_data": df.head(3).to_dict(orient="records")
    }
    print(json.dumps(info, indent=2))
except Exception as e:
    print(f"Error: {e}")
