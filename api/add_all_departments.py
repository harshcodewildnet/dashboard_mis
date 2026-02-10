#!/usr/bin/env python3
"""Add all 6 departments to the database"""

import sys
sys.path.insert(0, '/app')

from api.db import SessionLocal, Department

def main():
    db = SessionLocal()
    try:
        print("="*60)
        print("ADDING ALL 6 DEPARTMENTS")
        print("="*60)
        
        # Define all 6 departments
        departments_data = [
            {'k': 'DM', 'n': 'Digital Marketing', 'c': 'Digital Marketing'},
            {'k': 'INT_DM', 'n': 'International D M', 'c': 'International D M'},
            {'k': 'PPC', 'n': 'PPC', 'c': 'PPC'},
            {'k': 'SA', 'n': 'Staff Augmentation', 'c': 'Staff Augmentation'},
            {'k': 'OH', 'n': 'Overhead', 'c': 'Overhead'},
            {'k': 'WE', 'n': 'Wildnet Edge', 'c': 'Wildnet Edge'}
        ]
        
        # Add departments
        print("\nAdding departments...")
        print("-"*60)
        added_count = 0
        for d in departments_data:
            existing = db.query(Department).filter(Department.department_key == d['k']).first()
            if not existing:
                dept = Department(
                    department_key=d['k'],
                    department_name=d['n'],
                    cost_centre_parent=d['c']
                )
                db.add(dept)
                print(f"  ✓ Added: {d['n']} ({d['k']})")
                added_count += 1
            else:
                print(f"  - Already exists: {d['n']} ({d['k']})")
        
        db.commit()
        
        # Show final count
        print("\n" + "="*60)
        final_depts = db.query(Department).all()
        print(f"Total departments in database: {len(final_depts)}")
        print("="*60)
        print("\nAll departments:")
        for d in sorted(final_depts, key=lambda x: x.department_name):
            print(f"  • {d.department_key:\u003c10} - {d.department_name}")
        
        print("\n" + "="*60)
        print(f"✅ SUCCESS! {added_count} new departments added.")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return 1
    finally:
        db.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
