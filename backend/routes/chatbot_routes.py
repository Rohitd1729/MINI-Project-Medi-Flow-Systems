from flask import Blueprint, request, jsonify
from models.chatbot_kb import ChatbotKB, ChatbotLog, db
from routes.auth_routes import token_required
from datetime import datetime
import json

# Import advanced chatbot components
from chatbot.nlp_engine import MedicalNLPEngine
from chatbot.inference_engine import MedicalInferenceEngine
from chatbot.training_system import ChatbotTrainingSystem, ConversationContext

chatbot_bp = Blueprint('chatbot', __name__)

# Initialize advanced chatbot components
nlp_engine = MedicalNLPEngine()
inference_engine = MedicalInferenceEngine()
training_system = ChatbotTrainingSystem()

# Store conversation contexts (in production, use Redis or database)
conversation_contexts = {}

def get_or_create_context(user_id: int) -> ConversationContext:
    """Get or create conversation context for user"""
    if user_id not in conversation_contexts:
        conversation_contexts[user_id] = ConversationContext()
    return conversation_contexts[user_id]

@chatbot_bp.route('/query', methods=['POST'])
def chatbot_query():
    """Handle chatbot queries with advanced NLP and inference"""
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'message': 'Query is required'}), 400
        
        query = data['query']
        user_id = data.get('user_id', 0)
        
        # Get conversation context
        context = get_or_create_context(user_id)
        
        # Get all available drugs for NLP processing
        all_drugs = ChatbotKB.query.all()
        drug_names = [drug.name for drug in all_drugs]
        
        # Parse query using advanced NLP engine
        query_analysis = nlp_engine.parse_query(query, drug_names)
        
        # Check if we should use context from previous conversation
        drug_name = query_analysis['drug_name']
        if not drug_name and context.get_last_drug():
            # User might be asking follow-up question about previous drug
            drug_name = context.get_last_drug()
            query_analysis['drug_name'] = drug_name
            query_analysis['from_context'] = True
        
        intent = query_analysis['primary_intent']
        entities = query_analysis['entities']
        confidence = query_analysis['overall_confidence']
        
        # Log the query
        chat_log = ChatbotLog(
            user_id=user_id if user_id > 0 else None,
            query_text=query,
            intent=intent,
            entities=json.dumps(entities),
            timestamp=datetime.utcnow()
        )
        
        db.session.add(chat_log)
        db.session.commit()
        
        # Get suggestions for improvement
        suggestions = training_system.suggest_improvements(query_analysis)
        
        # If no drug found, provide helpful response
        if not drug_name:
            response = "I couldn't identify a specific medication in your query. Please mention the medication name clearly."
            if context.get_last_drug():
                response += f" Were you asking about {context.get_last_drug()}?"
            
            chat_log.response_text = response
            db.session.commit()
            
            return jsonify({
                'answer': response,
                'confidence': confidence,
                'suggestions': suggestions,
                'query_analysis': query_analysis
            }), 200
        
        # Find drug in knowledge base using fuzzy matching
        drug_entry = ChatbotKB.query.filter(
            ChatbotKB.name.ilike(f'%{drug_name}%')
        ).first()
        
        if not drug_entry:
            # Try fuzzy matching with all drugs
            from fuzzywuzzy import process
            best_match = process.extractOne(drug_name, drug_names)
            if best_match and best_match[1] >= 70:
                drug_entry = ChatbotKB.query.filter(
                    ChatbotKB.name == best_match[0]
                ).first()
                response_note = f"(Showing results for '{best_match[0]}')"
            else:
                response = f"I don't have information about '{drug_name}' in my knowledge base. Please check the spelling or try the generic name."
                chat_log.response_text = response
                db.session.commit()
                return jsonify({
                    'answer': response,
                    'confidence': 0.3,
                    'suggestions': ['Check medication spelling', 'Try using generic name', 'Browse available medications']
                }), 200
        else:
            response_note = None
        
        # Generate response using inference engine
        response_data = inference_engine.generate_response(
            intent,
            {'name': drug_entry.name, 'data': drug_entry.data},
            entities
        )
        
        response = response_data['response']
        if response_note:
            response = f"{response_note}\n\n{response}"
        
        response_confidence = response_data.get('confidence', confidence)
        
        # Update log with response
        chat_log.response_text = response
        db.session.commit()
        
        # Add to conversation context
        context.add_turn(query, response, drug_entry.name, intent)
        
        return jsonify({
            'answer': response,
            'confidence': response_confidence,
            'drug_name': drug_entry.name,
            'intent': intent,
            'suggestions': suggestions,
            'query_analysis': query_analysis,
            'log_id': chat_log.id,
            'category': response_data.get('category'),
            'context': context.get_context()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error processing query', 'error': str(e)}), 500

@chatbot_bp.route('/kb', methods=['GET'])
@token_required
def get_knowledge_base(current_user):
    """Get all knowledge base entries (Admin only)"""
    try:
        entries = ChatbotKB.query.all()
        
        result = []
        for entry in entries:
            result.append({
                'id': entry.id,
                'drug_id': entry.drug_id,
                'name': entry.name,
                'data': entry.data,
                'last_updated': entry.last_updated.isoformat()
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'message': 'Error retrieving knowledge base', 'error': str(e)}), 500

@chatbot_bp.route('/kb/<int:id>', methods=['GET'])
@token_required
def get_kb_entry(current_user, id):
    """Get a specific knowledge base entry (Admin only)"""
    try:
        entry = ChatbotKB.query.get(id)
        if not entry:
            return jsonify({'message': 'Entry not found'}), 404
        
        return jsonify({
            'id': entry.id,
            'drug_id': entry.drug_id,
            'name': entry.name,
            'data': entry.data,
            'last_updated': entry.last_updated.isoformat()
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error retrieving entry', 'error': str(e)}), 500

@chatbot_bp.route('/kb', methods=['POST'])
@token_required
def create_kb_entry(current_user):
    """Create a new knowledge base entry (Admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['drug_id', 'name', 'data']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'Missing required field: {field}'}), 400
        
        # Check if entry already exists
        if ChatbotKB.query.filter_by(drug_id=data['drug_id']).first():
            return jsonify({'message': 'Entry with this drug_id already exists'}), 409
        
        # Create new entry
        new_entry = ChatbotKB(
            drug_id=data['drug_id'],
            name=data['name'],
            data=data['data']
        )
        
        db.session.add(new_entry)
        db.session.commit()
        
        return jsonify({
            'message': 'Entry created successfully',
            'id': new_entry.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error creating entry', 'error': str(e)}), 500

@chatbot_bp.route('/kb/<int:id>', methods=['PUT'])
@token_required
def update_kb_entry(current_user, id):
    """Update a knowledge base entry (Admin only)"""
    try:
        entry = ChatbotKB.query.get(id)
        if not entry:
            return jsonify({'message': 'Entry not found'}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'drug_id' in data:
            entry.drug_id = data['drug_id']
        if 'name' in data:
            entry.name = data['name']
        if 'data' in data:
            entry.data = data['data']
        
        entry.last_updated = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'Entry updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating entry', 'error': str(e)}), 500

@chatbot_bp.route('/kb/<int:id>', methods=['DELETE'])
@token_required
def delete_kb_entry(current_user, id):
    """Delete a knowledge base entry (Admin only)"""
    try:
        entry = ChatbotKB.query.get(id)
        if not entry:
            return jsonify({'message': 'Entry not found'}), 404
        
        db.session.delete(entry)
        db.session.commit()
        
        return jsonify({'message': 'Entry deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error deleting entry', 'error': str(e)}), 500

@chatbot_bp.route('/logs', methods=['GET'])
@token_required
def get_chat_logs(current_user):
    """Get chatbot logs (Admin only)"""
    try:
        # Get query parameters
        limit = int(request.args.get('limit', 50))
        
        logs = ChatbotLog.query.order_by(ChatbotLog.timestamp.desc()).limit(limit).all()
        
        result = []
        for log in logs:
            result.append({
                'id': log.id,
                'user_id': log.user_id,
                'query_text': log.query_text,
                'intent': log.intent,
                'entities': log.entities,
                'response_text': log.response_text,
                'timestamp': log.timestamp.isoformat(),
                'flagged': log.flagged
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'message': 'Error retrieving logs', 'error': str(e)}), 500