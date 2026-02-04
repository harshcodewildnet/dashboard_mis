import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# Generate dummy data
print("Generating dummy data...")

num_rows = 500
start_date = datetime.now() - timedelta(days=365)
dates = [start_date + timedelta(days=x) for x in range(num_rows)]

ledgers = ["Sales Account", "Purchase Account", "Office Expenses", "Rent", "Salary"]
customers = ["Customer A", "Customer B", "Customer C", "Vendor X", "Vendor Y"]

data = {
    "Date": dates,
    "Ledger": np.random.choice(ledgers, num_rows),
    "Amount": np.random.uniform(100, 10000, num_rows).round(2),
    "Voucher Type": np.random.choice(["Sales", "Purchase", "Payment", "Receipt"], num_rows),
    "Customer": np.random.choice(customers, num_rows),
    "Description": ["Dummy transaction"] * num_rows,
    "Reference": [f"REF-{i:04d}" for i in range(num_rows)]
}

df = pd.DataFrame(data)

# Save to Excel
output_path = "data/MIS_Dummy.xlsx"
df.to_excel(output_path, index=False)

print(f"Dummy data saved to {output_path}")
