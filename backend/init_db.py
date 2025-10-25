from app import create_app
from models import db
from models.user import Role, User
from models.medicine import Company, Medicine
from models.customer import Customer, CartItem
from models.order import Order, OrderItem, OrderStatusHistory

def init_database():
    """Initialize the database with default data"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if roles already exist
        if Role.query.count() == 0:
            # Create default roles
            admin_role = Role(role_name='Admin')
            manager_role = Role(role_name='Manager')
            staff_role = Role(role_name='Staff')
            
            db.session.add_all([admin_role, manager_role, staff_role])
            db.session.commit()
            print("Roles created successfully")
        
        # Check if admin user exists
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            # Create default admin user
            admin_role = Role.query.filter_by(role_name='Admin').first()
            if admin_role:
                admin_user = User(
                    username='admin',
                    role_id=admin_role.role_id
                )
                admin_user.set_password('admin123')
                db.session.add(admin_user)
                db.session.commit()
                print("Admin user created successfully")
        
        # Check if sample companies exist
        if Company.query.count() == 0:
            # Create sample companies
            companies = [
                Company(name='Cipla', contact='contact@cipla.com', address='Mumbai, India'),
                Company(name='Sun Pharma', contact='info@sunpharma.com', address='Mumbai, India'),
                Company(name='Dr. Reddy\'s', contact='support@drreddys.com', address='Hyderabad, India'),
                Company(name='Lupin', contact='service@lupin.com', address='Mumbai, India'),
                Company(name='Aurobindo Pharma', contact='care@aurobindo.com', address='Hyderabad, India')
            ]
            
            db.session.add_all(companies)
            db.session.commit()
            print("Sample companies created successfully")
        
        print("Database initialization completed!")

if __name__ == '__main__':
    init_database()