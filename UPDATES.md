# Dashboard MIS - Updated UI

## Overview
This dashboard has been redesigned based on the provided wireframe specifications with enhanced visualizations and detailed analysis pages.

## New Features

### 🏠 Home Page (Updated)
The home page now features:
- **Profit by Month Section**: Displays current month's Income and Expense with clickable cards
- **Income Card**: Gradient purple card showing total income (links to Income Details page)
- **Expense Card**: Gradient pink card showing total expense (links to Expense Details page)
- **Net Profit Display**: Highlighted profit/loss for current month
- **Current Month Graph**: Daily performance chart showing Income, Expense, and Profit trends
- **Quick Stats Panel**: Cash Balance, Total Revenue, Total Expenses, and Net Profit metrics
- **Monthly Expenses Table**: Last 3 months of expense totals with trend visualization

### 📈 Income Details Page (NEW - Page 4)
Comprehensive income analysis with:
- **Total Income Header**: Large display showing current month's total income
- **Detailed Breakdown Table**: Ledger-wise income with columns:
  - Header (Ledger name)
  - Amount (Current month)
  - Previous Month
  - Variance % (month-over-month comparison)
- **Top 10 Income Sources**: Horizontal bar chart
- **Variance Analysis**: Visual comparison showing increases/decreases
- **Income Distribution**: Pie chart showing contribution of each source
- **Summary Statistics**: Total ledgers, average per ledger, highest source, average variance
- **Download Option**: Export income report as CSV

### 📉 Expense Details Page (NEW - Page 5)
Comprehensive expense analysis with:
- **Total Expense Header**: Large display showing current month's total expense
- **Detailed Breakdown Table**: Ledger-wise expenses with columns:
  - Header (Ledger name)
  - Amount (Current month)
  - Previous Month
  - Variance % (month-over-month comparison)
- **Top 10 Expense Categories**: Horizontal bar chart
- **Variance Analysis**: Visual comparison showing cost increases/decreases
- **Expense Distribution**: Pie chart showing expense allocation
- **Monthly Trends**: Line chart showing expense trends for top 5 categories over time
- **Summary Statistics**: Total categories, average per category, highest expense, average variance
- **Key Insights**: 
  - Significantly increased expenses (>10% variance)
  - Significantly decreased expenses (<10% variance)
- **Download Option**: Export expense report as CSV

## Technical Improvements

### New Utility Functions (metrics.py)
Added the following functions to support the new features:

1. `get_current_month_profit()` - Calculate current month's income, expense, and profit
2. `get_monthly_expenses_table()` - Get last N months of total expenses
3. `get_income_detail_with_variance()` - Income breakdown by ledger with MoM variance
4. `get_expense_detail_with_variance()` - Expense breakdown by ledger with MoM variance
5. `get_current_month_daily_profit()` - Daily profit data for current month graph

### UI Enhancements
- Modern gradient cards with shadow effects
- Color-coded metrics (green for positive, red for negative)
- Interactive charts with Plotly Dark theme
- Responsive column layouts
- Emoji icons for better visual hierarchy
- Clickable navigation between pages

## Installation & Setup

### 1. Generate Sample Data (for testing)
Since remote access is currently unavailable, you can ge nerate sample test data:

```powershell
python generate_sample_data.py
```

This will create `data/MIS_Report.xlsx` with 6 months of sample transactions.

### 2. Run the Dashboard

```powershell
cd dashboard
streamlit run app.py
```

The dashboard will be available at `http://localhost:8501`

## Page Structure

```
dashboard/
├── app.py                    # Main entry point
├── pages/
│   ├── 01_home.py           # Home page (UPDATED)
│   ├── 02_sales.py          # Sales analysis (existing)
│   ├── 03_ledger.py         # Ledger explorer (existing)
│   ├── 04_income.py         # Income details (NEW)
│   └── 05_expense.py        # Expense details (NEW)
└── utils/
    ├── metrics.py           # Calculation functions (UPDATED)
    ├── ui.py                # UI styling
    ├── config.py            # Configuration loader
    └── file_loader.py       # Excel file loader
```

## Configuration

The dashboard reads configuration from `dashboard/config.json`:

```json
{
  "revenue_keywords": ["sales", "service income", "revenue", "income"],
  "expense_keywords": ["expense", "cost", "rent", "salary", "utilities"],
  "cash_ledgers": ["Cash Account", "HDFC Bank", "Axis Bank", "ICICI Bank"]
}
```

You can customize these keywords to match your ledger naming conventions.

## Key Features by Wireframe

### ✅ Home Screen Requirements
- [x] Profit by month with current month display
- [x] Income and Expense as clickable sections
- [x] Graph of current month (daily profit/loss)
- [x] Monthly expenses table (last 3 months)

### ✅ Expense Page Requirements
- [x] Table with Header, Amount, Variance %
- [x] Variance calculated vs last month
- [x] Additional visualizations and insights

### ✅ Income Page Requirements
- [x] Table with Header, Amount, Variance %
- [x] Variance calculated vs last month
- [x] Additional visualizations and insights

## Additional Reports & Graphs

Beyond the wireframe requirements, the following have been added:

1. **Daily Performance Graph**: Shows income/expense/profit trends for current month
2. **Distribution Pie Charts**: Visual breakdown of income/expense sources
3. **Trend Analysis**: Monthly expense trends for top categories over time
4. **Variance Visualizations**: Color-coded bar charts showing MoM changes
5. **Key Insights Panel**: Automatically identifies significant changes
6. **Summary Statistics**: Quick metrics for each analysis page
7. **Download Options**: Export detailed reports as CSV files

## Data Requirements

The Excel file should have the following columns:
- `date`: Transaction date
- `ledger`: Ledger account name
- `amount`: Transaction amount (positive for income, negative for expenses)
- `customer`: Customer name (optional)
- `item`: Item/product name (optional)
- `expense_ledger_group`: Grouping for expenses (optional)

## Testing

Use the sample data generator to create test data:

```powershell
python generate_sample_data.py
```

This creates realistic transaction data with:
- 6 months of daily transactions
- Multiple income and expense ledgers
- Seasonal variations
- Month-over-month variance for testing

## Future Enhancements

Potential additions:
- Year-over-year comparisons
- Budget vs Actual analysis
- Forecasting & predictions
- Custom date range selection on detail pages
- Export to PDF reports
- Email report scheduling
- Advanced filtering options

## Support

For issues or questions, please check:
1. Ensure `data/MIS_Report.xlsx` exists and has the correct format
2. Verify all dependencies are installed: `pip install -r requirements.txt`
3. Check the console for error messages
4. Ensure Python 3.8+ is installed
