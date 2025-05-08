from flask import session

def initialize_brand_parameters():
    """Initialize brand parameters in session if not already present"""
    if 'brand_parameters' not in session:
        session['brand_parameters'] = {
            "personality": {
                "primary_traits": [],
                "secondary_traits": [],
                "traits_to_avoid": []
            },
            "formality": {
                "level": 5,  # Scale of 1-10
                "context_variations": {}
            },
            "emotional_tone": {
                "primary_emotions": [],
                "secondary_emotions": [],
                "emotions_to_avoid": [],
                "intensity": 5  # Scale of 1-10
            },
            "vocabulary": {
                "preferred_terms": [],
                "restricted_terms": [],
                "jargon_level": 5,  # Scale of 1-10
                "technical_complexity": 5,  # Scale of 1-10
                "custom_terminology": {}
            },
            "communication_style": {
                "storytelling_preference": 5,  # Scale of 1-10 (direct to narrative)
                "sentence_structure": {
                    "length_preference": 5,  # Scale of 1-10 (short to long)
                    "complexity_preference": 5  # Scale of 1-10 (simple to complex)
                },
                "rhetorical_devices": [],
                "cta_style": ""
            },
            "audience_adaptation": {
                "audience_segments": {},
                "channel_adaptations": {},
                "journey_stage_adaptations": {}
            }
        }
    
    if 'input_methods' not in session:
        session['input_methods'] = {
            "document_upload": {"used": False, "data": {}},
            "brand_interview": {"used": False, "data": {}},
            "web_scraper": {"used": False, "data": {}}
        }

def get_brand_parameters():
    """Get brand parameters from session"""
    initialize_brand_parameters()
    return session['brand_parameters']

def update_brand_parameters(parameters):
    """Update brand parameters in session"""
    session['brand_parameters'] = parameters
    session.modified = True

def get_input_methods():
    """Get input methods status from session"""
    initialize_brand_parameters()
    return session['input_methods']

def update_input_method(method_name, used=True, data=None):
    """Update input method status in session"""
    initialize_brand_parameters()
    
    if data is None:
        data = {}
    
    session['input_methods'][method_name] = {
        "used": used,
        "data": data
    }
    session.modified = True

def any_input_method_used():
    """Check if any input method has been used"""
    initialize_brand_parameters()
    return any(method["used"] for method in session['input_methods'].values())
