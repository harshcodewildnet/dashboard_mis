from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, Iterable, List, Optional, Tuple

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
        return pd.DataFrame(columns=["ledger", "current_amount", "previous_amount", "variance_pct"])
    
    current_month = df["date"].max().to_period("M")
    previous_month = current_month - 1
    
    filter_col = _get_filter_column(df)
    filter_series = df[filter_col].astype(str)
    revenue_mask = _match_keywords(filter_series, revenue_keywords)
    revenue_df = df.loc[revenue_mask].copy()
    revenue_df["month"] = revenue_df["date"].dt.to_period("M")
    
    current_data = revenue_df[revenue_df["month"] == current_month].groupby("ledger")["amount"].sum()
    previous_data = revenue_df[revenue_df["month"] == previous_month].groupby("ledger")["amount"].sum()
    
    result = pd.DataFrame({
        "ledger": current_data.index,
        "current_amount": current_data.values,
    })
    
    result["previous_amount"] = result["ledger"].map(previous_data).fillna(0)
    result["variance_pct"] = ((result["current_amount"] - result["previous_amount"]) / result["previous_amount"].replace(0, 1)) * 100
    result = result.sort_values("current_amount", ascending=False)
    
    return result


def get_expense_detail_with_variance(df: pd.DataFrame, expense_keywords: List[str]) -> pd.DataFrame:
    """Get expense breakdown by ledger with month-over-month variance"""
    if df.empty:
        return pd.DataFrame(columns=["ledger", "current_amount", "previous_amount", "variance_pct"])
    
    current_month = df["date"].max().to_period("M")
    previous_month = current_month - 1
    
    filter_col = _get_filter_column(df)
    filter_series = df[filter_col].astype(str)
    expense_mask = _match_keywords(filter_series, expense_keywords)
    expense_df = df.loc[expense_mask].copy()
    expense_df["month"] = expense_df["date"].dt.to_period("M")
    expense_df["amount"] = expense_df["amount"].abs()
    
    current_data = expense_df[expense_df["month"] == current_month].groupby("ledger")["amount"].sum()
    previous_data = expense_df[expense_df["month"] == previous_month].groupby("ledger")["amount"].sum()
    
    result = pd.DataFrame({
        "ledger": current_data.index,
        "current_amount": current_data.values,
    })
    
    result["previous_amount"] = result["ledger"].map(previous_data).fillna(0)
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
