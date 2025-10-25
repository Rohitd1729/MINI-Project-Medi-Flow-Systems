"""
Routes for chatbot training, feedback, and analytics
"""

from flask import Blueprint, request, jsonify
from routes.auth_routes import token_required
from chatbot.training_system import ChatbotTrainingSystem

training_bp = Blueprint('chatbot_training', __name__)

# Initialize training system
training_system = ChatbotTrainingSystem()

@training_bp.route('/feedback', methods=['POST'])
def submit_feedback():
    """Submit user feedback for a chatbot response"""
    try:
        data = request.get_json()
        
        if not data or 'log_id' not in data or 'feedback_type' not in data:
            return jsonify({'message': 'log_id and feedback_type are required'}), 400
        
        log_id = data['log_id']
        feedback_type = data['feedback_type']
        feedback_data = data.get('feedback_data', {})
        
        # Valid feedback types
        valid_types = ['rating', 'intent_correction', 'drug_correction', 'helpful', 'not_helpful']
        if feedback_type not in valid_types:
            return jsonify({'message': f'Invalid feedback_type. Must be one of: {", ".join(valid_types)}'}), 400
        
        # Record feedback
        success = training_system.record_feedback(log_id, feedback_type, feedback_data)
        
        if success:
            return jsonify({
                'message': 'Feedback recorded successfully',
                'log_id': log_id
            }), 200
        else:
            return jsonify({'message': 'Error recording feedback'}), 500
            
    except Exception as e:
        return jsonify({'message': 'Error processing feedback', 'error': str(e)}), 500

@training_bp.route('/analytics', methods=['GET'])
@token_required
def get_analytics(current_user):
    """Get chatbot performance analytics (Admin only)"""
    try:
        insights = training_system.get_training_insights()
        return jsonify(insights), 200
    except Exception as e:
        return jsonify({'message': 'Error retrieving analytics', 'error': str(e)}), 500

@training_bp.route('/analytics/intent-accuracy', methods=['GET'])
@token_required
def get_intent_accuracy(current_user):
    """Get intent classification accuracy metrics"""
    try:
        intent = request.args.get('intent')
        accuracy = training_system.get_intent_accuracy(intent)
        return jsonify(accuracy), 200
    except Exception as e:
        return jsonify({'message': 'Error retrieving intent accuracy', 'error': str(e)}), 500

@training_bp.route('/analytics/drug-recognition', methods=['GET'])
@token_required
def get_drug_recognition_accuracy(current_user):
    """Get drug name recognition accuracy metrics"""
    try:
        accuracy = training_system.get_drug_recognition_accuracy()
        return jsonify(accuracy), 200
    except Exception as e:
        return jsonify({'message': 'Error retrieving drug recognition accuracy', 'error': str(e)}), 500

@training_bp.route('/analytics/ratings', methods=['GET'])
@token_required
def get_average_ratings(current_user):
    """Get average user ratings for responses"""
    try:
        intent = request.args.get('intent')
        avg_rating = training_system.get_average_rating(intent)
        
        return jsonify({
            'intent': intent if intent else 'all',
            'average_rating': avg_rating
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error retrieving ratings', 'error': str(e)}), 500

@training_bp.route('/export', methods=['GET'])
@token_required
def export_training_data(current_user):
    """Export training data for backup or analysis (Admin only)"""
    try:
        filepath = training_system.export_training_data()
        return jsonify({
            'message': 'Training data exported successfully',
            'filepath': filepath
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error exporting training data', 'error': str(e)}), 500

@training_bp.route('/import', methods=['POST'])
@token_required
def import_training_data(current_user):
    """Import training data from file (Admin only)"""
    try:
        data = request.get_json()
        
        if not data or 'filepath' not in data:
            return jsonify({'message': 'filepath is required'}), 400
        
        filepath = data['filepath']
        success = training_system.import_training_data(filepath)
        
        if success:
            return jsonify({'message': 'Training data imported successfully'}), 200
        else:
            return jsonify({'message': 'Error importing training data'}), 500
            
    except Exception as e:
        return jsonify({'message': 'Error importing training data', 'error': str(e)}), 500
