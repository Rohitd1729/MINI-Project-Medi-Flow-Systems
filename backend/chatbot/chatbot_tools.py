"""
Chatbot Tools - Functions for calling internal APIs
These tools allow the chatbot to perform actions by calling existing Flask endpoints
"""

from typing import Dict, List, Optional, Any
from flask import current_app
from models import db, Medicine, Customer, CartItem, Order, OrderItem
from sqlalchemy import or_

class ChatbotTools:
    """
    Tools for the chatbot to interact with the database and perform actions
    """
    
    @staticmethod
    def search_products(query: str, customer_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Search for products in the catalog
        
        Args:
            query: Search term
            customer_id: Optional customer ID for personalization
            
        Returns:
            Dict with products list and metadata
        """
        try:
            # Search in medicine name (case-insensitive)
            # Using ilike for case-insensitive search
            products = Medicine.query.filter(
                Medicine.name.ilike(f'%{query}%')
            ).limit(10).all()
            
            # Debug: Print search results
            print(f"Search query: '{query}', Found {len(products)} products")
            if products:
                print(f"First product: {products[0].name}")
            else:
                # Try to find all medicines to debug
                all_medicines = Medicine.query.limit(5).all()
                print(f"Sample medicines in DB: {[m.name for m in all_medicines]}")
            
            result = {
                'success': True,
                'products': [{
                    'medicine_id': p.medicine_id,
                    'name': p.name,
                    'generic_name': p.name,  # Use name as generic_name
                    'company': p.company.name if p.company else 'Unknown',
                    'price': float(p.price),
                    'quantity': p.quantity,
                    'requires_prescription': p.product_type == 'Rx',
                    'medicine_type': p.product_type
                } for p in products],
                'count': len(products)
            }
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'products': []
            }
    
    @staticmethod
    def get_product_details(product_id: int) -> Dict[str, Any]:
        """
        Get detailed information about a specific product
        
        Args:
            product_id: Medicine ID
            
        Returns:
            Dict with product details
        """
        try:
            product = Medicine.query.get(product_id)
            
            if not product:
                return {
                    'success': False,
                    'error': 'Product not found'
                }
            
            return {
                'success': True,
                'product': {
                    'medicine_id': product.medicine_id,
                    'name': product.name,
                    'generic_name': product.name,  # Use name as generic_name
                    'company': product.company.name if product.company else 'Unknown',
                    'price': float(product.price),
                    'quantity': product.quantity,
                    'requires_prescription': product.product_type == 'Rx',
                    'medicine_type': product.product_type,
                    'batch_no': product.batch_no,
                    'exp_date': product.exp_date.isoformat() if product.exp_date else None,
                    'min_stock': product.min_stock
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def add_to_cart(customer_id: int, medicine_id: int, quantity: int = 1) -> Dict[str, Any]:
        """
        Add item to customer's cart
        
        Args:
            customer_id: Customer ID
            medicine_id: Medicine ID
            quantity: Quantity to add
            
        Returns:
            Dict with success status and cart info
        """
        try:
            # Check if medicine exists and has stock
            medicine = Medicine.query.get(medicine_id)
            if not medicine:
                return {
                    'success': False,
                    'error': 'Medicine not found'
                }
            
            if medicine.quantity < quantity:
                return {
                    'success': False,
                    'error': f'Only {medicine.quantity} units available'
                }
            
            # Check if item already in cart
            cart_item = CartItem.query.filter_by(
                customer_id=customer_id,
                medicine_id=medicine_id
            ).first()
            
            if cart_item:
                # Update quantity
                cart_item.quantity += quantity
            else:
                # Create new cart item
                cart_item = CartItem(
                    customer_id=customer_id,
                    medicine_id=medicine_id,
                    quantity=quantity
                )
                db.session.add(cart_item)
            
            db.session.commit()
            
            # Get updated cart
            cart_data = ChatbotTools.get_cart(customer_id)
            
            return {
                'success': True,
                'message': f'Added {medicine.name} to cart',
                'cart': cart_data
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_cart(customer_id: int) -> Dict[str, Any]:
        """
        Get customer's cart contents
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Dict with cart items and totals
        """
        try:
            cart_items = CartItem.query.filter_by(customer_id=customer_id).all()
            
            items = []
            total = 0
            requires_prescription = False
            
            for item in cart_items:
                medicine = item.medicine
                subtotal = float(medicine.price) * item.quantity
                total += subtotal
                
                is_rx = medicine.product_type == 'Rx'
                if is_rx:
                    requires_prescription = True
                
                items.append({
                    'cart_item_id': item.cart_item_id,
                    'medicine_id': medicine.medicine_id,
                    'medicine_name': medicine.name,
                    'price': float(medicine.price),
                    'quantity': item.quantity,
                    'subtotal': subtotal,
                    'requires_prescription': is_rx
                })
            
            return {
                'success': True,
                'items': items,
                'total': total,
                'item_count': len(items),
                'requires_prescription': requires_prescription
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'items': []
            }
    
    @staticmethod
    def get_customer_orders(customer_id: int, limit: int = 10) -> Dict[str, Any]:
        """
        Get customer's order history
        
        Args:
            customer_id: Customer ID
            limit: Maximum number of orders to return
            
        Returns:
            Dict with orders list
        """
        try:
            orders = Order.query.filter_by(customer_id=customer_id)\
                .order_by(Order.order_date.desc())\
                .limit(limit)\
                .all()
            
            orders_list = []
            for order in orders:
                orders_list.append({
                    'order_id': order.order_id,
                    'order_date': order.order_date.isoformat(),
                    'total_amount': float(order.total_amount),
                    'status': order.status,
                    'prescription_status': order.prescription_status,
                    'requires_prescription': order.requires_prescription
                })
            
            return {
                'success': True,
                'orders': orders_list,
                'count': len(orders_list)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'orders': []
            }
    
    @staticmethod
    def track_order(customer_id: int, order_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Track order status
        
        Args:
            customer_id: Customer ID
            order_id: Optional specific order ID (defaults to latest)
            
        Returns:
            Dict with order tracking information
        """
        try:
            if order_id:
                order = Order.query.filter_by(
                    order_id=order_id,
                    customer_id=customer_id
                ).first()
            else:
                # Get latest order
                order = Order.query.filter_by(customer_id=customer_id)\
                    .order_by(Order.order_date.desc())\
                    .first()
            
            if not order:
                return {
                    'success': False,
                    'error': 'No orders found'
                }
            
            # Define tracking stages
            stages = [
                {'stage': 'Order Placed', 'completed': True},
                {'stage': 'Processing', 'completed': order.status in ['Processing', 'Out for Delivery', 'Delivered']},
                {'stage': 'Out for Delivery', 'completed': order.status in ['Out for Delivery', 'Delivered']},
                {'stage': 'Delivered', 'completed': order.status == 'Delivered'}
            ]
            
            return {
                'success': True,
                'order_id': order.order_id,
                'current_status': order.status,
                'order_date': order.order_date.isoformat(),
                'total_amount': float(order.total_amount),
                'prescription_status': order.prescription_status,
                'tracking_stages': stages
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_customer_profile(customer_id: int) -> Dict[str, Any]:
        """
        Get customer profile information
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Dict with customer details
        """
        try:
            customer = Customer.query.get(customer_id)
            
            if not customer:
                return {
                    'success': False,
                    'error': 'Customer not found'
                }
            
            return {
                'success': True,
                'customer': {
                    'customer_id': customer.customer_id,
                    'name': customer.name,
                    'email': customer.email,
                    'phone': customer.phone,
                    'address': customer.address,
                    'city': customer.city,
                    'state': customer.state,
                    'pincode': customer.pincode
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def check_availability(medicine_id: int) -> Dict[str, Any]:
        """
        Check if a medicine is available in stock
        
        Args:
            medicine_id: Medicine ID
            
        Returns:
            Dict with availability status
        """
        try:
            medicine = Medicine.query.get(medicine_id)
            
            if not medicine:
                return {
                    'success': False,
                    'error': 'Medicine not found'
                }
            
            return {
                'success': True,
                'available': medicine.quantity > 0,
                'quantity': medicine.quantity,
                'medicine_name': medicine.name,
                'price': float(medicine.price)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


    @staticmethod
    def clear_cart(customer_id: int) -> Dict[str, Any]:
        """
        Clear all items from customer's cart
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Dict with success status
        """
        try:
            CartItem.query.filter_by(customer_id=customer_id).delete()
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Cart cleared successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def remove_from_cart(customer_id: int, medicine_id: int) -> Dict[str, Any]:
        """
        Remove specific item from cart
        
        Args:
            customer_id: Customer ID
            medicine_id: Medicine ID to remove
            
        Returns:
            Dict with success status
        """
        try:
            cart_item = CartItem.query.filter_by(
                customer_id=customer_id,
                medicine_id=medicine_id
            ).first()
            
            if not cart_item:
                return {
                    'success': False,
                    'error': 'Item not found in cart'
                }
            
            medicine_name = cart_item.medicine.name
            db.session.delete(cart_item)
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Removed {medicine_name} from cart'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def update_cart_quantity(customer_id: int, medicine_id: int, quantity: int) -> Dict[str, Any]:
        """
        Update quantity of item in cart
        
        Args:
            customer_id: Customer ID
            medicine_id: Medicine ID
            quantity: New quantity
            
        Returns:
            Dict with success status
        """
        try:
            cart_item = CartItem.query.filter_by(
                customer_id=customer_id,
                medicine_id=medicine_id
            ).first()
            
            if not cart_item:
                return {
                    'success': False,
                    'error': 'Item not found in cart'
                }
            
            # Check stock
            medicine = cart_item.medicine
            if medicine.quantity < quantity:
                return {
                    'success': False,
                    'error': f'Only {medicine.quantity} units available'
                }
            
            cart_item.quantity = quantity
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Updated {medicine.name} quantity to {quantity}'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_recommendations(customer_id: Optional[int] = None, category: str = None) -> Dict[str, Any]:
        """
        Get product recommendations
        
        Args:
            customer_id: Optional customer ID for personalized recommendations
            category: Optional category filter
            
        Returns:
            Dict with recommended products
        """
        try:
            # Get popular products (most in stock, good price)
            query = Medicine.query.filter(Medicine.quantity > 0)
            
            if category:
                query = query.filter(Medicine.product_type == category)
            
            # Order by quantity (popularity proxy) and limit to 5
            products = query.order_by(Medicine.quantity.desc()).limit(5).all()
            
            result = {
                'success': True,
                'products': [{
                    'medicine_id': p.medicine_id,
                    'name': p.name,
                    'generic_name': p.name,  # Use name as generic_name
                    'company': p.company.name if p.company else 'Unknown',
                    'price': float(p.price),
                    'quantity': p.quantity,
                    'requires_prescription': p.product_type == 'Rx',
                    'medicine_type': p.product_type
                } for p in products],
                'count': len(products)
            }
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'products': []
            }
    
    @staticmethod
    def find_substitutes(medicine_id: int) -> Dict[str, Any]:
        """
        Find substitute medicines (same generic name, different brand)
        
        Args:
            medicine_id: Medicine ID
            
        Returns:
            Dict with substitute products
        """
        try:
            medicine = Medicine.query.get(medicine_id)
            
            if not medicine:
                return {
                    'success': False,
                    'error': 'Medicine not found'
                }
            
            # Find medicines with same product type (OTC/Rx) as substitutes
            substitutes = Medicine.query.filter(
                Medicine.product_type == medicine.product_type,
                Medicine.medicine_id != medicine_id,
                Medicine.quantity > 0
            ).limit(5).all()
            
            result = {
                'success': True,
                'original': medicine.name,
                'generic_name': medicine.name,  # Use name as generic_name
                'substitutes': [{
                    'medicine_id': s.medicine_id,
                    'name': s.name,
                    'company': s.company.name if s.company else 'Unknown',
                    'price': float(s.price),
                    'price_difference': float(s.price - medicine.price),
                    'quantity': s.quantity,
                    'requires_prescription': s.product_type == 'Rx'
                } for s in substitutes],
                'count': len(substitutes)
            }
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'substitutes': []
            }
    
    @staticmethod
    def cancel_order(customer_id: int, order_id: int) -> Dict[str, Any]:
        """
        Cancel an order (only if status is 'Pending' or 'Processing')
        
        Args:
            customer_id: Customer ID
            order_id: Order ID to cancel
            
        Returns:
            Dict with success status
        """
        try:
            order = Order.query.filter_by(
                order_id=order_id,
                customer_id=customer_id
            ).first()
            
            if not order:
                return {
                    'success': False,
                    'error': 'Order not found'
                }
            
            # Check if order can be cancelled
            if order.status in ['Out for Delivery', 'Delivered']:
                return {
                    'success': False,
                    'error': f'Cannot cancel order with status: {order.status}'
                }
            
            order.status = 'Cancelled'
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Order #{order_id} has been cancelled',
                'order_id': order_id
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def reorder_from_last(customer_id: int) -> Dict[str, Any]:
        """
        Add items from last order to cart
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Dict with success status and items added
        """
        try:
            # Get last order
            last_order = Order.query.filter_by(customer_id=customer_id)\
                .order_by(Order.order_date.desc())\
                .first()
            
            if not last_order:
                return {
                    'success': False,
                    'error': 'No previous orders found'
                }
            
            # Get order items
            order_items = OrderItem.query.filter_by(order_id=last_order.order_id).all()
            
            added_items = []
            for item in order_items:
                # Check if medicine still exists and has stock
                medicine = Medicine.query.get(item.medicine_id)
                if medicine and medicine.quantity >= item.quantity:
                    # Add to cart
                    cart_item = CartItem.query.filter_by(
                        customer_id=customer_id,
                        medicine_id=item.medicine_id
                    ).first()
                    
                    if cart_item:
                        cart_item.quantity += item.quantity
                    else:
                        cart_item = CartItem(
                            customer_id=customer_id,
                            medicine_id=item.medicine_id,
                            quantity=item.quantity
                        )
                        db.session.add(cart_item)
                    
                    added_items.append(medicine.name)
            
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Added {len(added_items)} items from your last order',
                'items': added_items,
                'order_id': last_order.order_id
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }


# Singleton instance
chatbot_tools = ChatbotTools()
