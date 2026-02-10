#!/usr/bin/env python3
"""Script to update all page components with departmentKey prop"""

import os
import re

pages_dir = "d:/Dashboard-MIS/dashboard_mis/frontend/src/pages"

# Map of files to hook names
updates = {
    "IncomePage.tsx": "useIncome",
    "ExpensePage.tsx": "useExpense",
    "SalesPage.tsx": "useSales",
    "SummaryPage.tsx": "useSummary",
    "LedgerPage.tsx": "useLedger",
    "RowsPage.tsx": "useRows",
}

for filename, hook_name in updates.items():
    filepath = os.path.join(pages_dir, filename)
    
    if not os.path.exists(filepath):
        print(f"⚠ {filename} not found")
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Add prop interface if not exists
    if "interface" not in content or "Props" not in content:
        # Find export function line
        func_match = re.search(r'export function \w+\(\)', content)
        if func_match:
            func_name = filename.replace(".tsx", "")
            # Add interface before function
            interface_code = f"""interface {func_name}Props {{
  departmentKey?: string | null;
}}

"""
            content = content[:func_match.start()] + interface_code + content[func_match.start():]
    
    # Update function signature
    content = re.sub(
        r'(export function \w+)\(\)',
        r'\1({ departmentKey }: \1Props)',
        content,
        count=1
    )
    
    # Update hook call - different patterns for different hooks
    if hook_name in ["useSummary", "useSales", "useLedger", "useRows"]:
        # These hooks already take params object
        content = re.sub(
            rf'{hook_name}\((\{{[^}}]*\}})\)',
            rf'{hook_name}({{ ...\\1, departmentKey }})',
            content
        )
        # Fix the spread syntax
        content = content.replace('{ ...{', '{')
        content = content.replace('}, departmentKey }', ', departmentKey }')
    else:
        # Simple hooks like useHome, useIncome, useExpense
        content = re.sub(
            rf'{hook_name}\(\)',
            rf'{hook_name}(departmentKey)',
            content
        )
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Updated {filename}")
    else:
        print(f"- No changes needed for {filename}")

print("\n✅ All pages updated!")
