from app import create_app
from models import db

def migrate_database():
    """Add new columns to existing tables for customer portal"""
    app = create_app()
    
    with app.app_context():
        # Get database connection
        connection = db.engine.connect()
        
        try:
            # Add new columns to medicines table
            print("Adding new columns to medicines table...")
            
            # Check if product_type column exists
            result = connection.execute(db.text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='medicines' AND column_name='product_type'
            """))
            
            if not result.fetchone():
                connection.execute(db.text("""
                    ALTER TABLE medicines 
                    ADD COLUMN product_type VARCHAR(10) DEFAULT 'OTC'
                """))
                print("✅ Added product_type column")
            else:
                print("✅ product_type column already exists")
            
            # Check if description column exists
            result = connection.execute(db.text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='medicines' AND column_name='description'
            """))
            
            if not result.fetchone():
                connection.execute(db.text("""
                    ALTER TABLE medicines 
                    ADD COLUMN description TEXT
                """))
                print("✅ Added description column")
            else:
                print("✅ description column already exists")
            
            # Check if image_url column exists
            result = connection.execute(db.text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='medicines' AND column_name='image_url'
            """))
            
            if not result.fetchone():
                connection.execute(db.text("""
                    ALTER TABLE medicines 
                    ADD COLUMN image_url VARCHAR(255)
                """))
                print("✅ Added image_url column")
            else:
                print("✅ image_url column already exists")
            
            connection.commit()
            print("\n✅ Database migration completed successfully!")
            print("\nNow run: python add_sample_medicines.py")
            
        except Exception as e:
            connection.rollback()
            print(f"❌ Error during migration: {e}")
        finally:
            connection.close()

if __name__ == '__main__':
    migrate_database()
