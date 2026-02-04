from __future__ import annotations

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

from utils.config import load_config
from utils.file_loader import ExcelLoadError, latest_cache_key, load_excel_at_path
from utils.metrics import sales_by_item, sales_by_month, top_customers
from utils.ui import inject_global_styles


@st.cache_resource(show_spinner=False)
def get_config():
    return load_config()


@st.cache_data(show_spinner=True)
def get_data(cache_key: tuple[str, float]):
    config = get_config()
    path_str, _ = cache_key
    return load_excel_at_path(Path(path_str), config["excel_loader"])


def _revenue_view(df: pd.DataFrame, keywords) -> pd.DataFrame:
    if df.empty or "ledger" not in df.columns:
        return df.iloc[0:0]
    pattern = "|".join([kw.strip() for kw in keywords if kw.strip()])
    if not pattern:
        return df.iloc[0:0]
    mask = df["ledger"].astype(str).str.contains(pattern, case=False, na=False)
    return df.loc[mask].copy()


def render():
    st.title("Sales Analysis")
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

    revenue_keywords = config.get("revenue_keywords", [])
    top_n = st.sidebar.slider("Top N", 5, 25, 10)

    min_date = df["date"].min().date()
    max_date = df["date"].max().date()
    date_range = st.sidebar.date_input(
        "Date range", (min_date, max_date), min_value=min_date, max_value=max_date
    )
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range

    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date)
    filtered = df.loc[(df["date"] >= start_ts) & (df["date"] <= end_ts)]

    sales_df = _revenue_view(filtered, revenue_keywords)
    total_sales = float(sales_df["amount"].sum()) if not sales_df.empty else 0.0
    unique_customers = int(sales_df["customer"].nunique()) if "customer" in sales_df.columns else 0
    avg_ticket = total_sales / unique_customers if unique_customers else 0.0

    kpi_cols = st.columns(3)
    kpi_cols[0].metric("Total Sales", f"{total_sales:,.2f}")
    kpi_cols[1].metric("Unique Customers", f"{unique_customers:,}")
    kpi_cols[2].metric("Avg Ticket", f"{avg_ticket:,.2f}")

    st.subheader("Sales by Month")
    monthly = sales_by_month(filtered, revenue_keywords)
    if not monthly.empty:
        fig_month = px.area(monthly, x="month", y="total", title="Monthly Revenue", markers=True)
        st.plotly_chart(fig_month, use_container_width=True)
    else:
        st.info("No sales in the selected window.")

    cols = st.columns(2)
    with cols[0]:
        st.markdown("**Top Customers**")
        customers = top_customers(filtered, revenue_keywords, limit=top_n)
        if not customers.empty:
            fig_cust = px.bar(customers, x="total", y="customer", orientation="h", title="Top Customers")
            st.plotly_chart(fig_cust, use_container_width=True)
        else:
            st.info("No customer data in the selected window.")
    with cols[1]:
        st.markdown("**Sales by Item**")
        items = sales_by_item(filtered, revenue_keywords, limit=top_n)
        if not items.empty:
            fig_item = px.bar(items, x="total", y="item", orientation="h", title="Top Items")
            st.plotly_chart(fig_item, use_container_width=True)
        else:
            st.info("No item column or no sales by item in the selected window.")

    st.subheader("Filtered Rows")
    st.dataframe(filtered)
    st.download_button(
        "Download filtered CSV",
        filtered.to_csv(index=False).encode("utf-8"),
        file_name="sales_filtered.csv",
    )

    st.caption(
        f"Loaded {meta['rows']} rows from {meta['sheet']} in {meta['file_path']}. Last modified {meta['modified_at']}."
    )
    if st.button("Refresh data", type="secondary"):
        get_data.clear()
        st.rerun()


if __name__ == "__main__":
    render()
