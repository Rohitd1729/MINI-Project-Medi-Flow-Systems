from flask import Blueprint, request, jsonify
from models.customer import Customer, CartItem, db
from models.medicine import Medicine
from routes.customer_auth_routes import customer_token_required
from datetime import datetime

customer_cart_bp = Blueprint('customer_cart', __name__)

@customer_cart_bp.route('/cart', methods=['GET'])
@customer_token_required
def get_cart(current_customer):
    """Get customer's shopping cart"""
    try:
        cart_items = CartItem.query.filter_by(customer_id=current_customer.customer_id).all()
        
        result = []
        total = 0
        has_rx_items = False
        
        for item in cart_items:
            medicine = item.medicine
            
            # Check if medicine is still available
            is_available = (
                medicine.quantity >= item.quantity and
                medicine.exp_date > datetime.now().date()
            )
            
            subtotal = float(medicine.price) * item.quantity
            total += subtotal
            
            if medicine.product_type == 'Rx':
                has_rx_items = True
            
            result.append({
                'cart_item_id': item.cart_item_id,
                'medicine_id': medicine.medicine_id,
                'name': medicine.name,
                'company': medicine.company.name,
                'price': float(medicine.price),
                'quantity': item.quantity,
                'subtotal': subtotal,
                'product_type': medicine.product_type,
                'requires_prescription': medicine.product_type == 'Rx',
                'image_url': medicine.image_url or '/static/images/medicine-placeholder.png',
                'in_stock': is_available,
                'available_quantity': medicine.quantity,
                'added_at': item.added_at.isoformat()
            })
        
        return jsonify({
            'cart_items': result,
            'total': round(total, 2),
            'item_count': len(result),
            'requires_prescription': has_rx_items
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Error retrieving cart', 'error': str(e)}), 500

@customer_cart_bp.route('/cart/add', methods=['POST'])
@customer_token_required
def add_to_cart(current_customer):
    """Add item to cart"""
    try:
        data = request.get_json()
        
        if not data.get('medicine_id') or not data.get('quantity'):
            return jsonify({'message': 'Medicine ID and quantity required'}), 400
        
        medicine_id = data['medicine_id']
        quantity = int(data['quantity'])
        
        if quantity <= 0:
            return jsonify({'message': 'Quantity must be greater than 0'}), 400
        
        # Check if medicine exists and is available
        medicine = Medicine.query.get(medicine_id)
        if not medicine:
            return jsonify({'message': 'Medicine not found'}), 404
        
        if medicine.quantity < quantity:
            return jsonify({'message': f'Only {medicine.quantity} units available'}), 400
        
        if medicine.exp_date <= datetime.now().date():
            return jsonify({'message': 'Medicine has expired'}), 400
        
        # Check if item already in cart
        existing_item = CartItem.query.filter_by(
            customer_id=current_customer.customer_id,
            medicine_id=medicine_id
        ).first()
        
        if existing_item:
            # Update quantity
            new_quantity = existing_item.quantity + quantity
            if medicine.quantity < new_quantity:
                return jsonify({'message': f'Only {medicine.quantity} units available'}), 400
            
            existing_item.quantity = new_quantity
            db.session.commit()
            
            return jsonify({
                'message': 'Cart updated successfully',
                'cart_item_id': existing_item.cart_item_id,
                'quantity': existing_item.quantity
            }), 200
        else:
            # Add new item
            new_item = CartItem(
                customer_id=current_customer.customer_id,
                medicine_id=medicine_id,
                quantity=quantity
            )
            db.session.add(new_item)
            db.session.commit()
            
            return jsonify({
                'message': 'Item added to cart',
                'cart_item_id': new_item.cart_item_id
            }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error adding to cart', 'error': str(e)}), 500

@customer_cart_bp.route('/cart/update/<int:cart_item_id>', methods=['PUT'])
@customer_token_required
def update_cart_item(current_customer, cart_item_id):
    """Update cart item quantity"""
    try:
        data = request.get_json()
        
        if 'quantity' not in data:
            return jsonify({'message': 'Quantity required'}), 400
        
        quantity = int(data['quantity'])
        
        if quantity <= 0:
            return jsonify({'message': 'Quantity must be greater than 0'}), 400
        
        cart_item = CartItem.query.filter_by(
            cart_item_id=cart_item_id,
            customer_id=current_customer.customer_id
        ).first()
        
        if not cart_item:
            return jsonify({'message': 'Cart item not found'}), 404
        
        medicine = cart_item.medicine
        
        if medicine.quantity < quantity:
            return jsonify({'message': f'Only {medicine.quantity} units available'}), 400
        
        cart_item.quantity = quantity
        db.session.commit()
        
        return jsonify({
            'message': 'Cart updated successfully',
            'quantity': cart_item.quantity
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating cart', 'error': str(e)}), 500

@customer_cart_bp.route('/cart/remove/<int:cart_item_id>', methods=['DELETE'])
@customer_token_required
def remove_from_cart(current_customer, cart_item_id):
    """Remove item from cart"""
    try:
        cart_item = CartItem.query.filter_by(
            cart_item_id=cart_item_id,
            customer_id=current_customer.customer_id
        ).first()
        
        if not cart_item:
            return jsonify({'message': 'Cart item not found'}), 404
        
        db.session.delete(cart_item)
        db.session.commit()
        
        return jsonify({'message': 'Item removed from cart'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error removing item', 'error': str(e)}), 500

@customer_cart_bp.route('/cart/clear', methods=['DELETE'])
@customer_token_required
def clear_cart(current_customer):
    """Clear entire cart"""
    try:
        CartItem.query.filter_by(customer_id=current_customer.customer_id).delete()
        db.session.commit()
        
        return jsonify({'message': 'Cart cleared successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error clearing cart', 'error': str(e)}), 500

@customer_cart_bp.route('/cart/count', methods=['GET'])
@customer_token_required
def get_cart_count(current_customer):
    """Get number of items in cart"""
    try:
        count = CartItem.query.filter_by(customer_id=current_customer.customer_id).count()
        
        return jsonify({'count': count}), 200
        
    except Exception as e:
        return jsonify({'message': 'Error getting cart count', 'error': str(e)}), 500
