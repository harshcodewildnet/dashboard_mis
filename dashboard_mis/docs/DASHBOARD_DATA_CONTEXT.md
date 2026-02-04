# Dashboard Data & Excel File Context
**Document Version**: 1.0  
**Last Updated**: January 2026  
**Purpose**: Complete data specification for Copilot-assisted dashboard development

---

## 1. Project Overview

### Business Context
- **System**: Tally Prime Financial Management System
- **Purpose**: Extract financial transactions to Excel and build an interactive Streamlit dashboard
- **Data Source**: Single transactional Excel file with standardized schema (MIS Report format)
- **Dashboard**: Multi-page Streamlit app with KPIs, Sales Analysis, and Ledger Explorer

### Key Files
- **Input**: Excel file from SMB share (`\\172.16.16.159\Users\Sane Alam\Documents\MIS_DATA\MIS_Report_New.xlsx`)
- **Output**: Streamlit dashboard (`dashboard/app.py`) + supporting modules
- **Database**: PostgreSQL (optional; dashboard can load Excel directly)

---

## 2. Excel File Structure & Schema

### File Characteristics
| Property | Value |
|----------|-------|
| Format | XLSX (Excel 2007+) |
| Sheet Name(s) | Typically **"Transactions"** or **"Report"** (varies) |
| Row Count | 10,000–100,000+ rows (depends on company size) |
| Encoding | UTF-8 |
| File Naming | `MIS_Report_*.xlsx` or `MIS_Report_New.xlsx` |
| Last Modified | Check file's modified timestamp to pick the latest |

### Required Columns
The primary sheet must contain these columns (case-insensitive, order flexible):

| Column Name | Data Type | Description | Example |
|---|---|---|---|
| **Date** | `DATETIME` or `DATE` | Transaction date in YYYY-MM-DD format | 2025-01-15 |
| **Amount** | `FLOAT` / `DECIMAL` | Debit/Credit amount (see sign convention below) | 50000.00 |
| **Ledger** | `STRING` | Ledger account name from Tally | "Sales - Product A", "HDFC Bank", "Rent Expense" |
| **Customer** | `STRING` | Customer/Vendor/Party name (optional, may be blank) | "ABC Corporation" |
| **Voucher Type** | `STRING` (optional) | Invoice, Payment, Journal, etc. | "Sales", "Payment", "Journal" |
| **Description** | `STRING` (optional) | Transaction notes or memo | "Monthly rental paid" |
| **Reference** | `STRING` (optional) | Cheque number, PO number, etc. | "CHQ-12345" |
| **Quantity** | `FLOAT` (optional) | Units (if item-based transaction) | 100 |
| **Item** | `STRING` (optional) | Product/Service name | "Widget A" |
| **Cost Centre** | `STRING` (optional) | Department/Project code | "Sales-North", "Admin" |

### Sign Convention for Amount
- **Positive (+)**: Credit (income, liabilities, equity increases)
- **Negative (-)**: Debit (expenses, assets increases, liabilities decreases)
- **Standard Accounting**: Debit = Asset/Expense, Credit = Liability/Income

*Adjust in code if your Excel uses opposite convention (e.g., separate Debit/Credit columns).*

### Sample Data
```
Date           | Amount    | Ledger                | Customer              | Voucher Type | Description
2025-01-15     | 50000.00  | Sales Account - A     | ABC Corporation       | Sales        | Monthly invoice
2025-01-15     | -50000.00 | HDFC Bank            | ABC Corporation       | Receipt      | Payment received
2025-01-16     | -5000.00  | Rent Expense         | Landlord Inc          | Payment      | Monthly rent
2025-01-16     | 5000.00   | Office Account       | Landlord Inc          | Payment      | Rent paid
```

---

## 3. Data Validation Rules

### Before Loading
1. **No Missing Date**: Every row must have a date
2. **No Null Ledger**: Ledger column cannot be blank
3. **Valid Amount**: Amount must be numeric (integer or decimal)
4. **Balanced Transactions**: For each transaction, debit total = credit total (optional check)
5. **Date Range**: Filter to relevant period (e.g., FY: April–March or Jan–Dec)

