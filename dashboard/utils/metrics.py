from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd


@dataclass
class KpiResult:
    total_revenue: float
    total_expenses: float
    net_profit: float
    cash_balance: float


def _match_keywords(series: pd.Series, keywords: Iterable[str]) -> pd.Series:
    pattern = "|".join([kw.strip() for kw in keywords if kw.strip()])
    if not pattern:
        return series.notna() & False
    return series.str.contains(pattern, case=False, na=False)


def _get_filter_column(df: pd.DataFrame) -> str:
    """Determine which column to use for income/expense filtering"""
    # Prefer primary_group column if it exists
    if "primary_group" in df.columns:
        return "primary_group"
    return "ledger"


def calculate_kpis(df: pd.DataFrame, revenue_keywords: List[str], expense_keywords: List[str], cash_ledgers: List[str]) -> KpiResult:
    filter_col = _get_filter_column(df)
    filter_series = df[filter_col].astype(str)
    revenue_mask = _match_keywords(filter_series, revenue_keywords)
    expense_mask = _match_keywords(filter_series, expense_keywords)

    total_revenue = float(df.loc[revenue_mask, "amount"].sum())
    total_expenses = float(abs(df.loc[expense_mask, "amount"].sum()))
    net_profit = total_revenue - total_expenses
    cash_balance = float(df.loc[df["ledger"].isin(cash_ledgers), "amount"].sum())

    return KpiResult(
        total_revenue=total_revenue,
        total_expenses=total_expenses,
        net_profit=net_profit,
        cash_balance=cash_balance,
    )


def monthly_revenue_expense(df: pd.DataFrame, revenue_keywords: List[str], expense_keywords: List[str]) -> pd.DataFrame:
    filter_col = _get_filter_column(df)
    filter_series = df[filter_col].astype(str)
    revenue_mask = _match_keywords(filter_series, revenue_keywords)
    expense_mask = _match_keywords(filter_series, expense_keywords)

    df = df.assign(month=df["date"].dt.to_period("M").dt.to_timestamp())
    revenue = df.loc[revenue_mask].groupby("month")["amount"].sum()
    expenses = df.loc[expense_mask].groupby("month")["amount"].sum().abs()

    out = pd.DataFrame({"revenue": revenue, "expenses": expenses}).fillna(0.0).reset_index()
    return out


def top_customers(df: pd.DataFrame, revenue_keywords: List[str], limit: int = 10) -> pd.DataFrame:
    filter_col = _get_filter_column(df)
    filter_series = df[filter_col].astype(str)
    revenue_mask = _match_keywords(filter_series, revenue_keywords)
    grouped = df.loc[revenue_mask].groupby("customer")["amount"].sum()
    result = grouped.sort_values(ascending=False).head(limit).reset_index()
    result = result.rename(columns={"amount": "total"})
    return result


def sales_by_month(df: pd.DataFrame, revenue_keywords: List[str]) -> pd.DataFrame:
    filter_col = _get_filter_column(df)
    filter_series = df[filter_col].astype(str)
    revenue_mask = _match_keywords(filter_series, revenue_keywords)
    filtered = df.loc[revenue_mask].assign(month=df["date"].dt.to_period("M").dt.to_timestamp())
    grouped = filtered.groupby("month")["amount"].sum().reset_index()
    return grouped.rename(columns={"amount": "total"})


def sales_by_item(df: pd.DataFrame, revenue_keywords: List[str], limit: int = 10) -> pd.DataFrame:
    if "item" not in df.columns:
        return pd.DataFrame(columns=["item", "total"])
    ledger_series = df["ledger"].astype(str)
    revenue_mask = _match_keywords(ledger_series, revenue_keywords)
    grouped = df.loc[revenue_mask].groupby("item")["amount"].sum()
    result = grouped.sort_values(ascending=False).head(limit).reset_index()
    return result.rename(columns={"amount": "total"})


def ledger_statement(df: pd.DataFrame, ledger_name: str, start: date, end: date) -> Tuple[float, float, float, pd.DataFrame]:
    ledger_df = df.loc[df["ledger"] == ledger_name].sort_values("date")
    opening = float(ledger_df.loc[ledger_df["date"] < pd.Timestamp(start), "amount"].sum())
    period_df = ledger_df.loc[(ledger_df["date"] >= pd.Timestamp(start)) & (ledger_df["date"] <= pd.Timestamp(end))]
    period_total = float(period_df["amount"].sum())
    closing = opening + period_total

    statement = period_df.copy()
    if not statement.empty:
        statement["running_balance"] = statement["amount"].cumsum() + opening
    else:
        statement["running_balance"] = []
    return opening, period_total, closing, statement


