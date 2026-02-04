# Frontend Dashboard Plan: Tally Financial Analytics

## 1. Architecture
We will use **Streamlit** (Python) for the frontend.
- **Why?** It's rapid, data-centric, and connects natively to our PostgreSQL database.
- **Deployment**: It will run as a separate Docker container (`dashboard`) in the same `docker-compose` network.

## 2. Tech Stack
- **Framework**: Streamlit
- **Database Driver**: `psycopg2-binary` or `sqlalchemy`
- **Visualization**: `plotly` (interactive charts) and `pandas` (data manipulation)

## 3. Dashboard Structure (Pages)

### A. Home (Executive Summary)
*Target Audience: CFO / Owner*
- **KPI Cards**:
    - Total Revenue (YTD / MTD)
    - Total Expenses (YTD / MTD)
    - Net Profit
    - Cash & Bank Balance (Real-time)
- **Trend Chart**: Monthly Revenue vs. Expenses (Line Chart)

### B. Sales Analysis
*Target Audience: Sales Manager*
- **Filters**: Date Range, Ledger Group (e.g., "Sales Accounts")
- **Charts**:
    - Top 10 Customers (Bar Chart)
    - Sales by Month (Bar Chart)
    - Sales by Item (if Inventory exists)

### C. Ledger Explorer (Data Drill-down)
*Target Audience: Accountant / Auditor*
- **Search**: Dropdown to select any Ledger (e.g., "HDFC Bank", "Rent").
- **Table**: View all transactions (`trn_voucher` + `trn_accounting`) for that ledger.
- **Feature**: "Statement of Accounts" view (Opening Balance + Debits - Credits = Closing).

## 4. Implementation Steps
1.  **Create Folder**: `dashboard/`
2.  **Dependencies**: Create `dashboard/requirements.txt` (`streamlit`, `pandas`, `psycopg2-binary`, `plotly`).
3.  **App Logic**: Create `dashboard/app.py` with database connection logic.
4.  **Dockerize**: Add `Dockerfile` for the dashboard.
5.  **Compose**: Update `docker-compose.yml` to include the `dashboard` service on port `8501`.

## 5. Future Enhancements (Post-MVP)
- **Alerts**: Highlight negative cash balances or overdue bills.
- **Export**: Download filtered data as Excel/CSV.
