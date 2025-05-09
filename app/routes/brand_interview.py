from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.session_manager import get_brand_parameters, update_brand_parameters, update_input_method, get_input_methods
import json

brand_interview_bp = Blueprint('brand_interview', __name__)

# Define interview questions
INTERVIEW_QUESTIONS = {
    "personality": [
        {
            "question": "If your brand were a person, how would you describe their personality? (Select up to 3)",
            "type": "multiselect",
            "options": ["Innovative", "Trustworthy", "Playful", "Sophisticated", "Friendly", "Authoritative", "Bold", "Empathetic"],
            "name": "primary_traits",
            "max_selections": 3
        },
        {
            "question": "What secondary personality traits would your brand have? (Select up to 3)",
            "type": "multiselect",
            "options": ["Innovative", "Trustworthy", "Playful", "Sophisticated", "Friendly", "Authoritative", "Bold", "Empathetic"],
            "name": "secondary_traits",
            "max_selections": 3
        },
        {
            "question": "Which personality traits would you specifically want to avoid?",
            "type": "multiselect",
            "options": ["Innovative", "Trustworthy", "Playful", "Sophisticated", "Friendly", "Authoritative", "Bold", "Empathetic"],
            "name": "traits_to_avoid"
        }
    ],
    "formality": [
        {
            "question": "How formal or casual should your brand voice be?",
            "type": "range",
            "min": 1,
            "max": 10,
            "default": 5,
            "labels": {1: "Very Casual", 5: "Balanced", 10: "Very Formal"},
            "name": "formality_level"
        },
        {
            "question": "Does your brand's formality level change in different contexts? If so, please describe:",
            "type": "textarea",
            "name": "context_variations"
        }
    ],
    "emotional_tone": [
        {
            "question": "What primary emotions should your brand voice convey? (Select up to 2)",
            "type": "multiselect",
            "options": ["Optimistic", "Serious", "Passionate", "Calm", "Urgent", "Reassuring"],
            "name": "primary_emotions",
            "max_selections": 2
        },
        {
            "question": "What secondary emotions might your brand voice convey? (Select up to 2)",
            "type": "multiselect",
            "options": ["Optimistic", "Serious", "Passionate", "Calm", "Urgent", "Reassuring"],
            "name": "secondary_emotions",
            "max_selections": 2
        },
        {
            "question": "Which emotional tones should your brand specifically avoid?",
            "type": "multiselect",
            "options": ["Optimistic", "Serious", "Passionate", "Calm", "Urgent", "Reassuring"],
            "name": "emotions_to_avoid"
        },
        {
            "question": "How intense should your brand's emotional expression be?",
            "type": "range",
            "min": 1,
            "max": 10,
            "default": 5,
            "labels": {1: "Subtle", 5: "Moderate", 10: "Intense"},
            "name": "emotional_intensity"
        }
    ],
    "vocabulary": [
        {
            "question": "List some key terms or phrases that your brand should use frequently:",
            "type": "textarea",
            "name": "preferred_terms"
        },
        {
            "question": "List any terms or phrases that your brand should avoid:",
            "type": "textarea",
            "name": "restricted_terms"
        },
        {
            "question": "How much industry jargon should your brand use?",
            "type": "range",
            "min": 1,
            "max": 10,
            "default": 5,
            "labels": {1: "Minimal", 5: "Moderate", 10: "Extensive"},
            "name": "jargon_level"
        },
        {
            "question": "How technically complex should your language be?",
            "type": "range",
            "min": 1,
            "max": 10,
            "default": 5,
            "labels": {1: "Simple", 5: "Moderate", 10: "Complex"},
            "name": "technical_complexity"
        }
    ],
    "communication_style": [
        {
            "question": "Should your brand favor direct communication or storytelling?",
            "type": "range",
            "min": 1,
            "max": 10,
            "default": 5,
            "labels": {1: "Very Direct", 5: "Balanced", 10: "Narrative-focused"},
            "name": "storytelling_preference"
        },
        {
            "question": "What sentence length does your brand prefer?",
            "type": "range",
            "min": 1,
            "max": 10,
            "default": 5,
            "labels": {1: "Very Short", 5: "Medium", 10: "Long"},
            "name": "sentence_length"
        },
        {
            "question": "What sentence complexity does your brand prefer?",
            "type": "range",
            "min": 1,
            "max": 10,
            "default": 5,
            "labels": {1: "Very Simple", 5: "Moderate", 10: "Complex"},
            "name": "sentence_complexity"
        },
        {
            "question": "Which rhetorical devices should your brand use? (Select all that apply)",
            "type": "multiselect",
            "options": ["Questions", "Metaphors", "Analogies", "Repetition", "Alliteration", "Statistics", "Quotes"],
            "name": "rhetorical_devices"
        },
        {
            "question": "How would you describe your brand's call-to-action style?",
            "type": "textarea",
            "name": "cta_style"
        }
    ],
    "audience_adaptation": [
        {
            "question": "Does your brand voice change for different audience segments? If so, please describe:",
            "type": "textarea",
            "name": "audience_segments"
        },
        {
            "question": "Does your brand voice change across different channels? If so, please describe:",
            "type": "textarea",
            "name": "channel_adaptations"
        },
        {
            "question": "Does your brand voice change across different customer journey stages? If so, please describe:",
            "type": "textarea",
            "name": "journey_stages"
        }
    ]
}

