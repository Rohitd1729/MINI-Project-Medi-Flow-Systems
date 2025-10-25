from app import create_app
from models import db
from models.medicine import Medicine, Company
from datetime import datetime, timedelta

def add_sample_medicines():
    """Add sample medicines for testing the customer portal"""
    app = create_app()
    
    with app.app_context():
        # Get companies
        cipla = Company.query.filter_by(name='Cipla').first()
        sun_pharma = Company.query.filter_by(name='Sun Pharma').first()
        dr_reddys = Company.query.filter_by(name="Dr. Reddy's").first()
        lupin = Company.query.filter_by(name='Lupin').first()
        aurobindo = Company.query.filter_by(name='Aurobindo Pharma').first()
        
        if not cipla:
            print("Please run init_db.py first to create companies")
            return
        
        # Check if we already have enough medicines
        existing_count = Medicine.query.count()
        if existing_count >= 10:
            print(f"Already have {existing_count} medicines in database")
            return
        
        # Sample medicines with OTC and Rx classification
        medicines = [
            # OTC Medicines
            Medicine(
                name='Paracetamol 500mg',
                company_id=cipla.company_id,
                batch_no='PAR001',
                mfg_date=datetime.now().date() - timedelta(days=30),
                exp_date=datetime.now().date() + timedelta(days=730),
                quantity=500,
                min_stock=50,
                price=2.50,
                product_type='OTC',
                description='Pain reliever and fever reducer. Effective for headaches, muscle aches, and fever.'
            ),
            Medicine(
                name='Ibuprofen 400mg',
                company_id=sun_pharma.company_id,
                batch_no='IBU001',
                mfg_date=datetime.now().date() - timedelta(days=45),
                exp_date=datetime.now().date() + timedelta(days=720),
                quantity=300,
                min_stock=40,
                price=3.75,
                product_type='OTC',
                description='Anti-inflammatory pain reliever. Good for pain, fever, and inflammation.'
            ),
            Medicine(
                name='Cetirizine 10mg',
                company_id=dr_reddys.company_id,
                batch_no='CET001',
                mfg_date=datetime.now().date() - timedelta(days=20),
                exp_date=datetime.now().date() + timedelta(days=700),
                quantity=400,
                min_stock=50,
                price=1.50,
                product_type='OTC',
                description='Antihistamine for allergy relief. Treats hay fever, hives, and allergic reactions.'
            ),
            Medicine(
                name='Vitamin C 1000mg',
                company_id=lupin.company_id,
                batch_no='VTC001',
                mfg_date=datetime.now().date() - timedelta(days=15),
                exp_date=datetime.now().date() + timedelta(days=800),
                quantity=600,
                min_stock=60,
                price=5.00,
                product_type='OTC',
                description='Immune system support. Antioxidant supplement for overall health.'
            ),
            Medicine(
                name='Antacid Tablets',
                company_id=aurobindo.company_id,
                batch_no='ANT001',
                mfg_date=datetime.now().date() - timedelta(days=25),
                exp_date=datetime.now().date() + timedelta(days=650),
                quantity=350,
                min_stock=40,
                price=2.00,
                product_type='OTC',
                description='Relief from heartburn and acid indigestion. Fast-acting formula.'
            ),
            
            # Prescription (Rx) Medicines
            Medicine(
                name='Amoxicillin 500mg',
                company_id=cipla.company_id,
                batch_no='AMX001',
                mfg_date=datetime.now().date() - timedelta(days=40),
                exp_date=datetime.now().date() + timedelta(days=600),
                quantity=200,
                min_stock=30,
                price=8.50,
                product_type='Rx',
                description='Antibiotic for bacterial infections. Prescription required. Treats respiratory, ear, and urinary tract infections.'
            ),
            Medicine(
                name='Metformin 500mg',
                company_id=sun_pharma.company_id,
                batch_no='MET001',
                mfg_date=datetime.now().date() - timedelta(days=35),
                exp_date=datetime.now().date() + timedelta(days=680),
                quantity=250,
                min_stock=35,
                price=4.25,
                product_type='Rx',
                description='Diabetes medication. Prescription required. Controls blood sugar levels in type 2 diabetes.'
            ),
            Medicine(
                name='Atorvastatin 20mg',
                company_id=dr_reddys.company_id,
                batch_no='ATO001',
                mfg_date=datetime.now().date() - timedelta(days=50),
                exp_date=datetime.now().date() + timedelta(days=620),
                quantity=180,
                min_stock=25,
                price=6.75,
                product_type='Rx',
                description='Cholesterol-lowering medication. Prescription required. Reduces risk of heart disease.'
            ),
            Medicine(
                name='Lisinopril 10mg',
                company_id=lupin.company_id,
                batch_no='LIS001',
                mfg_date=datetime.now().date() - timedelta(days=30),
                exp_date=datetime.now().date() + timedelta(days=700),
                quantity=220,
                min_stock=30,
                price=5.50,
                product_type='Rx',
                description='Blood pressure medication. Prescription required. Treats hypertension and heart failure.'
            ),
            Medicine(
                name='Omeprazole 20mg',
                company_id=aurobindo.company_id,
                batch_no='OME001',
                mfg_date=datetime.now().date() - timedelta(days=28),
                exp_date=datetime.now().date() + timedelta(days=710),
                quantity=300,
                min_stock=40,
                price=7.00,
                product_type='Rx',
                description='Proton pump inhibitor. Prescription required. Treats GERD and stomach ulcers.'
            ),
            
            # More OTC options
            Medicine(
                name='Aspirin 75mg',
                company_id=cipla.company_id,
                batch_no='ASP001',
                mfg_date=datetime.now().date() - timedelta(days=22),
                exp_date=datetime.now().date() + timedelta(days=740),
                quantity=450,
                min_stock=50,
                price=1.75,
                product_type='OTC',
                description='Pain reliever and blood thinner. Low-dose for heart health.'
            ),
            Medicine(
                name='Multivitamin Tablets',
                company_id=sun_pharma.company_id,
                batch_no='MLT001',
                mfg_date=datetime.now().date() - timedelta(days=18),
                exp_date=datetime.now().date() + timedelta(days=820),
                quantity=500,
                min_stock=60,
                price=8.00,
                product_type='OTC',
                description='Complete daily vitamin and mineral supplement. Supports overall health.'
            ),
        ]
        
        db.session.add_all(medicines)
        db.session.commit()
        
        print(f"Successfully added {len(medicines)} sample medicines!")
        print("\nOTC Medicines: 7")
        print("Rx Medicines: 5")
        print("\nCustomers can now browse and purchase medicines!")

if __name__ == '__main__':
    add_sample_medicines()
