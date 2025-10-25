from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import all models
from .user import User, Role
from .medicine import Medicine, Company
from .customer import Customer, CartItem
from .order import Order, OrderItem, OrderStatusHistory