from flask import Flask, send_from_directory
from flask_cors import CORS
from config import Config
from models import db
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Disable strict slashes to prevent redirects
    app.url_map.strict_slashes = False
    
    # Initialize extensions
    db.init_app(app)
    # Configure CORS properly
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # Register blueprints - Staff Portal
    from routes.auth_routes import auth_bp
    from routes.medicine_routes import medicine_bp
    from routes.sales_routes import sales_bp
    from routes.purchase_routes import purchase_bp
    from routes.report_routes import report_bp
    from routes.admin_routes import admin_bp
    from routes.chatbot_routes import chatbot_bp
    from routes.chatbot_routes_v2 import chatbot_v2_bp  # New API-first chatbot
    from routes.chatbot_training_routes import training_bp
    from routes.staff_order_routes import staff_order_bp
    
    # Register blueprints - Customer Portal
    from routes.customer_auth_routes import customer_auth_bp
    from routes.customer_product_routes import customer_product_bp
    from routes.customer_cart_routes import customer_cart_bp
    from routes.customer_order_routes import customer_order_bp
    
    # Staff Portal Routes
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(medicine_bp, url_prefix='/api/medicines')
    app.register_blueprint(sales_bp, url_prefix='/api/sales')
    app.register_blueprint(purchase_bp, url_prefix='/api/purchase')
    app.register_blueprint(report_bp, url_prefix='/api/reports')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(chatbot_bp, url_prefix='/api/chat/old')  # Old expert system (fallback)
    app.register_blueprint(chatbot_v2_bp, url_prefix='/api/chat')  # New API-first chatbot
    app.register_blueprint(training_bp, url_prefix='/api/chat/training')
    app.register_blueprint(staff_order_bp, url_prefix='/api/staff')
    
    # Customer Portal Routes
    app.register_blueprint(customer_auth_bp, url_prefix='/api/customer')
    app.register_blueprint(customer_product_bp, url_prefix='/api/shop')
    app.register_blueprint(customer_cart_bp, url_prefix='/api/customer')
    app.register_blueprint(customer_order_bp, url_prefix='/api/customer')
    
    @app.route('/')
    def index():
        return {'message': 'Medi-Flow Systems API - Smart Management. Better Health.'}
    
    # Serve uploaded prescription files
    @app.route('/uploads/prescriptions/<path:filename>')
    def serve_prescription(filename):
        uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads', 'prescriptions')
        return send_from_directory(uploads_dir, filename)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)