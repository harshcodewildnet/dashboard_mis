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


def calculate_kpis(df: pd.DataFrame, revenue_keywords: List[str], expense_keywords: List[str], cash_ledgers: List[str]) -> KpiResult:
    ledger_series = df["ledger"].astype(str)
    revenue_mask = _match_keywords(ledger_series, revenue_keywords)
    expense_mask = _match_keywords(ledger_series, expense_keywords)

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
    ledger_series = df["ledger"].astype(str)
    revenue_mask = _match_keywords(ledger_series, revenue_keywords)
    expense_mask = _match_keywords(ledger_series, expense_keywords)

    df = df.assign(month=df["date"].dt.to_period("M").dt.to_timestamp())
    revenue = df.loc[revenue_mask].groupby("month")["amount"].sum()
    expenses = df.loc[expense_mask].groupby("month")["amount"].sum().abs()

    out = pd.DataFrame({"revenue": revenue, "expenses": expenses}).fillna(0.0).reset_index()
    return out


def top_customers(df: pd.DataFrame, revenue_keywords: List[str], limit: int = 10) -> pd.DataFrame:
    ledger_series = df["ledger"].astype(str)
    revenue_mask = _match_keywords(ledger_series, revenue_keywords)
    grouped = df.loc[revenue_mask].groupby("customer")["amount"].sum()
    result = grouped.sort_values(ascending=False).head(limit).reset_index()
    result = result.rename(columns={"amount": "total"})
    return result


def sales_by_month(df: pd.DataFrame, revenue_keywords: List[str]) -> pd.DataFrame:
    ledger_series = df["ledger"].astype(str)
    revenue_mask = _match_keywords(ledger_series, revenue_keywords)
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
