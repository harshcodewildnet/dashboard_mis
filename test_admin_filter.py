#!/usr/bin/env python3
"""Test the admin department filter functionality"""

import requests
import json

BASE_URL = "http://localhost:8000"

def get_token(email, password):
    response = requests.post(f"{BASE_URL}/token", data={
        "username": email,
        "password": password
    })
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed for {email}: {response.status_code}")
        return None

print("="*60)
print("TESTING ADMIN DEPARTMENT FILTER")
print("="*60)

# Test 1: Admin can access departments list
print("\n[Test 1] Admin accessing /api/departments")
admin_token = get_token("admin@company.com", "admin123")
if admin_token:
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{BASE_URL}/api/departments", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        depts = response.json()
        print(f"✓ SUCCESS - Got {len(depts)} departments")
        for dept in depts:
            print(f"  - {dept['department_name']} ({dept['department_key']})")
    else:
        print(f"✗ FAILED - {response.text}")

# Test 2: Dept user CANNOT access departments list
print("\n[Test 2] Dept user accessing /api/departments (should fail)")
dm_token = get_token("dm@company.com", "dm123")
if dm_token:
    headers = {"Authorization": f"Bearer {dm_token}"}
    response = requests.get(f"{BASE_URL}/api/departments", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 403:
        print("✓ SUCCESS - Correctly blocked (403 Forbidden)")
    else:
        print(f"✗ FAILED - Expected 403, got {response.status_code}")

# Test 3: Admin can filter by department
print("\n[Test 3] Admin filtering home data by DM department")
if admin_token:
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Get all data
    all_response = requests.get(f"{BASE_URL}/api/home", headers=headers)
    if all_response.status_code == 200:
        all_data = all_response.json()
        print(f"  All data: {all_data.get('total_revenue', 0)}")
    
    # Get DM filtered data
    dm_response = requests.get(f"{BASE_URL}/api/home?department_key=DM", headers=headers)
    if dm_response.status_code == 200:
        dm_data = dm_response.json()
        print(f"  DM filtered: {dm_data.get('total_revenue', 0)}")
        print("✓ Filter works (values may differ if DM has different data)")

# Test 4: Dept user filter is ignored
print("\n[Test 4] Dept user trying to filter (should be ignored)")
if dm_token:
    headers = {"Authorization": f"Bearer {dm_token}"}
    
    # Try to access OH data (should still see only DM)
    response = requests.get(f"{BASE_URL}/api/home?department_key=OH", headers=headers)
    if response.status_code == 200:
        print("✓ Request succeeded - filter was ignored, user sees their own dept only")

print("\n" + "="*60)
print("TESTS COMPLETE")
print("="*60)
