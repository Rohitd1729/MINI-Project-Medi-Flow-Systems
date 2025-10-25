import json
from models.chatbot_kb import ChatbotKB, db
import os

def load_drugs_to_db():
    """Load drugs from JSON file to database"""
    try:
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(script_dir, '..', 'drugs.json')
        
        # Read the JSON file
        with open(json_path, 'r') as f:
            drugs_data = json.load(f)
        
        # Clear existing data
        ChatbotKB.query.delete()
        
        # Load drugs into database
        for drug in drugs_data:
            drug_entry = ChatbotKB(
                drug_id=drug['drug_id'],
                name=drug['name'],
                data=drug
            )
            db.session.add(drug_entry)
        
        db.session.commit()
        print(f"Successfully loaded {len(drugs_data)} drugs into the database")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error loading drugs: {str(e)}")
        return False

if __name__ == '__main__':
    load_drugs_to_db()