def analyze_interview_with_ai(responses):
    """Analyze interview responses using AI for deeper insights"""
    # Check if API integration is enabled
    if not session.get('api_settings', {}).get('integration_enabled', False) or not session.get('api_settings', {}).get('api_key'):
        flash('API integration is required for brand voice analysis. Please configure API settings.', 'danger')
        raise Exception("API integration is not enabled or API key is missing. Please configure API settings.")

    try:
        # Import the API client
        from app.utils.api_client import APIClient
        import json

        # Format the interview responses for analysis
        formatted_responses = json.dumps(responses, indent=2)

        # Create a prompt that explains the interview responses
        analysis_text = f"""
        Brand Voice Interview Responses:

        {formatted_responses}

        Please analyze these brand interview responses to extract deeper insights about the brand voice.
        """

        # Create API client and analyze
        api_provider = session['api_settings']['api_provider']
        api_key = session['api_settings']['api_key']

        print(f"Using {api_provider} API for brand interview analysis")
        api_client = APIClient(api_provider, api_key)
        success, results = api_client.analyze_text(analysis_text)

        if success:
            print("AI analysis of interview responses successful")
            return True, results
        else:
            error_msg = results.get('error', 'Unknown error')
            print(f"AI analysis failed: {error_msg}")
            raise Exception(f"API analysis failed: {error_msg}")
    except Exception as e:
        print(f"Error in AI interview analysis: {str(e)}")
        raise Exception(f"Error in AI interview analysis: {str(e)}")

