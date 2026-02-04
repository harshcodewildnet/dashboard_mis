# Quick Start Guide - Dashboard MIS

## ✅ Dashboard is Now Running!

The dashboard is currently accessible at: **http://localhost:8502**

## 📊 What's Been Implemented

Based on your mockup images, all required features have been implemented:

### 1. Home Page
- **Profit by Month (Current Month)** section showing:
  - Income card (clickable - navigates to Income page)
  - Expense card (clickable - navigates to Expense page)
  - Net Profit display
  
- **Graph of Current Month** showing:
  - Daily income, expense, and profit trends
  - Interactive visualization

- **Monthly Expenses Table** showing:
  - Last 3 months (Dec, Jan, Feb format)
  - Total expense amounts
  - Visual bar chart

### 2. Income Page
- **Table with columns:**
  - Header (Ledger name)
  - Amount (Current month)
  - Previous Month
  - Variance % (calculated from last month)
  
- **Additional Features:**
  - Top 10 income sources chart
  - Variance visualization
  - Distribution pie chart
  - Download CSV option

### 3. Expense Page
- **Table with columns:**
  - Header (Ledger name)
  - Amount (Current month)
  - Previous Month
  - Variance % (calculated from last month)
  
- **Additional Features:**
  - Top 10 expense categories chart
  - Variance visualization
  - Monthly trends for top 5 categories
  - Key insights (increasing/decreasing expenses)
  - Download CSV option

## 🚀 How to Use

### Starting the Dashboard
```bash
docker-compose up -d dashboard
```

### Stopping the Dashboard
```bash
docker-compose down
```

### Viewing Logs
```bash
docker logs dashboard_mis-dashboard-1
```

### Accessing the Dashboard
Open your browser to: http://localhost:8502

## 📁 Data Configuration

The dashboard is now configured to read from the local `data/` directory.

**Current data file:** `data/MIS_Report.xlsx` or `data/MIS_Report_2020-04-01_2025-12-31 (65).xlsx`

### To Update with Your Data:
1. Place your Excel file in the `data/` directory
2. File name should match pattern: `MIS_Report*.xlsx`
3. Ensure it has these columns:
   - Date
   - Ledger
   - Amount
   - Customer (optional)
   - Item (optional)

## 🔧 Configuration

Edit `dashboard/config.json` to customize:

### Revenue Keywords (for Income detection)
```json
"revenue_keywords": [
  "sales",
  "service income", 
  "revenue",
  "income"
]
```

### Expense Keywords (for Expense detection)
```json
"expense_keywords": [
  "expense",
  "cost",
  "rent",
  "salary",
  "utilities"
]
```

### Cash Ledgers (for Cash Balance calculation)
```json
"cash_ledgers": [
  "Cash Account",
  "HDFC Bank",
  "Axis Bank",
  "ICICI Bank",
  "SBI Account"
]
```

## 📱 Navigation

The dashboard has 5 main pages:
1. **Home** - Executive summary with clickable Income/Expense cards
2. **Sales Analysis** - Customer and item analysis
3. **Ledger Explorer** - Individual ledger statements
4. **Income Details** - Detailed income breakdown with variance
5. **Expense Details** - Detailed expense breakdown with variance

Click on Income/Expense cards from the Home page to navigate to detail pages!

## 🎨 Features Matching Your Mockup

✅ **Home Screen:**
- Profit by month → Current month section
- Income/Expense boxes → Colored clickable cards
- Graph of current month → Daily performance chart
- Monthly Expenses (Dec, Jan, Feb) → Last 3 months table

✅ **Expense Page:**
- Table with header, Amount, Variance % → Implemented with Previous Month column too
- Variance calculated by last month → ✅ Working

✅ **Income Page:**
- Table with header, Amount, Variance % → Implemented with Previous Month column too
- Variance calculated by last month → ✅ Working

## 📊 Additional Enhancements

Beyond the mockup, the dashboard also includes:
- 📈 Interactive charts (hover for details)
- 📥 Export to CSV functionality
- 🔄 Data refresh button
- 📊 Distribution pie charts
- 📉 Trend analysis
- 💡 Key insights and statistics
- 🎯 Quick stats sidebar
- 🌙 Dark theme
- ✨ Gradient colored cards
- 📱 Responsive layout

## ⚡ Performance Tips

- Dashboard auto-caches data for fast performance
- Click "Refresh Data" button to reload from Excel
- Data refreshes automatically when Excel file is modified

## 🐛 Troubleshooting

### Dashboard won't start?
```bash
docker-compose down
docker-compose build dashboard
docker-compose up -d dashboard
```

### Can't see data?
- Check Excel file exists in `data/` directory
- Verify column names (Date, Ledger, Amount)
- Check keywords in config.json match your ledger names

### Variance showing 0%?
- Need at least 2 months of data
- Current month is based on latest date in Excel

## 📞 Support

For detailed documentation, see: `DASHBOARD_SETUP.md`

---

**Status:** ✅ Dashboard is live and running!
**URL:** http://localhost:8502
**Data Source:** Local `data/` directory
