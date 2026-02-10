import requests

# Test login endpoint
url = "http://localhost:8000/token"
data = {
    "username": "admin@company.com",
    "password": "admin123"
}

try:
    response = requests.post(url, data=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
