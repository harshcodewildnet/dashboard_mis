import requests
import json

BASE_URL = "http://localhost:8000"

def get_token():
    auth_data = {
        "username": "admin@company.com",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/token", data=auth_data)
    return response.json()["access_token"]

def verify_hierarchy():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    print("Fetching hierarchy...")
    response = requests.get(f"{BASE_URL}/api/expenses/hierarchy", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("Success! Root nodes found:")
        for node in data["hierarchy"]:
            print(f"- {node['label']} (Total: {node['total']:,.2f})")
            if 'children' in node:
                print(f"  Children count: {len(node['children'])}")
                if node['label'] == 'Salary' and node['children']:
                    c = node['children'][0]
                    print(f"    Example Salary Node: {c['label']} (ID: {c.get('empId')})")
    else:
        print(f"Failed! Status: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    try:
        verify_hierarchy()
    except Exception as e:
        print(f"Error: {e}")