### Data Cleanup
- Trim whitespace from ledger and customer names
- Convert date strings to `datetime.date` or `pd.Timestamp`
- Replace `None` / `NaN` in optional columns with empty string
- Remove duplicate rows based on (Date, Ledger, Amount, Customer)

---

## 4. Derived Metrics & Calculations

### Home Page KPIs

#### 1. Total Revenue
```
Revenue = SUM(Amount WHERE Ledger LIKE 'Sales%')
```
- Filter transactions where ledger name contains "Sales"
- Sum all amounts (positive values)

#### 2. Total Expenses
```
Expenses = ABS(SUM(Amount WHERE Ledger LIKE '%Expense%' OR '%Cost%'))
```
- Filter transactions where ledger contains "Expense" or "Cost"
- Sum absolute values (convert negative to positive)

#### 3. Net Profit
```
Net Profit = Total Revenue - Total Expenses
```

#### 4. Cash/Bank Balance
```
Cash Balance = SUM(Amount WHERE Ledger IN ('Cash Account', 'HDFC Bank', 'Axis Bank', ...))
```
- **Note**: Requires mapping of which ledgers represent "cash" and "bank" accounts
- Store mapping in config or hardcode list of cash/bank ledger names

#### 5. Monthly Trend (Revenue vs Expenses)
```
GROUP BY MONTH(Date)
  Monthly Revenue = SUM(Amount WHERE Sales Ledger) per month
  Monthly Expenses = ABS(SUM(Amount WHERE Expense Ledger)) per month
```
- Plot as dual-axis line chart (Month on X, Revenue/Expense on Y)

### Sales Analysis KPIs

#### Top Customers by Revenue
```
GROUP BY Customer
  Customer Total = SUM(Amount WHERE Customer='X' AND Ledger LIKE 'Sales%')
SORT BY Total DESC
LIMIT 10
```
- Bar chart: Top 10 customers by total sales
- Filter by date range (from sidebar)

#### Sales by Month
```
GROUP BY MONTH(Date)
  Monthly Sales = SUM(Amount WHERE Ledger LIKE 'Sales%')
```
- Bar chart: Monthly sales trend

#### Sales by Item (if Item column exists)
```
GROUP BY Item
  Item Total = SUM(Quantity * Amount) or SUM(Amount)
```
- Bar chart: Top items by revenue or quantity

### Ledger Explorer

#### Opening Balance
```
Opening Balance = SUM(Amount WHERE Ledger='X' AND Date < Start Date)
```

#### Period Transactions
```
Period Amount = SUM(Amount WHERE Ledger='X' AND Date BETWEEN Start AND End)
```

#### Closing Balance
```
Closing Balance = Opening Balance + Period Amount
```

#### Statement Format
| Date | Description | Amount | Running Balance |
|---|---|---|---|
| 2025-01-01 | Opening | — | 10,000 |
| 2025-01-15 | Sale | 5,000 | 15,000 |
| 2025-01-20 | Expense | -2,000 | 13,000 |

---

## 5. Data Model Relationships

### Entity Relationships
```
[Excel File]
    ├── Transactions (rows)
    │   ├── Date (when)
    │   ├── Ledger (what account)
    │   ├── Amount (how much)
    │   ├── Customer (who)
    │   └── Optional: Voucher Type, Item, Cost Centre
    │
    ├── Ledger Master (derived)
    │   ├── Ledger Name
    │   ├── Ledger Group (Sales, Expense, Asset, etc.)
    │   └── Ledger Type (P&L or Balance Sheet)
    │
    └── Customer Master (derived)
        ├── Customer Name
        └── Total Transactions
```

### Grouping Logic

#### Ledger Groups (based on name patterns)
```python
LEDGER_GROUPS = {
    'Sales': ['Sales', 'Service Income', 'Revenue'],
    'Expense': ['Expense', 'Cost', 'Rent', 'Salary'],
    'Cash/Bank': ['Cash', 'Bank', 'HDFC', 'Axis'],
    'Receivables': ['Debtors', 'Receivable'],
    'Payables': ['Creditors', 'Payable'],
    'Fixed Assets': ['Asset', 'Equipment', 'Property'],
    'Other': []  # Default fallback
}
```

