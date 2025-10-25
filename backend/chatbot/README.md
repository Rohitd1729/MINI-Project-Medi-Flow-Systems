# Medical Expert Chatbot - Technical Overview

## Architecture

```
User Query
    ↓
NLP Engine (nlp_engine.py)
    ├─ Intent Classification
    ├─ Drug Name Extraction (Fuzzy Matching)
    ├─ Entity Extraction
    └─ Confidence Calculation
    ↓
Inference Engine (inference_engine.py)
    ├─ Rule Application
    ├─ Response Generation
    └─ Safety Checks
    ↓
Training System (training_system.py)
    ├─ Feedback Collection
    ├─ Accuracy Tracking
    └─ Learning
    ↓
Response + Metadata
```

## Files

- **nlp_engine.py** - Natural language processing
- **inference_engine.py** - Expert system reasoning
- **training_system.py** - Learning and feedback
- **loader.py** - Knowledge base loader
- **models/** - Trained models and data

## Key Classes

### MedicalNLPEngine
```python
nlp_engine = MedicalNLPEngine()
result = nlp_engine.parse_query(query, drug_list)
# Returns: intent, drug_name, entities, confidence
```

### MedicalInferenceEngine
```python
inference_engine = MedicalInferenceEngine()
response = inference_engine.generate_response(intent, drug_data, entities)
# Returns: formatted response with confidence
```

### ChatbotTrainingSystem
```python
training_system = ChatbotTrainingSystem()
training_system.record_feedback(log_id, feedback_type, data)
insights = training_system.get_training_insights()
```

## Adding New Drugs

Edit `backend/drugs.json`:
```json
{
  "drug_id": "unique_id",
  "name": "Drug Name",
  "class": "Drug Class",
  "indications": ["Use 1", "Use 2"],
  "adult_dosage": "Dosage info",
  "paediatric_dosage": "Pediatric dosage",
  "side_effects": ["Effect 1", "Effect 2"],
  "contraindications": ["Condition 1"],
  "substitutes": ["Alternative 1"],
  "prescription_required": true
}
```

Then reload:
```bash
python chatbot/loader.py
```

## Adding New Intents

Edit `nlp_engine.py` → `intent_patterns`:
```python
'new_intent': [
    r'\bpattern1\b',
    r'\bpattern2\b'
]
```

Add response generator in `inference_engine.py`:
```python
def _generate_new_intent_response(self, drug_name, data, entities):
    # Generate response
    return {'response': '...', 'confidence': 0.9}
```

## Testing

```python
# Test NLP
from chatbot.nlp_engine import MedicalNLPEngine
nlp = MedicalNLPEngine()
result = nlp.parse_query("What is the dosage of Paracetamol?", drug_list)
print(result)

# Test Inference
from chatbot.inference_engine import MedicalInferenceEngine
inference = MedicalInferenceEngine()
response = inference.generate_response('dosage', drug_data, {})
print(response)
```

## Performance Tuning

### Fuzzy Matching Threshold
Edit `nlp_engine.py` line ~85:
```python
if match and match[1] >= 70:  # Adjust threshold (70-90)
```

### Confidence Weights
Edit `nlp_engine.py` → `calculate_confidence()`:
```python
drug_weight = 0.4    # Adjust weights
intent_weight = 0.3
entity_weight = 0.2
query_weight = 0.1
```

## Monitoring

View analytics:
```bash
curl http://localhost:5000/api/chat/training/analytics
```

Export training data:
```bash
curl http://localhost:5000/api/chat/training/export
```
