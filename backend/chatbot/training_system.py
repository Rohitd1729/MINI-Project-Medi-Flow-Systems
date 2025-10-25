"""
Training and Feedback System for Medical Chatbot
Enables learning from user interactions and feedback
"""

from typing import Dict, List, Optional
from datetime import datetime
import json
from collections import defaultdict
import pickle
import os

class ChatbotTrainingSystem:
    """
    Training system that learns from user feedback and improves responses
    Implements reinforcement learning concepts for chatbot improvement
    """
    
    def __init__(self, model_path='chatbot/models'):
        self.model_path = model_path
        self.feedback_data = defaultdict(list)
        self.intent_accuracy = defaultdict(lambda: {'correct': 0, 'total': 0})
        self.drug_recognition_accuracy = defaultdict(lambda: {'correct': 0, 'total': 0})
        self.response_ratings = defaultdict(list)
        
        # Create models directory if it doesn't exist
        os.makedirs(model_path, exist_ok=True)
        
        # Load existing training data
        self.load_training_data()
    
    def record_feedback(self, query_id: int, feedback_type: str, feedback_data: Dict) -> bool:
        """
        Record user feedback for a specific query
        
        Args:
            query_id: ID of the chatbot log entry
            feedback_type: Type of feedback ('rating', 'correction', 'helpful', 'not_helpful')
            feedback_data: Additional feedback information
        
        Returns:
            Success status
        """
        try:
            feedback_entry = {
                'query_id': query_id,
                'feedback_type': feedback_type,
                'feedback_data': feedback_data,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.feedback_data[query_id].append(feedback_entry)
            
            # Update accuracy metrics based on feedback
            if feedback_type == 'intent_correction':
                self._update_intent_accuracy(feedback_data)
            elif feedback_type == 'drug_correction':
                self._update_drug_accuracy(feedback_data)
            elif feedback_type == 'rating':
                self._update_response_rating(feedback_data)
            
            # Save updated training data
            self.save_training_data()
            
            return True
        except Exception as e:
            print(f"Error recording feedback: {str(e)}")
            return False
    
    def _update_intent_accuracy(self, feedback_data: Dict):
        """Update intent classification accuracy metrics"""
        predicted_intent = feedback_data.get('predicted_intent')
        correct_intent = feedback_data.get('correct_intent')
        
        if predicted_intent and correct_intent:
            self.intent_accuracy[predicted_intent]['total'] += 1
            if predicted_intent == correct_intent:
                self.intent_accuracy[predicted_intent]['correct'] += 1
    
    def _update_drug_accuracy(self, feedback_data: Dict):
        """Update drug recognition accuracy metrics"""
        predicted_drug = feedback_data.get('predicted_drug')
        correct_drug = feedback_data.get('correct_drug')
        
        if predicted_drug and correct_drug:
            self.drug_recognition_accuracy[predicted_drug]['total'] += 1
            if predicted_drug.lower() == correct_drug.lower():
                self.drug_recognition_accuracy[predicted_drug]['correct'] += 1
    
    def _update_response_rating(self, feedback_data: Dict):
        """Update response quality ratings"""
        intent = feedback_data.get('intent')
        rating = feedback_data.get('rating', 0)
        
        if intent and rating:
            self.response_ratings[intent].append(rating)
    
    def get_intent_accuracy(self, intent: str = None) -> Dict:
        """Get accuracy metrics for intent classification"""
        if intent:
            data = self.intent_accuracy.get(intent, {'correct': 0, 'total': 0})
            accuracy = (data['correct'] / data['total'] * 100) if data['total'] > 0 else 0
            return {
                'intent': intent,
                'accuracy': round(accuracy, 2),
                'correct': data['correct'],
                'total': data['total']
            }
        else:
            # Return overall accuracy
            total_correct = sum(data['correct'] for data in self.intent_accuracy.values())
            total_queries = sum(data['total'] for data in self.intent_accuracy.values())
            overall_accuracy = (total_correct / total_queries * 100) if total_queries > 0 else 0
            
            return {
                'overall_accuracy': round(overall_accuracy, 2),
                'total_queries': total_queries,
                'by_intent': {
                    intent: self.get_intent_accuracy(intent)
                    for intent in self.intent_accuracy.keys()
                }
            }
    
    def get_drug_recognition_accuracy(self) -> Dict:
        """Get accuracy metrics for drug name recognition"""
        total_correct = sum(data['correct'] for data in self.drug_recognition_accuracy.values())
        total_queries = sum(data['total'] for data in self.drug_recognition_accuracy.values())
        overall_accuracy = (total_correct / total_queries * 100) if total_queries > 0 else 0
        
        return {
            'overall_accuracy': round(overall_accuracy, 2),
            'total_queries': total_queries,
            'correct_recognitions': total_correct
        }
    
    def get_average_rating(self, intent: str = None) -> float:
        """Get average user rating for responses"""
        if intent:
            ratings = self.response_ratings.get(intent, [])
            return round(sum(ratings) / len(ratings), 2) if ratings else 0.0
        else:
            all_ratings = [rating for ratings in self.response_ratings.values() for rating in ratings]
            return round(sum(all_ratings) / len(all_ratings), 2) if all_ratings else 0.0
    
    def get_training_insights(self) -> Dict:
        """Get comprehensive training insights and recommendations"""
        insights = {
            'intent_accuracy': self.get_intent_accuracy(),
            'drug_recognition_accuracy': self.get_drug_recognition_accuracy(),
            'average_rating': self.get_average_rating(),
            'total_feedback_entries': sum(len(feedback) for feedback in self.feedback_data.values()),
            'recommendations': []
        }
        
        # Generate recommendations based on metrics
        if insights['intent_accuracy']['overall_accuracy'] < 80:
            insights['recommendations'].append(
                "Intent classification accuracy is below 80%. Consider adding more training examples."
            )
        
        if insights['drug_recognition_accuracy']['overall_accuracy'] < 85:
            insights['recommendations'].append(
                "Drug recognition accuracy is below 85%. Consider improving fuzzy matching threshold."
            )
        
        if insights['average_rating'] < 3.5:
            insights['recommendations'].append(
                "Average user rating is below 3.5/5. Review response templates and add more detailed information."
            )
        
        # Identify intents with low accuracy
        low_accuracy_intents = [
            intent_data['intent']
            for intent_data in insights['intent_accuracy'].get('by_intent', {}).values()
            if intent_data['accuracy'] < 70 and intent_data['total'] >= 5
        ]
        
        if low_accuracy_intents:
            insights['recommendations'].append(
                f"Low accuracy intents: {', '.join(low_accuracy_intents)}. Add more pattern examples."
            )
        
        return insights
    
    def export_training_data(self, filepath: str = None) -> str:
        """Export training data for analysis or backup"""
        if not filepath:
            filepath = os.path.join(self.model_path, f'training_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        
        export_data = {
            'feedback_data': dict(self.feedback_data),
            'intent_accuracy': dict(self.intent_accuracy),
            'drug_recognition_accuracy': dict(self.drug_recognition_accuracy),
            'response_ratings': dict(self.response_ratings),
            'export_timestamp': datetime.utcnow().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return filepath
    
    def import_training_data(self, filepath: str) -> bool:
        """Import training data from file"""
        try:
            with open(filepath, 'r') as f:
                import_data = json.load(f)
            
            # Merge imported data with existing data
            for query_id, feedback_list in import_data.get('feedback_data', {}).items():
                self.feedback_data[int(query_id)].extend(feedback_list)
            
            # Update accuracy metrics
            for intent, data in import_data.get('intent_accuracy', {}).items():
                self.intent_accuracy[intent]['correct'] += data['correct']
                self.intent_accuracy[intent]['total'] += data['total']
            
            for drug, data in import_data.get('drug_recognition_accuracy', {}).items():
                self.drug_recognition_accuracy[drug]['correct'] += data['correct']
                self.drug_recognition_accuracy[drug]['total'] += data['total']
            
            for intent, ratings in import_data.get('response_ratings', {}).items():
                self.response_ratings[intent].extend(ratings)
            
            self.save_training_data()
            return True
        except Exception as e:
            print(f"Error importing training data: {str(e)}")
            return False
    
    def save_training_data(self):
        """Save training data to disk"""
        try:
            data_file = os.path.join(self.model_path, 'training_data.pkl')
            with open(data_file, 'wb') as f:
                pickle.dump({
                    'feedback_data': dict(self.feedback_data),
                    'intent_accuracy': dict(self.intent_accuracy),
                    'drug_recognition_accuracy': dict(self.drug_recognition_accuracy),
                    'response_ratings': dict(self.response_ratings)
                }, f)
        except Exception as e:
            print(f"Error saving training data: {str(e)}")
    
    def load_training_data(self):
        """Load training data from disk"""
        try:
            data_file = os.path.join(self.model_path, 'training_data.pkl')
            if os.path.exists(data_file):
                with open(data_file, 'rb') as f:
                    data = pickle.load(f)
                    self.feedback_data = defaultdict(list, data.get('feedback_data', {}))
                    self.intent_accuracy = defaultdict(
                        lambda: {'correct': 0, 'total': 0},
                        data.get('intent_accuracy', {})
                    )
                    self.drug_recognition_accuracy = defaultdict(
                        lambda: {'correct': 0, 'total': 0},
                        data.get('drug_recognition_accuracy', {})
                    )
                    self.response_ratings = defaultdict(list, data.get('response_ratings', {}))
        except Exception as e:
            print(f"Error loading training data: {str(e)}")
    
    def suggest_improvements(self, query_analysis: Dict) -> List[str]:
        """Suggest improvements based on query analysis and historical data"""
        suggestions = []
        
        intent = query_analysis.get('primary_intent')
        confidence = query_analysis.get('overall_confidence', 0)
        
        # Low confidence suggestions
        if confidence < 0.6:
            suggestions.append("Query confidence is low. Consider rephrasing with more specific details.")
        
        # Intent-specific suggestions
        intent_accuracy = self.get_intent_accuracy(intent)
        if intent_accuracy['accuracy'] < 75 and intent_accuracy['total'] >= 5:
            suggestions.append(f"The system has lower accuracy for '{intent}' queries. Please verify the response.")
        
        # Drug recognition suggestions
        if not query_analysis.get('drug_name'):
            suggestions.append("No drug name detected. Please mention the specific medication name.")
        elif query_analysis.get('drug_confidence', 0) < 80:
            suggestions.append("Drug name recognition confidence is low. Please verify the spelling.")
        
        return suggestions


class ConversationContext:
    """
    Maintains conversation context for multi-turn dialogues
    """
    
    def __init__(self, max_history=5):
        self.max_history = max_history
        self.history = []
        self.current_drug = None
        self.current_intent = None
        self.user_preferences = {}
    
    def add_turn(self, query: str, response: str, drug: str = None, intent: str = None):
        """Add a conversation turn to history"""
        turn = {
            'query': query,
            'response': response,
            'drug': drug,
            'intent': intent,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.history.append(turn)
        
        # Maintain max history size
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        # Update current context
        if drug:
            self.current_drug = drug
        if intent:
            self.current_intent = intent
    
    def get_context(self) -> Dict:
        """Get current conversation context"""
        return {
            'current_drug': self.current_drug,
            'current_intent': self.current_intent,
            'history_length': len(self.history),
            'recent_drugs': list(set(turn['drug'] for turn in self.history if turn['drug'])),
            'recent_intents': list(set(turn['intent'] for turn in self.history if turn['intent']))
        }
    
    def get_last_drug(self) -> Optional[str]:
        """Get the last mentioned drug in conversation"""
        for turn in reversed(self.history):
            if turn['drug']:
                return turn['drug']
        return None
    
    def clear(self):
        """Clear conversation history"""
        self.history = []
        self.current_drug = None
        self.current_intent = None
