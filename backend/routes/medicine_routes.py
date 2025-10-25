from flask import Blueprint, request, jsonify
from models.medicine import Medicine, Company, db
from models.user import User
from routes.auth_routes import token_required, role_required
from datetime import datetime, timedelta

medicine_bp = Blueprint('medicines', __name__)

@medicine_bp.route('/', methods=['GET'])
@token_required
def get_medicines(current_user):
    """Get all medicines with optional filtering"""
    try:
        # Get query parameters
        name_filter = request.args.get('name')
        company_filter = request.args.get('company')
        expiring_soon = request.args.get('expiring_soon', False)
        
        # Build query
        query = Medicine.query.join(Company)
        
        if name_filter:
            query = query.filter(Medicine.name.ilike(f'%{name_filter}%'))
        
        if company_filter:
            query = query.filter(Company.name.ilike(f'%{company_filter}%'))
        
        if expiring_soon:
            # Medicines expiring within 30 days
            threshold_date = datetime.now().date() + timedelta(days=30)
            query = query.filter(Medicine.exp_date <= threshold_date)
        
        medicines = query.all()
        
        result = []
        for med in medicines:
            result.append({
                'medicine_id': med.medicine_id,
                'name': med.name,
                'company': med.company.name,
                'batch_no': med.batch_no,
                'mfg_date': med.mfg_date.isoformat(),
                'exp_date': med.exp_date.isoformat(),
                'quantity': med.quantity,
                'min_stock': med.min_stock,
                'price': float(med.price),
                'days_to_expiry': (med.exp_date - datetime.now().date()).days
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'message': 'Error retrieving medicines', 'error': str(e)}), 500

@medicine_bp.route('/<int:id>', methods=['GET'])
@token_required
def get_medicine(current_user, id):
    """Get a specific medicine by ID"""
    try:
        medicine = Medicine.query.get(id)
        if not medicine:
            return jsonify({'message': 'Medicine not found'}), 404
        
        return jsonify({
            'medicine_id': medicine.medicine_id,
            'name': medicine.name,
            'company_id': medicine.company_id,
            'company': medicine.company.name,
            'batch_no': medicine.batch_no,
            'mfg_date': medicine.mfg_date.isoformat(),
            'exp_date': medicine.exp_date.isoformat(),
            'quantity': medicine.quantity,
            'min_stock': medicine.min_stock,
            'price': float(medicine.price)
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error retrieving medicine', 'error': str(e)}), 500

@medicine_bp.route('/', methods=['POST'])
@token_required
@role_required('Admin')
def create_medicine(current_user):
    """Create a new medicine (Admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields - accept either company_id or company_name
        required_fields = ['name', 'batch_no', 'mfg_date', 'exp_date', 'quantity', 'price']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'Missing required field: {field}'}), 400
        
        # Handle company - either by ID or by name
        company_id = None
        if 'company_id' in data and data['company_id']:
            # Use existing company by ID
            company = Company.query.get(data['company_id'])
            if not company:
                return jsonify({'message': 'Company not found'}), 404
            company_id = company.company_id
        elif 'company_name' in data and data['company_name']:
            # Find or create company by name
            company_name = data['company_name'].strip()
            company = Company.query.filter_by(name=company_name).first()
            if not company:
                # Create new company
                company = Company(name=company_name)
                db.session.add(company)
                db.session.flush()  # Get the company_id
            company_id = company.company_id
        else:
            return jsonify({'message': 'Either company_id or company_name is required'}), 400
        
        # Create new medicine
        new_medicine = Medicine(
            name=data['name'],
            company_id=company_id,
            batch_no=data['batch_no'],
            mfg_date=datetime.strptime(data['mfg_date'], '%Y-%m-%d').date(),
            exp_date=datetime.strptime(data['exp_date'], '%Y-%m-%d').date(),
            quantity=data['quantity'],
            min_stock=data.get('min_stock', 10),
            price=data['price']
        )
        
        db.session.add(new_medicine)
        db.session.commit()
        
        return jsonify({
            'message': 'Medicine created successfully',
            'medicine_id': new_medicine.medicine_id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error creating medicine', 'error': str(e)}), 500

@medicine_bp.route('/<int:id>', methods=['PUT'])
@token_required
@role_required('Admin')
def update_medicine(current_user, id):
    """Update a medicine (Admin only)"""
    try:
        medicine = Medicine.query.get(id)
        if not medicine:
            return jsonify({'message': 'Medicine not found'}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'name' in data:
            medicine.name = data['name']
        
        # Handle company - either by ID or by name
        if 'company_id' in data and data['company_id']:
            company = Company.query.get(data['company_id'])
            if not company:
                return jsonify({'message': 'Company not found'}), 404
            medicine.company_id = data['company_id']
        elif 'company_name' in data and data['company_name']:
            # Find or create company by name
            company_name = data['company_name'].strip()
            company = Company.query.filter_by(name=company_name).first()
            if not company:
                # Create new company
                company = Company(name=company_name)
                db.session.add(company)
                db.session.flush()
            medicine.company_id = company.company_id
        
        if 'batch_no' in data:
            medicine.batch_no = data['batch_no']
        if 'mfg_date' in data:
            medicine.mfg_date = datetime.strptime(data['mfg_date'], '%Y-%m-%d').date()
        if 'exp_date' in data:
            medicine.exp_date = datetime.strptime(data['exp_date'], '%Y-%m-%d').date()
        if 'quantity' in data:
            medicine.quantity = data['quantity']
        if 'min_stock' in data:
            medicine.min_stock = data['min_stock']
        if 'price' in data:
            medicine.price = data['price']
        
        db.session.commit()
        
        return jsonify({'message': 'Medicine updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating medicine', 'error': str(e)}), 500

@medicine_bp.route('/<int:id>', methods=['DELETE'])
@token_required
@role_required('Admin')
def delete_medicine(current_user, id):
    """Delete a medicine (Admin only)"""
    try:
        medicine = Medicine.query.get(id)
        if not medicine:
            return jsonify({'message': 'Medicine not found'}), 404
        
        db.session.delete(medicine)
        db.session.commit()
        
        return jsonify({'message': 'Medicine deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error deleting medicine', 'error': str(e)}), 500

@medicine_bp.route('/low-stock', methods=['GET'])
@token_required
def get_low_stock_medicines(current_user):
    """Get medicines with low stock"""
    try:
        medicines = Medicine.query.filter(
            Medicine.quantity <= Medicine.min_stock
        ).join(Company).all()
        
        result = []
        for med in medicines:
            result.append({
                'medicine_id': med.medicine_id,
                'name': med.name,
                'company': med.company.name,
                'quantity': med.quantity,
                'min_stock': med.min_stock,
                'reorder_needed': med.quantity <= med.min_stock
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'message': 'Error retrieving low stock medicines', 'error': str(e)}), 500