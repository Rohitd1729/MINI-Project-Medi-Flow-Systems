"""
Advanced NLP Engine for Medical Chatbot
Handles entity extraction, intent classification, and fuzzy matching
"""

import re
from fuzzywuzzy import fuzz, process
from typing import Dict, List, Tuple, Optional
import json

class MedicalNLPEngine:
    """Advanced NLP engine for medical chatbot with fuzzy matching and entity extraction"""
    
    def __init__(self):
        # Intent patterns with multiple variations
        self.intent_patterns = {
            'dosage': [
                r'\b(dosage|dose|how much|quantity|amount|take|consume)\b',
                r'\b(mg|ml|tablet|capsule|times|daily|frequency)\b'
            ],
            'side_effects': [
                r'\b(side effect|adverse|reaction|problem|issue|harm|danger)\b',
                r'\b(after taking|caused by|because of)\b'
            ],
            'substitutes': [
                r'\b(substitute|alternative|replace|instead|similar|equivalent)\b',
                r'\b(other option|different|change)\b'
            ],
            'indications': [
                r'\b(indication|use|used for|treat|cure|help|purpose)\b',
                r'\b(what is.*for|why take|benefit)\b'
            ],
            'contraindications': [
                r'\b(contraindication|avoid|not take|should not|cannot|forbidden)\b',
                r'\b(when not|who should not|danger|risk)\b'
            ],
            'interactions': [
                r'\b(interact|combination|together|with|along with)\b',
                r'\b(mix|combine|take with)\b'
            ],
            'storage': [
                r'\b(store|storage|keep|preserve|shelf life|expiry)\b',
                r'\b(temperature|refrigerate|room temperature)\b'
            ],
            'pregnancy': [
                r'\b(pregnan|lactation|breastfeed|nursing|mother)\b',
                r'\b(safe during pregnancy|while pregnant)\b'
            ]
        }
        
        # Common medical terms for context
        self.medical_terms = [
            'tablet', 'capsule', 'syrup', 'injection', 'mg', 'ml',
            'morning', 'evening', 'night', 'before meal', 'after meal',
            'empty stomach', 'with food', 'daily', 'twice', 'thrice'
        ]
        
        # Question words that indicate queries
        self.question_words = ['what', 'when', 'where', 'how', 'why', 'which', 'who', 'can', 'should', 'is', 'are']
        
    def extract_drug_name(self, query: str, drug_list: List[str]) -> Optional[Tuple[str, int]]:
        """
        Extract drug name from query using fuzzy matching
        Returns: (drug_name, confidence_score) or None
        """
        query_lower = query.lower()
        
        # Try exact match first
        for drug in drug_list:
            if drug.lower() in query_lower:
                return (drug, 100)
        
        # Extract potential drug names (capitalized words or words after "about", "for", etc.)
        potential_drugs = []
        
        # Look for words after key phrases
        patterns = [
            r'(?:about|for|regarding|concerning|of)\s+([A-Za-z]+)',
            r'(?:drug|medicine|medication|tablet)\s+([A-Za-z]+)',
            r'\b([A-Z][a-z]+(?:in|ol|ide|ine|ate|one))\b'  # Common drug suffixes
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, query)
            potential_drugs.extend(matches)
        
        # Also consider all words as potential drug names
        words = re.findall(r'\b[A-Za-z]{4,}\b', query)
        potential_drugs.extend(words)
        
        # Use fuzzy matching to find best match
        best_match = None
        best_score = 0
        
        for potential in potential_drugs:
            match = process.extractOne(potential, drug_list, scorer=fuzz.ratio)
            if match and match[1] > best_score and match[1] >= 70:  # 70% threshold
                best_match = match[0]
                best_score = match[1]
        
        if best_match:
            return (best_match, best_score)
        
        return None
    
    def classify_intent(self, query: str) -> List[Tuple[str, float]]:
        """
        Classify user intent using pattern matching
        Returns: List of (intent, confidence) tuples sorted by confidence
        """
        query_lower = query.lower()
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            matches = 0
            
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    matches += 1
                    score += 1
            
            if matches > 0:
                # Normalize score (0-1 range)
                confidence = min(score / len(patterns), 1.0)
                intent_scores[intent] = confidence
        
        # If no specific intent found, check for general query
        if not intent_scores:
            # Check if it's a question
            if any(word in query_lower.split()[:3] for word in self.question_words):
                intent_scores['general'] = 0.5
            else:
                intent_scores['general'] = 0.3
        
        # Sort by confidence
        sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_intents
    
    def extract_entities(self, query: str) -> Dict[str, any]:
        """
        Extract entities like dosage, frequency, time, etc.
        """
        entities = {}
        query_lower = query.lower()
        
        # Extract dosage amounts
        dosage_pattern = r'(\d+(?:\.\d+)?)\s*(mg|ml|g|mcg|iu)'
        dosage_matches = re.findall(dosage_pattern, query_lower)
        if dosage_matches:
            entities['dosage_amount'] = dosage_matches
        
        # Extract frequency
        frequency_patterns = [
            (r'\b(once|twice|thrice|three times)\s*(?:a|per)?\s*day\b', 'frequency'),
            (r'\bevery\s+(\d+)\s+hours?\b', 'interval'),
            (r'\b(daily|morning|evening|night|bedtime)\b', 'time_of_day')
        ]
        
        for pattern, entity_type in frequency_patterns:
            matches = re.findall(pattern, query_lower)
            if matches:
                entities[entity_type] = matches
        
        # Extract age (for pediatric dosing)
        age_pattern = r'(\d+)\s*(?:year|yr|month|mo)s?\s*old'
        age_matches = re.findall(age_pattern, query_lower)
        if age_matches:
            entities['age'] = age_matches
        
        # Check for pregnancy/lactation
        if re.search(r'\b(pregnan|lactation|breastfeed)', query_lower):
            entities['special_condition'] = 'pregnancy_lactation'
        
        return entities
    
    def calculate_confidence(self, drug_match_score: int, intent_confidence: float, 
                           has_entities: bool, query_length: int) -> float:
        """
        Calculate overall confidence score for the response
        """
        # Weight factors
        drug_weight = 0.4
        intent_weight = 0.3
        entity_weight = 0.2
        query_weight = 0.1
        
        # Normalize drug match score (0-100 to 0-1)
        drug_score = drug_match_score / 100.0
        
        # Entity score
        entity_score = 1.0 if has_entities else 0.5
        
        # Query length score (prefer queries with reasonable length)
        query_score = min(query_length / 50.0, 1.0) if query_length > 5 else 0.5
        
        # Calculate weighted confidence
        confidence = (
            drug_score * drug_weight +
            intent_confidence * intent_weight +
            entity_score * entity_weight +
            query_score * query_weight
        )
        
        return round(confidence, 2)
    
    def parse_query(self, query: str, drug_list: List[str]) -> Dict[str, any]:
        """
        Complete query parsing pipeline
        Returns comprehensive analysis of the query
        """
        # Extract drug name
        drug_match = self.extract_drug_name(query, drug_list)
        
        # Classify intent
        intents = self.classify_intent(query)
        primary_intent = intents[0] if intents else ('general', 0.3)
        
        # Extract entities
        entities = self.extract_entities(query)
        
        # Calculate confidence
        drug_score = drug_match[1] if drug_match else 0
        confidence = self.calculate_confidence(
            drug_score,
            primary_intent[1],
            len(entities) > 0,
            len(query)
        )
        
        return {
            'drug_name': drug_match[0] if drug_match else None,
            'drug_confidence': drug_score,
            'primary_intent': primary_intent[0],
            'intent_confidence': primary_intent[1],
            'all_intents': intents,
            'entities': entities,
            'overall_confidence': confidence,
            'query_length': len(query)
        }
