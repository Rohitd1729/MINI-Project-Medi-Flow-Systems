from app import create_app
from models import db
from models.medicine import Medicine

def update_existing_medicines():
    """Update existing medicines with product_type and descriptions"""
    app = create_app()
    
    with app.app_context():
        medicines = Medicine.query.all()
        
        if not medicines:
            print("No medicines found. Run add_sample_medicines.py first.")
            return
        
        print(f"Found {len(medicines)} medicines. Updating...")
        
        # Update each medicine with product_type and description
        for med in medicines:
            # Set default product_type if not set
            if not med.product_type:
                # Make some medicines Rx based on name
                rx_keywords = ['amoxicillin', 'metformin', 'atorvastatin', 'lisinopril', 'omeprazole', 
                               'antibiotic', 'diabetes', 'cholesterol', 'blood pressure']
                
                is_rx = any(keyword in med.name.lower() for keyword in rx_keywords)
                med.product_type = 'Rx' if is_rx else 'OTC'
            
            # Set default description if not set
            if not med.description:
                med.description = f"{med.name} - Quality medicine from {med.company.name}"
            
            # Set default image_url if not set
            if not med.image_url:
                med.image_url = 'https://via.placeholder.com/300x200?text=Medicine'
        
        db.session.commit()
        
        # Count OTC vs Rx
        otc_count = Medicine.query.filter_by(product_type='OTC').count()
        rx_count = Medicine.query.filter_by(product_type='Rx').count()
        
        print(f"\n✅ Updated {len(medicines)} medicines successfully!")
        print(f"   OTC Medicines: {otc_count}")
        print(f"   Rx Medicines: {rx_count}")
        print("\nCustomers can now browse products!")

if __name__ == '__main__':
    update_existing_medicines()