def monthly_totals(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "date" not in df.columns:
        return pd.DataFrame()
    return (
        df.assign(month=df["date"].dt.to_period("M").dt.to_timestamp())
        .groupby("month")["amount"]
        .sum()
        .reset_index()
        .sort_values("month")
    )


def group_summary(df: pd.DataFrame, group_col: str, top_n: int = 10) -> pd.DataFrame:
    if df.empty or group_col not in df.columns:
        return pd.DataFrame(columns=[group_col, "total"])
    grouped = df.groupby(group_col)["amount"].sum().reset_index().rename(columns={"amount": "total"})
    return grouped.sort_values("total", ascending=False).head(top_n)


def top_ledgers(df: pd.DataFrame, limit: int = 15) -> pd.DataFrame:
    if df.empty or "ledger" not in df.columns:
        return pd.DataFrame(columns=["ledger", "total"])
    grouped = df.groupby("ledger")["amount"].sum().reset_index().rename(columns={"amount": "total"})
    return grouped.sort_values("total", ascending=False).head(limit)


def get_current_month_profit(df: pd.DataFrame, revenue_keywords: List[str], expense_keywords: List[str]) -> Tuple[float, float, float]:
    """Get current month's income, expense, and profit"""
    if df.empty:
        return 0.0, 0.0, 0.0
    
    current_month = df["date"].max().to_period("M")
    month_df = df[df["date"].dt.to_period("M") == current_month]
    
    filter_col = _get_filter_column(month_df)
    filter_series = month_df[filter_col].astype(str)
    revenue_mask = _match_keywords(filter_series, revenue_keywords)
    expense_mask = _match_keywords(filter_series, expense_keywords)
    
    income = float(month_df.loc[revenue_mask, "amount"].sum())
    expense = float(abs(month_df.loc[expense_mask, "amount"].sum()))
    profit = income - expense
    
    return income, expense, profit


def get_monthly_expenses_table(df: pd.DataFrame, expense_keywords: List[str], n_months: int = 3) -> pd.DataFrame:
    """Get last N months of total expenses"""
    if df.empty:
        return pd.DataFrame(columns=["month", "total_expense"])
    
    filter_col = _get_filter_column(df)
    filter_series = df[filter_col].astype(str)
    expense_mask = _match_keywords(filter_series, expense_keywords)
    expense_df = df.loc[expense_mask].copy()
    
    expense_df["month"] = expense_df["date"].dt.to_period("M").dt.to_timestamp()
    monthly = expense_df.groupby("month")["amount"].sum().abs().reset_index()
    monthly = monthly.rename(columns={"amount": "total_expense"})
    monthly = monthly.sort_values("month", ascending=False).head(n_months)
    
    return monthly.sort_values("month")


def get_income_detail_with_variance(df: pd.DataFrame, revenue_keywords: List[str]) -> pd.DataFrame:
    """Get income breakdown by ledger with month-over-month variance"""
    if df.empty:
        return pd.DataFrame(columns=["ledger", "current_amount", "previous_amount", "two_months_ago_amount", "variance_pct"])
    
    current_month = df["date"].max().to_period("M")
    previous_month = current_month - 1
    two_months_ago = current_month - 2
    
    filter_col = _get_filter_column(df)
    filter_series = df[filter_col].astype(str)
    revenue_mask = _match_keywords(filter_series, revenue_keywords)
    revenue_df = df.loc[revenue_mask].copy()
    revenue_df["month"] = revenue_df["date"].dt.to_period("M")
    
    current_data = revenue_df[revenue_df["month"] == current_month].groupby("ledger")["amount"].sum()
    previous_data = revenue_df[revenue_df["month"] == previous_month].groupby("ledger")["amount"].sum()
    two_months_ago_data = revenue_df[revenue_df["month"] == two_months_ago].groupby("ledger")["amount"].sum()
    
    result = pd.DataFrame({
        "ledger": current_data.index,
        "current_amount": current_data.values,
    })
    
    result["previous_amount"] = result["ledger"].map(previous_data).fillna(0)
    result["two_months_ago_amount"] = result["ledger"].map(two_months_ago_data).fillna(0)
    result["variance_pct"] = ((result["current_amount"] - result["previous_amount"]) / result["previous_amount"].replace(0, 1)) * 100
    result = result.sort_values("current_amount", ascending=False)
    
    return result


def get_expense_detail_with_variance(df: pd.DataFrame, expense_keywords: List[str]) -> pd.DataFrame:
    """Get expense breakdown by ledger with month-over-month variance"""
    if df.empty:
        return pd.DataFrame(columns=["ledger", "current_amount", "previous_amount", "two_months_ago_amount", "variance_pct"])
    
    current_month = df["date"].max().to_period("M")
    previous_month = current_month - 1
    two_months_ago = current_month - 2
    
    filter_col = _get_filter_column(df)
    filter_series = df[filter_col].astype(str)
    expense_mask = _match_keywords(filter_series, expense_keywords)
    expense_df = df.loc[expense_mask].copy()
    expense_df["month"] = expense_df["date"].dt.to_period("M")
    expense_df["amount"] = expense_df["amount"].abs()
    
    current_data = expense_df[expense_df["month"] == current_month].groupby("ledger")["amount"].sum()
    previous_data = expense_df[expense_df["month"] == previous_month].groupby("ledger")["amount"].sum()
    two_months_ago_data = expense_df[expense_df["month"] == two_months_ago].groupby("ledger")["amount"].sum()
    
    result = pd.DataFrame({
        "ledger": current_data.index,
        "current_amount": current_data.values,
    })
    
    result["previous_amount"] = result["ledger"].map(previous_data).fillna(0)
    result["two_months_ago_amount"] = result["ledger"].map(two_months_ago_data).fillna(0)
    result["variance_pct"] = ((result["current_amount"] - result["previous_amount"]) / result["previous_amount"].replace(0, 1)) * 100
    result = result.sort_values("current_amount", ascending=False)
    
    return result


def get_current_month_daily_profit(df: pd.DataFrame, revenue_keywords: List[str], expense_keywords: List[str]) -> pd.DataFrame:
    """Get daily profit data for current month"""
    if df.empty:
        return pd.DataFrame(columns=["date", "income", "expense", "profit"])
    
    current_month = df["date"].max().to_period("M")
    month_df = df[df["date"].dt.to_period("M") == current_month].copy()
    
    filter_col = _get_filter_column(month_df)
    filter_series = month_df[filter_col].astype(str)
    revenue_mask = _match_keywords(filter_series, revenue_keywords)
    expense_mask = _match_keywords(filter_series, expense_keywords)
    
    daily_income = month_df.loc[revenue_mask].groupby("date")["amount"].sum()
    daily_expense = month_df.loc[expense_mask].groupby("date")["amount"].sum().abs()
    
    result = pd.DataFrame({
        "date": daily_income.index.union(daily_expense.index),
    })
    result["income"] = result["date"].map(daily_income).fillna(0)
    result["expense"] = result["date"].map(daily_expense).fillna(0)
    result["profit"] = result["income"] - result["expense"]
    
    return result.sort_values("date")


def get_monthly_profit_by_cost_center(df: pd.DataFrame, revenue_keywords: List[str], expense_keywords: List[str]) -> pd.DataFrame:
    """Get monthly profit breakdown by cost center for current year.
    
    Returns a DataFrame with cost centers as rows and months as columns, showing profit for each combination.
    """
    if df.empty:
        return pd.DataFrame(columns=["cost_centre_parent"])
    
    # Filter to current year only
    current_year = df["date"].max().year
    df_current_year = df[df["date"].dt.year == current_year].copy()
    
    if df_current_year.empty:
        return pd.DataFrame(columns=["cost_centre_parent"])
    
    # Add month column
    df_current_year["month"] = df_current_year["date"].dt.to_period("M")
    
    # Get filter column
    filter_col = _get_filter_column(df_current_year)
    filter_series = df_current_year[filter_col].astype(str)
    
    # Separate income and expense data
    revenue_mask = _match_keywords(filter_series, revenue_keywords)
    expense_mask = _match_keywords(filter_series, expense_keywords)
    
    # Calculate income by cost center and month
    income_df = df_current_year.loc[revenue_mask].groupby(["cost_centre_parent", "month"])["amount"].sum()
    
    # Calculate expense by cost center and month
    expense_df = df_current_year.loc[expense_mask].groupby(["cost_centre_parent", "month"])["amount"].sum().abs()
    
    # Combine into a single DataFrame
    combined = pd.DataFrame({
        "income": income_df,
        "expense": expense_df
    }).fillna(0)
    
    # Calculate profit
    combined["profit"] = combined["income"] - combined["expense"]
    
    # Reset index to make cost_centre_parent and month regular columns
    combined = combined.reset_index()
    
    # Pivot to get cost centers as rows and months as columns
    pivot = combined.pivot(index="cost_centre_parent", columns="month", values="profit").fillna(0)
    
    # Add total column
    pivot["total"] = pivot.sum(axis=1)
    
    # Reset index to make cost_centre_parent a column
    result = pivot.reset_index()
    
    return result


def get_monthly_profit_by_client(df: pd.DataFrame, revenue_keywords: List[str], expense_keywords: List[str], sort_order: str = "desc") -> pd.DataFrame:
    """Get monthly profit breakdown by client (party name) for current year.
    
    Filters for clients (entities with non-zero income) to exclude pure vendors.
    Returns a DataFrame with client names as rows and months as columns.
    """
    if df.empty:
        return pd.DataFrame(columns=["name"])
    
    # Filter to current year only
    current_year = df["date"].max().year
    df_current_year = df[df["date"].dt.year == current_year].copy()
    
    if df_current_year.empty:
        return pd.DataFrame(columns=["name"])
    
    # Add month column
    df_current_year["month"] = df_current_year["date"].dt.to_period("M")
    
    # Ensure name column exists
    if "name" not in df_current_year.columns:
        return pd.DataFrame(columns=["name"])

    # Clean names: strip whitespace and handle NaN
    df_current_year["name"] = df_current_year["name"].fillna("Unknown").astype(str).str.strip()
    
    # Get filter column
    filter_col = _get_filter_column(df_current_year)
    filter_series = df_current_year[filter_col].astype(str)
    
    # Identify Income and Expense Rows
    revenue_mask = _match_keywords(filter_series, revenue_keywords)
    expense_mask = _match_keywords(filter_series, expense_keywords)
    
    # Calculate income by name and month
    income_series = df_current_year.loc[revenue_mask].groupby(["name", "month"])["amount"].sum()
    
    # Calculate expense by name and month (expenses are debits so convert to positive for subtraction logic)
    # Usually expenses are debits (positive in Tally if Dr/Cr logic? No, amount is signed?)
    # Wait, existing logic uses .abs() for expenses.
    expense_series = df_current_year.loc[expense_mask].groupby(["name", "month"])["amount"].sum().abs()
    
    # Combine dataframes
    # This aligns on (name, month) index
    combined = pd.DataFrame({
        "income": income_series,
        "expense": expense_series
    }).fillna(0)
    
    # Calculate profit
    combined["profit"] = combined["income"] - combined["expense"]
    
    # Reset index to access columns
    combined = combined.reset_index()
    
    # FILTER: Keep only Names that have ANY non-zero Total Income across the year
    # This distinguishes Clients (Income source) from Vendors (Expense destination)
    total_income_per_client = combined.groupby("name")["income"].sum()
    valid_clients = total_income_per_client[total_income_per_client != 0].index
    
    # Filter for valid clients
    filtered_combined = combined[combined["name"].isin(valid_clients)]
    
    if filtered_combined.empty:
         return pd.DataFrame(columns=["name"])

    # Pivot: Rows=Name, Cols=Month, Values=Profit
    pivot = filtered_combined.pivot(index="name", columns="month", values="profit").fillna(0)
    
    # Add total column
    pivot["total"] = pivot.sum(axis=1)
    
    # Sort by Total Profit descending
    pivot = pivot.sort_values("total", ascending=(sort_order == "asc"))
    
    return pivot.reset_index()
def get_hierarchical_expenses(
    df: pd.DataFrame, 
    excel_path: str,
    user_cost_centre_parent: Optional[str] = None,
    is_admin: bool = False
) -> List[Dict[str, Any]]:
    """Returns a hierarchical structure of expenses (Salary & Direct Expenses) with RBAC applied."""
    if df.empty:
        return []

    # Filter to current year
    current_year = df["date"].max().year
    df_current = df[df["date"].dt.year == current_year].copy()
    
    # helper for monthly array
    def get_monthly_array(grouped_series):
        arr = [0.0] * 12
        for month, val in grouped_series.items():
            if isinstance(month, (pd.Timestamp, datetime, date)):
                m_idx = month.month - 1
                if 0 <= m_idx < 12:
                    arr[m_idx] = float(abs(val))
        return arr

    # --- 1. Direct Expenses Branch ---
    direct_expenses_df = df_current[df_current["primary_group"] == "Direct Expenses"].copy()
    
    # Apply RBAC to Direct Expenses
    if not is_admin and user_cost_centre_parent:
        direct_expenses_df = direct_expenses_df[direct_expenses_df["cost_centre_parent"] == user_cost_centre_parent]

    direct_expenses_df["month"] = direct_expenses_df["date"].dt.to_period("M").dt.to_timestamp()
    
    direct_root_months = get_monthly_array(direct_expenses_df.groupby("month")["amount"].sum())
    direct_children = []

    # Level 1: Cost Centre Parent
    cc_parents = direct_expenses_df["cost_centre_parent"].dropna().unique()
    for cp in sorted(cc_parents):
        cp_df = direct_expenses_df[direct_expenses_df["cost_centre_parent"] == cp]
        cp_months = get_monthly_array(cp_df.groupby("month")["amount"].sum())
        cp_node = {
            "id": f"de_{cp}",
            "label": str(cp),
            "months": cp_months,
            "total": sum(cp_months),
            "children": []
        }
        
        # Level 2: Cost Centre
        ccs = cp_df["cost_centre"].dropna().unique()
        for cc in sorted(ccs):
            cc_df = cp_df[cp_df["cost_centre"] == cc]
            cc_months = get_monthly_array(cc_df.groupby("month")["amount"].sum())
            cc_node = {
                "id": f"de_{cp}_{cc}",
                "label": str(cc),
                "months": cc_months,
                "total": sum(cc_months),
                "children": []
            }
            
            # Level 3: Ledgers
            ledgers = cc_df["ledger"].dropna().unique()
            for led in sorted(ledgers):
                led_df = cc_df[cc_df["ledger"] == led]
                led_months = get_monthly_array(led_df.groupby("month")["amount"].sum())
                cc_node["children"].append({
                    "id": f"de_{cp}_{cc}_{led}",
                    "label": str(led),
                    "months": led_months,
                    "total": sum(led_months)
                })
            
            cp_node["children"].append(cc_node)
        direct_children.append(cp_node)

    direct_root = {
        "id": "direct_expenses_root",
        "label": "Direct Expenses",
        "months": direct_root_months,
        "total": sum(direct_root_months),
        "children": direct_children
    }

    # --- 2. Salary Branch ---
    salary_root = {
        "id": "salary_root",
        "label": "Salary",
        "months": [0.0] * 12,
        "total": 0.0,
        "children": []
    }

    try:
        # Load Salary List sheet
        salary_df = pd.read_excel(excel_path, sheet_name="Salary List")
        
        # Apply RBAC to Salary List
        if not is_admin and user_cost_centre_parent:
            salary_df = salary_df[salary_df["Alloc Parent Template"] == user_cost_centre_parent]

        # MonthKey mapping (Apr_24, May_24...)
        month_map = {
            'Jan': 0, 'Feb': 1, 'Mar': 2, 'Apr': 3, 'May': 4, 'Jun': 5,
            'Jul': 6, 'Aug': 7, 'Sep': 8, 'Oct': 9, 'Nov': 10, 'Dec': 11
        }
        
        def parse_month_year(key):
            if not isinstance(key, str) or '_' not in key:
                return None, None
            parts = key.split('_')
            mon = parts[0].strip()
            yr_str = parts[1].strip()
            try:
                yr = int("20" + yr_str)
            except:
                yr = None
            return month_map.get(mon), yr

        salary_df[["m_idx", "year"]] = salary_df["MonthKey"].apply(lambda x: pd.Series(parse_month_year(x)))
        
        # Filter salary to match current_year
        salary_df = salary_df[salary_df["year"] == current_year]
        
        if not salary_df.empty:
            # Aggregate by Employee
            emp_groups = salary_df.groupby(["Employee Name", "Emp ID"], dropna=False)
            
            salary_total_months = [0.0] * 12
            
            for (name, eid), group in emp_groups:
                if pd.isna(name) or pd.isna(eid):
                    continue
                
                emp_months = [0.0] * 12
                for _, row in group.iterrows():
                    m_idx = row["m_idx"]
                    if m_idx is not None and not pd.isna(m_idx):
                        amount = float(row.get("CTC", 0))
                        emp_months[int(m_idx)] += amount
                        salary_total_months[int(m_idx)] += amount
                
                salary_root["children"].append({
                    "id": f"sal_{eid}",
                    "label": str(name),
                    "empId": str(eid),
                    "months": emp_months,
                    "total": sum(emp_months),
                    "isSalary": True
                })
            
            # Sort children by total salary descending
            salary_root["children"].sort(key=lambda x: x["total"], reverse=True)
            
            salary_root["months"] = salary_total_months
            salary_root["total"] = sum(salary_total_months)
    except Exception as e:
        # Re-raise or log properly if needed
        import traceback
        print(f"Error processing Salary List: {e}")
        traceback.print_exc()

    return [salary_root, direct_root]

