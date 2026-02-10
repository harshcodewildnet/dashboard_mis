#!/usr/bin/env python3
"""Quick verification script to test departments API"""

from api.db import SessionLocal, Department, User
from api.main import app
from api.auth import pwd_context
from fastapi.testclient import TestClient

def main():
    print("=" * 60)
    print("Department Dropdown Verification")
    print("=" * 60)
    
    # Check database
    db = SessionLocal()
    try:
        depts = db.query(Department).all()
        users = db.query(User).all()
        
        print(f"\n✓ Database has {len(depts)} departments:")
        for d in depts:
            print(f"   - {d.department_key}: {d.department_name}")
        
        print(f"\n✓ Database has {len(users)} users:")
        for u in users:
            print(f"   - {u.email} ({u.role}) - Dept: {u.department_key or 'ALL'}")
        
        # Test API endpoint
        print("\n" + "=" * 60)
        print("Testing /api/departments endpoint...")
        print("=" * 60)
        
        client = TestClient(app)
        
        # Login as admin
        response = client.post("/token", data={
            "username": "admin@company.com",
            "password": "admin123"
        })
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            print(f"✓ Admin login successful")
            
            # Fetch departments
            dept_response = client.get(
                "/api/departments",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if dept_response.status_code == 200:
                api_depts = dept_response.json()
                print(f"✓ /api/departments returned {len(api_depts)} departments:")
                for d in api_depts:
                    print(f"   - {d['department_key']}: {d['department_name']}")
                print("\n✅ ALL TESTS PASSED! Department dropdown should work now!")
            else:
                print(f"✗ Failed to fetch departments: {dept_response.status_code}")
                print(f"   Response: {dept_response.text}")
        else:
            print(f"✗ Admin login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    finally:
        db.close()
    
    print("=" * 60)

if __name__ == "__main__":
    main()
