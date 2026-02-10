#!/usr/bin/env python3
"""Initialize the database and seed with default users"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, '/app')

from api.db import SessionLocal, User, Department, init_db, Base, engine
from api.auth import pwd_context

def main():
    print("="*50)
    print("Database Initialization Script")
    print("="*50)
    
    # Drop and recreate all tables
    print("\n[1/4] Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)
    print("✓ Tables dropped")
    
    print("\n[2/4] Creating tables...")
    init_db()
    print("✓ Tables created")
    
    db = SessionLocal()
    try:
        # Seed Departments
        print("\n[3/4] Seeding departments...")
        depts = [
            {'k': 'DM', 'n': 'Digital Marketing', 'c': 'Digital Marketing'},
            {'k': 'OH', 'n': 'Overhead', 'c': 'Overhead'}
        ]
        for d in depts:
            dept = Department(
                department_key=d['k'],
                department_name=d['n'],
                cost_centre_parent=d['c']
            )
            db.add(dept)
            print(f"  ✓ Created department: {d['n']}")
        
        db.commit()
        
        # Seed Users
        print("\n[4/4] Seeding users...")
        users = [
            {'e': 'admin@company.com', 'p': 'admin123', 'r': 'ADMIN', 'd': None},
            {'e': 'dm@company.com', 'p': 'dm123', 'r': 'DEPT_HEAD', 'd': 'DM'}
        ]
        
        for u in users:
            hashed = pwd_context.hash(u['p'])
            user = User(
                email=u['e'],
                password_hash=hashed,
                role=u['r'],
                department_key=u['d']
            )
            db.add(user)
            print(f"  ✓ Created user: {u['e']} (password: {u['p']})")
            
        db.commit()
        
        print("\n" + "="*50)
        print("Database initialized successfully!")
        print("="*50)
        print("\nDefault Credentials:")
        print("  Admin: admin@company.com / admin123")
        print("  Dept Head: dm@company.com / dm123")
        print("="*50)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        db.rollback()
        return 1
    finally:
        db.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
