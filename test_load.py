import sys
from pathlib import Path
sys.path.insert(0, '/app')
from dashboard.utils.file_loader import load_latest_excel
from dashboard.utils.config import load_config

config = load_config(Path('/app/dashboard/config.json'))
df, meta = load_latest_excel(config['excel_loader'])

print(f"Loaded {meta['rows']} rows from sheet: {meta['sheet']}")
print(f"Columns: {list(df.columns)}")
print(f"Has primary_group: {'primary_group' in df.columns}")

if 'primary_group' in df.columns:
    print(f"\nUnique Primary Groups:")
    print(df['primary_group'].value_counts())
