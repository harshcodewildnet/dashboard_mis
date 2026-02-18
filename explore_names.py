
import pandas as pd
import sys
import os

# Add parent directory to path to import dashboard modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboard.utils.file_loader import load_excel_at_path, latest_cache_key
from dashboard.utils.config import load_config

def explore_names():
    print("Loading config...")
    config = load_config()
    
    print("Loading data...")
    from pathlib import Path
    path_str, _ = latest_cache_key(config["excel_loader"])
    df, _ = load_excel_at_path(Path(path_str), config["excel_loader"])
    
    print(f"Total Rows: {len(df)}")
    
    if "name" not in df.columns:
        print("ERROR: 'name' column not found!")
        print("Columns found:", df.columns.tolist())
        return

    # clean names
    df["name"] = df["name"].fillna("Unknown").astype(str).str.strip()
    
    # Get keywords
    rev_kw = config.get("revenue_keywords", config.get("revenue_ledgers", []))
    exp_kw = config.get("expense_ledgers", config.get("expense_keywords", []))
    
    print(f"Revenue Keywords: {len(rev_kw)}")
    print(f"Expense Keywords: {len(exp_kw)}")
    
    # Identify Transaction Types
    # We need to look at 'ledger' or 'primary_group' depending on config.
    # Usually 'ledger' contains the income/expense head.
    
    # Helper to check if row is revenue/expense
    def is_match(val, keywords):
        if not keywords: return False
        val_str = str(val)
        return any(k.lower() in val_str.lower() for k in keywords)

    # We will assume 'ledger' column holds the classification info
    # (or whatever column is used for income/expense id)
    # The default metric logic uses `_get_filter_column`.
    # I'll just look at 'ledger' and 'primary_group' to be safe.
    
    df["is_rev"] = df["ledger"].apply(lambda x: is_match(x, rev_kw))
    df["is_exp"] = df["ledger"].apply(lambda x: is_match(x, exp_kw))
    
    # Group by Name
    name_stats = df.groupby("name").agg(
        total_rows=("amount", "count"),
        rev_rows=("is_rev", "sum"),
        exp_rows=("is_exp", "sum"),
        total_amount=("amount", "sum")
    ).reset_index()
    
    total_names = len(name_stats)
    print(f"\nTotal Unique Names: {total_names}")
    
    # 1. Pure Clients (Only Revenue)
    pure_clients = name_stats[ (name_stats["rev_rows"] > 0) & (name_stats["exp_rows"] == 0) ]
    print(f"Pure Clients (Revenue only): {len(pure_clients)}")
    
    # 2. Pure Vendors (Only Expense)
    pure_vendors = name_stats[ (name_stats["rev_rows"] == 0) & (name_stats["exp_rows"] > 0) ]
    print(f"Pure Vendors (Expense only): {len(pure_vendors)}")
    
    # 3. Mixed (Both)
    mixed = name_stats[ (name_stats["rev_rows"] > 0) & (name_stats["exp_rows"] > 0) ]
    print(f"Mixed Entities (Revenue & Expense): {len(mixed)}")
    
    # 4. Unclassified (Neither Revenue nor Expense - e.g. Balance Sheet, Transfers)
    unclassified = name_stats[ (name_stats["rev_rows"] == 0) & (name_stats["exp_rows"] == 0) ]
    print(f"Unclassified (Balance Sheet/Other): {len(unclassified)}")
    
    print("\n--- Top 10 Clients (by Revenue Rows) ---")
    print(pure_clients.sort_values("total_amount", ascending=False).head(10)[["name", "total_amount"]])
    
    print("\n--- Top 10 Vendors (by Expense Rows) ---")
    print(pure_vendors.sort_values("total_amount", ascending=False).head(10)[["name", "total_amount"]])
    
    if not mixed.empty:
        print("\n--- Mixed Entities ---")
        print(mixed.head(10))
        
    if not unclassified.empty:
        print("\n--- Unclassified Samples ---")
        print(unclassified["name"].head(10).tolist())

if __name__ == "__main__":
    explore_names()
