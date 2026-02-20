#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/suraj-kumar/Desktop/scrapper/scrapper_api')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote
from src.models.test_models import Base, Test

# Build database URL with proper password encoding
username = "root"
password = "Suraj@24!"
host = "127.0.0.1"
port = 3306
database = "scraper_db"

# URL encode the password
encoded_password = quote(password, safe='')
DATABASE_URL = f"mysql+pymysql://{username}:{encoded_password}@{host}:{port}/{database}"

print(f"Connecting to: {DATABASE_URL}")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

tests_list = [
    'Complete Blood Count (CBC)',
    'Hemoglobin (Hb)',
    'Blood Group ABO & Rh Typing',
    'Blood Glucose Fasting',
    'Blood Glucose Post Prandial',
    'HbA1c',
    'Lipid Profile',
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
]

def insert_tests():
    db = SessionLocal()
    try:
        for test_name in tests_list:
            existing = db.query(Test).filter(Test.test_name == test_name).first()
            if not existing:
                new_test = Test(test_name=test_name, is_active=True)
                db.add(new_test)
                print(f"✓ Added: {test_name}")
            else:
                print(f"✗ Already exists: {test_name}")
        
        db.commit()
        print(f"\n✅ Successfully inserted all tests!")
        
        count = db.query(Test).count()
        print(f"📊 Total tests in database: {count}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    insert_tests()
