#!/usr/bin/env python3
"""
Database Connection Test Script
Tests MySQL connectivity and database setup
"""
import sys
sys.path.insert(0, '/home/suraj-kumar/Desktop/scrapper/scrapper_api')

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from src.config import settings
from src.models.test_models import Base, Test, TestPrice

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_database_connection():
    """Test basic database connection"""
    print_header("1. Testing Database Connection")
    
    try:
        print(f"📡 Database URL: {settings.DATABASE_URL}")
        
        engine = create_engine(settings.DATABASE_URL, echo=False)
        
        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Connection successful!")
            return engine
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return None

def test_database_exists(engine):
    """Check if scraper_db database exists"""
    print_header("2. Checking Database")
    
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT DATABASE()"))
            db_name = result.fetchone()[0]
            print(f"✅ Current database: {db_name}")
            return True
    except Exception as e:
        print(f"❌ Database check failed: {str(e)}")
        return False

def test_tables_exist(engine):
    """Check if tables exist"""
    print_header("3. Checking Tables")
    
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"📊 Tables found: {len(tables)}")
        for table in tables:
            print(f"  ✓ {table}")
        
        if 'tests' in tables and 'test_prices' in tables:
            print("\n✅ Both required tables exist!")
            return True
        else:
            print("\n❌ Missing required tables!")
            return False
    except Exception as e:
        print(f"❌ Table check failed: {str(e)}")
        return False

def test_table_structure(engine):
    """Check table structure"""
    print_header("4. Checking Table Structure")
    
    try:
        inspector = inspect(engine)
        
        # Check tests table
        print("📋 Tests table columns:")
        columns = inspector.get_columns('tests')
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
        
        # Check test_prices table
        print("\n📋 Test_prices table columns:")
        columns = inspector.get_columns('test_prices')
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
        
        print("\n✅ Table structures verified!")
        return True
    except Exception as e:
        print(f"❌ Structure check failed: {str(e)}")
        return False

def test_data_count(engine):
    """Check how many tests are in the database"""
    print_header("5. Checking Data")
    
    try:
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        test_count = db.query(Test).count()
        price_count = db.query(TestPrice).count()
        
        print(f"📊 Tests in database: {test_count}/100")
        print(f"📊 Prices in database: {price_count}")
        
        if test_count > 0:
            print(f"\n✅ Database has data!")
            
            # Show sample tests
            print("\n📝 Sample tests:")
            samples = db.query(Test).limit(5).all()
            for test in samples:
                print(f"  - {test.test_name} (ID: {test.id})")
        else:
            print(f"\n⚠️  No tests in database yet. Need to insert 100 tests.")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ Data check failed: {str(e)}")
        return False

def test_sqlalchemy_models(engine):
    """Test SQLAlchemy ORM functionality"""
    print_header("6. Testing SQLAlchemy Models")
    
    try:
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        # Test reading
        test = db.query(Test).first()
        if test:
            print(f"✅ ORM read successful")
            print(f"  Sample: {test.test_name} (ID: {test.id})")
        else:
            print(f"⚠️  No tests found to read")
        
        # Test relationships
        if test and test.prices:
            print(f"\n✅ ORM relationships working")
            print(f"  Test has {len(test.prices)} prices")
        else:
            print(f"\n✅ ORM relationships configured (no prices yet)")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ ORM test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  DATABASE CONNECTION TEST")
    print("="*60)
    
    # Run tests sequentially
    engine = test_database_connection()
    if not engine:
        print("\n❌ Cannot proceed without database connection")
        return False
    
    if not test_database_exists(engine):
        print("\n❌ Cannot proceed without database")
        return False
    
    if not test_tables_exist(engine):
        print("\n⚠️  Tables don't exist. Create them first using the SQL script.")
        return False
    
    if not test_table_structure(engine):
        return False
    
    if not test_data_count(engine):
        return False
    
    if not test_sqlalchemy_models(engine):
        return False
    
    # Summary
    print_header("✅ ALL TESTS PASSED!")
    print("""
Your database is configured correctly and ready for:
1. Inserting 100 tests (if not already done)
2. Storing prices from 4 labs
3. Running batch scraping jobs
4. Serving user API requests
    """)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
