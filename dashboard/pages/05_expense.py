from __future__ import annotations

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

from utils.config import load_config
from utils.file_loader import ExcelLoadError, latest_cache_key, load_excel_at_path
from utils.metrics import get_expense_detail_with_variance, get_current_month_profit
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
    st.title("📉 Expense Details")
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
    
    # Header with total expense
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
             padding: 40px; border-radius: 15px; color: white; text-align: center;
             box-shadow: 0 4px 20px rgba(245, 87, 108, 0.5); margin-bottom: 30px;'>
            <h2 style='margin: 0; opacity: 0.9;'>Total Expense - {current_month}</h2>
            <h1 style='margin: 15px 0; font-size: 3.5em;'>₹{expense:,.0f}</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Get expense breakdown with variance
    expense_details = get_expense_detail_with_variance(df, expense_keywords)
    
    if not expense_details.empty:
        st.markdown("### 📊 Expense Breakdown by Ledger")
        st.markdown("*Comparison with previous month*")
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Format the dataframe for display
        display_df = expense_details.copy()
        display_df["Current Month"] = display_df["current_amount"].apply(lambda x: f"₹{x:,.0f}")
        display_df["Previous Month"] = display_df["previous_amount"].apply(lambda x: f"₹{x:,.0f}")
        display_df["Variance %"] = display_df["variance_pct"].apply(lambda x: f"{x:+.1f}%")
        display_df["Ledger"] = display_df["ledger"]
        
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
                expense_details.head(10),
                x="current_amount",
                y="ledger",
                orientation="h",
                title="Top 10 Expense Categories",
                labels={"current_amount": "Amount (₹)", "ledger": "Ledger"},
                color="current_amount",
                color_continuous_scale="Reds"
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
            variance_df = expense_details.head(10).copy()
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
                color_discrete_map={"Increase": "#ef4444", "Decrease": "#10b981", "No Change": "#6b7280"}
            )
            fig_variance.update_layout(
                height=500, 
                template="plotly_white",
                hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial")
            )
            st.plotly_chart(fig_variance, use_container_width=True)
        
        # Pie chart for expense distribution
        st.markdown("### 📊 Expense Distribution")
        fig_pie = px.pie(
            expense_details.head(10),
            values="current_amount",
            names="ledger",
            title="Expense Categories Distribution (Top 10)",
            color_discrete_sequence=px.colors.sequential.Reds_r
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(
            height=500, 
            template="plotly_white",
            hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial")
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Trend analysis - expenses over time
        st.markdown("### 📈 Expense Trends")
        
        # Get monthly expense data for top 5 ledgers
        ledger_series = df["ledger"].astype(str)
        pattern = "|".join([kw.strip() for kw in expense_keywords if kw.strip()])
        expense_mask = ledger_series.str.contains(pattern, case=False, na=False)
        expense_df = df.loc[expense_mask].copy()
        expense_df["amount"] = expense_df["amount"].abs()
        expense_df["month"] = expense_df["date"].dt.to_period("M").dt.to_timestamp()
        
        top_5_ledgers = expense_details.head(5)["ledger"].tolist()
        trend_data = expense_df[expense_df["ledger"].isin(top_5_ledgers)]
        
        if not trend_data.empty:
            monthly_trends = trend_data.groupby(["month", "ledger"])["amount"].sum().reset_index()
            
            fig_trend = px.line(
                monthly_trends,
                x="month",
                y="amount",
                color="ledger",
                title="Monthly Expense Trends (Top 5 Categories)",
                labels={"amount": "Amount (₹)", "month": "Month", "ledger": "Category"},
                markers=True
            )
            fig_trend.update_layout(
                height=400, 
                template="plotly_white",
                hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial")
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        
        # Summary statistics
        st.markdown("### 📊 Summary Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Expense Categories", len(expense_details))
        with col2:
            avg_expense = expense_details["current_amount"].mean()
            st.metric("Average per Category", f"₹{avg_expense:,.0f}")
        with col3:
            max_expense = expense_details["current_amount"].max()
            st.metric("Highest Expense", f"₹{max_expense:,.0f}")
        with col4:
            avg_variance = expense_details["variance_pct"].mean()
            variance_color = "inverse" if avg_variance > 0 else "normal"
            st.metric("Avg Variance", f"{avg_variance:+.1f}%", 
                     delta=f"{avg_variance:.1f}%",
                     delta_color=variance_color)
        
        # Expense insights
        st.markdown("### 💡 Key Insights")
        
        increasing_expenses = expense_details[expense_details["variance_pct"] > 10]
        decreasing_expenses = expense_details[expense_details["variance_pct"] < -10]
        
        col1, col2 = st.columns(2)
        
        with col1:
            if not increasing_expenses.empty:
                st.markdown("#### ⚠️ Significantly Increased")
                for _, row in increasing_expenses.head(5).iterrows():
                    st.markdown(f"- **{row['ledger']}**: ₹{row['current_amount']:,.0f} ({row['variance_pct']:+.1f}%)")
            else:
                st.success("No significant expense increases")
        
        with col2:
            if not decreasing_expenses.empty:
                st.markdown("#### ✅ Significantly Decreased")
                for _, row in decreasing_expenses.head(5).iterrows():
                    st.markdown(f"- **{row['ledger']}**: ₹{row['current_amount']:,.0f} ({row['variance_pct']:+.1f}%)")
            else:
                st.info("No significant expense decreases")
        
        # Download option
        st.markdown("---")
        csv_data = expense_details.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Expense Report (CSV)",
            data=csv_data,
            file_name=f"expense_report_{current_month.replace(' ', '_')}.csv",
            mime="text/csv",
        )
    
    else:
        st.warning("No expense data available for analysis")
    
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
