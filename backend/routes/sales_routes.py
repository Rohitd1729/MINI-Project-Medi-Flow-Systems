from flask import Blueprint, request, jsonify
from models.sale import Sale, db
from models.medicine import Medicine
from routes.auth_routes import token_required, role_required
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import base64

sales_bp = Blueprint('sales', __name__)

@sales_bp.route('/', methods=['GET'])
@token_required
def get_sales(current_user):
    """Get all sales with optional filtering"""
    try:
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        medicine_id = request.args.get('medicine_id')
        
        # Build query
        query = Sale.query
        
        if start_date:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(Sale.date >= start)
        
        if end_date:
            end = datetime.strptime(end_date, '%Y-%m-%d')
            query = query.filter(Sale.date <= end)
        
        if medicine_id:
            query = query.filter(Sale.medicine_id == medicine_id)
        
        sales = query.all()
        
        result = []
        for sale in sales:
            result.append({
                'sale_id': sale.sale_id,
                'medicine_id': sale.medicine_id,
                'medicine_name': sale.medicine.name,
                'quantity': sale.quantity,
                'price': float(sale.price),
                'total': float(sale.total),
                'customer_name': sale.customer_name,
                'date': sale.date.isoformat()
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'message': 'Error retrieving sales', 'error': str(e)}), 500

@sales_bp.route('/', methods=['POST'])
@token_required
def create_sale(current_user):
    """Create a new sale"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['medicine_id', 'quantity', 'customer_name']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'Missing required field: {field}'}), 400
        
        # Check if medicine exists
        medicine = Medicine.query.get(data['medicine_id'])
        if not medicine:
            return jsonify({'message': 'Medicine not found'}), 404
        
        # Check if enough stock is available
        if medicine.quantity < data['quantity']:
            return jsonify({'message': 'Insufficient stock'}), 400
        
        # Calculate total
        total = medicine.price * data['quantity']
        
        # Create new sale
        new_sale = Sale(
            medicine_id=data['medicine_id'],
            quantity=data['quantity'],
            price=medicine.price,
            total=total,
            customer_name=data['customer_name']
        )
        
        # Update medicine stock
        medicine.quantity -= data['quantity']
        
        db.session.add(new_sale)
        db.session.commit()
        
        return jsonify({
            'message': 'Sale created successfully',
            'sale_id': new_sale.sale_id,
            'total': float(total)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error creating sale', 'error': str(e)}), 500

@sales_bp.route('/<int:id>', methods=['GET'])
@token_required
def get_sale(current_user, id):
    """Get a specific sale by ID"""
    try:
        sale = Sale.query.get(id)
        if not sale:
            return jsonify({'message': 'Sale not found'}), 404
        
        return jsonify({
            'sale_id': sale.sale_id,
            'medicine_id': sale.medicine_id,
            'medicine_name': sale.medicine.name,
            'quantity': sale.quantity,
            'price': float(sale.price),
            'total': float(sale.total),
            'customer_name': sale.customer_name,
            'date': sale.date.isoformat()
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error retrieving sale', 'error': str(e)}), 500

@sales_bp.route('/invoice/<int:id>', methods=['GET'])
@token_required
def generate_invoice(current_user, id):
    """Generate PDF invoice for a sale"""
    try:
        sale = Sale.query.get(id)
        if not sale:
            return jsonify({'message': 'Sale not found'}), 404
        
        # Create PDF in memory
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Add content to PDF
        pdf.drawString(100, height - 100, f"Invoice #{sale.sale_id}")
        pdf.drawString(100, height - 120, f"Date: {sale.date.strftime('%Y-%m-%d %H:%M:%S')}")
        pdf.drawString(100, height - 140, f"Customer: {sale.customer_name}")
        pdf.drawString(100, height - 160, "-" * 50)
        pdf.drawString(100, height - 180, f"Item: {sale.medicine.name}")
        pdf.drawString(100, height - 200, f"Quantity: {sale.quantity}")
        pdf.drawString(100, height - 220, f"Price: ${float(sale.price):.2f}")
        pdf.drawString(100, height - 240, f"Total: ${float(sale.total):.2f}")
        
        pdf.save()
        
        # Get PDF data
        buffer.seek(0)
        pdf_data = buffer.read()
        buffer.close()
        
        # Encode as base64 for JSON response
        pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
        
        return jsonify({
            'filename': f'invoice_{sale.sale_id}.pdf',
            'data': pdf_base64
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error generating invoice', 'error': str(e)}), 500