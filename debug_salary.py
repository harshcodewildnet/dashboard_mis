import pandas as pd
from dashboard.utils.file_loader import latest_cache_key
from dashboard.utils.config import load_config
import os

config = load_config()
excel_path, _ = latest_cache_key(config['excel_loader'])
print(f"Excel Path: {excel_path}")

# Check Transaction Dump
df_raw = pd.read_excel(excel_path, sheet_name='Transaction Dump', nrows=5)
print(f"Transaction Dump Raw Rows:\n{df_raw}")
print(f"Transaction Dump Columns: {df_raw.columns.tolist()}")

# Attempt to find date column
df = pd.read_excel(excel_path, sheet_name='Transaction Dump', skiprows=1)
print(f"Transaction Dump Columns (skiprows=1): {df.columns.tolist()}")

if 'date' in df.columns:
    max_date = pd.to_datetime(df['date']).max()
elif 'Date' in df.columns:
    max_date = pd.to_datetime(df['Date']).max()
    df.rename(columns={'Date': 'date'}, inplace=True)
else:
    # Look for any date-like column
    date_cols = [c for c in df.columns if 'date' in str(c).lower()]
    print(f"Potential date columns: {date_cols}")
    if date_cols:
        max_date = pd.to_datetime(df[date_cols[0]]).max()
        df.rename(columns={date_cols[0]: 'date'}, inplace=True)
    else:
        print("CRITICAL: No date column found!")
        max_date = pd.Timestamp.now()

print(f"Max date found: {max_date}")
current_year = max_date.year
print(f"Current Year Resolved: {current_year}")

# Check Salary List
s = pd.read_excel(excel_path, sheet_name='Salary List')
print(f"Salary List Rows: {len(s)}")
print(f"MonthKey head: {s['MonthKey'].head(2).tolist()}")

def parse_month_key(key):
    if not isinstance(key, str) or '_' not in key:
        return None, None
    mon_str, yr_str = key.split('_')
    # Mon_YY format
    month_map = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }
    m = month_map.get(mon_str)
    try:
        y = int("20" + yr_str)
    except:
        y = None
    return m, y

# Simulate metrics.py logic
month_map = {
    'Jan': 0, 'Feb': 1, 'Mar': 2, 'Apr': 3, 'May': 4, 'Jun': 5,
    'Jul': 6, 'Aug': 7, 'Sep': 8, 'Oct': 9, 'Nov': 10, 'Dec': 11
}

def parse_month_key_full(key):
    if not isinstance(key, str) or '_' not in key:
        return None
    mon = key.split('_')[0].strip()
    return month_map.get(mon)

s['m_idx'] = s['MonthKey'].apply(parse_month_key_full)
print(f"m_idx value counts:\n{s['m_idx'].value_counts()}")

# Filter to current year (2025)
s_2025 = s[s['MonthKey'].str.contains('_25', na=False)]
print(f"Rows for 2025: {len(s_2025)}")

emp_groups = s_2025.groupby(["Employee Name", "Emp ID"])
print(f"Employee groups: {len(emp_groups)}")

salary_total_months = [0.0] * 12
for (name, eid), group in emp_groups:
    emp_months = [0.0] * 12
    for _, row in group.iterrows():
        m_idx = row['m_idx']
        if m_idx is not None:
            amount = float(row.get('CTC', 0))
            emp_months[m_idx] += amount
            salary_total_months[m_idx] += amount

print(f"Simulated Total Salary: {sum(salary_total_months)}")
print(f"Monthly breakdown: {salary_total_months}")
