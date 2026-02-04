from __future__ import annotations

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

from dateutil.relativedelta import relativedelta

from utils.config import load_config
from utils.file_loader import ExcelLoadError, latest_cache_key, load_excel_at_path
from utils.metrics import (
    KpiResult,
    calculate_kpis,
    monthly_totals,
    group_summary,
    top_ledgers,
)
from utils.ui import inject_global_styles


@st.cache_resource(show_spinner=False)
def get_config():
    return load_config()


@st.cache_data(show_spinner=True)
def get_data(cache_key: tuple[str, float]):
    config = get_config()
    path_str, _ = cache_key
    return load_excel_at_path(Path(path_str), config["excel_loader"])


def _date_bounds(df):
    return df["date"].min().date(), df["date"].max().date()


def _apply_date_filter(df, start, end):
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    return df.loc[(df["date"] >= start_ts) & (df["date"] <= end_ts)]


def _kpi_cards(kpis: KpiResult):
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", f"{kpis.total_revenue:,.2f}")
    col2.metric("Total Expenses", f"{kpis.total_expenses:,.2f}")
    col3.metric("Net Profit", f"{kpis.net_profit:,.2f}")
    col4.metric("Cash / Bank", f"{kpis.cash_balance:,.2f}")


def _data_info(meta, df):
    st.caption(
        f"File: {Path(meta['file_path']).name} | Sheet: {meta['sheet']} | Rows: {meta['rows']} | Last modified: {meta['modified_at']}"
    )
    st.caption(
        f"Date coverage: {df['date'].min().date()} → {df['date'].max().date()} | Columns: {', '.join(df.columns)}"
    )


def render():
    st.title("Home — Executive Summary")
    inject_global_styles()

    try:
        config = get_config()
        cache_key = latest_cache_key(config["excel_loader"])
        df, meta = get_data(cache_key)
    except ExcelLoadError as exc:
        st.error(f"Excel load failed: {exc}")
        st.stop()
    if df.empty:
        st.warning("Loaded Excel has no rows after validation.")
        st.stop()

    config = get_config()
    revenue_keywords = config.get("revenue_keywords", [])
    expense_keywords = config.get("expense_keywords", [])
    cash_ledgers = config.get("cash_ledgers", [])

    min_date, max_date = _date_bounds(df)
    default_start = max_date - relativedelta(months=1)
    date_range = st.sidebar.date_input(
        "Date range", (default_start, max_date), min_value=min_date, max_value=max_date
    )
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range

    filtered = _apply_date_filter(df, start_date, end_date)

    kpis = calculate_kpis(filtered, revenue_keywords, expense_keywords, cash_ledgers)
    _kpi_cards(kpis)

    st.subheader("Monthly Totals")
    monthly = monthly_totals(filtered)
    if not monthly.empty:
        fig = px.area(monthly, x="month", y="amount", title="Monthly Net Amount", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data for the selected period.")

    cols = st.columns(2)
    with cols[0]:
        st.markdown("**By Ledger Group**")
        by_group = group_summary(filtered, "expense_ledger_group", top_n=10)
        if not by_group.empty:
            fig = px.bar(by_group, x="expense_ledger_group", y="total", title="Top Groups")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No ledger group data.")
    with cols[1]:
        st.markdown("**Top Ledgers**")
        led = top_ledgers(filtered, limit=10)
        if not led.empty:
            fig = px.bar(led, x="ledger", y="total", title="Top Ledgers")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No ledger data.")

    st.subheader("Data Table (filtered)")
    st.dataframe(filtered)
    st.download_button(
        "Download filtered CSV", filtered.to_csv(index=False).encode("utf-8"), file_name="filtered_data.csv"
    )

    _data_info(meta, df)
    if st.button("Refresh data", type="secondary"):
        get_data.clear()
        st.rerun()


if __name__ == "__main__":
    render()
