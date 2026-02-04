"""
Script to generate sample MIS data for testing the dashboard
"""
import pandas as pd
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
random.seed(42)

# Date range: Last 6 months
end_date = datetime(2026, 1, 22)
start_date = end_date - timedelta(days=180)
date_range = pd.date_range(start=start_date, end=end_date, freq='D')

# Define ledger categories
income_ledgers = [
    "Sales - Product A",
    "Sales - Product B", 
    "Sales - Product C",
    "Service Income",
    "Consulting Revenue",
    "License Revenue",
]

expense_ledgers = [
    "Salary Expense",
    "Rent Expense",
    "Utilities Expense",
    "Marketing Expense",
    "Travel Expense",
    "Office Supplies Expense",
    "Insurance Expense",
    "Maintenance Expense",
    "Software Subscriptions Expense",
    "Professional Fees Expense",
]

cash_ledgers = [
    "Cash Account",
    "HDFC Bank",
    "Axis Bank"
]

customers = [
    "ABC Corp",
    "XYZ Ltd",
    "Tech Solutions Inc",
    "Global Trading Co",
    "Prime Industries",
    "Smart Systems",
    "Digital Ventures",
    "Innovative Solutions"
]

items = [
    "Product A",
    "Product B",
    "Product C",
    "Service Package 1",
    "Service Package 2",
    "Consulting Hours",
    "License - Standard",
    "License - Premium"
]

# Generate transactions
transactions = []

for date in date_range:
    # Generate 2-5 income transactions per day
    num_income = random.randint(2, 5)
    for _ in range(num_income):
        ledger = random.choice(income_ledgers)
        customer = random.choice(customers)
        item = random.choice(items)
        
        # Base amount varies by ledger
        if "Product A" in ledger:
            base_amount = random.uniform(5000, 15000)
        elif "Product B" in ledger:
            base_amount = random.uniform(3000, 10000)
        elif "Service" in ledger:
            base_amount = random.uniform(8000, 25000)
        else:
            base_amount = random.uniform(2000, 12000)
        
        # Add some monthly variation
        month_factor = 1.0 + (date.month % 3) * 0.1  # Slight seasonal variation
        amount = base_amount * month_factor
        
        transactions.append({
            "date": date,
            "ledger": ledger,
            "customer": customer,
            "item": item,
            "amount": round(amount, 2),
            "expense_ledger_group": "Revenue"
        })
    
    # Generate 3-7 expense transactions per day
    num_expenses = random.randint(3, 7)
    for _ in range(num_expenses):
        ledger = random.choice(expense_ledgers)
        
        # Different expense patterns
        if "Salary" in ledger:
            # Monthly salary on 1st of month
            if date.day == 1:
                amount = -random.uniform(80000, 120000)
            else:
                continue  # No salary on other days
        elif "Rent" in ledger:
            # Monthly rent on 5th of month
            if date.day == 5:
                amount = -random.uniform(25000, 30000)
            else:
                continue
        elif "Utilities" in ledger:
            amount = -random.uniform(500, 2000)
        elif "Marketing" in ledger:
            amount = -random.uniform(1000, 8000)
        else:
            amount = -random.uniform(500, 5000)
        
        transactions.append({
            "date": date,
            "ledger": ledger,
            "customer": "",
            "item": "",
            "amount": round(amount, 2),
            "expense_ledger_group": "Operating Expenses"
        })
    
    # Generate cash transactions occasionally
    if random.random() > 0.7:
        cash_ledger = random.choice(cash_ledgers)
        transactions.append({
            "date": date,
            "ledger": cash_ledger,
            "customer": "",
            "item": "",
            "amount": round(random.uniform(-5000, 10000), 2),
            "expense_ledger_group": "Cash/Bank"
        })

# Create DataFrame
df = pd.DataFrame(transactions)

# Sort by date
df = df.sort_values("date")

# Save to Excel
output_file = "data/MIS_Report.xlsx"
df.to_excel(output_file, sheet_name="Transactions", index=False)

print(f"✅ Sample data generated successfully!")
print(f"📁 File saved to: {output_file}")
print(f"📊 Total transactions: {len(df)}")
print(f"📅 Date range: {df['date'].min().date()} to {df['date'].max().date()}")
print(f"\nIncome ledgers: {len(df[df['amount'] > 0])}")
print(f"Expense ledgers: {len(df[df['amount'] < 0])}")
print(f"\nTotal Income: ₹{df[df['amount'] > 0]['amount'].sum():,.2f}")
print(f"Total Expenses: ₹{abs(df[df['amount'] < 0]['amount'].sum()):,.2f}")
