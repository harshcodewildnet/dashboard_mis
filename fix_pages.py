#!/usr/bin/env python3
"""Fix the broken function signatures in page files"""

import os
import re

pages_dir = "d:/Dashboard-MIS/dashboard_mis/frontend/src/pages"

# Files to fix
files = [
    "IncomePage.tsx",
    "ExpensePage.tsx",
    "SalesPage.tsx",
    "SummaryPage.tsx",
    "LedgerPage.tsx",
    "RowsPage.tsx", 
]

for filename in files:
    filepath = os.path.join(pages_dir, filename)
    
    if not os.path.exists(filepath):
        print(f"⚠ {filename} not found")
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Fix broken function signature
    content = re.sub(
        r'export function (\w+)\(\{ departmentKey \}: export function (\w+)Props\)',
        r'export function \1({ departmentKey }: \2Props)',
        content
    )
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Fixed {filename}")
    else:
        print(f"- No fix needed for {filename}")

print("\n✅ All pages fixed!")
