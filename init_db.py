#!/usr/bin/env python3
"""
Database initialization script
Creates all tables and adds sample test data
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import settings
from src.models.test_models import Base, Test

def init_db():
    """Initialize database with tables and sample data"""
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL, echo=True)
        
        # Create all tables
        print("\n" + "="*70)
        print("Creating database tables...")
        print("="*70)
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully")
        
        # Create session
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        try:
            # Add sample tests if they don't exist
            print("\n" + "="*70)
            print("Adding sample test data...")
            print("="*70)
            
            sample_tests = [
                "Complete Blood Count (CBC)",
                "Lipid Profile",
                "Thyroid Function Test (TSH, T3, T4)",
                "Liver Function Test (LFT)",
                "Kidney Function Test (KFT)",
                "Blood Sugar (Fasting)",
                "Blood Sugar (Random)",
                "HbA1c (Glycated Hemoglobin)",
                "Vitamin D (25-OH)",
                "Vitamin B12",
                "Iron Studies",
                "Calcium & Phosphorus",
                "Uric Acid",
                "C-Reactive Protein (CRP)",
                "Prothrombin Time (PT/INR)",
                "Activated Partial Thromboplastin Time (aPTT)",
                "Hemoglobin Electrophoresis",
                "TSH (Thyroid Stimulating Hormone)",
                "Testosterone (Total)",
                "PSA (Prostate Specific Antigen)"
            ]
            
            added_count = 0
            for test_name in sample_tests:
                # Check if test already exists
                existing = session.query(Test).filter(Test.test_name == test_name).first()
                if not existing:
                    test = Test(test_name=test_name, is_active=True)
                    session.add(test)
                    added_count += 1
            
            session.commit()
            print(f"✅ Added {added_count} sample tests")
            
            # Display all tests
            all_tests = session.query(Test).filter(Test.is_active == True).all()
            print(f"\n📋 Total active tests in database: {len(all_tests)}")
            for test in all_tests:
                print(f"   - {test.test_name}")
                
        finally:
            session.close()
        
        print("\n" + "="*70)
        print("✅ Database initialization completed successfully!")
        print("="*70)
        return True
        
    except Exception as e:
        print(f"\n❌ Error initializing database: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_db()
    sys.exit(0 if success else 1)
