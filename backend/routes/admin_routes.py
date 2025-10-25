from flask import Blueprint, request, jsonify
from models.user import User, Role, db
from models.medicine import Company
from routes.auth_routes import token_required, role_required

admin_bp = Blueprint('admin', __name__)

# User Management

@admin_bp.route('/users', methods=['GET'])
@token_required
@role_required('Admin')
def get_users(current_user):
    """Get all users (Admin only)"""
    try:
        users = User.query.all()
        
        result = []
        for user in users:
            result.append({
                'user_id': user.user_id,
                'username': user.username,
                'role': user.role.role_name,
                'created_at': user.created_at.isoformat()
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'message': 'Error retrieving users', 'error': str(e)}), 500

@admin_bp.route('/users/<int:id>', methods=['GET'])
@token_required
@role_required('Admin')
def get_user(current_user, id):
    """Get a specific user by ID (Admin only)"""
    try:
        user = User.query.get(id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify({
            'user_id': user.user_id,
            'username': user.username,
            'role_id': user.role_id,
            'role': user.role.role_name,
            'created_at': user.created_at.isoformat()
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error retrieving user', 'error': str(e)}), 500

@admin_bp.route('/users', methods=['POST'])
@token_required
@role_required('Admin')
def create_user(current_user):
    """Create a new user (Admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'password', 'role_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'Missing required field: {field}'}), 400
        
        # Check if username already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': 'Username already exists'}), 409
        
        # Check if role exists
        role = Role.query.get(data['role_id'])
        if not role:
            return jsonify({'message': 'Role not found'}), 404
        
        # Create new user
        new_user = User(
            username=data['username'],
            role_id=data['role_id']
        )
        new_user.set_password(data['password'])
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'message': 'User created successfully',
            'user_id': new_user.user_id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error creating user', 'error': str(e)}), 500

@admin_bp.route('/users/<int:id>', methods=['PUT'])
@token_required
@role_required('Admin')
def update_user(current_user, id):
    """Update a user (Admin only)"""
    try:
        user = User.query.get(id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'username' in data:
            # Check if username already exists for another user
            existing_user = User.query.filter_by(username=data['username']).first()
            if existing_user and existing_user.user_id != id:
                return jsonify({'message': 'Username already exists'}), 409
            user.username = data['username']
        
        if 'role_id' in data:
            # Check if role exists
            role = Role.query.get(data['role_id'])
            if not role:
                return jsonify({'message': 'Role not found'}), 404
            user.role_id = data['role_id']
        
        if 'password' in data:
            user.set_password(data['password'])
        
        db.session.commit()
        
        return jsonify({'message': 'User updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating user', 'error': str(e)}), 500

@admin_bp.route('/users/<int:id>', methods=['DELETE'])
@token_required
@role_required('Admin')
def delete_user(current_user, id):
    """Delete a user (Admin only)"""
    try:
        user = User.query.get(id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Prevent deleting the current user
        if user.user_id == current_user.user_id:
            return jsonify({'message': 'Cannot delete yourself'}), 400
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error deleting user', 'error': str(e)}), 500

# Role Management

@admin_bp.route('/roles', methods=['GET'])
@token_required
@role_required('Admin')
def get_roles(current_user):
    """Get all roles (Admin only)"""
    try:
        roles = Role.query.all()
        
        result = []
        for role in roles:
            result.append({
                'role_id': role.role_id,
                'role_name': role.role_name
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'message': 'Error retrieving roles', 'error': str(e)}), 500

# Company Management

@admin_bp.route('/companies', methods=['GET'])
@token_required
def get_companies(current_user):
    """Get all companies"""
    try:
        companies = Company.query.all()
        
        result = []
        for company in companies:
            result.append({
                'company_id': company.company_id,
                'name': company.name,
                'contact': company.contact,
                'address': company.address
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'message': 'Error retrieving companies', 'error': str(e)}), 500

@admin_bp.route('/companies/<int:id>', methods=['GET'])
@token_required
def get_company(current_user, id):
    """Get a specific company by ID"""
    try:
        company = Company.query.get(id)
        if not company:
            return jsonify({'message': 'Company not found'}), 404
        
        return jsonify({
            'company_id': company.company_id,
            'name': company.name,
            'contact': company.contact,
            'address': company.address
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error retrieving company', 'error': str(e)}), 500

@admin_bp.route('/companies', methods=['POST'])
@token_required
@role_required('Admin')
def create_company(current_user):
    """Create a new company (Admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'Missing required field: {field}'}), 400
        
        # Create new company
        new_company = Company(
            name=data['name'],
            contact=data.get('contact', ''),
            address=data.get('address', '')
        )
        
        db.session.add(new_company)
        db.session.commit()
        
        return jsonify({
            'message': 'Company created successfully',
            'company_id': new_company.company_id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error creating company', 'error': str(e)}), 500

@admin_bp.route('/companies/<int:id>', methods=['PUT'])
@token_required
@role_required('Admin')
def update_company(current_user, id):
    """Update a company (Admin only)"""
    try:
        company = Company.query.get(id)
        if not company:
            return jsonify({'message': 'Company not found'}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'name' in data:
            company.name = data['name']
        if 'contact' in data:
            company.contact = data['contact']
        if 'address' in data:
            company.address = data['address']
        
        db.session.commit()
        
        return jsonify({'message': 'Company updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating company', 'error': str(e)}), 500

@admin_bp.route('/companies/<int:id>', methods=['DELETE'])
@token_required
@role_required('Admin')
def delete_company(current_user, id):
    """Delete a company (Admin only)"""
    try:
        company = Company.query.get(id)
        if not company:
            return jsonify({'message': 'Company not found'}), 404
        
        db.session.delete(company)
        db.session.commit()
        
        return jsonify({'message': 'Company deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error deleting company', 'error': str(e)}), 500