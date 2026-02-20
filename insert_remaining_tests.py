#!/usr/bin/env python3
"""
Insert remaining 95 tests into the database
"""
import sys
sys.path.insert(0, '/home/suraj-kumar/Desktop/scrapper/scrapper_api')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import settings
from src.models.test_models import Test

# Already in database (5 tests)
existing_tests = [
    'Bilirubin Profile',
    'Iron Profile',
    'Lipid Profile',
    'Thyroid Function Test (TFT)',
    'Complete Blood Count (CBC)',
]

# Remaining 95 tests to insert
remaining_tests = [
    'Hemoglobin (Hb)',
    'Blood Group ABO & Rh Typing',
    'Blood Glucose Fasting',
    'Blood Glucose Post Prandial',
    'HbA1c',
    'Liver Function Test (LFT)',
    'Kidney Function Test (KFT)',
    'Serum Creatinine',
    'Blood Urea (BUN)',
    'Serum Electrolytes',
    'Urine Routine & Microscopy',
    'Urine Albumin',
    'Albumin Creatinine Ratio (ACR)',
    'Thyroid Profile (T3, T4, TSH)',
    'TSH',
    'Free T3',
    'Free T4',
    'Vitamin D (25-OH)',
    'Vitamin B12',
    'Serum Calcium',
    'Serum Phosphorus',
    'Serum Magnesium',
    'Iron Studies',
    'Serum Ferritin',
    'C-Reactive Protein (CRP)',
    'ESR (Erythrocyte Sedimentation Rate)',
    'Prothrombin Time (PT/INR)',
    'APPT',
    'Dengue IgG & IgM',
    'Malaria Antigen Test',
    'Widal Test',
    'Hepatitis B Surface Antigen (HBsAg)',
    'Anti-HCV Antibody',
    'HIV 1 & 2 Antibody',
    'Urine Pregnancy Test',
    'Beta-HCG',
    'PSA (Prostate Specific Antigen)',
    'AFP (Alpha Fetoprotein)',
    'CEA (Carcinoembryonic Antigen)',
    'CA-125',
    'CA-19-9',
    'Troponin-I',
    'CK-MB',
    'BNP (B-Type Natriuretic Peptide)',
    'ECG',
    '2D Echocardiography',
    'Chest X-Ray',
    'Ultrasound Whole Abdomen',
    'Ultrasound Pelvis',
    'Ultrasound Pregnancy',
    'CT Scan Brain',
    'MRI Brain',
    'CT Scan Chest',
    'CT Scan Abdomen',
    'Mammography',
    'DEXA Bone Mineral Density',
    'Pap Smear',
    'Stool Routine Examination',
    'Stool Occult Blood',
    'Blood Culture',
    'Urine Culture & Sensitivity',
    'AFB Smear (ZN Stain)',
    'AFB GeneXpert (TB PCR)',
    'Sputum Culture',
    'COVID-19 RT-PCR',
    'D-Dimer',
    'Procalcitonin',
    'ANA by IFA',
    'Rheumatoid Factor (RF)',
    'Anti-CCP Antibody',
    'Uric Acid',
    'Amylase',
    'Lipase',
    'Electrocardiogram Holter Monitoring',
    'Pulmonary Function Test (PFT)',
    'Allergy Screening Panel (Phadiatop)',
    'Total IgE',
    'Bilirubin Direct',
    'Bilirubin Indirect',
    'Bilirubin (Total + Direct)',
    'Total Bilirubin',
    'Free T3 & T4',
    'Testosterone',
    'Progesterone',
    'Estradiol',
    'Prolactin',
    'Cortisol',
    'DHEA-S',
    'LH (Luteinizing Hormone)',
    'FSH (Follicle Stimulating Hormone)',
    'TSH Full Profile',
    'Albumin',
    'Globulin',
    'A/G Ratio',
    'Total Protein',
    'Glucose',
    'Fasting Blood Sugar',
    'Random Blood Sugar',
]

def insert_remaining_tests():
    """Insert remaining 95 tests into database"""
    engine = create_engine(settings.DATABASE_URL, echo=False)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    print("=" * 60)
    print("  INSERTING REMAINING 95 TESTS")
    print("=" * 60 + "\n")
    
    inserted = 0
    skipped = 0
    
    try:
        for test_name in remaining_tests:
            # Check if already exists
            existing = db.query(Test).filter(Test.test_name == test_name).first()
            
            if not existing:
                new_test = Test(test_name=test_name, is_active=True)
                db.add(new_test)
                inserted += 1
                print(f"✓ Added: {test_name}")
            else:
                skipped += 1
                print(f"✗ Already exists: {test_name}")
        
        # Commit all changes
        db.commit()
        
        # Verify total count
        total = db.query(Test).count()
        
        print("\n" + "=" * 60)
        print(f"✅ INSERTION COMPLETE")
        print("=" * 60)
        print(f"✓ Tests inserted: {inserted}")
        print(f"✗ Tests skipped: {skipped}")
        print(f"📊 Total tests in database: {total}/100")
        
        if total == 100:
            print("\n🎉 All 100 tests successfully loaded!")
        else:
            print(f"\n⚠️  Total is {total}, expected 100")
            print(f"   Missing: {100 - total} tests")
        
    except Exception as e:
        print(f"\n❌ Error during insertion: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    insert_remaining_tests()
