from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import json
from datetime import datetime
from app.utils.session_manager import get_brand_parameters, update_brand_parameters, get_input_methods, any_input_method_used
from app.utils.example_generator import generate_example_copy

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def index():
    # Check if any input method has been used
    if not any_input_method_used():
        flash('You need to complete at least one input method before accessing the dashboard.', 'warning')
        return redirect(url_for('home.index'))
    
    # Get brand parameters and input methods
    brand_parameters = get_brand_parameters()
    input_methods = get_input_methods()
    
    # Generate example copy
    example_copy = generate_example_copy(brand_parameters)
    
    return render_template('dashboard/index.html',
                          brand_parameters=brand_parameters,
                          input_methods=input_methods,
                          example_copy=example_copy)

@dashboard_bp.route('/dashboard/update', methods=['POST'])
def update():
    # Get current brand parameters
    brand_parameters = get_brand_parameters()
    
    # Update parameters based on form data
    form_data = request.form.to_dict(flat=False)
    
    # Process personality traits
    if 'primary_traits[]' in form_data:
        brand_parameters['personality']['primary_traits'] = [trait.lower() for trait in form_data['primary_traits[]']]
    
    if 'secondary_traits[]' in form_data:
        brand_parameters['personality']['secondary_traits'] = [trait.lower() for trait in form_data['secondary_traits[]']]
    
    if 'traits_to_avoid[]' in form_data:
        brand_parameters['personality']['traits_to_avoid'] = [trait.lower() for trait in form_data['traits_to_avoid[]']]
    
    # Process formality
    if 'formality_level' in form_data:
        brand_parameters['formality']['level'] = int(form_data['formality_level'][0])
    
    if 'context_variations' in form_data:
        brand_parameters['formality']['context_variations'] = {'general': form_data['context_variations'][0]}
    
    # Process emotional tone
    if 'primary_emotions[]' in form_data:
        brand_parameters['emotional_tone']['primary_emotions'] = [emotion.lower() for emotion in form_data['primary_emotions[]']]
    
    if 'secondary_emotions[]' in form_data:
        brand_parameters['emotional_tone']['secondary_emotions'] = [emotion.lower() for emotion in form_data['secondary_emotions[]']]
    
    if 'emotions_to_avoid[]' in form_data:
        brand_parameters['emotional_tone']['emotions_to_avoid'] = [emotion.lower() for emotion in form_data['emotions_to_avoid[]']]
    
    if 'emotional_intensity' in form_data:
        brand_parameters['emotional_tone']['intensity'] = int(form_data['emotional_intensity'][0])
    
    # Process vocabulary
    if 'preferred_terms' in form_data:
        terms = [term.strip() for term in form_data['preferred_terms'][0].split(',') if term.strip()]
        brand_parameters['vocabulary']['preferred_terms'] = terms
    
    if 'restricted_terms' in form_data:
        terms = [term.strip() for term in form_data['restricted_terms'][0].split(',') if term.strip()]
        brand_parameters['vocabulary']['restricted_terms'] = terms
    
    if 'jargon_level' in form_data:
        brand_parameters['vocabulary']['jargon_level'] = int(form_data['jargon_level'][0])
    
    if 'technical_complexity' in form_data:
        brand_parameters['vocabulary']['technical_complexity'] = int(form_data['technical_complexity'][0])
    
    # Process communication style
    if 'storytelling_preference' in form_data:
        brand_parameters['communication_style']['storytelling_preference'] = int(form_data['storytelling_preference'][0])
    
    if 'sentence_length' in form_data:
        brand_parameters['communication_style']['sentence_structure']['length_preference'] = int(form_data['sentence_length'][0])
    
    if 'sentence_complexity' in form_data:
        brand_parameters['communication_style']['sentence_structure']['complexity_preference'] = int(form_data['sentence_complexity'][0])
    
    if 'rhetorical_devices[]' in form_data:
        brand_parameters['communication_style']['rhetorical_devices'] = form_data['rhetorical_devices[]']
    
    if 'cta_style' in form_data:
        brand_parameters['communication_style']['cta_style'] = form_data['cta_style'][0]
    
    # Process audience adaptation
    if 'audience_segments' in form_data:
        brand_parameters['audience_adaptation']['audience_segments'] = {'general': form_data['audience_segments'][0]}
    
    if 'channel_adaptations' in form_data:
        brand_parameters['audience_adaptation']['channel_adaptations'] = {'general': form_data['channel_adaptations'][0]}
    
    if 'journey_stages' in form_data:
        brand_parameters['audience_adaptation']['journey_stage_adaptations'] = {'general': form_data['journey_stages'][0]}
    
    # Update brand parameters in session
    update_brand_parameters(brand_parameters)
    
    flash('Brand voice parameters updated successfully!', 'success')
    return redirect(url_for('dashboard.index'))

@dashboard_bp.route('/dashboard/export')
def export():
    # Get brand parameters
    brand_parameters = get_brand_parameters()
    
    # Convert to JSON
    params_json = json.dumps(brand_parameters, indent=2)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"brand_voice_parameters_{timestamp}.json"
    
    # Return as downloadable file
    response = jsonify(brand_parameters)
    response.headers.set('Content-Disposition', f'attachment; filename={filename}')
    response.headers.set('Content-Type', 'application/json')
    
    return response

@dashboard_bp.route('/dashboard/generate-example')
def generate_example():
    # Get brand parameters
    brand_parameters = get_brand_parameters()
    
    # Generate example copy
    example_copy = generate_example_copy(brand_parameters)
    
    return jsonify({'example': example_copy})
