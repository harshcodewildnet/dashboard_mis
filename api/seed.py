import sys
import os
sys.path.append('/app')

from api.db import SessionLocal, User, Department, init_db
from api.auth import pwd_context

def seed():
    print("Starting DB Initialization...")
    init_db()
    db = SessionLocal()
    
    # Seed Departments
    depts = [
        {'k': 'DM', 'n': 'Digital Marketing', 'c': 'Digital Marketing'},
        {'k': 'OH', 'n': 'Overhead', 'c': 'Overhead'}
    ]
    for d in depts:
        if not db.query(Department).filter(Department.department_key == d['k']).first():
            print(f"Seeding Department: {d['n']}")
            db.add(Department(
                department_key=d['k'],
                department_name=d['n'],
                cost_centre_parent=d['c']
            ))
    
    db.commit()
    
    # Seed Users
    users = [
        {'e': 'admin@company.com', 'p': 'admin123', 'r': 'ADMIN', 'd': None},
        {'e': 'dm@company.com', 'p': 'dm123', 'r': 'DEPT_HEAD', 'd': 'DM'}
    ]
    
    for u in users:
        if not db.query(User).filter(User.email == u['e']).first():
            print(f"Seeding User: {u['e']}")
            hashed = pwd_context.hash(u['p'])
            db.add(User(
                email=u['e'],
                password_hash=hashed,
                role=u['r'],
                department_key=u['d']
            ))
            
    db.commit()
    print("DB Seeded Successfully")

if __name__ == "__main__":
    seed()
