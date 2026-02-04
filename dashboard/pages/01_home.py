from __future__ import annotations

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

from dateutil.relativedelta import relativedelta

from utils.config import load_config
from utils.file_loader import ExcelLoadError, latest_cache_key, load_excel_at_path
from utils.metrics import (
    KpiResult,
    calculate_kpis,
    get_current_month_profit,
    get_monthly_expenses_table,
    get_current_month_daily_profit,
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


def render():
    st.title("📊 Home - Executive Summary")
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
    expense_keywords = config.get("expense_keywords", [])
    cash_ledgers = config.get("cash_ledgers", [])

    # Get current month data
    income, expense, profit = get_current_month_profit(df, revenue_keywords, expense_keywords)
    current_month = df["date"].max().strftime("%B %Y")
    
    st.markdown(f"### 💰 Profit by Month - {current_month}")
    st.markdown("---")
    
    # Income and Expense cards side by side
    col1, col2 = st.columns(2)
    
    with col1:
        # Income card - clickable
        with st.container():
            st.markdown("""
                <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                     padding: 30px; border-radius: 15px; color: white; 
                     box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);'>
                    <h3 style='margin: 0; font-size: 1.2em; opacity: 0.9;'>Income</h3>
                    <h1 style='margin: 10px 0; font-size: 2.5em;'>₹{:,.0f}</h1>
                </div>
            """.format(income), unsafe_allow_html=True)
            
            if st.button("📈 View Income Details", key="income_btn", use_container_width=True):
                st.switch_page("pages/04_income.py")
    
    with col2:
        # Expense card - clickable
        with st.container():
            st.markdown("""
                <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                     padding: 30px; border-radius: 15px; color: white;
                     box-shadow: 0 4px 15px rgba(245, 87, 108, 0.4);'>
                    <h3 style='margin: 0; font-size: 1.2em; opacity: 0.9;'>Expense</h3>
                    <h1 style='margin: 10px 0; font-size: 2.5em;'>₹{:,.0f}</h1>
                </div>
            """.format(expense), unsafe_allow_html=True)
            
            if st.button("📉 View Expense Details", key="expense_btn", use_container_width=True):
                st.switch_page("pages/05_expense.py")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Net Profit display
    profit_color = "#10b981" if profit >= 0 else "#ef4444"
    st.markdown(f"""
        <div style='background: rgba(16, 185, 129, 0.1); 
             padding: 20px; border-radius: 10px; text-align: center;
             border: 2px solid {profit_color};'>
            <h4 style='margin: 0; color: {profit_color};'>Net Profit: ₹{profit:,.0f}</h4>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Graph of current month
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown("### 📈 Graph of Current Month")
        daily_profit = get_current_month_daily_profit(df, revenue_keywords, expense_keywords)
        
        if not daily_profit.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=daily_profit["date"], 
                y=daily_profit["income"],
                name="Income",
                mode='lines+markers',
                line=dict(color='#667eea', width=3),
                fill='tonexty'
            ))
            fig.add_trace(go.Scatter(
                x=daily_profit["date"], 
                y=daily_profit["expense"],
                name="Expense",
                mode='lines+markers',
                line=dict(color='#f5576c', width=3),
                fill='tozeroy'
            ))
            fig.add_trace(go.Scatter(
                x=daily_profit["date"], 
                y=daily_profit["profit"],
                name="Profit",
                mode='lines+markers',
                line=dict(color='#10b981', width=3, dash='dash')
            ))
            
            fig.update_layout(
                title=f"Daily Performance - {current_month}",
                xaxis_title="Date",
                yaxis_title="Amount (₹)",
                hovermode='x unified',
                height=400,
                template="plotly_white",
                hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial")
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for current month")
    
    with col_right:
        st.markdown("### 📊 Quick Stats")
        kpis = calculate_kpis(df, revenue_keywords, expense_keywords, cash_ledgers)
        
        st.metric("💰 Cash Balance", f"₹{kpis.cash_balance:,.0f}")
        st.metric("📈 Total Revenue", f"₹{kpis.total_revenue:,.0f}")
        st.metric("📉 Total Expenses", f"₹{kpis.total_expenses:,.0f}")
        st.metric("💵 Net Profit", f"₹{kpis.net_profit:,.0f}", 
                 delta=f"{((kpis.net_profit / kpis.total_revenue) * 100) if kpis.total_revenue else 0:.1f}%")
    
    st.markdown("---")
    
    # Monthly Expenses Table
    st.markdown("### 📅 Monthly Expenses")
    monthly_expenses = get_monthly_expenses_table(df, expense_keywords, n_months=3)
    
    if not monthly_expenses.empty:
        # Format the table nicely
        monthly_expenses["Month"] = monthly_expenses["month"].dt.strftime("%B %Y")
        monthly_expenses["Total Expense"] = monthly_expenses["total_expense"].apply(lambda x: f"₹{x:,.0f}")
        
        display_df = monthly_expenses[["Month", "Total Expense"]]
        
        st.dataframe(
            display_df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Month": st.column_config.TextColumn("Month", width="medium"),
                "Total Expense": st.column_config.TextColumn("Total Expense", width="medium"),
            }
        )
        
        # Bar chart for monthly expenses
        fig_expenses = px.bar(
            monthly_expenses, 
            x="month", 
            y="total_expense",
            title="Monthly Expense Trend",
            labels={"month": "Month", "total_expense": "Amount (₹)"},
            color_discrete_sequence=["#f5576c"]
        )
        fig_expenses.update_layout(
            height=300, 
            template="plotly_white",
            hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial")
        )
        st.plotly_chart(fig_expenses, use_container_width=True)
    else:
        st.info("No expense data available")
    
    # Footer with data info
    st.markdown("---")
    st.caption(
        f"📁 **File:** {Path(meta['file_path']).name} | "
        f"📄 **Sheet:** {meta['sheet']} | "
        f"📊 **Rows:** {meta['rows']} | "
        f"🕒 **Last modified:** {meta['modified_at']}"
    )
    
    if st.button("🔄 Refresh Data", type="secondary"):
        get_data.clear()
        st.rerun()


if __name__ == "__main__":
    render()
