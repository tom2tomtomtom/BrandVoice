from flask import session

def initialize_brand_parameters(reset=False):
    """
    Initialize brand parameters in session if not already present

    Args:
        reset: If True, reset all parameters even if they already exist
    """
    if 'brand_parameters' not in session or reset:
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

    if 'input_methods' not in session or reset:
        session['input_methods'] = {
            "document_upload": {"used": False, "data": {}},
            "brand_interview": {"used": False, "data": {}},
            "web_scraper": {"used": False, "data": {}}
        }

def get_brand_parameters():
    """Get brand parameters from session"""
    initialize_brand_parameters()
    return session['brand_parameters']

def update_brand_parameters(parameters, method_name=None, merge=True):
    """
    Update brand parameters in session

    Args:
        parameters: The brand parameters to update
        method_name: The input method that provided these parameters
        merge: Whether to merge with existing parameters (True) or replace them (False)
    """
    initialize_brand_parameters()

    if not merge:
        # Simply replace all parameters
        session['brand_parameters'] = parameters
        session.modified = True
        return

    # Store the original parameters in the input method's data if method_name is provided
    if method_name and method_name in session['input_methods']:
        # Make sure the input method has a parameters field
        if 'parameters' not in session['input_methods'][method_name]:
            session['input_methods'][method_name]['parameters'] = {}

        # Store the parameters
        session['input_methods'][method_name]['parameters'] = parameters

        # Print for debugging
        print(f"Stored parameters for {method_name}:")
        if 'personality' in parameters:
            print(f"Personality primary traits: {parameters['personality']['primary_traits']}")
            print(f"Personality secondary traits: {parameters['personality']['secondary_traits']}")

    # Merge parameters from all input methods
    merge_brand_parameters()