---

## 6. File Discovery & Loading Strategy

### Step 1: File Discovery
```python
import os
import pandas as pd
from pathlib import Path

# SMB Share path
SMB_SHARE = r"\\172.16.16.159\Users\Sane Alam\Documents\MIS_DATA"

# Find all Excel files
excel_files = [f for f in os.listdir(SMB_SHARE) if f.endswith('.xlsx')]

# Sort by modified time, pick the newest
latest_file = max(
    excel_files,
    key=lambda f: os.path.getmtime(os.path.join(SMB_SHARE, f))
)

file_path = os.path.join(SMB_SHARE, latest_file)
file_mtime = os.path.getmtime(file_path)
```

### Step 2: Load with openpyxl
```python
import openpyxl
import pandas as pd

# Load Excel file
wb = openpyxl.load_workbook(file_path)

# Get sheet name (try common names first)
sheet_name = None
for name in ['Transactions', 'Report', 'Data', 'Sheet1']:
    if name in wb.sheetnames:
        sheet_name = name
        break

if sheet_name is None:
    sheet_name = wb.sheetnames[0]  # Fallback to first sheet

# Read with pandas
df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
```

### Step 3: Cache Strategy
```python
# Cache by file modification time
CACHE = {}

def load_excel_cached(file_path):
    mtime = os.path.getmtime(file_path)
    cache_key = (file_path, mtime)
    
    if cache_key not in CACHE:
        df = pd.read_excel(file_path, engine='openpyxl')
        CACHE[cache_key] = df
    
    return CACHE[cache_key]
```

---

## 7. Column Name Standardization

The DataFrame may have column names with spaces, special characters, or inconsistent casing.

### Normalization Steps
```python
import re

def normalize_columns(df):
    """Normalize column names to snake_case."""
    df.columns = [
        re.sub(r'[\s\-]', '_', col.lower().strip())
        for col in df.columns
    ]
    return df

# Expected output
# 'Date' → 'date'
# 'Amount Paid' → 'amount_paid'
# 'Customer/Vendor' → 'customer_vendor'
```

### Column Mapping
```python
COLUMN_MAPPING = {
    'date': ['date', 'transaction_date', 'date_of_transaction'],
    'amount': ['amount', 'value', 'transaction_amount'],
    'ledger': ['ledger', 'account', 'account_name', 'ledger_name'],
    'customer': ['customer', 'vendor', 'party', 'customer_name'],
    'voucher_type': ['voucher_type', 'type', 'transaction_type'],
    'description': ['description', 'memo', 'notes'],
    'reference': ['reference', 'ref', 'cheque_number'],
    'quantity': ['quantity', 'qty', 'units'],
    'item': ['item', 'product', 'item_name'],
    'cost_centre': ['cost_centre', 'cost_center', 'department', 'project']
}

def find_column(df, key):
    """Find a column in df by aliases."""
    normalized_cols = {col.lower(): col for col in df.columns}
    for alias in COLUMN_MAPPING.get(key, []):
        if alias in normalized_cols:
            return normalized_cols[alias]
    return None
```

---

## 8. Streamlit Dashboard Structure

### File Organization
```
dashboard/
├── app.py                    # Main Streamlit app
├── requirements.txt          # Python dependencies
├── .streamlit/
│   └── config.toml          # Streamlit theme & config
├── utils/
│   ├── file_loader.py       # Excel file discovery & loading
│   ├── validations.py       # Data validation
│   ├── metrics.py           # KPI calculations
│   └── __init__.py
├── pages/
│   ├── 01_home.py           # Home/Executive Summary
│   ├── 02_sales.py          # Sales Analysis
│   ├── 03_ledger.py         # Ledger Explorer
│   └── __init__.py
└── .gitignore
```

### Dependencies (requirements.txt)
```
streamlit==1.40.0
pandas==2.2.0
openpyxl==3.11.0
plotly==5.18.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-dateutil==2.8.2
```