def update_brand_parameters_from_interview(responses):
    """Update brand parameters based on interview responses"""
    brand_parameters = get_brand_parameters()

    # Try to get AI-enhanced insights first
    try:
        ai_success, ai_results = analyze_interview_with_ai(responses)
        print("Using AI-enhanced insights for brand parameters")
    except Exception as e:
        # If API analysis fails, redirect to API settings
        flash(f'API analysis failed: {str(e)}', 'danger')
        return redirect(url_for('api_settings'))

    # If AI analysis was successful, use those insights to enhance the basic mapping
    if ai_success and ai_results:

        # Extract AI recommendations if available
        if "recommendations" in ai_results:
            recommendations = ai_results["recommendations"]

            # Apply AI recommendations to brand parameters
            if "personality_traits" in recommendations:
                if "primary" in recommendations["personality_traits"]:
                    brand_parameters["personality"]["primary_traits"] = recommendations["personality_traits"]["primary"]
                if "secondary" in recommendations["personality_traits"]:
                    brand_parameters["personality"]["secondary_traits"] = recommendations["personality_traits"]["secondary"]

            if "emotional_tone" in recommendations:
                if "primary" in recommendations["emotional_tone"]:
                    brand_parameters["emotional_tone"]["primary_emotions"] = recommendations["emotional_tone"]["primary"]
                if "secondary" in recommendations["emotional_tone"]:
                    brand_parameters["emotional_tone"]["secondary_emotions"] = recommendations["emotional_tone"]["secondary"]

            if "formality" in recommendations:
                if "level" in recommendations["formality"]:
                    brand_parameters["formality"]["level"] = recommendations["formality"]["level"]

            if "vocabulary" in recommendations:
                if "preferred_terms" in recommendations["vocabulary"]:
                    brand_parameters["vocabulary"]["preferred_terms"] = recommendations["vocabulary"]["preferred_terms"]
                if "jargon_level" in recommendations["vocabulary"]:
                    brand_parameters["vocabulary"]["jargon_level"] = recommendations["vocabulary"]["jargon_level"]

            if "communication_style" in recommendations:
                if "storytelling_preference" in recommendations["communication_style"]:
                    brand_parameters["communication_style"]["storytelling_preference"] = recommendations["communication_style"]["storytelling_preference"]
                if "sentence_structure" in recommendations["communication_style"]:
                    if "length_preference" in recommendations["communication_style"]["sentence_structure"]:
                        brand_parameters["communication_style"]["sentence_structure"]["length_preference"] = recommendations["communication_style"]["sentence_structure"]["length_preference"]
                    if "complexity_preference" in recommendations["communication_style"]["sentence_structure"]:
                        brand_parameters["communication_style"]["sentence_structure"]["complexity_preference"] = recommendations["communication_style"]["sentence_structure"]["complexity_preference"]

    # Apply basic mapping for any parameters not set by AI
    # Update personality traits
    if not ai_success or "primary_traits" not in brand_parameters["personality"] or not brand_parameters["personality"]["primary_traits"]:
        if "primary_traits" in responses:
            brand_parameters["personality"]["primary_traits"] = [trait.lower() for trait in responses["primary_traits"]]
    if not ai_success or "secondary_traits" not in brand_parameters["personality"] or not brand_parameters["personality"]["secondary_traits"]:
        if "secondary_traits" in responses:
            brand_parameters["personality"]["secondary_traits"] = [trait.lower() for trait in responses["secondary_traits"]]
    if "traits_to_avoid" in responses:
        brand_parameters["personality"]["traits_to_avoid"] = [trait.lower() for trait in responses["traits_to_avoid"]]

    # Update formality
    if not ai_success or "level" not in brand_parameters["formality"] or not brand_parameters["formality"]["level"]:
        if "formality_level" in responses:
            brand_parameters["formality"]["level"] = int(responses["formality_level"])
    if "context_variations" in responses:
        brand_parameters["formality"]["context_variations"] = {"general": responses["context_variations"]}

    # Update emotional tone
    if not ai_success or "primary_emotions" not in brand_parameters["emotional_tone"] or not brand_parameters["emotional_tone"]["primary_emotions"]:
        if "primary_emotions" in responses:
            brand_parameters["emotional_tone"]["primary_emotions"] = [emotion.lower() for emotion in responses["primary_emotions"]]
    if not ai_success or "secondary_emotions" not in brand_parameters["emotional_tone"] or not brand_parameters["emotional_tone"]["secondary_emotions"]:
        if "secondary_emotions" in responses:
            brand_parameters["emotional_tone"]["secondary_emotions"] = [emotion.lower() for emotion in responses["secondary_emotions"]]
    if "emotions_to_avoid" in responses:
        brand_parameters["emotional_tone"]["emotions_to_avoid"] = [emotion.lower() for emotion in responses["emotions_to_avoid"]]
    if "emotional_intensity" in responses:
        brand_parameters["emotional_tone"]["intensity"] = int(responses["emotional_intensity"])

    # Update vocabulary
    if not ai_success or "preferred_terms" not in brand_parameters["vocabulary"] or not brand_parameters["vocabulary"]["preferred_terms"]:
        if "preferred_terms" in responses:
            terms = [term.strip() for term in responses["preferred_terms"].split(",") if term.strip()]
            brand_parameters["vocabulary"]["preferred_terms"] = terms
    if "restricted_terms" in responses:
        terms = [term.strip() for term in responses["restricted_terms"].split(",") if term.strip()]
        brand_parameters["vocabulary"]["restricted_terms"] = terms
    if not ai_success or "jargon_level" not in brand_parameters["vocabulary"] or not brand_parameters["vocabulary"]["jargon_level"]:
        if "jargon_level" in responses:
            brand_parameters["vocabulary"]["jargon_level"] = int(responses["jargon_level"])
    if "technical_complexity" in responses:
        brand_parameters["vocabulary"]["technical_complexity"] = int(responses["technical_complexity"])

    # Update communication style
    if not ai_success or "storytelling_preference" not in brand_parameters["communication_style"] or not brand_parameters["communication_style"]["storytelling_preference"]:
        if "storytelling_preference" in responses:
            brand_parameters["communication_style"]["storytelling_preference"] = int(responses["storytelling_preference"])
    if not ai_success or "length_preference" not in brand_parameters["communication_style"]["sentence_structure"] or not brand_parameters["communication_style"]["sentence_structure"]["length_preference"]:
        if "sentence_length" in responses:
            brand_parameters["communication_style"]["sentence_structure"]["length_preference"] = int(responses["sentence_length"])
    if not ai_success or "complexity_preference" not in brand_parameters["communication_style"]["sentence_structure"] or not brand_parameters["communication_style"]["sentence_structure"]["complexity_preference"]:
        if "sentence_complexity" in responses:
            brand_parameters["communication_style"]["sentence_structure"]["complexity_preference"] = int(responses["sentence_complexity"])
    if "rhetorical_devices" in responses:
        brand_parameters["communication_style"]["rhetorical_devices"] = responses["rhetorical_devices"]
    if "cta_style" in responses:
        brand_parameters["communication_style"]["cta_style"] = responses["cta_style"]

    # Update audience adaptation
    if "audience_segments" in responses:
        brand_parameters["audience_adaptation"]["audience_segments"] = {"general": responses["audience_segments"]}
    if "channel_adaptations" in responses:
        brand_parameters["audience_adaptation"]["channel_adaptations"] = {"general": responses["channel_adaptations"]}
    if "journey_stages" in responses:
        brand_parameters["audience_adaptation"]["journey_stage_adaptations"] = {"general": responses["journey_stages"]}

    # Update brand parameters with method name for merging
    update_brand_parameters(brand_parameters, method_name="brand_interview")
    return brand_parameters

