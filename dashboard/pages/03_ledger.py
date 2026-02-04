from __future__ import annotations

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

from utils.config import load_config
from utils.file_loader import ExcelLoadError, latest_cache_key, load_excel_at_path
from utils.metrics import ledger_statement
from utils.ui import inject_global_styles


@st.cache_resource(show_spinner=False)
def get_config():
    return load_config()


@st.cache_data(show_spinner=True)
def get_data(cache_key: tuple[str, float]):
    config = get_config()
    path_str, _ = cache_key
    return load_excel_at_path(Path(path_str), config["excel_loader"])


def render():
    st.title("Ledger Explorer")
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

    if "ledger" not in df.columns:
        st.warning("No ledger column found in the data.")
        st.stop()

    ledgers = sorted(df["ledger"].dropna().unique())
    selected_ledger = st.selectbox("Ledger", options=ledgers)
    min_date = df["date"].min().date()
    max_date = df["date"].max().date()
    date_range = st.date_input("Date range", (min_date, max_date), min_value=min_date, max_value=max_date)
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range

    opening, period_total, closing, statement = ledger_statement(
        df, selected_ledger, pd.Timestamp(start_date), pd.Timestamp(end_date)
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Opening Balance", f"{opening:,.2f}")
    col2.metric("Period Movement", f"{period_total:,.2f}")
    col3.metric("Closing Balance", f"{closing:,.2f}")

    st.subheader("Running Balance")
    if not statement.empty:
        fig = px.line(statement, x="date", y="running_balance", markers=True, title="Running Balance")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No transactions in the selected window.")

    st.subheader("Transactions")
    if statement.empty:
        st.info("No transactions in the selected window.")
    else:
        st.dataframe(
            statement,
            column_config={
                "date": st.column_config.DateColumn("Date"),
                "amount": st.column_config.NumberColumn("Amount", format="%,.2f"),
                "running_balance": st.column_config.NumberColumn("Running Balance", format="%,.2f"),
            },
            use_container_width=True,
        )
        st.download_button(
            "Download statement CSV", statement.to_csv(index=False).encode("utf-8"), file_name="ledger_statement.csv"
        )

    st.caption(
        f"Loaded {meta['rows']} rows from {meta['sheet']} in {meta['file_path']}. Last modified {meta['modified_at']}."
    )
    if st.button("Refresh data", type="secondary"):
        get_data.clear()
        st.rerun()


if __name__ == "__main__":
    render()