### App Structure (app.py)
```python
import streamlit as st
import pandas as pd
from utils.file_loader import load_latest_excel
from utils.metrics import calculate_kpis

# Page Config
st.set_page_config(page_title="Tally Finance Dashboard", layout="wide")

# Sidebar
st.sidebar.title("Tally Financial Dashboard")
page = st.sidebar.radio("Navigate", 
    ["Home", "Sales Analysis", "Ledger Explorer", "Settings"])

# Global Date Filter
start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date")

# Load Data
df = load_latest_excel()

# Render Pages
if page == "Home":
    # Display KPIs (Total Revenue, Expenses, Net Profit, Cash Balance)
    # Monthly trend chart
    pass
elif page == "Sales Analysis":
    # Top customers, sales by month, sales by item
    pass
elif page == "Ledger Explorer":
    # Ledger dropdown, transaction table, balance statement
    pass
```

---

## 9. Database Schema (Optional: For Future PostgreSQL Integration)

If migrating to PostgreSQL in the future:

### Main Tables
```sql
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    transaction_date DATE NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    ledger_name VARCHAR(255) NOT NULL,
    customer_name VARCHAR(255),
    voucher_type VARCHAR(50),
    description TEXT,
    reference VARCHAR(50),
    quantity NUMERIC,
    item_name VARCHAR(255),
    cost_centre VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE ledgers (
    ledger_id SERIAL PRIMARY KEY,
    ledger_name VARCHAR(255) UNIQUE NOT NULL,
    ledger_group VARCHAR(100),
    ledger_type VARCHAR(50)  -- 'P&L' or 'Balance Sheet'
);

CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(255) UNIQUE NOT NULL,
    total_transactions INT DEFAULT 0,
    last_transaction_date DATE
);

CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_ledger ON transactions(ledger_name);
CREATE INDEX idx_transactions_customer ON transactions(customer_name);
```

---

## 10. Configuration File (config.json)

```json
{
  "excel_loader": {
    "smb_share": "\\\\172.16.16.159\\Users\\Sane Alam\\Documents\\MIS_DATA",
    "file_pattern": "MIS_Report*.xlsx",
    "default_sheet": "Transactions",
    "fallback_sheets": ["Report", "Data", "Sheet1"]
  },
  "dashboard": {
    "app_title": "Tally Financial Dashboard",
    "layout": "wide",
    "port": 8501,
    "theme": "light"
  },
  "cash_ledgers": [
    "Cash Account",
    "HDFC Bank",
    "Axis Bank",
    "ICICI Bank",
    "SBI Account"
  ],
  "revenue_keywords": [
    "Sales",
    "Service Income",
    "Revenue",
    "Income"
  ],
  "expense_keywords": [
    "Expense",
    "Cost",
    "Rent",
    "Salary",
    "Utilities"
  ],
  "date_format": "YYYY-MM-DD",
  "currency": "INR",
  "currency_symbol": "₹"
}
```

---

## 11. Data Quality & Validation Checklist

### Pre-Load Validation
- [ ] File exists and is readable
- [ ] File is valid Excel format
- [ ] Sheet contains expected columns (Date, Amount, Ledger)
- [ ] No more than 1M rows (performance limit)

### Post-Load Validation
- [ ] All Date values parse correctly
- [ ] No NULL values in Ledger column
- [ ] Amount is numeric (no text values)
- [ ] Date range is within expected fiscal year
- [ ] Customer column has <5% NULL values
- [ ] Duplicate detection (same Date + Ledger + Amount)

### Warning Conditions
- [ ] More than 10% NULL in optional columns
- [ ] Negative revenue or positive expenses (possible sign reversal)
- [ ] Zero-amount transactions (10+ rows)
- [ ] Future-dated transactions (beyond today)

---

## 12. Example Filtering & Grouping Queries

### Query 1: Total Revenue by Month
```python
df_sales = df[df['ledger'].str.contains('Sales', case=False)]
revenue_by_month = df_sales.groupby(df_sales['date'].dt.to_period('M'))['amount'].sum()
```

### Query 2: Top 10 Customers
```python
top_customers = (
    df[df['ledger'].str.contains('Sales', case=False)]
    .groupby('customer')['amount']
    .sum()
    .nlargest(10)
)
```

