import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)

# Create date range for last 3 months
end_date = datetime(2026, 1, 22)  # Current date
start_date = end_date - timedelta(days=90)

# Generate dates
all_dates = []
for i in range(90):
    date = start_date + timedelta(days=i)
    # Create 3-8 transactions per day
    num_transactions = np.random.randint(3, 9)
    all_dates.extend([date] * num_transactions)

# Income ledgers
income_ledgers = [
    'Sales Revenue - Product A',
    'Sales Revenue - Product B', 
    'Service Income - Consulting',
    'Service Income - Support',
    'Other Income',
    'Interest Income'
]

# Expense ledgers
expense_ledgers = [
    'Rent Expense',
    'Salary Expense',
    'Utilities Expense',
    'Marketing Expense',
    'Office Supplies Expense',
    'Travel Expense',
    'Insurance Expense',
    'Depreciation Expense'
]

# Cash ledgers
cash_ledgers = [
    'Cash Account',
    'HDFC Bank',
    'Axis Bank',
    'ICICI Bank'
]

# Create transactions
transactions = []
for date in all_dates:
    # Decide if it's income or expense (70% income, 30% expense)
    is_income = np.random.random() < 0.7
    
    if is_income:
        ledger = np.random.choice(income_ledgers)
        amount = np.random.randint(5000, 100000)
        customer = f"Customer {np.random.randint(1, 30)}"
        item = f"Product {np.random.randint(1, 10)}"
    else:
        ledger = np.random.choice(expense_ledgers)
        amount = -np.random.randint(3000, 50000)
        customer = f"Vendor {np.random.randint(1, 20)}"
        item = ""
    
    transactions.append({
        'Date': date,
        'Ledger': ledger,
        'Amount': amount,
        'Customer': customer,
        'Item': item,
        'Voucher_Type': 'Sales' if is_income else 'Payment',
        'Description': f"Transaction on {date.strftime('%Y-%m-%d')}",
        'Reference': f"REF{np.random.randint(10000, 99999)}"
    })

# Create DataFrame
df = pd.DataFrame(transactions)

# Sort by date
df = df.sort_values('Date').reset_index(drop=True)

# Save to Excel
output_file = 'data/MIS_Report.xlsx'
df.to_excel(output_file, sheet_name='Transactions', index=False)

print(f"✅ Sample data created successfully!")
print(f"📁 File: {output_file}")
print(f"📊 Total transactions: {len(df)}")
print(f"📅 Date range: {df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}")
print(f"\n💰 Income ledgers: {len([t for t in transactions if t['Amount'] > 0])}")
print(f"💸 Expense ledgers: {len([t for t in transactions if t['Amount'] < 0])}")
