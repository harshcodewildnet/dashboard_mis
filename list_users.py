#!/usr/bin/env python3
"""List all users with details for documentation"""

import sys
sys.path.insert(0, '/app')

from api.db import SessionLocal, User, Department

db = SessionLocal()
try:
    users = db.query(User).all()
    print(f"\n{'='*60}")
    print(f"TOTAL USERS IN DATABASE: {len(users)}")
    print(f"{'='*60}\n")
    
    for i, user in enumerate(users, 1):
        print(f"USER {i}:")
        print(f"  Email:      {user.email}")
        print(f"  Password:   admin123")  # Default password for all
        print(f"  Role:       {user.role}")
        print(f"  Department: {user.department_key if user.department_key else 'None (Full Access)'}")
        print(f"  Active:     {user.is_active}")
        
        if user.department_key:
            dept = db.query(Department).filter(Department.department_key == user.department_key).first()
            if dept:
                print(f"  Dept Name:  {dept.department_name}")
                print(f"  Cost Ctr:   {dept.cost_centre_parent}")
        
        print(f"  {'-'*56}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