### Query 3: Cash Balance Over Time
```python
cash_ledgers = ['Cash Account', 'HDFC Bank', 'Axis Bank']
cash_df = df[df['ledger'].isin(cash_ledgers)].sort_values('date')
cash_df['running_balance'] = cash_df['amount'].cumsum()
```

### Query 4: Ledger Statement (Opening + Period + Closing)
```python
ledger_name = "HDFC Bank"
ledger_df = df[df['ledger'] == ledger_name].sort_values('date')
opening_balance = ledger_df[ledger_df['date'] < start_date]['amount'].sum()
period_balance = ledger_df[(ledger_df['date'] >= start_date) & 
                           (ledger_df['date'] <= end_date)]['amount'].sum()
closing_balance = opening_balance + period_balance
```

---

## 13. UI/UX Notes for Copilot

### Home Page
- Use Streamlit `st.metric()` for KPI cards
- Color code: Green (Profit), Red (Loss), Blue (Balance)
- Display MTD and YTD side-by-side

### Sales Analysis
- Use Plotly `go.Bar()` and `go.Line()` for charts
- Add filters: Date Range, Ledger Group, Customer
- Export to CSV/Excel button

### Ledger Explorer
- Dropdown to select ledger (populated from distinct values)
- Table with pagination (show 50 rows per page)
- Add "Show Details" to expand transaction notes

### Settings Page (Optional)
- Allow manual date range override
- Cache refresh button
- Display file info (name, loaded date, row count)

---

## 14. Testing Data Sample

Use this sample data to validate dashboard logic:

```python
sample_data = {
    'date': ['2025-01-15', '2025-01-15', '2025-01-16', '2025-01-20'],
    'amount': [50000, -50000, -5000, 5000],
    'ledger': ['Sales - Product A', 'HDFC Bank', 'Rent Expense', 'Office Account'],
    'customer': ['ABC Corp', 'ABC Corp', 'Landlord Inc', 'Landlord Inc'],
    'voucher_type': ['Sales', 'Receipt', 'Payment', 'Payment'],
    'description': ['Monthly invoice', 'Payment received', 'Monthly rent', 'Rent paid']
}

df_test = pd.DataFrame(sample_data)
df_test['date'] = pd.to_datetime(df_test['date'])
```

---

## 15. Troubleshooting Guide

| Issue | Cause | Solution |
|---|---|---|
| "Sheet not found" | Excel sheet name differs | Update `default_sheet` in config.json |
| NaN in Amount column | Non-numeric data | Check Excel for text formulas |
| Zero revenue | Ledger name mismatch | Verify ledger names in Excel vs. config |
| Slow dashboard | Large file (>50MB) | Split Excel into monthly sheets |
| SMB share unreachable | Network issue | Use local copy or change `smb_share` path |

---

## 16. Deployment Checklist

- [ ] Excel file readable from SMB share
- [ ] All required Python packages installed
- [ ] `config.json` updated with correct paths
- [ ] Date range set to available data
- [ ] Ledger groups verified against actual ledger names
- [ ] KPI calculations tested with sample data
- [ ] Dashboard renders all 3 pages without error
- [ ] Charts are interactive (hover, zoom, export)
- [ ] Filters update data without lag
- [ ] Cache works (reload doesn't re-fetch Excel)

---

## 17. Future Enhancements

1. **Profitability Analysis**: P&L statement by department/project
2. **Alerts & Notifications**: Low cash balance warning
3. **Budget vs Actual**: Compare spending to budget
4. **Multi-Company**: Toggle between companies
5. **Export Reports**: Download P&L, Balance Sheet as PDF/Excel
6. **Audit Trail**: Track which reports were viewed and when
7. **Email Integration**: Schedule daily/weekly emails with KPIs
8. **Mobile App**: React Native or Flutter mobile dashboard

---

## Contact & Support
For questions about data schema, file format, or calculations, refer to:
- **Database Owner**: Refer to `COPILOT_CONTEXT.md` in `dashboard/mis_pipeline/`
- **Tally Extraction**: See `tally-export-config.yaml`
- **Sample Files**: `dashboard/mis_pipeline/sample_docs/`
