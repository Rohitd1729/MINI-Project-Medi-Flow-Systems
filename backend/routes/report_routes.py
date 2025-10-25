from flask import Blueprint, request, jsonify
from models.medicine import Medicine, Company, db
from models.sale import Sale
from models.purchase import Purchase
from routes.auth_routes import token_required
from datetime import datetime, timedelta
from sqlalchemy import func
import pandas as pd
import io

report_bp = Blueprint('reports', __name__)

@report_bp.route('/dashboard', methods=['GET'])
@token_required
def dashboard_stats(current_user):
    """Get dashboard statistics"""
    try:
        # Get date range (last 30 days by default)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Total medicines
        total_medicines = Medicine.query.count()
        
        # Low stock medicines
        low_stock_count = Medicine.query.filter(
            Medicine.quantity <= Medicine.min_stock
        ).count()
        
        # Expiring soon (within 30 days)
        expiring_soon_count = Medicine.query.filter(
            Medicine.exp_date <= (datetime.now().date() + timedelta(days=30))
        ).count()
        
        # Total sales in period
        total_sales = db.session.query(func.sum(Sale.total)).filter(
            Sale.date.between(start_date, end_date)
        ).scalar() or 0
        
        # Total purchases in period
        total_purchases = db.session.query(func.sum(Purchase.total)).filter(
            Purchase.date.between(start_date, end_date)
        ).scalar() or 0
        
        return jsonify({
            'total_medicines': total_medicines,
            'low_stock_medicines': low_stock_count,
            'expiring_soon': expiring_soon_count,
            'sales_period_total': float(total_sales),
            'purchases_period_total': float(total_purchases)
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error retrieving dashboard stats', 'error': str(e)}), 500

@report_bp.route('/sales-summary', methods=['GET'])
@token_required
def sales_summary(current_user):
    """Get sales summary"""
    try:
        # Get query parameters
        period = request.args.get('period', 'monthly')  # daily, weekly, monthly
        limit = int(request.args.get('limit', 10))
        
        if period == 'daily':
            date_format = '%Y-%m-%d'
            group_by = func.date_trunc('day', Sale.date)
        elif period == 'weekly':
            date_format = 'Week %W, %Y'
            group_by = func.date_trunc('week', Sale.date)
        else:  # monthly
            date_format = '%Y-%m'
            group_by = func.date_trunc('month', Sale.date)
        
        # Query sales grouped by period
        sales_data = db.session.query(
            group_by.label('period'),
            func.sum(Sale.total).label('total_sales'),
            func.count(Sale.sale_id).label('transaction_count')
        ).group_by(group_by).order_by(group_by.desc()).limit(limit).all()
        
        result = []
        for row in sales_data:
            result.append({
                'period': row.period.strftime(date_format) if row.period else None,
                'total_sales': float(row.total_sales),
                'transaction_count': row.transaction_count
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'message': 'Error retrieving sales summary', 'error': str(e)}), 500

@report_bp.route('/top-medicines', methods=['GET'])
@token_required
def top_medicines(current_user):
    """Get top selling medicines"""
    try:
        limit = int(request.args.get('limit', 10))
        
        # Query top medicines by sales quantity
        top_meds = db.session.query(
            Medicine.name,
            Company.name.label('company'),
            func.sum(Sale.quantity).label('total_quantity'),
            func.sum(Sale.total).label('total_revenue')
        ).join(Sale, Medicine.medicine_id == Sale.medicine_id)\
         .join(Company, Medicine.company_id == Company.company_id)\
         .group_by(Medicine.medicine_id, Medicine.name, Company.name)\
         .order_by(func.sum(Sale.quantity).desc())\
         .limit(limit).all()
        
        result = []
        for row in top_meds:
            result.append({
                'medicine_name': row.name,
                'company': row.company,
                'total_quantity': int(row.total_quantity),
                'total_revenue': float(row.total_revenue)
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'message': 'Error retrieving top medicines', 'error': str(e)}), 500

@report_bp.route('/expiry-list', methods=['GET'])
@token_required
def expiry_list(current_user):
    """Get list of medicines expiring soon"""
    try:
        # Medicines expiring within 90 days
        threshold_date = datetime.now().date() + timedelta(days=90)
        
        expiring_meds = Medicine.query.filter(
            Medicine.exp_date <= threshold_date
        ).order_by(Medicine.exp_date.asc()).all()
        
        result = []
        for med in expiring_meds:
            days_to_expiry = (med.exp_date - datetime.now().date()).days
            result.append({
                'medicine_id': med.medicine_id,
                'name': med.name,
                'company': med.company.name,
                'batch_no': med.batch_no,
                'exp_date': med.exp_date.isoformat(),
                'days_to_expiry': days_to_expiry,
                'quantity': med.quantity
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'message': 'Error retrieving expiry list', 'error': str(e)}), 500

@report_bp.route('/export/<table>', methods=['GET'])
@token_required
def export_table(current_user, table):
    """Export table data as CSV"""
    try:
        # Map table names to models
        table_map = {
            'medicines': Medicine,
            'sales': Sale,
            'purchases': Purchase
        }
        
        if table not in table_map:
            return jsonify({'message': 'Invalid table name'}), 400
        
        # Get all records
        model = table_map[table]
        records = model.query.all()
        
        # Convert to DataFrame
        data = []
        if table == 'medicines':
            for record in records:
                data.append({
                    'medicine_id': record.medicine_id,
                    'name': record.name,
                    'company_id': record.company_id,
                    'batch_no': record.batch_no,
                    'mfg_date': record.mfg_date.isoformat(),
                    'exp_date': record.exp_date.isoformat(),
                    'quantity': record.quantity,
                    'min_stock': record.min_stock,
                    'price': float(record.price)
                })
        elif table == 'sales':
            for record in records:
                data.append({
                    'sale_id': record.sale_id,
                    'medicine_id': record.medicine_id,
                    'quantity': record.quantity,
                    'price': float(record.price),
                    'total': float(record.total),
                    'customer_name': record.customer_name,
                    'date': record.date.isoformat()
                })
        elif table == 'purchases':
            for record in records:
                data.append({
                    'purchase_id': record.purchase_id,
                    'supplier_id': record.supplier_id,
                    'medicine_id': record.medicine_id,
                    'quantity': record.quantity,
                    'cost_price': float(record.cost_price),
                    'total': float(record.total),
                    'invoice_no': record.invoice_no,
                    'date': record.date.isoformat()
                })
        
        df = pd.DataFrame(data)
        
        # Convert to CSV
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()
        csv_buffer.close()
        
        return jsonify({
            'filename': f'{table}.csv',
            'data': csv_data
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error exporting data', 'error': str(e)}), 500