import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def get_token(email, password):
    resp = requests.post(f"{BASE_URL}/token", data={"username": email, "password": password})
    if resp.status_code != 200:
        print(f"Login failed for {email}: {resp.text}")
        return None
    return resp.json()["access_token"]

def verify_access(email, password, expected_count=None, should_see_all=False):
    print(f"\n--- Testing {email} ---")
    token = get_token(email, password)
    if not token:
        return

    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Get Me
    me = requests.get(f"{BASE_URL}/api/me", headers=headers).json()
    print(f"Role: {me['role']}, Dept: {me.get('department_key')}, CC Parent: {me.get('cost_centre_parent')}")

    # 2. Get Rows (Check filtering)
    rows_resp = requests.get(f"{BASE_URL}/api/rows?limit=5000", headers=headers)
    if rows_resp.status_code != 200:
        print(f"Failed to get rows: {rows_resp.text}")
        return
    
    rows = rows_resp.json()["rows"]
    count = len(rows)
    print(f"Visible Rows: {count}")

    if count == 0:
        print("WARNING: No rows visible.")
        return

    # Check content
    cc_parents = set(r.get("cost_centre_parent", "UNKNOWN") for r in rows)
    print(f"Visible Cost Centre Parents: {cc_parents}")

    if should_see_all:
        if len(cc_parents) <= 1:
            print("WARNING: Admin sees only one value? Might be data issue or filter bug.")
        else:
            print("SUCCESS: Admin sees multiple depts.")
    else:
        # Dept Head
        allowed = me['cost_centre_parent']
        # Normalize for comparison
        is_clean = all(str(p).strip() == str(allowed).strip() for p in cc_parents)
        if is_clean:
            print(f"SUCCESS: Only sees {allowed}")
        else:
            print(f"FAIL: Sees unauthorized data! Found: {cc_parents}")

if __name__ == "__main__":
    try:
        # 1. Test Admin (Should see multiple depts)
        verify_access("admin@company.com", "admin123", should_see_all=True)

        # 2. Test DM Head (Should only see Digital Marketing)
        verify_access("dm@company.com", "dm123", should_see_all=False)

        # 3. Test PPC Head (Should only see PPC)
        verify_access("ppc@company.com", "ppc123", should_see_all=False)

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

