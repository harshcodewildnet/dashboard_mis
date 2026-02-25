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


def ledger_statement(
    df: pd.DataFrame, 
    ledger_name: Optional[str], 
    start: date, 
    end: date,
    cost_center: Optional[str] = None
) -> Tuple[float, float, float, pd.DataFrame]:
    """Calculate ledger statement with transactions and running balance."""
    if ledger_name:
        mask = df["ledger"] == ledger_name
    elif cost_center:
        mask = df["cost_centre"] == cost_center
    else:
        # Fallback to empty if neither provided
        mask = pd.Series(False, index=df.index)

    ledger_df = df.loc[mask].sort_values("date")
    
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


def get_ledger_monthly_summary(
    df: pd.DataFrame,
    cost_center: Optional[str] = None,
    ledger_name: Optional[str] = None,
    n_months: int = 6,
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Get n-month breakdown for all ledgers in a cost center, or for a specific ledger."""
    sub = df.copy()

    if ledger_name:
        sub = sub[sub["ledger"] == ledger_name]
    elif cost_center:
        sub = sub[sub["cost_centre"] == cost_center]

    if sub.empty:
        return [], []

    # Build n periods back from max date
    max_date = df["date"].max()
    cur_period = max_date.to_period("M")
    periods = [cur_period - i for i in range(n_months)]

    month_labels = [p.strftime("%b %Y") for p in periods]

    sub["_period"] = sub["date"].dt.to_period("M")
    sub = sub[sub["_period"].isin(periods)]

    # If filtering by ledger: return a single-row summary with month amounts
    if ledger_name:
        grouped = sub.groupby("_period")["amount"].sum()
        months = [float(abs(grouped.get(p, 0.0))) for p in periods]
        summary = [{
            "ledger": str(ledger_name),
            "months": months,
            "total": sum(months),
        }]
        return summary, month_labels

    # Else: one row per ledger under the cost center
    summary = []
    for ledger in sorted(sub["ledger"].dropna().unique()):
        led_df = sub[sub["ledger"] == ledger]
        grouped = led_df.groupby("_period")["amount"].sum()
        months = [float(abs(grouped.get(p, 0.0))) for p in periods]
        summary.append({
            "ledger": str(ledger),
            "months": months,
            "total": sum(months),
        })

    summary.sort(key=lambda x: x["total"], reverse=True)
    return summary, month_labels


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
    """Get monthly revenue breakdown by cost center parent and cost center for current year.
    
    Returns a DataFrame with [cost_centre_parent, cost_centre] as index and months as columns.
    """
    if df.empty:
        return pd.DataFrame(columns=["cost_centre_parent", "cost_centre"])
    
    # Filter to current year only
    current_year = df["date"].max().year
    df_current_year = df[df["date"].dt.year == current_year].copy()
    
    if df_current_year.empty:
        return pd.DataFrame(columns=["cost_centre_parent", "cost_centre"])
    
    # Add month column (format: YYYY-MM)
    df_current_year["month"] = df_current_year["date"].dt.strftime("%Y-%m")
    
    # Get filter column
    filter_col = _get_filter_column(df_current_year)
    filter_series = df_current_year[filter_col].astype(str)
    
    # Separate income and expense data
    revenue_mask = _match_keywords(filter_series, revenue_keywords)
    
    # Calculate income by cost center parent, sub cost center, and month
    # We group by both levels of hierarchy
    income_df = df_current_year.loc[revenue_mask].groupby(
        ["cost_centre_parent", "cost_centre", "month"]
    )["amount"].sum().reset_index()
    
    if income_df.empty:
        return pd.DataFrame(columns=["cost_centre_parent", "cost_centre"])

    # Pivot to get cost centers as rows and months as columns
    pivot = income_df.pivot(
        index=["cost_centre_parent", "cost_centre"], 
        columns="month", 
        values="amount"
    ).fillna(0)

    # Add total column
    pivot["total"] = pivot.sum(axis=1)

    # Reset index to return a regular DataFrame
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
    
    # Use income (revenue) only — don't subtract expense
    combined = income_series.rename("income").reset_index().fillna(0)

    # FILTER: Keep only Names that have ANY non-zero Total Income across the year
    # This distinguishes Clients (Income source) from Vendors (Expense destination)
    total_income_per_client = combined.groupby("name")["income"].sum()
    valid_clients = total_income_per_client[total_income_per_client != 0].index

    # Filter for valid clients
    filtered_combined = combined[combined["name"].isin(valid_clients)]

    if filtered_combined.empty:
        return pd.DataFrame(columns=["name"])

    # Pivot: Rows=Name, Cols=Month, Values=Revenue
    pivot = filtered_combined.pivot(index="name", columns="month", values="income").fillna(0)

    # Add total column
    pivot["total"] = pivot.sum(axis=1)

    # Sort by Total Revenue descending
    pivot = pivot.sort_values("total", ascending=(sort_order == "asc"))

    return pivot.reset_index()
def get_hierarchical_expenses_v2(
    df: pd.DataFrame,
    excel_path: str,
    user_cost_centre_parent: Optional[str] = None,
    is_admin: bool = False
) -> List[Dict[str, Any]]:
    """
    Returns the new 6-section expense breakdown for the Expense Page.
    Columns: 3 months (current, previous, prev-prev) instead of full 12.

    Sections:
      1. Direct Expenses    — Primary Group == "Direct Expenses"
      2. Outsource Vendor   — Expenses Ledger Group == "Outsource Vendor Payment"
      3. Salary             — Salary List, Remark != "Support Team", Expense Head != "Marketing"
      4. Overhead           — sub-sections:
            4a. Support Salary   — Salary List, Remark == "Support Team"
            4b. Marketing Salary — Salary List, Expense Head == "Marketing"
      5. Marketing Expenses — Expenses Ledger Group == "Marketing (Exp)"
    """
    if df.empty:
        return []

    # ── derive the 3 display months ──────────────────────────────────────
    max_date = df["date"].max()
    cur_period  = max_date.to_period("M")
    prev_period = cur_period - 1
    pp_period   = cur_period - 2
    periods = [cur_period, prev_period, pp_period]

    def months_for(series_by_period: "pd.Series") -> List[float]:
        """Return [cur, prev, pp] amounts given a Series indexed by Period."""
        out = []
        for p in periods:
            val = series_by_period.get(p, 0.0)
            out.append(float(abs(val)))
        return out

    def agg_3m(sub_df: pd.DataFrame, col: str = "amount") -> List[float]:
        """Group sub_df by month period and return 3 month values."""
        if sub_df.empty:
            return [0.0, 0.0, 0.0]
        sub_df = sub_df.copy()
        sub_df["_period"] = sub_df["date"].dt.to_period("M")
        grouped = sub_df.groupby("_period")[col].sum()
        return months_for(grouped)

    # ── RBAC helper ───────────────────────────────────────────────────────
    def rbac(sub_df: pd.DataFrame) -> pd.DataFrame:
        if not is_admin and user_cost_centre_parent and "cost_centre_parent" in sub_df.columns:
            return sub_df[sub_df["cost_centre_parent"] == user_cost_centre_parent]
        return sub_df

    # filter to 3-month window for main sheet sections
    df_3m = df[df["date"].dt.to_period("M").isin(periods)].copy()

    # SECTION 1 — Direct Expenses
    # ─────────────────────────────────────────────────────────────────────
    if "primary_group" in df_3m.columns:
        de_df = rbac(df_3m[df_3m["primary_group"] == "Direct Expenses"])
    else:
        de_df = pd.DataFrame(columns=df_3m.columns)

    de_root_months = agg_3m(de_df)
    de_children = []

    # Level 1: AllocParent Template
    # Level 2: Sub Cost Center (Cost Center)
    
    apt_col = "alloc_parent_template" if "alloc_parent_template" in de_df.columns else "cost_centre_parent"
    cc_col = "cost_centre" if "cost_centre" in de_df.columns else "cost_centre"

    for apt in sorted(de_df[apt_col].dropna().unique()):
        apt_df = de_df[de_df[apt_col] == apt]
        apt_months = agg_3m(apt_df)
        apt_node: Dict[str, Any] = {
            "id": f"de_apt_{apt}", "label": str(apt),
            "months": apt_months, "total": sum(apt_months), "children": []
        }
        for cc in sorted(apt_df[cc_col].dropna().unique()):
            cc_df = apt_df[apt_df[cc_col] == cc]
            cc_months = agg_3m(cc_df)
            cc_node: Dict[str, Any] = {
                "id": f"de_subcc_{apt}_{cc}", "label": str(cc),
                "months": cc_months, "total": sum(cc_months),
                "children": []
            }
            # Level 3: Ledger Name
            for led in sorted(cc_df["ledger"].dropna().unique()):
                led_df = cc_df[cc_df["ledger"] == led]
                led_months = agg_3m(led_df)
                cc_node["children"].append({
                    "id": f"de_ledger_{apt}_{cc}_{led}", 
                    "label": str(led),
                    "months": led_months, 
                    "total": sum(led_months),
                    "children": [] # Final level
                })
            apt_node["children"].append(cc_node)
        de_children.append(apt_node)

    direct_root: Dict[str, Any] = {
        "id": "direct_expenses_root", "label": "Direct Expenses",
        "sectionType": "direct",
        "months": de_root_months, "total": sum(de_root_months),
        "children": de_children
    }

    # ─────────────────────────────────────────────────────────────────────
    # SECTION 2 — Outsource Vendor Expense
    # ─────────────────────────────────────────────────────────────────────
    ov_col = "expense_ledger_group" if "expense_ledger_group" in df_3m.columns else None
    if ov_col is None:
        ov_df = pd.DataFrame(columns=df_3m.columns)
    else:
        ov_df = rbac(df_3m[df_3m[ov_col] == "Outsource Vendor Payment"])

    ov_root_months = agg_3m(ov_df)
    ov_children = []

    apt_col = "alloc_parent_template" if "alloc_parent_template" in ov_df.columns else "cost_centre_parent"
    cc_col = "cost_centre" if "cost_centre" in ov_df.columns else "cost_centre"

    for apt in sorted(ov_df[apt_col].dropna().unique()):
        apt_df = ov_df[ov_df[apt_col] == apt]
        apt_months = agg_3m(apt_df)
        apt_node = {
            "id": f"ov_apt_{apt}", "label": str(apt),
            "months": apt_months, "total": sum(apt_months), "children": []
        }
        for cc in sorted(apt_df[cc_col].dropna().unique()):
            cc_df = apt_df[apt_df[cc_col] == cc]
            cc_months = agg_3m(cc_df)
            cc_node = {
                "id": f"ov_subcc_{apt}_{cc}", "label": str(cc),
                "months": cc_months, "total": sum(cc_months), "children": []
            }
            for led in sorted(cc_df["ledger"].dropna().unique()):
                led_df = cc_df[cc_df["ledger"] == led]
                led_months = agg_3m(led_df)
                cc_node["children"].append({
                    "id": f"ov_ledger_{apt}_{cc}_{led}", "label": str(led),
                    "months": led_months, "total": sum(led_months),
                })
            apt_node["children"].append(cc_node)
        ov_children.append(apt_node)

    outsource_root: Dict[str, Any] = {
        "id": "outsource_vendor_root", "label": "Outsource Vendor Expense",
        "sectionType": "outsource_vendor_root",
        "months": ov_root_months, "total": sum(ov_root_months),
        "children": ov_children
    }


    # ─────────────────────────────────────────────────────────────────────
    # SECTION 3, 4a, 4b — Salary + Overhead (from Salary List sheet)
    # ─────────────────────────────────────────────────────────────────────
    salary_root: Dict[str, Any] = {
        "id": "salary_root", "label": "Salary",
        "sectionType": "salary",
        "months": [0.0, 0.0, 0.0], "total": 0.0, "children": []
    }
    support_salary_root: Dict[str, Any] = {
        "id": "support_salary_root", "label": "Support Salary",
        "sectionType": "support_salary",
        "months": [0.0, 0.0, 0.0], "total": 0.0, "children": []
    }
    mkt_salary_root: Dict[str, Any] = {
        "id": "mkt_salary_root", "label": "Marketing Salary",
        "sectionType": "marketing_salary",
        "months": [0.0, 0.0, 0.0], "total": 0.0, "children": []
    }

    try:
        month_map = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
        }

        def parse_month_key(key) -> Optional[pd.Period]:
            if not isinstance(key, str) or '_' not in key:
                return None
            parts = key.split('_')
            if len(parts) != 2:
                return None
            mon_str, yr_str = parts[0].strip(), parts[1].strip()
            month_num = month_map.get(mon_str)
            if month_num is None:
                return None
            try:
                year = int("20" + yr_str)
            except ValueError:
                return None
            return pd.Period(year=year, month=month_num, freq="M")

        sal_raw = pd.read_excel(excel_path, sheet_name="Salary List")

        # Apply RBAC
        if not is_admin and user_cost_centre_parent and "Alloc Parent Template" in sal_raw.columns:
            sal_raw = sal_raw[sal_raw["Alloc Parent Template"] == user_cost_centre_parent]

        # Parse period
        sal_raw["_period"] = sal_raw["MonthKey"].apply(parse_month_key)
        sal_raw = sal_raw[sal_raw["_period"].notna()]

        # Filter to 3 display months
        sal_3m = sal_raw[sal_raw["_period"].isin(periods)].copy()

        def sal_agg_3m_by_alloc(sub_sal: pd.DataFrame) -> List[float]:
            """Aggregate CTC by period for salary sub-dataframe."""
            if sub_sal.empty:
                return [0.0, 0.0, 0.0]
            grouped = sub_sal.groupby("_period")["CTC"].sum()
            return months_for(grouped)

        def build_salary_section(sub_sal: pd.DataFrame, id_prefix: str) -> List[Dict[str, Any]]:
            """Build cost-center rows for a salary sub-section."""
            rows = []
            if "Alloc Parent Template" not in sub_sal.columns or sub_sal.empty:
                return rows
            for apt in sorted(sub_sal["Alloc Parent Template"].dropna().unique()):
                apt_df = sub_sal[sub_sal["Alloc Parent Template"] == apt]
                apt_months = sal_agg_3m_by_alloc(apt_df)
                rows.append({
                    "id": f"{id_prefix}_{apt}",
                    "label": str(apt),
                    "months": apt_months,
                    "total": sum(apt_months)
                })
            return sorted(rows, key=lambda x: x["total"], reverse=True)

        # ── Section 3: Salary (Remark != "Support Team" AND Remark != "Marketing") ──
        remark_col   = "Remark" if "Remark" in sal_3m.columns else None

        sal_section_df = sal_3m.copy()
        if remark_col:
            sal_section_df = sal_section_df[
                ~sal_section_df[remark_col].astype(str).str.fullmatch("Support Team", case=False, na=False) &
                ~sal_section_df[remark_col].astype(str).str.fullmatch("Marketing", case=False, na=False)
            ]

        sal_months = sal_agg_3m_by_alloc(sal_section_df)
        salary_root["months"] = sal_months
        salary_root["total"]  = sum(sal_months)
        salary_root["children"] = build_salary_section(sal_section_df, "sal")

        # ── Section 4a: Support Salary (Remark == "Support Team") ──
        if remark_col:
            sup_sal_df = sal_3m[
                sal_3m[remark_col].astype(str).str.fullmatch("Support Team", case=False, na=False)
            ]
        else:
            sup_sal_df = pd.DataFrame(columns=sal_3m.columns)

        sup_months = sal_agg_3m_by_alloc(sup_sal_df)
        support_salary_root["months"]   = sup_months
        support_salary_root["total"]    = sum(sup_months)
        support_salary_root["children"] = build_salary_section(sup_sal_df, "sup")

        # ── Section 4b: Marketing Salary (Remark == "Marketing") ──
        if remark_col:
            mkt_sal_df = sal_3m[
                sal_3m[remark_col].astype(str).str.fullmatch("Marketing", case=False, na=False)
            ]
        else:
            mkt_sal_df = pd.DataFrame(columns=sal_3m.columns)

        mkt_sal_months = sal_agg_3m_by_alloc(mkt_sal_df)
        mkt_salary_root["months"]   = mkt_sal_months
        mkt_salary_root["total"]    = sum(mkt_sal_months)
        mkt_salary_root["children"] = build_salary_section(mkt_sal_df, "mkts")

    except Exception as e:
        import traceback
        print(f"[get_hierarchical_expenses_v2] Error loading Salary List: {e}")
        traceback.print_exc()

    # Overhead parent (wraps Support Salary + Marketing Salary)
    overhead_root: Dict[str, Any] = {
        "id": "overhead_root", "label": "Overhead",
        "sectionType": "overhead",
        "months": [s + m for s, m in zip(support_salary_root["months"], mkt_salary_root["months"])],
        "total": support_salary_root["total"] + mkt_salary_root["total"],
        "children": [support_salary_root, mkt_salary_root]
    }

    # ─────────────────────────────────────────────────────────────────────
    # SECTION 5 — Marketing Expenses  (Expenses Ledger Group == "Marketing (Exp)")
    # ─────────────────────────────────────────────────────────────────────
    if ov_col:
        mkt_exp_df = rbac(df_3m[df_3m[ov_col] == "Marketing (Exp)"])
    else:
        mkt_exp_df = pd.DataFrame(columns=df_3m.columns)

    mkt_exp_root_months = agg_3m(mkt_exp_df)
    mkt_exp_children = []

    mkt_apt_col = "alloc_parent_template" if "alloc_parent_template" in mkt_exp_df.columns else "cost_centre_parent"
    mkt_cc_col  = "cost_centre" if "cost_centre" in mkt_exp_df.columns else None

    if mkt_apt_col in mkt_exp_df.columns:
        for apt in sorted(mkt_exp_df[mkt_apt_col].dropna().unique()):
            apt_df = mkt_exp_df[mkt_exp_df[mkt_apt_col] == apt]
            apt_months = agg_3m(apt_df)
            apt_node: Dict[str, Any] = {
                "id": f"mkte_apt_{apt}", "label": str(apt),
                "months": apt_months, "total": sum(apt_months), "children": []
            }
            if mkt_cc_col and mkt_cc_col in apt_df.columns:
                for cc in sorted(apt_df[mkt_cc_col].dropna().unique()):
                    cc_df = apt_df[apt_df[mkt_cc_col] == cc]
                    cc_months = agg_3m(cc_df)
                    cc_node: Dict[str, Any] = {
                        "id": f"mkte_cc_{apt}_{cc}", "label": str(cc),
                        "months": cc_months, "total": sum(cc_months), "children": []
                    }
                    # Level 3: Ledger Name
                    for led in sorted(cc_df["ledger"].dropna().unique()):
                        led_df = cc_df[cc_df["ledger"] == led]
                        led_months = agg_3m(led_df)
                        cc_node["children"].append({
                            "id": f"mkte_ledger_{apt}_{cc}_{led}", "label": str(led),
                            "months": led_months, "total": sum(led_months),
                        })
                    apt_node["children"].append(cc_node)
            mkt_exp_children.append(apt_node)

    mkt_expense_root: Dict[str, Any] = {
        "id": "marketing_expenses_root", "label": "Marketing Expenses",
        "sectionType": "marketing_expenses",
        "months": mkt_exp_root_months, "total": sum(mkt_exp_root_months),
        "children": mkt_exp_children
    }

    # ─────────────────────────────────────────────────────────────────────
    # Return all sections in order + month labels
    # ─────────────────────────────────────────────────────────────────────
    month_labels = [p.strftime("%b %Y") for p in periods]

    return {
        "month_labels": month_labels,
        "sections": [
            direct_root,
            outsource_root,
            salary_root,
            overhead_root,
            mkt_expense_root,
        ]
    }


def get_hierarchical_expenses(
    df: pd.DataFrame, 
    excel_path: str,
    user_cost_centre_parent: Optional[str] = None,
    is_admin: bool = False
) -> List[Dict[str, Any]]:
    """Legacy wrapper — kept for backward compatibility with old endpoint."""
    if df.empty:
        return []

    current_year = df["date"].max().year
    df_current = df[df["date"].dt.year == current_year].copy()

    def get_monthly_array(grouped_series):
        arr = [0.0] * 12
        for month, val in grouped_series.items():
            if isinstance(month, (pd.Timestamp, datetime, date)):
                m_idx = month.month - 1
                if 0 <= m_idx < 12:
                    arr[m_idx] = float(abs(val))
        return arr

    direct_expenses_df = df_current[df_current.get("primary_group", pd.Series(dtype=str)).eq("Direct Expenses")
                                    if "primary_group" in df_current.columns
                                    else []].copy()
    if "primary_group" in df_current.columns:
        direct_expenses_df = df_current[df_current["primary_group"] == "Direct Expenses"].copy()
    else:
        direct_expenses_df = pd.DataFrame(columns=df_current.columns)

    if not is_admin and user_cost_centre_parent:
        direct_expenses_df = direct_expenses_df[direct_expenses_df["cost_centre_parent"] == user_cost_centre_parent]

    direct_expenses_df["month"] = direct_expenses_df["date"].dt.to_period("M").dt.to_timestamp()
    direct_root_months = get_monthly_array(direct_expenses_df.groupby("month")["amount"].sum())
    direct_children = []
    for cp in sorted(direct_expenses_df["cost_centre_parent"].dropna().unique()):
        cp_df = direct_expenses_df[direct_expenses_df["cost_centre_parent"] == cp]
        cp_months = get_monthly_array(cp_df.groupby("month")["amount"].sum())
        cp_node = {"id": f"de_{cp}", "label": str(cp), "months": cp_months, "total": sum(cp_months), "children": []}
        for cc in sorted(cp_df["cost_centre"].dropna().unique()):
            cc_df = cp_df[cp_df["cost_centre"] == cc]
            cc_months = get_monthly_array(cc_df.groupby("month")["amount"].sum())
            cc_node = {"id": f"de_{cp}_{cc}", "label": str(cc), "months": cc_months, "total": sum(cc_months), "children": []}
            for led in sorted(cc_df["ledger"].dropna().unique()):
                led_df = cc_df[cc_df["ledger"] == led]
                led_months = get_monthly_array(led_df.groupby("month")["amount"].sum())
                cc_node["children"].append({"id": f"de_{cp}_{cc}_{led}", "label": str(led), "months": led_months, "total": sum(led_months)})
            cp_node["children"].append(cc_node)
        direct_children.append(cp_node)

    direct_root = {"id": "direct_expenses_root", "label": "Direct Expenses", "months": direct_root_months, "total": sum(direct_root_months), "children": direct_children}

    salary_root: Dict[str, Any] = {"id": "salary_root", "label": "Salary", "months": [0.0] * 12, "total": 0.0, "children": []}
    try:
        salary_df = pd.read_excel(excel_path, sheet_name="Salary List")
        if not is_admin and user_cost_centre_parent:
            salary_df = salary_df[salary_df["Alloc Parent Template"] == user_cost_centre_parent]
        month_map = {'Jan': 0, 'Feb': 1, 'Mar': 2, 'Apr': 3, 'May': 4, 'Jun': 5, 'Jul': 6, 'Aug': 7, 'Sep': 8, 'Oct': 9, 'Nov': 10, 'Dec': 11}
        def parse_month_year(key):
            if not isinstance(key, str) or '_' not in key:
                return None, None
            parts = key.split('_')
            try: yr = int("20" + parts[1].strip())
            except: yr = None
            return month_map.get(parts[0].strip()), yr
        salary_df[["m_idx", "year"]] = salary_df["MonthKey"].apply(lambda x: pd.Series(parse_month_year(x)))
        salary_df = salary_df[salary_df["year"] == current_year]
        if not salary_df.empty:
            emp_groups = salary_df.groupby(["Employee Name", "Emp ID"], dropna=False)
            salary_total_months = [0.0] * 12
            for (name, eid), group in emp_groups:
                if pd.isna(name) or pd.isna(eid): continue
                emp_months = [0.0] * 12
                for _, row in group.iterrows():
                    m_idx = row["m_idx"]
                    if m_idx is not None and not pd.isna(m_idx):
                        amount = float(row.get("CTC", 0))
                        emp_months[int(m_idx)] += amount
                        salary_total_months[int(m_idx)] += amount
                salary_root["children"].append({"id": f"sal_{eid}", "label": str(name), "empId": str(eid), "months": emp_months, "total": sum(emp_months), "isSalary": True})
            salary_root["children"].sort(key=lambda x: x["total"], reverse=True)
            salary_root["months"] = salary_total_months
            salary_root["total"] = sum(salary_total_months)
    except Exception as e:
        import traceback
        print(f"Error processing Salary List: {e}")
        traceback.print_exc()

    return [salary_root, direct_root]