def merge_brand_parameters():
    """
    Intelligently merge brand parameters from all input methods that have been used
    to create a comprehensive brand voice profile
    """
    initialize_brand_parameters()

    # Get all input methods that have been used
    input_methods = session['input_methods']
    used_methods = [method for method, data in input_methods.items() if data.get('used', False)]

    if not used_methods:
        return  # No methods used yet

    # Initialize merged parameters with default values
    merged = get_brand_parameters()

    # Track which methods contributed to each parameter for reporting
    parameter_sources = {
        "personality": {"primary_traits": [], "secondary_traits": [], "traits_to_avoid": []},
        "emotional_tone": {"primary_emotions": [], "secondary_emotions": [], "emotions_to_avoid": [], "intensity": []},
        "formality": {"level": []},
        "vocabulary": {"preferred_terms": [], "jargon_level": [], "technical_complexity": []},
        "communication_style": {"storytelling_preference": [], "sentence_structure": {"length_preference": [], "complexity_preference": []}},
    }

    # Collect all parameters from used methods
    all_parameters = {}
    for method in used_methods:
        if 'parameters' in input_methods[method]:
            all_parameters[method] = input_methods[method]['parameters']

    # Debug: Print all collected parameters
    print("\nAll collected parameters:")
    for method, params in all_parameters.items():
        print(f"Method: {method}")
        if 'personality' in params:
            print(f"  Personality primary traits: {params['personality'].get('primary_traits', [])}")
            print(f"  Personality secondary traits: {params['personality'].get('secondary_traits', [])}")
        if 'emotional_tone' in params:
            print(f"  Emotional tone primary: {params['emotional_tone'].get('primary_emotions', [])}")
            print(f"  Emotional tone secondary: {params['emotional_tone'].get('secondary_emotions', [])}")

    # Merge personality traits
    all_primary_traits = []
    all_secondary_traits = []
    all_traits_to_avoid = []

    for method, params in all_parameters.items():
        if 'personality' in params:
            if 'primary_traits' in params['personality']:
                # Make sure primary_traits is a list
                if isinstance(params['personality']['primary_traits'], list):
                    all_primary_traits.extend(params['personality']['primary_traits'])
                    parameter_sources['personality']['primary_traits'].append(method)
            if 'secondary_traits' in params['personality']:
                # Make sure secondary_traits is a list
                if isinstance(params['personality']['secondary_traits'], list):
                    all_secondary_traits.extend(params['personality']['secondary_traits'])
                    parameter_sources['personality']['secondary_traits'].append(method)
            if 'traits_to_avoid' in params['personality']:
                # Make sure traits_to_avoid is a list
                if isinstance(params['personality']['traits_to_avoid'], list):
                    all_traits_to_avoid.extend(params['personality']['traits_to_avoid'])
                    parameter_sources['personality']['traits_to_avoid'].append(method)

    # Count occurrences of each trait
    from collections import Counter
    primary_counter = Counter(all_primary_traits)
    secondary_counter = Counter(all_secondary_traits)
    avoid_counter = Counter(all_traits_to_avoid)

    # Debug: Print counters
    print("\nPersonality trait counters:")
    print(f"Primary traits: {primary_counter}")
    print(f"Secondary traits: {secondary_counter}")

    # Select the most common traits
    merged['personality']['primary_traits'] = [trait for trait, _ in primary_counter.most_common(3)]
    merged['personality']['secondary_traits'] = [trait for trait, _ in secondary_counter.most_common(3)]
    merged['personality']['traits_to_avoid'] = [trait for trait, _ in avoid_counter.most_common(3)]

    # Debug: Print merged traits
    print("\nMerged personality traits:")
    print(f"Primary traits: {merged['personality']['primary_traits']}")
    print(f"Secondary traits: {merged['personality']['secondary_traits']}")

    # Ensure we have at least some traits if counters are empty
    if not merged['personality']['primary_traits']:
        merged['personality']['primary_traits'] = ['innovative', 'trustworthy', 'friendly']
    if not merged['personality']['secondary_traits']:
        merged['personality']['secondary_traits'] = ['bold', 'empathetic', 'playful']

    # If we have web_scraper or document_upload parameters, prioritize them
    for priority_method in ['web_scraper', 'document_upload']:
        if priority_method in all_parameters and 'personality' in all_parameters[priority_method]:
            if 'primary_traits' in all_parameters[priority_method]['personality'] and all_parameters[priority_method]['personality']['primary_traits']:
                # Replace at least one trait with priority method traits
                priority_traits = all_parameters[priority_method]['personality']['primary_traits']
                print(f"  Adding {priority_method} primary traits: {priority_traits}")
                for trait in priority_traits:
                    if trait not in merged['personality']['primary_traits'] and len(merged['personality']['primary_traits']) > 0:
                        merged['personality']['primary_traits'][0] = trait
                        break

            if 'secondary_traits' in all_parameters[priority_method]['personality'] and all_parameters[priority_method]['personality']['secondary_traits']:
                # Replace at least one trait with priority method traits
                priority_traits = all_parameters[priority_method]['personality']['secondary_traits']
                print(f"  Adding {priority_method} secondary traits: {priority_traits}")
                for trait in priority_traits:
                    if trait not in merged['personality']['secondary_traits'] and len(merged['personality']['secondary_traits']) > 0:
                        merged['personality']['secondary_traits'][0] = trait
                        break

    # Merge emotional tone
    all_primary_emotions = []
    all_secondary_emotions = []
    all_emotions_to_avoid = []
    all_intensities = []

    for method, params in all_parameters.items():
        if 'emotional_tone' in params:
            if 'primary_emotions' in params['emotional_tone']:
                # Make sure primary_emotions is a list
                if isinstance(params['emotional_tone']['primary_emotions'], list):
                    all_primary_emotions.extend(params['emotional_tone']['primary_emotions'])
                    parameter_sources['emotional_tone']['primary_emotions'].append(method)
            if 'secondary_emotions' in params['emotional_tone']:
                # Make sure secondary_emotions is a list
                if isinstance(params['emotional_tone']['secondary_emotions'], list):
                    all_secondary_emotions.extend(params['emotional_tone']['secondary_emotions'])
                    parameter_sources['emotional_tone']['secondary_emotions'].append(method)
            if 'emotions_to_avoid' in params['emotional_tone']:
                # Make sure emotions_to_avoid is a list
                if isinstance(params['emotional_tone']['emotions_to_avoid'], list):
                    all_emotions_to_avoid.extend(params['emotional_tone']['emotions_to_avoid'])
                    parameter_sources['emotional_tone']['emotions_to_avoid'].append(method)
            if 'intensity' in params['emotional_tone']:
                all_intensities.append(params['emotional_tone']['intensity'])
                parameter_sources['emotional_tone']['intensity'].append(method)

    # Count occurrences of each emotion
    primary_emotion_counter = Counter(all_primary_emotions)
    secondary_emotion_counter = Counter(all_secondary_emotions)
    avoid_emotion_counter = Counter(all_emotions_to_avoid)

    # Debug: Print counters
    print("\nEmotional tone counters:")
    print(f"Primary emotions: {primary_emotion_counter}")
    print(f"Secondary emotions: {secondary_emotion_counter}")

    # Select the most common emotions
    merged['emotional_tone']['primary_emotions'] = [emotion for emotion, _ in primary_emotion_counter.most_common(3)]
    merged['emotional_tone']['secondary_emotions'] = [emotion for emotion, _ in secondary_emotion_counter.most_common(3)]
    merged['emotional_tone']['emotions_to_avoid'] = [emotion for emotion, _ in avoid_emotion_counter.most_common(3)]

    # Debug: Print merged emotions
    print("\nMerged emotional tones:")
    print(f"Primary emotions: {merged['emotional_tone']['primary_emotions']}")
    print(f"Secondary emotions: {merged['emotional_tone']['secondary_emotions']}")

    # Ensure we have at least some emotions if counters are empty
    if not merged['emotional_tone']['primary_emotions']:
        merged['emotional_tone']['primary_emotions'] = ['optimistic', 'passionate']
    if not merged['emotional_tone']['secondary_emotions']:
        merged['emotional_tone']['secondary_emotions'] = ['reassuring', 'calm']

    # If we have web_scraper or document_upload parameters, prioritize them
    for priority_method in ['web_scraper', 'document_upload']:
        if priority_method in all_parameters and 'emotional_tone' in all_parameters[priority_method]:
            if 'primary_emotions' in all_parameters[priority_method]['emotional_tone'] and all_parameters[priority_method]['emotional_tone']['primary_emotions']:
                # Replace at least one emotion with priority method emotions
                priority_emotions = all_parameters[priority_method]['emotional_tone']['primary_emotions']
                print(f"  Adding {priority_method} primary emotions: {priority_emotions}")
                for emotion in priority_emotions:
                    if emotion not in merged['emotional_tone']['primary_emotions'] and len(merged['emotional_tone']['primary_emotions']) > 0:
                        merged['emotional_tone']['primary_emotions'][0] = emotion
                        break

            if 'secondary_emotions' in all_parameters[priority_method]['emotional_tone'] and all_parameters[priority_method]['emotional_tone']['secondary_emotions']:
                # Replace at least one emotion with priority method emotions
                priority_emotions = all_parameters[priority_method]['emotional_tone']['secondary_emotions']
                print(f"  Adding {priority_method} secondary emotions: {priority_emotions}")
                for emotion in priority_emotions:
                    if emotion not in merged['emotional_tone']['secondary_emotions'] and len(merged['emotional_tone']['secondary_emotions']) > 0:
                        merged['emotional_tone']['secondary_emotions'][0] = emotion
                        break

    # Average the intensity if available
    if all_intensities:
        merged['emotional_tone']['intensity'] = round(sum(all_intensities) / len(all_intensities))

    # Merge formality level
    all_formality_levels = []

    for method, params in all_parameters.items():
        if 'formality' in params and 'level' in params['formality']:
            all_formality_levels.append(params['formality']['level'])
            parameter_sources['formality']['level'].append(method)

    # Average the formality level if available
    if all_formality_levels:
        merged['formality']['level'] = round(sum(all_formality_levels) / len(all_formality_levels))

    # Merge vocabulary
    all_preferred_terms = []
    all_jargon_levels = []
    all_technical_complexities = []

    for method, params in all_parameters.items():
        if 'vocabulary' in params:
            if 'preferred_terms' in params['vocabulary']:
                all_preferred_terms.extend(params['vocabulary']['preferred_terms'])
                parameter_sources['vocabulary']['preferred_terms'].append(method)
            if 'jargon_level' in params['vocabulary']:
                all_jargon_levels.append(params['vocabulary']['jargon_level'])
                parameter_sources['vocabulary']['jargon_level'].append(method)
            if 'technical_complexity' in params['vocabulary']:
                all_technical_complexities.append(params['vocabulary']['technical_complexity'])
                parameter_sources['vocabulary']['technical_complexity'].append(method)

    # Count occurrences of each term
    preferred_term_counter = Counter(all_preferred_terms)

    # Select the most common terms
    merged['vocabulary']['preferred_terms'] = [term for term, _ in preferred_term_counter.most_common(10)]

    # Average the jargon level and technical complexity if available
    if all_jargon_levels:
        merged['vocabulary']['jargon_level'] = round(sum(all_jargon_levels) / len(all_jargon_levels))
    if all_technical_complexities:
        merged['vocabulary']['technical_complexity'] = round(sum(all_technical_complexities) / len(all_technical_complexities))

    # Merge communication style
    all_storytelling_prefs = []
    all_length_prefs = []
    all_complexity_prefs = []

    for method, params in all_parameters.items():
        if 'communication_style' in params:
            if 'storytelling_preference' in params['communication_style']:
                all_storytelling_prefs.append((params['communication_style']['storytelling_preference'], method))
            if 'sentence_structure' in params['communication_style']:
                if 'length_preference' in params['communication_style']['sentence_structure']:
                    all_length_prefs.append((params['communication_style']['sentence_structure']['length_preference'], method))
                if 'complexity_preference' in params['communication_style']['sentence_structure']:
                    all_complexity_prefs.append((params['communication_style']['sentence_structure']['complexity_preference'], method))

    # Debug: Print communication style preferences
    print("\nCommunication style preferences:")
    print(f"Storytelling preferences: {all_storytelling_prefs}")
    print(f"Length preferences: {all_length_prefs}")
    print(f"Complexity preferences: {all_complexity_prefs}")

    # Average the preferences if available, with priority for web_scraper and document_upload
    if all_storytelling_prefs:
        # Check if we have web_scraper or document_upload preferences
        priority_prefs = [pref for pref, method in all_storytelling_prefs if method in ['web_scraper', 'document_upload']]
        if priority_prefs:
            merged['communication_style']['storytelling_preference'] = round(sum(priority_prefs) / len(priority_prefs))
            parameter_sources['communication_style']['storytelling_preference'] = ['web_scraper', 'document_upload']
        else:
            merged['communication_style']['storytelling_preference'] = round(sum(pref for pref, _ in all_storytelling_prefs) / len(all_storytelling_prefs))
            parameter_sources['communication_style']['storytelling_preference'] = [method for _, method in all_storytelling_prefs]
    else:
        # Default value if no preferences are available
        merged['communication_style']['storytelling_preference'] = 5

    if all_length_prefs:
        # Check if we have web_scraper or document_upload preferences
        priority_prefs = [pref for pref, method in all_length_prefs if method in ['web_scraper', 'document_upload']]
        if priority_prefs:
            merged['communication_style']['sentence_structure']['length_preference'] = round(sum(priority_prefs) / len(priority_prefs))
            parameter_sources['communication_style']['sentence_structure']['length_preference'] = ['web_scraper', 'document_upload']
        else:
            merged['communication_style']['sentence_structure']['length_preference'] = round(sum(pref for pref, _ in all_length_prefs) / len(all_length_prefs))
            parameter_sources['communication_style']['sentence_structure']['length_preference'] = [method for _, method in all_length_prefs]
    else:
        # Default value if no preferences are available
        merged['communication_style']['sentence_structure']['length_preference'] = 5

    if all_complexity_prefs:
        # Check if we have web_scraper or document_upload preferences
        priority_prefs = [pref for pref, method in all_complexity_prefs if method in ['web_scraper', 'document_upload']]
        if priority_prefs:
            merged['communication_style']['sentence_structure']['complexity_preference'] = round(sum(priority_prefs) / len(priority_prefs))
            parameter_sources['communication_style']['sentence_structure']['complexity_preference'] = ['web_scraper', 'document_upload']
        else:
            merged['communication_style']['sentence_structure']['complexity_preference'] = round(sum(pref for pref, _ in all_complexity_prefs) / len(all_complexity_prefs))
            parameter_sources['communication_style']['sentence_structure']['complexity_preference'] = [method for _, method in all_complexity_prefs]
    else:
        # Default value if no preferences are available
        merged['communication_style']['sentence_structure']['complexity_preference'] = 5

    # Debug: Print merged communication style
    print("\nMerged communication style:")
    print(f"Storytelling preference: {merged['communication_style']['storytelling_preference']}")
    print(f"Length preference: {merged['communication_style']['sentence_structure']['length_preference']}")
    print(f"Complexity preference: {merged['communication_style']['sentence_structure']['complexity_preference']}")

    # Store the merged parameters and parameter sources
    session['brand_parameters'] = merged
    session['parameter_sources'] = parameter_sources
    session.modified = True

    # Print the final merged parameters for debugging
    print("\nFinal merged brand parameters:")
    print(f"Personality primary traits: {merged['personality']['primary_traits']}")
    print(f"Personality secondary traits: {merged['personality']['secondary_traits']}")
    print(f"Emotional tone primary: {merged['emotional_tone']['primary_emotions']}")
    print(f"Emotional tone secondary: {merged['emotional_tone']['secondary_emotions']}")
    print(f"Formality level: {merged['formality']['level']}")
    print(f"Communication style - storytelling: {merged['communication_style']['storytelling_preference']}")
    print(f"Communication style - length: {merged['communication_style']['sentence_structure']['length_preference']}")
    print(f"Communication style - complexity: {merged['communication_style']['sentence_structure']['complexity_preference']}")

def get_input_methods():
    """Get input methods status from session"""
    initialize_brand_parameters()
    return session['input_methods']

def update_input_method(method_name, used=True, data=None):
    """Update input method status in session"""
    initialize_brand_parameters()

    if data is None:
        data = {}

    # Preserve any existing parameters
    existing_parameters = {}
    if method_name in session['input_methods'] and 'parameters' in session['input_methods'][method_name]:
        existing_parameters = session['input_methods'][method_name]['parameters']

    session['input_methods'][method_name] = {
        "used": used,
        "data": data,
        "parameters": existing_parameters
    }

    print(f"Updated input method {method_name}:")
    print(f"Used: {used}")
    print(f"Has data: {bool(data)}")
    print(f"Has parameters: {bool(existing_parameters)}")

    session.modified = True

def any_input_method_used():
    """Check if any input method has been used"""
    initialize_brand_parameters()
    return any(method["used"] for method in session['input_methods'].values())