@brand_interview_bp.route('/brand-interview', methods=['GET', 'POST'])
def index():
    # Check if API integration is enabled and we have API settings
    if not session.get('api_settings', {}).get('integration_enabled', False) or not session.get('api_settings', {}).get('api_key'):
        flash('API integration is required for brand voice analysis. Please configure API settings.', 'danger')
        return redirect(url_for('api_settings'))

    # Initialize or get current section
    if 'current_section' not in session:
        session['current_section'] = 'personality'

    # Initialize or get interview responses
    if 'interview_responses' not in session:
        session['interview_responses'] = {}

    if request.method == 'POST':
        # Get form data
        form_data = request.form.to_dict(flat=False)

        # Process form data
        responses = {}
        for key, value in form_data.items():
            if len(value) == 1:
                responses[key] = value[0]
            else:
                responses[key] = value

        # Save responses to session
        session['interview_responses'].update(responses)
        session.modified = True

        # Handle navigation
        if 'next_section' in request.form:
            # Get next section
            sections = list(INTERVIEW_QUESTIONS.keys())
            current_index = sections.index(session['current_section'])

            if current_index < len(sections) - 1:
                # Go to next section
                session['current_section'] = sections[current_index + 1]
            else:
                # Complete interview
                result = update_brand_parameters_from_interview(session['interview_responses'])

                # Check if the function returned a redirect (in case of API error)
                if result is not None and hasattr(result, 'status_code'):
                    return result

                update_input_method('brand_interview', True, session['interview_responses'])

                # Clear interview session data
                session.pop('current_section', None)
                session.pop('interview_responses', None)

                flash('Interview completed! Your brand voice parameters have been updated.', 'success')
                return redirect(url_for('brand_interview.results'))

        elif 'prev_section' in request.form:
            # Get previous section
            sections = list(INTERVIEW_QUESTIONS.keys())
            current_index = sections.index(session['current_section'])

            if current_index > 0:
                # Go to previous section
                session['current_section'] = sections[current_index - 1]

    # Get current section questions
    current_section = session['current_section']
    questions = INTERVIEW_QUESTIONS[current_section]

    # Calculate progress
    sections = list(INTERVIEW_QUESTIONS.keys())
    current_index = sections.index(current_section)
    progress = (current_index) / len(sections) * 100

    return render_template('brand_interview/index.html',
                          current_section=current_section,
                          questions=questions,
                          progress=progress,
                          sections=sections,
                          current_index=current_index,
                          responses=session.get('interview_responses', {}))

@brand_interview_bp.route('/brand-interview/results')
def results():
    # Get input methods status
    input_methods = get_input_methods()

    # Check if brand interview has been used
    if not input_methods['brand_interview']['used']:
        flash('Please complete the brand interview first.', 'warning')
        return redirect(url_for('brand_interview.index'))

    # Get brand parameters
    brand_parameters = get_brand_parameters()

    return render_template('brand_interview/results.html',
                          brand_parameters=brand_parameters)
