
import sys
import pandas as pd
from dashboard.utils.config import load_config
from dashboard.utils.file_loader import load_excel_at_path

def explore_names():
    try:
        # Load config
        print("Loading config...")
        config = load_config()
        
        # Get data file path
        # config['excel_loader']['smb_share'] should be correct due to auto-detection in load_config
        data_path = config["excel_loader"]["smb_share"]
        file_pattern = config["excel_loader"].get("file_pattern", "*.xlsx")
        
        print(f"Data path: {data_path}")
        print(f"File pattern: {file_pattern}")
        
        # We need to discover the file first because load_excel_at_path takes a specific path
        from pathlib import Path
        from dashboard.utils.file_loader import discover_latest_file
        
        latest_file = discover_latest_file(Path(data_path), file_pattern)
        print(f"Loading file: {latest_file}")
        
        # Load data
        # Note: load_excel_at_path returns (df, metadata)
        # We need to pass the excel_loader config part or the whole config?
        # definition: def load_excel_at_path(excel_path: Path, excel_config: Dict[str, object])
        df, _ = load_excel_at_path(latest_file, config["excel_loader"])
        
        print(f"Data loaded. Rows: {len(df)}")
        print(f"Columns: {df.columns.tolist()}")
        
        # Get keywords - try both singular and plural forms found in configs
        rev_kw = config.get("revenue_keywords", config.get("revenue_ledgers", []))
        exp_kw = config.get("expense_keywords", config.get("expense_ledgers", []))
        
        print(f"Revenue Keywords: {len(rev_kw)}")
        print(f"Expense Keywords: {len(exp_kw)}")
        
        # Filter for Revenue
        rev_mask = df['ledger'].str.contains('|'.join(rev_kw), case=False, na=False)
        rev_df = df[rev_mask]
        rev_names = set(rev_df['name'].dropna().unique())
        
        # Filter for Expense
        exp_mask = df['ledger'].str.contains('|'.join(exp_kw), case=False, na=False)
        exp_df = df[exp_mask]
        exp_names = set(exp_df['name'].dropna().unique())
        
        # Convert to strings for comparison and remove empty/whitespace
        rev_names = {str(n).strip() for n in rev_names if str(n).strip()}
        exp_names = {str(n).strip() for n in exp_names if str(n).strip()}
        
        intersection = rev_names.intersection(exp_names)
        
        print("\n=== Analysis Results ===")
        print(f"Unique Client Names (Revenue side): {len(rev_names)}")
        print(f"Unique Vendor Names (Expense side): {len(exp_names)}")
        print(f"Names appearing in BOTH (Overlap): {len(intersection)}")
        
        if intersection:
            print("\nTop 10 Overlapping Names:")
            for name in sorted(list(intersection))[:10]:
                print(f"- {name}")
                
            # Random sample of profit calculation for an intersection
            sample_name = list(intersection)[0]
            rev_amt = rev_df[rev_df['name'].str.strip() == sample_name]['amount'].sum()
            exp_amt = exp_df[exp_df['name'].str.strip() == sample_name]['amount'].sum()
            print(f"\nExample Profit Check for '{sample_name}':")
            print(f"  Revenue: {rev_amt:,.2f}")
            print(f"  Expense: {exp_amt:,.2f}")
            print(f"  Profit:  {(rev_amt - exp_amt):,.2f}")
        else:
            print("\nNo overlap found between Revenue and Expense names.")
            print("Conclusion: 'Profit by Client' is likely not possible as Expenses are not tagged with Client names.")
            
        print("\nTop 10 Revenue Clients:")
        top_clients = rev_df.groupby('name')['amount'].sum().sort_values(ascending=False).head(10)
        for name, amt in top_clients.items():
            print(f"- {name}: {amt:,.2f}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    explore_names()
