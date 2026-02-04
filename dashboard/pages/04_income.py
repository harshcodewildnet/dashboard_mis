from __future__ import annotations

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

from utils.config import load_config
from utils.file_loader import ExcelLoadError, latest_cache_key, load_excel_at_path
from utils.metrics import get_income_detail_with_variance, get_current_month_profit
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
    st.title("📈 Income Details")
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
    
    # Get current month info
    income, expense, profit = get_current_month_profit(df, revenue_keywords, expense_keywords)
    current_month = df["date"].max().strftime("%B %Y")
    
    # Header with total income
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
             padding: 40px; border-radius: 15px; color: white; text-align: center;
             box-shadow: 0 4px 20px rgba(102, 126, 234, 0.5); margin-bottom: 30px;'>
            <h2 style='margin: 0; opacity: 0.9;'>Total Income - {current_month}</h2>
            <h1 style='margin: 15px 0; font-size: 3.5em;'>₹{income:,.0f}</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Get income breakdown with variance
    income_details = get_income_detail_with_variance(df, revenue_keywords)
    
    if not income_details.empty:
        st.markdown("### 📊 Income Breakdown by Ledger")
        st.markdown("*Comparison with previous month*")
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Format the dataframe for display
        display_df = income_details.copy()
        display_df["Current Month"] = display_df["current_amount"].apply(lambda x: f"₹{x:,.0f}")
        display_df["Previous Month"] = display_df["previous_amount"].apply(lambda x: f"₹{x:,.0f}")
        display_df["Variance %"] = display_df["variance_pct"].apply(lambda x: f"{x:+.1f}%")
        display_df["Ledger"] = display_df["ledger"]
        
        # Color code the variance
        def highlight_variance(row):
            if row["variance_pct"] > 0:
                return [''] * 4 + ['background-color: rgba(16, 185, 129, 0.2); color: #10b981']
            elif row["variance_pct"] < 0:
                return [''] * 4 + ['background-color: rgba(239, 68, 68, 0.2); color: #ef4444']
            else:
                return [''] * 5
        
        # Display styled dataframe
        st.dataframe(
            display_df[["Ledger", "Current Month", "Previous Month", "Variance %"]],
            hide_index=True,
            use_container_width=True,
            column_config={
                "Ledger": st.column_config.TextColumn("Header", width="medium"),
                "Current Month": st.column_config.TextColumn("Amount", width="medium"),
                "Previous Month": st.column_config.TextColumn("Previous Month", width="medium"),
                "Variance %": st.column_config.TextColumn("Variance %", width="medium"),
            }
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart of current amounts
            fig_bar = px.bar(
                income_details.head(10),
                x="current_amount",
                y="ledger",
                orientation="h",
                title="Top 10 Income Sources",
                labels={"current_amount": "Amount (₹)", "ledger": "Ledger"},
                color="current_amount",
                color_continuous_scale="Purples"
            )
            fig_bar.update_layout(
                height=500, 
                template="plotly_white", 
                showlegend=False,
                hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial")
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            # Variance visualization
            variance_df = income_details.head(10).copy()
            variance_df["color"] = variance_df["variance_pct"].apply(
                lambda x: "Increase" if x > 0 else "Decrease" if x < 0 else "No Change"
            )
            
            fig_variance = px.bar(
                variance_df,
                x="variance_pct",
                y="ledger",
                orientation="h",
                title="Month-over-Month Variance",
                labels={"variance_pct": "Variance %", "ledger": "Ledger"},
                color="color",
                color_discrete_map={"Increase": "#10b981", "Decrease": "#ef4444", "No Change": "#6b7280"}
            )
            fig_variance.update_layout(
                height=500, 
                template="plotly_white",
                hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial")
            )
            st.plotly_chart(fig_variance, use_container_width=True)
        
        # Pie chart for income distribution
        st.markdown("### 📈 Income Distribution")
        fig_pie = px.pie(
            income_details.head(10),
            values="current_amount",
            names="ledger",
            title="Income Sources Distribution (Top 10)",
            color_discrete_sequence=px.colors.sequential.Purples_r
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(
            height=500, 
            template="plotly_white",
            hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial")
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Summary statistics
        st.markdown("### 📊 Summary Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Income Ledgers", len(income_details))
        with col2:
            avg_income = income_details["current_amount"].mean()
            st.metric("Average per Ledger", f"₹{avg_income:,.0f}")
        with col3:
            max_income = income_details["current_amount"].max()
            st.metric("Highest Income Source", f"₹{max_income:,.0f}")
        with col4:
            avg_variance = income_details["variance_pct"].mean()
            st.metric("Avg Variance", f"{avg_variance:+.1f}%", 
                     delta=f"{avg_variance:.1f}%")
        
        # Download option
        st.markdown("---")
        csv_data = income_details.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Income Report (CSV)",
            data=csv_data,
            file_name=f"income_report_{current_month.replace(' ', '_')}.csv",
            mime="text/csv",
        )
    
    else:
        st.warning("No income data available for analysis")
    
    # Footer
    st.markdown("---")
    st.caption(
        f"📁 **File:** {Path(meta['file_path']).name} | "
        f"📄 **Sheet:** {meta['sheet']} | "
        f"🕒 **Last modified:** {meta['modified_at']}"
    )
    
    # Back to home button
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("pages/01_home.py")
    
    if st.button("🔄 Refresh Data", type="secondary"):
        get_data.clear()
        st.rerun()


if __name__ == "__main__":
    render()
