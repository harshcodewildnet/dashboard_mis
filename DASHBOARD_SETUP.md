# Dashboard MIS - Setup and Usage Guide

## Overview
This dashboard has been configured to work with local data instead of remote SMB share access. All pages match the mockup design requirements.

## Current Dashboard Structure

### Pages Implemented

1. **Home Page** (`pages/01_home.py`)
   - ✅ Profit by Month (Current Month)
   - ✅ Income and Expense cards (clickable to navigate to detail pages)
   - ✅ Graph of current month (daily income, expense, profit)
   - ✅ Monthly Expenses table (last 3 months: Dec, Jan, Feb)
   - ✅ Quick stats (Cash Balance, Total Revenue, Total Expenses, Net Profit)

2. **Sales Page** (`pages/02_sales.py`)
   - ✅ Total sales, unique customers, average ticket
   - ✅ Sales by month chart
   - ✅ Top customers and items visualization

3. **Ledger Page** (`pages/03_ledger.py`)
   - ✅ Ledger explorer with running balance
   - ✅ Transaction history and statements

4. **Income Page** (`pages/04_income.py`)
   - ✅ Table with Header (Ledger), Amount, Previous Month, and Variance %
   - ✅ Variance calculated by comparing current month with previous month
   - ✅ Top 10 income sources bar chart
   - ✅ Month-over-month variance visualization
   - ✅ Income distribution pie chart
   - ✅ Summary statistics
   - ✅ Download CSV option

5. **Expense Page** (`pages/05_expense.py`)
   - ✅ Table with Header (Ledger), Amount, Previous Month, and Variance %
   - ✅ Variance calculated by comparing current month with previous month
   - ✅ Top 10 expense categories bar chart
   - ✅ Month-over-month variance visualization
   - ✅ Expense distribution pie chart
   - ✅ Monthly expense trends for top 5 categories
   - ✅ Summary statistics
   - ✅ Key insights (increasing/decreasing expenses)

## Configuration Changes

### Updated `dashboard/config.json`
```json
{
  "excel_loader": {
    "smb_share": "c:/Users/Harsh Dhiman/Documents/Code/dashboard_mis/data",
    "file_pattern": "MIS_Report*.xlsx",
    "default_sheet": "Transactions",
    "fallback_sheets": ["Report", "Data", "Sheet1"]
  }
}
```

The path has been changed from `/data` (remote SMB) to the local `data/` directory.

## Running the Dashboard

### Option 1: Using Docker (Recommended)

1. **Start the dashboard:**
   ```bash
   docker-compose up dashboard
   ```

2. **Access the dashboard:**
   - Open browser to `http://localhost:8502`

3. **Stop the dashboard:**
   ```bash
   docker-compose down
   ```

### Option 2: Running Locally

1. **Install Python dependencies:**
   ```bash
   cd dashboard
   pip install -r requirements.txt
   ```

2. **Run Streamlit:**
   ```bash
   streamlit run app.py --server.port=8502
   ```

3. **Access the dashboard:**
   - Open browser to `http://localhost:8502`

## Data Requirements

### Excel File Structure
The dashboard expects an Excel file with the following columns:

**Required Columns:**
- `Date` - Transaction date
- `Ledger` - Account/Ledger name
- `Amount` - Transaction amount (positive for income, negative for expenses)

**Optional Columns:**
- `Customer` - Customer/Vendor name
- `Item` - Product/Service item
- `Voucher_Type` - Type of transaction
- `Description` - Transaction description
- `Reference` - Reference number

### Sample Data
A sample Excel file is located at: `data/MIS_Report.xlsx`

The file should contain transactions spanning at least 2-3 months to properly display variance calculations.

## Features by Page

### Home Page Features
1. **Current Month Summary**
   - Displays Income and Expense in colored cards
   - Shows Net Profit calculated as Income - Expense
   - Clickable cards navigate to detail pages

2. **Current Month Graph**
   - Daily breakdown showing Income, Expense, and Profit trends
   - Interactive Plotly chart with hover details

3. **Monthly Expenses Table**
   - Last 3 months of total expenses
   - Visual bar chart showing trend

4. **Quick Stats Sidebar**
   - Cash balance from configured cash ledgers
   - Overall totals for revenue and expenses
   - Net profit with percentage

### Income Detail Page Features
1. **Breakdown Table**
   - All income ledgers for current month
   - Previous month amounts
   - Variance percentage (Green = increase, Red = decrease)

2. **Visualizations**
   - Top 10 income sources (horizontal bar)
   - Variance comparison chart
   - Income distribution pie chart

3. **Summary Statistics**
   - Total number of income ledgers
   - Average per ledger
   - Highest income source
   - Average variance percentage

4. **Export**
   - Download detailed report as CSV

### Expense Detail Page Features
1. **Breakdown Table**
   - All expense ledgers for current month
   - Previous month amounts
   - Variance percentage (Red = increase, Green = decrease)

2. **Visualizations**
   - Top 10 expense categories (horizontal bar)
   - Variance comparison chart
   - Expense distribution pie chart
   - Monthly trend line chart for top 5 categories

3. **Key Insights**
   - Expenses with >10% increase
   - Expenses with >10% decrease

4. **Summary Statistics**
   - Total expense categories
   - Average per category
   - Highest expense
   - Average variance

## Configuration Keywords

Update these in `dashboard/config.json` to match your data:

### Revenue Keywords
```json
"revenue_keywords": [
  "sales",
  "service income",
  "revenue",
  "income"
]
```

### Expense Keywords
```json
"expense_keywords": [
  "expense",
  "cost",
  "rent",
  "salary",
  "utilities"
]
```

### Cash Ledgers
```json
"cash_ledgers": [
  "Cash Account",
  "HDFC Bank",
  "Axis Bank",
  "ICICI Bank",
  "SBI Account"
]
```

## Troubleshooting

### Issue: "Excel load failed"
- **Solution:** Check that the Excel file exists in the `data/` directory
- Verify the file pattern in `config.json` matches your file name

### Issue: "No rows after validation"
- **Solution:** Ensure your Excel has columns named `Date`, `Ledger`, and `Amount`
- Check that dates are in proper date format
- Verify amounts are numeric

### Issue: "No income/expense data"
- **Solution:** Update `revenue_keywords` and `expense_keywords` in config.json
- Make sure ledger names in your Excel contain these keywords

### Issue: Variance showing as 0%
- **Solution:** Ensure you have data for at least 2 consecutive months
- Current month is based on the latest date in your Excel file

## Next Steps

1. **Update Data**: Replace `data/MIS_Report.xlsx` with your actual MIS data
2. **Configure Keywords**: Update config.json with your actual ledger name patterns
3. **Test**: Run the dashboard and verify all pages load correctly
4. **Customize**: Adjust colors, themes, or add additional metrics as needed

## Additional Features

The dashboard also includes:
- Automatic data refresh button
- File metadata display (name, sheet, rows, last modified)
- Dark theme with professional color schemes
- Responsive layout for different screen sizes
- Navigation between pages

## Support

For issues or questions:
1. Check the terminal/console output for error messages
2. Verify Excel file structure matches requirements
3. Review config.json settings
4. Check that all dependencies are installed
