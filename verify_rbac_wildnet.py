import requests
import sys

BASE_URL = "http://localhost:8000"

def verify_wildnet_rbac():
    print("="*60)
    print("VERIFYING WILDNET RBAC")
    print("="*60)

    # 1. Login as Wildnet
    login_data = {
        "username": "wildnet@company.com", 
        "password": "wildnet123"
    }
    
    try:
        print("Logging in as wildnet@company.com...")
        resp = requests.post(f"{BASE_URL}/token", data=login_data)
        
        if resp.status_code != 200:
            print(f"Login Failed: {resp.status_code}")
            print(resp.text)
            return False
            
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✓ Login Successful")

        # 2. Fetch Summary Data (which uses _apply_rbac)
        print("\nFetching Summary Data...")
        resp = requests.get(f"{BASE_URL}/api/summary", headers=headers)
        
        if resp.status_code != 200:
            print(f"Fetch Failed: {resp.status_code}")
            return False
            
        data = resp.json()
        print("✓ Data Fetched")
        
        # 3. Check 'by_group' breakdown
        # This endpoint returns 'by_group' which lists cost centres. 
        # If RBAC works, this should ONLY contain 'Wildnet Edge' or be consistent with it.
        # Actually, let's look at the summary totals or top_ledgers depending on what's available.
        # But even better, let's fetch /api/rows and check distinct cost_centre_parent
        
        if "by_group" in data:
            print("\nChecking 'by_group' in Summary:")
            valid = True
            for item in data["by_group"]:
                print(f"  - {item['label']}: {item['value']}")
                if item['label'] != "Wildnet Edge":
                   # Note: Depending on logic, it might show others as 0 or not show them.
                   # _apply_rbac filters the SOURCE dataframe. So others should not exist.
                   # However, if the code fills missing groups with 0, they might appear.
                   # But let's verify rows for absolute certainty.
                   pass

        # 4. Fetch Rows to be certain
        print("\nFetching Rows (First 50)...")
        resp = requests.get(f"{BASE_URL}/api/rows?limit=50", headers=headers)
        rows_data = resp.json()
        
        print(f"Fetched {rows_data['count']} rows.")
        
        departments = set()
        for row in rows_data['rows']:
            if 'cost_centre_parent' in row:
                departments.add(row['cost_centre_parent'])
                
        print("\nUnique Departments found in rows:")
        for d in departments:
            print(f"  • {d}")
            
        if len(departments) == 1 and "Wildnet Edge" in departments:
            print("\n✅ VERIFICATION SUCCESS: Only 'Wildnet Edge' data is visible.")
            return True
        elif len(departments) == 0:
             print("\n⚠️  No data found. This might be correct if Wildnet has no transactions.")
             return True
        else:
            print("\n❌ VERIFICATION FAILED: Found other departments!")
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    verify_wildnet_rbac()
