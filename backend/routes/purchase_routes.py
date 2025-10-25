from flask import Blueprint, request, jsonify
from models.purchase import Purchase, db
from models.medicine import Medicine
from routes.auth_routes import token_required, role_required
from datetime import datetime

purchase_bp = Blueprint('purchases', __name__)

@purchase_bp.route('/', methods=['GET'])
@token_required
def get_purchases(current_user):
    """Get all purchases with optional filtering"""
    try:
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        medicine_id = request.args.get('medicine_id')
        
        # Build query
        query = Purchase.query
        
        if start_date:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(Purchase.date >= start)
        
        if end_date:
            end = datetime.strptime(end_date, '%Y-%m-%d')
            query = query.filter(Purchase.date <= end)
        
        if medicine_id:
            query = query.filter(Purchase.medicine_id == medicine_id)
        
        purchases = query.all()
        
        result = []
        for purchase in purchases:
            result.append({
                'purchase_id': purchase.purchase_id,
                'supplier_id': purchase.supplier_id,
                'medicine_id': purchase.medicine_id,
                'medicine_name': purchase.medicine.name,
                'quantity': purchase.quantity,
                'cost_price': float(purchase.cost_price),
                'total': float(purchase.total),
                'invoice_no': purchase.invoice_no,
                'date': purchase.date.isoformat()
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'message': 'Error retrieving purchases', 'error': str(e)}), 500

@purchase_bp.route('/', methods=['POST'])
@token_required
@role_required('Admin')
def create_purchase(current_user):
    """Create a new purchase (Admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['supplier_id', 'medicine_id', 'quantity', 'cost_price', 'invoice_no']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'Missing required field: {field}'}), 400
        
        # Check if medicine exists
        medicine = Medicine.query.get(data['medicine_id'])
        if not medicine:
            # If medicine doesn't exist, create it
            return jsonify({'message': 'Medicine not found. Please create medicine first.'}), 404
        
        # Calculate total
        total = data['cost_price'] * data['quantity']
        
        # Create new purchase
        new_purchase = Purchase(
            supplier_id=data['supplier_id'],
            medicine_id=data['medicine_id'],
            quantity=data['quantity'],
            cost_price=data['cost_price'],
            total=total,
            invoice_no=data['invoice_no']
        )
        
        # Update medicine stock
        medicine.quantity += data['quantity']
        
        db.session.add(new_purchase)
        db.session.commit()
        
        return jsonify({
            'message': 'Purchase created successfully',
            'purchase_id': new_purchase.purchase_id,
            'total': float(total)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error creating purchase', 'error': str(e)}), 500

@purchase_bp.route('/<int:id>', methods=['GET'])
@token_required
def get_purchase(current_user, id):
    """Get a specific purchase by ID"""
    try:
        purchase = Purchase.query.get(id)
        if not purchase:
            return jsonify({'message': 'Purchase not found'}), 404
        
        return jsonify({
            'purchase_id': purchase.purchase_id,
            'supplier_id': purchase.supplier_id,
            'medicine_id': purchase.medicine_id,
            'medicine_name': purchase.medicine.name,
            'quantity': purchase.quantity,
            'cost_price': float(purchase.cost_price),
            'total': float(purchase.total),
            'invoice_no': purchase.invoice_no,
            'date': purchase.date.isoformat()
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error retrieving purchase', 'error': str(e)}), 500