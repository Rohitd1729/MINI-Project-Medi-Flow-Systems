"""
Chatbot Routes V2 - API-First Conversational E-Commerce Assistant
Replaces the old expert system with an action-oriented chatbot
"""

from flask import Blueprint, request, jsonify
from models.chatbot_kb import ChatbotLog, db
from routes.customer_auth_routes import customer_token_required
from datetime import datetime
import json

# Import new chatbot components
from chatbot.chatbot_engine_v2 import chatbot_engine, Intent
from chatbot.chatbot_tools import chatbot_tools

chatbot_v2_bp = Blueprint('chatbot_v2', __name__)

@chatbot_v2_bp.route('/query', methods=['POST'])
def chatbot_query_v2():
    """
    Handle chatbot queries with the new API-first engine
    Supports both authenticated and unauthenticated requests
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'message': 'Query is required'}), 400
        
        query = data['query']
        customer_id = data.get('customer_id')  # Optional, from JWT
        customer_token = data.get('token')  # Optional JWT token
        
        # Detect intent and extract entities
        intent, entity = chatbot_engine.detect_intent(query)
        
        # Initialize response data
        response_data = {
            'intent': intent,
            'entity': entity,
            'requires_auth': False,
            'requires_file_upload': False,
            'interactive_components': []
        }
        
        # Handle different intents
        if intent == Intent.GREETING:
            # Get customer name if logged in
            customer_name = None
            if customer_id:
                profile_result = chatbot_tools.get_customer_profile(customer_id)
                if profile_result['success']:
                    customer_name = profile_result['customer']['name']
            
            response_text = chatbot_engine.format_greeting_response(customer_name)
            response_data['answer'] = response_text
        
        elif intent == Intent.HELP:
            response_text = chatbot_engine.format_help_response()
            response_data['answer'] = response_text
        
        elif intent == Intent.SEARCH_PRODUCT:
            if not entity:
                response_data['answer'] = "What medicine are you looking for?"
            else:
                # Search products
                search_result = chatbot_tools.search_products(entity, customer_id)
                
                if search_result['success']:
                    response_text = chatbot_engine.format_product_response(search_result['products'])
                    response_data['answer'] = response_text
                    response_data['products'] = search_result['products']
                    
                    # Store products in context for follow-up
                    chatbot_engine.update_context('last_products', search_result['products'])
                    
                    # Add interactive components (Add to Cart buttons)
                    if search_result['products']:
                        response_data['interactive_components'] = [{
                            'type': 'product_card',
                            'products': search_result['products']
                        }]
                else:
                    response_data['answer'] = chatbot_engine.format_error_response(search_result['error'])
        
        elif intent == Intent.ADD_TO_CART:
            # Check authentication
            if not customer_id:
                response_data['answer'] = chatbot_engine.format_auth_required_response('add items to your cart')
                response_data['requires_auth'] = True
            else:
                # Extract product ID from query or context
                product_id = chatbot_engine.extract_product_id(query, chatbot_engine.context)
                
                if not product_id and entity:
                    # Try to search for the product first
                    search_result = chatbot_tools.search_products(entity, customer_id)
                    if search_result['success'] and search_result['products']:
                        product_id = search_result['products'][0]['medicine_id']
                
                if not product_id:
                    response_data['answer'] = "Which product would you like to add to your cart? Please specify the product name or ID."
                else:
                    # Add to cart
                    cart_result = chatbot_tools.add_to_cart(customer_id, product_id, quantity=1)
                    
                    if cart_result['success']:
                        response_data['answer'] = cart_result['message'] + f"\n\nYour cart total is now ₹{cart_result['cart']['total']:.2f}."
                        response_data['cart'] = cart_result['cart']
                        response_data['interactive_components'] = [{
                            'type': 'cart_actions',
                            'actions': ['view_cart', 'continue_shopping', 'checkout']
                        }]
                    else:
                        response_data['answer'] = chatbot_engine.format_error_response(cart_result['error'])
        
        elif intent == Intent.VIEW_CART:
            # Check authentication
            if not customer_id:
                response_data['answer'] = chatbot_engine.format_auth_required_response('view your cart')
                response_data['requires_auth'] = True
            else:
                # Get cart
                cart_result = chatbot_tools.get_cart(customer_id)
                
                if cart_result['success']:
                    response_text = chatbot_engine.format_cart_response(cart_result)
                    response_data['answer'] = response_text
                    response_data['cart'] = cart_result
                    
                    if cart_result['items']:
                        response_data['interactive_components'] = [{
                            'type': 'cart_summary',
                            'cart': cart_result
                        }]
                else:
                    response_data['answer'] = chatbot_engine.format_error_response(cart_result['error'])
        
        elif intent == Intent.TRACK_ORDER:
            # Check authentication
            if not customer_id:
                response_data['answer'] = chatbot_engine.format_auth_required_response('track your orders')
                response_data['requires_auth'] = True
            else:
                # Track order
                tracking_result = chatbot_tools.track_order(customer_id)
                
                if tracking_result['success']:
                    response_text = chatbot_engine.format_order_tracking_response(tracking_result)
                    response_data['answer'] = response_text
                    response_data['tracking'] = tracking_result
                    response_data['interactive_components'] = [{
                        'type': 'order_tracking',
                        'tracking_data': tracking_result
                    }]
                else:
                    response_data['answer'] = chatbot_engine.format_error_response(tracking_result['error'])
        
        elif intent == Intent.ORDER_HISTORY:
            # Check authentication
            if not customer_id:
                response_data['answer'] = chatbot_engine.format_auth_required_response('view your order history')
                response_data['requires_auth'] = True
            else:
                # Get order history
                orders_result = chatbot_tools.get_customer_orders(customer_id)
                
                if orders_result['success']:
                    response_text = chatbot_engine.format_order_history_response(orders_result['orders'])
                    response_data['answer'] = response_text
                    response_data['orders'] = orders_result['orders']
                    
                    if orders_result['orders']:
                        response_data['interactive_components'] = [{
                            'type': 'order_list',
                            'orders': orders_result['orders']
                        }]
                else:
                    response_data['answer'] = chatbot_engine.format_error_response(orders_result['error'])
        
        elif intent == Intent.PRESCRIPTION_ORDER:
            # Check authentication
            if not customer_id:
                response_data['answer'] = chatbot_engine.format_auth_required_response('order with prescription')
                response_data['requires_auth'] = True
            else:
                response_text = chatbot_engine.format_prescription_order_response()
                response_data['answer'] = response_text
                response_data['requires_file_upload'] = True
                response_data['interactive_components'] = [{
                    'type': 'file_upload',
                    'accept': '.png,.jpg,.jpeg,.pdf',
                    'max_size': 5242880,  # 5MB
                    'endpoint': '/api/customer/orders/place'
                }]
        
        elif intent == Intent.CHECK_AVAILABILITY:
            if not entity:
                response_data['answer'] = "Which medicine would you like to check availability for?"
            else:
                # Search for the product first
                search_result = chatbot_tools.search_products(entity, customer_id)
                
                if search_result['success'] and search_result['products']:
                    product = search_result['products'][0]
                    if product['quantity'] > 0:
                        response_data['answer'] = f"Yes, **{product['name']}** is available! We have {product['quantity']} units in stock at ₹{product['price']:.2f} each."
                    else:
                        response_data['answer'] = f"Sorry, **{product['name']}** is currently out of stock. Would you like to check similar products?"
                    
                    response_data['products'] = [product]
                else:
                    response_data['answer'] = f"I couldn't find '{entity}' in our catalog. Please check the spelling or try a different name."
        
        elif intent == Intent.PRODUCT_INFO:
            if not entity:
                response_data['answer'] = "Which product would you like to know more about?"
            else:
                # Search for the product
                search_result = chatbot_tools.search_products(entity, customer_id)
                
                if search_result['success'] and search_result['products']:
                    product = search_result['products'][0]
                    response_text = f"**{product['name']}**\n\n"
                    response_text += f"Generic Name: {product['generic_name']}\n"
                    response_text += f"Company: {product['company']}\n"
                    response_text += f"Price: ₹{product['price']:.2f}\n"
                    response_text += f"Type: {'Prescription (Rx)' if product['requires_prescription'] else 'Over-the-Counter (OTC)'}\n"
                    response_text += f"Stock: {product['quantity']} units available\n\n"
                    response_text += "Would you like to add it to your cart?"
                    
                    response_data['answer'] = response_text
                    response_data['products'] = [product]
                    response_data['interactive_components'] = [{
                        'type': 'product_card',
                        'products': [product]
                    }]
                else:
                    response_data['answer'] = f"I couldn't find information about '{entity}'. Please check the spelling."
        
        elif intent == Intent.CLEAR_CART:
            # Check authentication
            if not customer_id:
                response_data['answer'] = chatbot_engine.format_auth_required_response('clear your cart')
                response_data['requires_auth'] = True
            else:
                clear_result = chatbot_tools.clear_cart(customer_id)
                if clear_result['success']:
                    response_data['answer'] = "✅ Your cart has been cleared successfully! Ready to start fresh?"
                else:
                    response_data['answer'] = chatbot_engine.format_error_response(clear_result['error'])
        
        elif intent == Intent.REMOVE_FROM_CART:
            # Check authentication
            if not customer_id:
                response_data['answer'] = chatbot_engine.format_auth_required_response('remove items from cart')
                response_data['requires_auth'] = True
            else:
                if not entity:
                    response_data['answer'] = "Which item would you like to remove from your cart?"
                else:
                    # Search for product
                    search_result = chatbot_tools.search_products(entity, customer_id)
                    if search_result['success'] and search_result['products']:
                        product_id = search_result['products'][0]['medicine_id']
                        remove_result = chatbot_tools.remove_from_cart(customer_id, product_id)
                        if remove_result['success']:
                            response_data['answer'] = f"✅ {remove_result['message']}"
                        else:
                            response_data['answer'] = chatbot_engine.format_error_response(remove_result['error'])
                    else:
                        response_data['answer'] = f"I couldn't find '{entity}' in your cart."
        
        elif intent == Intent.CANCEL_ORDER:
            # Check authentication
            if not customer_id:
                response_data['answer'] = chatbot_engine.format_auth_required_response('cancel orders')
                response_data['requires_auth'] = True
            else:
                # Get latest order or specific order
                orders_result = chatbot_tools.get_customer_orders(customer_id, limit=1)
                if orders_result['success'] and orders_result['orders']:
                    order_id = orders_result['orders'][0]['order_id']
                    cancel_result = chatbot_tools.cancel_order(customer_id, order_id)
                    if cancel_result['success']:
                        response_data['answer'] = f"✅ {cancel_result['message']}"
                    else:
                        response_data['answer'] = chatbot_engine.format_error_response(cancel_result['error'])
                else:
                    response_data['answer'] = "You don't have any orders to cancel."
        
        elif intent == Intent.REORDER:
            # Check authentication
            if not customer_id:
                response_data['answer'] = chatbot_engine.format_auth_required_response('reorder')
                response_data['requires_auth'] = True
            else:
                reorder_result = chatbot_tools.reorder_from_last(customer_id)
                if reorder_result['success']:
                    response_text = f"✅ {reorder_result['message']}\n\n"
                    response_text += "Items added:\n"
                    for item in reorder_result['items']:
                        response_text += f"• {item}\n"
                    response_text += "\nWould you like to view your cart or proceed to checkout?"
                    response_data['answer'] = response_text
                    response_data['interactive_components'] = [{
                        'type': 'cart_actions',
                        'actions': ['view_cart', 'checkout']
                    }]
                else:
                    response_data['answer'] = chatbot_engine.format_error_response(reorder_result['error'])
        
        elif intent == Intent.RECOMMEND_PRODUCTS:
            recommend_result = chatbot_tools.get_recommendations(customer_id)
            if recommend_result['success']:
                response_text = "Here are our top recommended products:\n\n"
                for i, product in enumerate(recommend_result['products'], 1):
                    badge = "Rx" if product['requires_prescription'] else "OTC"
                    response_text += f"{i}. **{product['name']}** - ₹{product['price']:.2f} [{badge}]\n"
                response_text += "\nWould you like to add any of these to your cart?"
                response_data['answer'] = response_text
                response_data['products'] = recommend_result['products']
                response_data['interactive_components'] = [{
                    'type': 'product_card',
                    'products': recommend_result['products']
                }]
            else:
                response_data['answer'] = chatbot_engine.format_error_response(recommend_result['error'])
        
        elif intent == Intent.FIND_SUBSTITUTES:
            if not entity:
                response_data['answer'] = "Which medicine would you like to find substitutes for?"
            else:
                # Search for the product first
                search_result = chatbot_tools.search_products(entity, customer_id)
                if search_result['success'] and search_result['products']:
                    product_id = search_result['products'][0]['medicine_id']
                    substitute_result = chatbot_tools.find_substitutes(product_id)
                    
                    if substitute_result['success']:
                        if substitute_result['count'] > 0:
                            response_text = f"**Substitutes for {substitute_result['original']}**\n\n"
                            response_text += f"Generic Name: {substitute_result['generic_name']}\n\n"
                            response_text += "Alternatives:\n"
                            for i, sub in enumerate(substitute_result['substitutes'], 1):
                                price_diff = sub['price_difference']
                                diff_text = f"₹{abs(price_diff):.2f} {'cheaper' if price_diff < 0 else 'more expensive'}"
                                response_text += f"{i}. **{sub['name']}** - ₹{sub['price']:.2f} ({diff_text})\n"
                            response_text += "\nAll contain the same active ingredient."
                            response_data['answer'] = response_text
                            response_data['products'] = substitute_result['substitutes']
                            response_data['interactive_components'] = [{
                                'type': 'product_card',
                                'products': substitute_result['substitutes']
                            }]
                        else:
                            response_data['answer'] = f"No substitutes found for {substitute_result['original']}."
                    else:
                        response_data['answer'] = chatbot_engine.format_error_response(substitute_result['error'])
                else:
                    response_data['answer'] = f"I couldn't find '{entity}' in our catalog."
        
        elif intent == Intent.CHECKOUT:
            # Check authentication
            if not customer_id:
                response_data['answer'] = chatbot_engine.format_auth_required_response('checkout')
                response_data['requires_auth'] = True
            else:
                cart_result = chatbot_tools.get_cart(customer_id)
                if cart_result['success'] and cart_result['items']:
                    response_text = "Great! Let me take you to checkout.\n\n"
                    response_text += f"**Cart Summary:**\n"
                    response_text += f"• {cart_result['item_count']} item(s)\n"
                    response_text += f"• Total: ₹{cart_result['total']:.2f}\n\n"
                    if cart_result['requires_prescription']:
                        response_text += "⚠️ Your cart contains prescription medicines. You'll need to upload a prescription.\n\n"
                    response_text += "Click below to proceed to checkout."
                    response_data['answer'] = response_text
                    response_data['cart'] = cart_result
                    response_data['interactive_components'] = [{
                        'type': 'checkout_button'
                    }]
                else:
                    response_data['answer'] = "Your cart is empty. Would you like to browse our products?"
        
        elif intent == Intent.DRUG_INFO:
            # Fallback to old expert system for drug information
            # This can be kept for medical information queries
            response_data['answer'] = "For detailed medical information about medicines (dosage, side effects, interactions), please consult our pharmacist or refer to the product information leaflet.\n\n⚠️ **Important**: I cannot provide medical advice. Always consult a healthcare professional."
            response_data['fallback'] = True
        
        else:  # Intent.UNKNOWN
            response_data['answer'] = "I'm not sure I understand. I can help you with:\n\n• Searching for medicines\n• Adding items to cart\n• Tracking orders\n• Ordering with prescription\n\nWhat would you like to do?"
        
        # Log the interaction
        try:
            chat_log = ChatbotLog(
                user_id=customer_id,
                query_text=query,
                intent=intent,
                entities=json.dumps({'entity': entity}),
                response_text=response_data.get('answer', ''),
                timestamp=datetime.utcnow()
            )
            db.session.add(chat_log)
            db.session.commit()
            response_data['log_id'] = chat_log.id
        except Exception as log_error:
            print(f"Error logging chat: {log_error}")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"Chatbot error: {str(e)}")
        return jsonify({
            'message': 'Error processing query',
            'error': str(e),
            'answer': "I encountered an error. Please try again or contact support."
        }), 500


@chatbot_v2_bp.route('/context', methods=['POST'])
def update_context():
    """Update conversation context (for maintaining state)"""
    try:
        data = request.get_json()
        key = data.get('key')
        value = data.get('value')
        
        if key and value:
            chatbot_engine.update_context(key, value)
            return jsonify({'message': 'Context updated'}), 200
        
        return jsonify({'message': 'Key and value required'}), 400
        
    except Exception as e:
        return jsonify({'message': 'Error updating context', 'error': str(e)}), 500


@chatbot_v2_bp.route('/context', methods=['DELETE'])
def clear_context():
    """Clear conversation context"""
    try:
        chatbot_engine.clear_context()
        return jsonify({'message': 'Context cleared'}), 200
    except Exception as e:
        return jsonify({'message': 'Error clearing context', 'error': str(e)}), 500
