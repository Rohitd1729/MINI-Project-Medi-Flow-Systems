"""
Chatbot 2.0 - API-First Conversational E-Commerce Assistant
A state-aware, action-oriented chatbot that integrates with existing Flask APIs
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

class Intent:
    """Intent types for the chatbot"""
    SEARCH_PRODUCT = "search_product"
    ADD_TO_CART = "add_to_cart"
    VIEW_CART = "view_cart"
    TRACK_ORDER = "track_order"
    ORDER_HISTORY = "order_history"
    PRESCRIPTION_ORDER = "prescription_order"
    CHECK_AVAILABILITY = "check_availability"
    PRODUCT_INFO = "product_info"
    DRUG_INFO = "drug_info"  # Fallback to old system
    GREETING = "greeting"
    HELP = "help"
    
    # NEW ADVANCED FEATURES
    CLEAR_CART = "clear_cart"
    REMOVE_FROM_CART = "remove_from_cart"
    UPDATE_QUANTITY = "update_quantity"
    CANCEL_ORDER = "cancel_order"
    REORDER = "reorder"
    RECOMMEND_PRODUCTS = "recommend_products"
    COMPARE_PRICES = "compare_prices"
    FIND_SUBSTITUTES = "find_substitutes"
    BULK_ADD = "bulk_add"
    CHECKOUT = "checkout"
    
    UNKNOWN = "unknown"

class ChatbotEngineV2:
    """
    New chatbot engine with intent detection and tool-calling capabilities
    """
    
    def __init__(self):
        self.intent_patterns = self._initialize_intent_patterns()
        self.context = {}  # Store conversation context
        
    def _initialize_intent_patterns(self) -> Dict[str, List[str]]:
        """Initialize regex patterns for intent detection"""
        return {
            Intent.SEARCH_PRODUCT: [
                r"(?:do you have|search|find|looking for|need|want)\s+(.+)",
                r"(?:price of|cost of|how much is)\s+(.+)",
                r"(?:show me|get me)\s+(.+)",
            ],
            Intent.ADD_TO_CART: [
                r"add\s+(.+?)\s+to\s+(?:my\s+)?cart",
                r"(?:i want to buy|buy|purchase)\s+(.+)",
                r"add\s+(.+)",
            ],
            Intent.VIEW_CART: [
                r"(?:show|view|check|see)\s+(?:my\s+)?cart",
                r"what'?s?\s+in\s+my\s+cart",
                r"cart\s+(?:items|contents)",
            ],
            Intent.TRACK_ORDER: [
                r"(?:track|where is|status of)\s+(?:my\s+)?order",
                r"order\s+(?:status|tracking)",
                r"where'?s?\s+my\s+(?:order|package|delivery)",
            ],
            Intent.ORDER_HISTORY: [
                r"(?:my\s+)?(?:order\s+)?history",
                r"(?:previous|past|old)\s+orders",
                r"show\s+(?:my\s+)?orders",
            ],
            Intent.PRESCRIPTION_ORDER: [
                r"(?:order|buy|need)\s+(?:with\s+)?(?:my\s+)?prescription",
                r"(?:rx|prescription)\s+(?:order|medicine|drug)",
                r"upload\s+prescription",
            ],
            Intent.CHECK_AVAILABILITY: [
                r"(?:is|are)\s+(.+?)\s+(?:available|in stock)",
                r"(?:do you have|got)\s+(.+?)\s+(?:available|in stock)",
            ],
            Intent.PRODUCT_INFO: [
                r"(?:tell me about|info about|information on|details of)\s+(.+)",
                r"what is\s+(.+)",
            ],
            Intent.DRUG_INFO: [
                r"(?:dosage|dose|side effects|interactions)\s+(?:of|for)?\s*(.+)",
                r"how to take\s+(.+)",
                r"contraindications\s+(?:of|for)?\s*(.+)",
            ],
            Intent.GREETING: [
                r"^(?:hi|hello|hey|good morning|good afternoon|good evening)",
                r"^(?:start|begin)",
            ],
            Intent.HELP: [
                r"help",
                r"what can you do",
                r"how do i",
                r"commands",
            ],
            Intent.CLEAR_CART: [
                r"(?:clear|empty|remove all|delete all)\s+(?:my\s+)?cart",
                r"start over",
                r"reset\s+cart",
            ],
            Intent.REMOVE_FROM_CART: [
                r"remove\s+(.+?)\s+from\s+cart",
                r"delete\s+(.+?)\s+from\s+cart",
                r"take out\s+(.+)",
            ],
            Intent.UPDATE_QUANTITY: [
                r"(?:change|update|set)\s+(?:quantity|qty)\s+(?:of\s+)?(.+?)\s+to\s+(\d+)",
                r"(?:make it|change to)\s+(\d+)\s+(.+)",
            ],
            Intent.CANCEL_ORDER: [
                r"cancel\s+(?:my\s+)?order",
                r"cancel\s+order\s+#?(\d+)",
                r"(?:i want to|need to)\s+cancel",
            ],
            Intent.REORDER: [
                r"(?:reorder|order again|buy again)\s+(?:from\s+)?(?:my\s+)?(?:last|previous)\s+order",
                r"same as last time",
                r"repeat\s+(?:my\s+)?(?:last|previous)\s+order",
            ],
            Intent.RECOMMEND_PRODUCTS: [
                r"(?:recommend|suggest|show me)\s+(?:some\s+)?(?:products|medicines|items)",
                r"what should i (?:buy|get|order)",
                r"(?:popular|best selling|trending)\s+(?:products|medicines)",
            ],
            Intent.COMPARE_PRICES: [
                r"compare\s+(?:prices of\s+)?(.+)",
                r"(?:cheaper|better price)\s+(?:than|for)\s+(.+)",
                r"price comparison",
            ],
            Intent.FIND_SUBSTITUTES: [
                r"(?:substitute|alternative|replacement)\s+(?:for|of)?\s*(.+)",
                r"(?:similar to|like)\s+(.+)",
                r"generic\s+(?:version of|for)\s+(.+)",
            ],
            Intent.BULK_ADD: [
                r"add\s+(.+?)\s+and\s+(.+)",
                r"(?:i need|get me)\s+(.+?),\s*(.+)",
            ],
            Intent.CHECKOUT: [
                r"(?:proceed to|go to|start)\s+checkout",
                r"(?:i want to|ready to)\s+(?:checkout|pay|complete order)",
                r"finish\s+(?:my\s+)?order",
            ],
        }
    
    def detect_intent(self, query: str) -> Tuple[str, Optional[str]]:
        """
        Detect user intent and extract entity from query
        
        Returns:
            Tuple of (intent, entity)
        """
        query_lower = query.lower().strip()
        
        # Check each intent pattern
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, query_lower)
                if match:
                    # Extract entity if captured group exists
                    entity = match.group(1).strip() if match.groups() else None
                    return intent, entity
        
        return Intent.UNKNOWN, None
    
    def extract_product_id(self, query: str, context: Dict) -> Optional[int]:
        """Extract product ID from query or context"""
        # Check if product ID is in context (from previous search)
        if 'last_products' in context:
            # Try to match product name in query with context products
            query_lower = query.lower()
            for product in context['last_products']:
                if product['name'].lower() in query_lower:
                    return product['medicine_id']
        
        # Try to extract numeric ID from query
        match = re.search(r'(?:id|#)\s*(\d+)', query.lower())
        if match:
            return int(match.group(1))
        
        return None
    
    def format_product_response(self, products: List[Dict]) -> str:
        """Format product search results into a conversational response"""
        if not products:
            return "I couldn't find any products matching your search. Would you like to try a different search term?"
        
        if len(products) == 1:
            product = products[0]
            response = f"Yes, we have **{product['name']}** for ₹{product['price']:.2f}. "
            
            if product.get('requires_prescription'):
                response += "This is a **prescription (Rx) medicine**. "
            else:
                response += "This is an **over-the-counter (OTC) medicine**. "
            
            if product.get('quantity', 0) > 0:
                response += f"We have {product['quantity']} units in stock. "
            else:
                response += "Currently out of stock. "
            
            response += "\n\nWould you like to add it to your cart?"
            
        else:
            response = f"I found {len(products)} products:\n\n"
            for i, product in enumerate(products[:5], 1):  # Limit to 5 results
                badge = "Rx" if product.get('requires_prescription') else "OTC"
                response += f"{i}. **{product['name']}** - ₹{product['price']:.2f} [{badge}]\n"
            
            response += "\nWhich one would you like to know more about?"
        
        return response
    
    def format_cart_response(self, cart_data: Dict) -> str:
        """Format cart contents into a conversational response"""
        items = cart_data.get('items', [])
        
        if not items:
            return "Your cart is empty. Would you like to browse our products?"
        
        response = f"You have **{len(items)} item(s)** in your cart:\n\n"
        
        for item in items:
            response += f"• **{item['medicine_name']}** - Qty: {item['quantity']} - ₹{item['subtotal']:.2f}\n"
        
        total = cart_data.get('total', 0)
        response += f"\n**Cart Total: ₹{total:.2f}**\n\n"
        
        # Check if prescription required
        requires_rx = any(item.get('requires_prescription') for item in items)
        if requires_rx:
            response += "⚠️ Your cart contains prescription medicines. You'll need to upload a prescription during checkout.\n\n"
        
        response += "Ready to checkout?"
        
        return response
    
    def format_order_tracking_response(self, tracking_data: Dict) -> str:
        """Format order tracking information"""
        order_id = tracking_data.get('order_id')
        status = tracking_data.get('current_status')
        
        response = f"**Order #{order_id}**\n\n"
        response += f"Current Status: **{status}**\n\n"
        
        stages = tracking_data.get('tracking_stages', [])
        if stages:
            response += "Progress:\n"
            for stage in stages:
                icon = "✅" if stage['completed'] else "⏳"
                response += f"{icon} {stage['stage']}\n"
        
        if tracking_data.get('prescription_status'):
            response += f"\nPrescription Status: **{tracking_data['prescription_status']}**"
        
        return response
    
    def format_order_history_response(self, orders: List[Dict]) -> str:
        """Format order history"""
        if not orders:
            return "You haven't placed any orders yet. Would you like to start shopping?"
        
        response = f"You have **{len(orders)} order(s)**:\n\n"
        
        for order in orders[:5]:  # Show last 5 orders
            response += f"• **Order #{order['order_id']}** - {order['order_date']} - ₹{order['total_amount']:.2f} - Status: {order['status']}\n"
        
        response += "\nWould you like to track any of these orders?"
        
        return response
    
    def format_prescription_order_response(self) -> str:
        """Guide user through prescription order process"""
        response = "I can help you order prescription medicines! Here's how it works:\n\n"
        response += "1. Upload your prescription (PNG, JPG, or PDF)\n"
        response += "2. Our pharmacists will review it\n"
        response += "3. Once approved, we'll add the medicines to your order\n"
        response += "4. You'll receive a confirmation when ready\n\n"
        response += "Please use the file upload button below to submit your prescription."
        
        return response
    
    def format_greeting_response(self, customer_name: Optional[str] = None) -> str:
        """Generate greeting response"""
        if customer_name:
            response = f"Hello {customer_name}! 👋 How can I help you today?\n\n"
        else:
            response = "Hello! 👋 Welcome to Medi-Flow Systems. How can I help you today?\n\n"
        
        response += "I can help you with:\n"
        response += "• 🔍 Search for medicines\n"
        response += "• 🛒 Add items to your cart\n"
        response += "• 📦 Track your orders\n"
        response += "• 💊 Order with prescription\n"
        response += "• ℹ️ Get medicine information\n\n"
        response += "Just ask me anything!"
        
        return response
    
    def format_help_response(self) -> str:
        """Generate help response"""
        response = "**Here's what I can do for you:**\n\n"
        response += "**Shopping:**\n"
        response += "• \"Do you have Paracetamol?\" - Search products\n"
        response += "• \"Add Crocin to cart\" - Add items to cart\n"
        response += "• \"Show my cart\" - View cart contents\n\n"
        response += "**Orders:**\n"
        response += "• \"Track my order\" - Check order status\n"
        response += "• \"Order history\" - View past orders\n"
        response += "• \"Order with prescription\" - Upload Rx\n\n"
        response += "**Information:**\n"
        response += "• \"Tell me about Aspirin\" - Product details\n"
        response += "• \"Dosage of Paracetamol\" - Medicine info\n\n"
        response += "What would you like to do?"
        
        return response
    
    def format_error_response(self, error_message: str) -> str:
        """Format error message"""
        return f"I encountered an issue: {error_message}\n\nPlease try again or contact support if the problem persists."
    
    def format_auth_required_response(self, action: str) -> str:
        """Response when authentication is required"""
        return f"To {action}, you'll need to log in or create an account first.\n\nWould you like me to guide you to the login page?"
    
    def update_context(self, key: str, value: Any):
        """Update conversation context"""
        self.context[key] = value
    
    def get_context(self, key: str) -> Any:
        """Get value from conversation context"""
        return self.context.get(key)
    
    def clear_context(self):
        """Clear conversation context"""
        self.context = {}


# Singleton instance
chatbot_engine = ChatbotEngineV2()
