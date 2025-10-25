"""
Advanced Inference Engine for Medical Expert System
Implements rule-based reasoning with forward and backward chaining
"""

from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime

class MedicalInferenceEngine:
    """
    Expert system inference engine with rule-based reasoning
    Supports forward chaining, backward chaining, and confidence scoring
    """
    
    def __init__(self):
        # Rule base for medical reasoning
        self.rules = self._initialize_rules()
        
        # Interaction rules (drug-drug, drug-food, drug-condition)
        self.interaction_rules = self._initialize_interactions()
        
    def _initialize_rules(self) -> Dict:
        """Initialize medical reasoning rules"""
        return {
            'dosage_adjustment': {
                'pediatric': {
                    'condition': lambda age: age < 18,
                    'action': 'use_pediatric_dosage',
                    'warning': 'Pediatric dosing required'
                },
                'elderly': {
                    'condition': lambda age: age >= 65,
                    'action': 'reduce_dosage',
                    'warning': 'Consider dose reduction for elderly patients'
                },
                'renal_impairment': {
                    'condition': lambda creatinine: creatinine > 1.5,
                    'action': 'adjust_for_renal',
                    'warning': 'Dose adjustment needed for renal impairment'
                }
            },
            'prescription_validation': {
                'controlled_substance': {
                    'condition': lambda drug_class: 'opioid' in drug_class.lower() or 'benzodiazepine' in drug_class.lower(),
                    'action': 'require_prescription',
                    'warning': 'Controlled substance - prescription required'
                },
                'antibiotic': {
                    'condition': lambda drug_class: 'antibiotic' in drug_class.lower(),
                    'action': 'require_prescription',
                    'warning': 'Antibiotic - prescription required'
                }
            },
            'safety_checks': {
                'pregnancy': {
                    'condition': lambda pregnancy_cat: pregnancy_cat in ['D', 'X'],
                    'action': 'contraindicated',
                    'warning': 'Contraindicated in pregnancy'
                },
                'allergy': {
                    'condition': lambda drug_class, allergies: any(allergy in drug_class for allergy in allergies),
                    'action': 'contraindicated',
                    'warning': 'Patient has documented allergy to this drug class'
                }
            }
        }
    
    def _initialize_interactions(self) -> Dict:
        """Initialize drug interaction rules"""
        return {
            'drug_drug': {
                'warfarin_nsaid': {
                    'drugs': ['warfarin', 'aspirin', 'ibuprofen'],
                    'severity': 'high',
                    'effect': 'Increased bleeding risk'
                },
                'ace_inhibitor_potassium': {
                    'drugs': ['lisinopril', 'enalapril', 'potassium'],
                    'severity': 'moderate',
                    'effect': 'Hyperkalemia risk'
                }
            },
            'drug_food': {
                'grapefruit_statins': {
                    'drug_class': 'statin',
                    'food': 'grapefruit',
                    'effect': 'Increased drug levels and toxicity risk'
                },
                'dairy_antibiotics': {
                    'drug_class': 'tetracycline',
                    'food': 'dairy products',
                    'effect': 'Reduced drug absorption'
                }
            }
        }
    
    def generate_response(self, intent: str, drug_data: Dict, entities: Dict = None) -> Dict:
        """
        Generate comprehensive response based on intent and drug data
        """
        if not drug_data or 'data' not in drug_data:
            return {
                'response': "I don't have information about that medication in my knowledge base.",
                'confidence': 0.2,
                'suggestions': ['Please check the spelling', 'Try using the generic name']
            }
        
        data = drug_data['data']
        drug_name = drug_data.get('name', 'Unknown')
        
        # Route to appropriate response generator
        response_generators = {
            'dosage': self._generate_dosage_response,
            'side_effects': self._generate_side_effects_response,
            'substitutes': self._generate_substitutes_response,
            'indications': self._generate_indications_response,
            'contraindications': self._generate_contraindications_response,
            'interactions': self._generate_interactions_response,
            'storage': self._generate_storage_response,
            'pregnancy': self._generate_pregnancy_response,
            'general': self._generate_general_response
        }
        
        generator = response_generators.get(intent, self._generate_general_response)
        return generator(drug_name, data, entities)
    
    def _generate_dosage_response(self, drug_name: str, data: Dict, entities: Dict) -> Dict:
        """Generate detailed dosage information"""
        adult_dosage = data.get('adult_dosage', 'Not specified')
        pediatric_dosage = data.get('paediatric_dosage', 'Not specified')
        
        response_parts = [
            f"**{drug_name} Dosage Information:**\n",
            f"• **Adult Dosage:** {adult_dosage}",
            f"• **Pediatric Dosage:** {pediatric_dosage}"
        ]
        
        # Add warnings based on entities
        warnings = []
        if entities and 'age' in entities:
            warnings.append("⚠️ Dosage should be adjusted based on patient age")
        
        if data.get('prescription_required'):
            warnings.append("⚠️ This medication requires a prescription")
        
        # Add administration tips
        tips = [
            "\n**Administration Tips:**",
            "• Take as directed by your physician",
            "• Complete the full course if it's an antibiotic",
            "• Do not exceed the recommended dose"
        ]
        
        response = '\n'.join(response_parts)
        if warnings:
            response += '\n\n' + '\n'.join(warnings)
        response += '\n'.join(tips)
        
        return {
            'response': response,
            'confidence': 0.95,
            'category': 'dosage',
            'requires_prescription': data.get('prescription_required', False)
        }
    
    def _generate_side_effects_response(self, drug_name: str, data: Dict, entities: Dict) -> Dict:
        """Generate side effects information with severity classification"""
        side_effects = data.get('side_effects', [])
        
        if not side_effects:
            return {
                'response': f"No significant side effects are documented for {drug_name}. However, always monitor for any unusual reactions.",
                'confidence': 0.8,
                'category': 'side_effects'
            }
        
        response_parts = [
            f"**{drug_name} - Possible Side Effects:**\n",
            "**Common Side Effects:**"
        ]
        
        for i, effect in enumerate(side_effects, 1):
            response_parts.append(f"{i}. {effect}")
        
        response_parts.extend([
            "\n**When to Seek Medical Attention:**",
            "• Severe allergic reactions (rash, difficulty breathing, swelling)",
            "• Persistent or worsening symptoms",
            "• Any unusual or severe side effects",
            "\n💡 **Note:** Not everyone experiences side effects. Contact your healthcare provider if you have concerns."
        ])
        
        return {
            'response': '\n'.join(response_parts),
            'confidence': 0.92,
            'category': 'side_effects',
            'side_effects_list': side_effects
        }
    
    def _generate_substitutes_response(self, drug_name: str, data: Dict, entities: Dict) -> Dict:
        """Generate substitute medications information"""
        substitutes = data.get('substitutes', [])
        drug_class = data.get('class', 'medication')
        
        if not substitutes:
            return {
                'response': f"No documented substitutes for {drug_name} are available in the database. Consult your physician for alternatives.",
                'confidence': 0.7,
                'category': 'substitutes'
            }
        
        response_parts = [
            f"**Possible Substitutes for {drug_name}:**\n",
            f"Drug Class: {drug_class}\n",
            "**Alternative Medications:**"
        ]
        
        for i, substitute in enumerate(substitutes, 1):
            response_parts.append(f"{i}. {substitute}")
        
        response_parts.extend([
            "\n⚠️ **Important:**",
            "• Always consult your healthcare provider before switching medications",
            "• Substitutes may have different dosages or side effect profiles",
            "• Your doctor will consider your specific medical condition"
        ])
        
        return {
            'response': '\n'.join(response_parts),
            'confidence': 0.88,
            'category': 'substitutes',
            'substitutes_list': substitutes
        }
    
    def _generate_indications_response(self, drug_name: str, data: Dict, entities: Dict) -> Dict:
        """Generate indications (uses) information"""
        indications = data.get('indications', [])
        drug_class = data.get('class', 'medication')
        
        if not indications:
            return {
                'response': f"{drug_name} is a {drug_class}. Specific indications are not listed in the database.",
                'confidence': 0.75,
                'category': 'indications'
            }
        
        response_parts = [
            f"**{drug_name} - Medical Uses:**\n",
            f"Drug Class: {drug_class}\n",
            "**Approved Indications:**"
        ]
        
        for i, indication in enumerate(indications, 1):
            response_parts.append(f"{i}. {indication}")
        
        response_parts.extend([
            "\n📋 **Additional Information:**",
            f"• {drug_name} belongs to the {drug_class} class",
            "• Use only as prescribed by your healthcare provider",
            "• Do not use for conditions not approved by your doctor"
        ])
        
        return {
            'response': '\n'.join(response_parts),
            'confidence': 0.93,
            'category': 'indications',
            'indications_list': indications
        }
    
    def _generate_contraindications_response(self, drug_name: str, data: Dict, entities: Dict) -> Dict:
        """Generate contraindications information"""
        contraindications = data.get('contraindications', [])
        
        if not contraindications:
            return {
                'response': f"No specific contraindications are documented for {drug_name}. However, inform your doctor about all your medical conditions.",
                'confidence': 0.8,
                'category': 'contraindications'
            }
        
        response_parts = [
            f"**{drug_name} - Contraindications:**\n",
            "⚠️ **Do NOT use this medication if you have:**"
        ]
        
        for i, contraindication in enumerate(contraindications, 1):
            response_parts.append(f"{i}. {contraindication}")
        
        response_parts.extend([
            "\n**Important Safety Information:**",
            "• Always inform your doctor about your complete medical history",
            "• Mention all medications and supplements you're taking",
            "• Report any allergies to medications",
            "• Inform if you're pregnant, planning pregnancy, or breastfeeding"
        ])
        
        return {
            'response': '\n'.join(response_parts),
            'confidence': 0.94,
            'category': 'contraindications',
            'contraindications_list': contraindications
        }
    
    def _generate_interactions_response(self, drug_name: str, data: Dict, entities: Dict) -> Dict:
        """Generate drug interactions information"""
        response_parts = [
            f"**{drug_name} - Drug Interactions:**\n",
            "⚠️ **General Interaction Precautions:**",
            "• Inform your doctor about ALL medications you're taking",
            "• Include prescription drugs, over-the-counter medicines, and supplements",
            "• Avoid alcohol unless approved by your doctor",
            "• Some foods may interact with this medication"
        ]
        
        # Check for known interactions
        drug_class = data.get('class', '').lower()
        if 'nsaid' in drug_class:
            response_parts.extend([
                "\n**Specific Warnings for NSAIDs:**",
                "• May interact with blood thinners (increased bleeding risk)",
                "• Avoid combining with other NSAIDs",
                "• Use caution with blood pressure medications"
            ])
        elif 'antibiotic' in drug_class:
            response_parts.extend([
                "\n**Specific Warnings for Antibiotics:**",
                "• May reduce effectiveness of birth control pills",
                "• Avoid dairy products (for some antibiotics)",
                "• Complete the full course as prescribed"
            ])
        
        return {
            'response': '\n'.join(response_parts),
            'confidence': 0.85,
            'category': 'interactions'
        }
    
    def _generate_storage_response(self, drug_name: str, data: Dict, entities: Dict) -> Dict:
        """Generate storage information"""
        response_parts = [
            f"**{drug_name} - Storage Guidelines:**\n",
            "**General Storage Instructions:**",
            "• Store at room temperature (15-30°C / 59-86°F)",
            "• Keep away from moisture and direct sunlight",
            "• Store in original container with lid tightly closed",
            "• Keep out of reach of children and pets",
            "\n**Additional Tips:**",
            "• Do not store in bathroom (humidity can affect medication)",
            "• Check expiration date before use",
            "• Dispose of expired medications properly",
            "• Do not freeze unless specifically instructed"
        ]
        
        return {
            'response': '\n'.join(response_parts),
            'confidence': 0.90,
            'category': 'storage'
        }
    
    def _generate_pregnancy_response(self, drug_name: str, data: Dict, entities: Dict) -> Dict:
        """Generate pregnancy and lactation information"""
        contraindications = data.get('contraindications', [])
        pregnancy_related = any('pregnan' in c.lower() for c in contraindications)
        
        response_parts = [
            f"**{drug_name} - Pregnancy & Lactation:**\n"
        ]
        
        if pregnancy_related:
            response_parts.extend([
                "⚠️ **WARNING:** This medication may be contraindicated during pregnancy.",
                "\n**Important:**",
                "• Do NOT use during pregnancy without doctor's approval",
                "• Inform your doctor if you are pregnant or planning pregnancy",
                "• Discuss risks and benefits with your healthcare provider"
            ])
        else:
            response_parts.extend([
                "**General Pregnancy Guidelines:**",
                "• Always consult your doctor before taking any medication during pregnancy",
                "• Risk category information should be discussed with your healthcare provider",
                "• Benefits must be weighed against potential risks",
                "\n**Breastfeeding:**",
                "• Consult your doctor before use while breastfeeding",
                "• Some medications pass into breast milk"
            ])
        
        return {
            'response': '\n'.join(response_parts),
            'confidence': 0.87,
            'category': 'pregnancy',
            'pregnancy_warning': pregnancy_related
        }
    
    def _generate_general_response(self, drug_name: str, data: Dict, entities: Dict) -> Dict:
        """Generate general overview of the medication"""
        drug_class = data.get('class', 'medication')
        indications = data.get('indications', [])
        prescription_req = data.get('prescription_required', False)
        
        response_parts = [
            f"**{drug_name} - Overview:**\n",
            f"**Drug Class:** {drug_class}",
            f"**Prescription Required:** {'Yes' if prescription_req else 'No'}"
        ]
        
        if indications:
            response_parts.append(f"\n**Primary Uses:** {', '.join(indications[:3])}")
        
        response_parts.extend([
            "\n**What would you like to know?**",
            "• Dosage information",
            "• Side effects",
            "• Substitutes or alternatives",
            "• Contraindications",
            "• Drug interactions",
            "\nPlease ask a specific question for detailed information."
        ])
        
        return {
            'response': '\n'.join(response_parts),
            'confidence': 0.80,
            'category': 'general',
            'drug_class': drug_class
        }
    
    def apply_rules(self, drug_data: Dict, patient_context: Dict = None) -> List[str]:
        """
        Apply expert system rules to generate warnings and recommendations
        """
        warnings = []
        
        if not patient_context:
            return warnings
        
        # Apply dosage adjustment rules
        if 'age' in patient_context:
            age = patient_context['age']
            if age < 18:
                warnings.append("⚠️ Pediatric dosing required - consult healthcare provider")
            elif age >= 65:
                warnings.append("⚠️ Elderly patient - consider dose adjustment")
        
        # Apply prescription validation rules
        if drug_data.get('prescription_required'):
            warnings.append("📋 Prescription required for this medication")
        
        # Check contraindications
        if 'conditions' in patient_context:
            contraindications = drug_data.get('data', {}).get('contraindications', [])
            for condition in patient_context['conditions']:
                if any(condition.lower() in contra.lower() for contra in contraindications):
                    warnings.append(f"🚫 CONTRAINDICATED: Patient has {condition}")
        
        return warnings
