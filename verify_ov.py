import requests
import json

BASE_URL = "http://localhost:8000"
TOKEN_URL = "http://localhost:8000/token"

def get_token():
    resp = requests.post(TOKEN_URL, data={"username": "admin@company.com", "password": "admin123"})
    return resp.json()["access_token"]

def test_hierarchy():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/api/expenses/hierarchy", headers=headers)
    data = resp.json()
    
    sections = data.get("sections", [])
    ov = next((s for s in sections if s["sectionType"] == "outsource_vendor_root"), None)
    
    if ov:
        print("Outsource Vendor Expenses Section Found.")
        if ov["children"]:
            l1 = ov["children"][0]
            print(f"Level 1 (Template): {l1['label']}")
            if l1["children"]:
                l2 = l1["children"][0]
                print(f"Level 2 (Cost Center): {l2['label']}")
                if l2["children"]:
                    l3 = l2["children"][0]
                    print(f"Level 3 (Ledger): {l3['label']}")
                    print(f"L3 ID samples: {l3['id']}")
                    return l3["label"]
                else:
                    print("Level 3 not found!")
    else:
        print("Outsource Vendor Expenses Section NOT found!")
    return None

if __name__ == "__main__":
    test_hierarchy()
