import os
import json
import nltk
import PyPDF2
import requests
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, make_response
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from bs4 import BeautifulSoup
from werkzeug.utils import secure_filename
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
import re

# Download necessary NLTK data
try:
    nltk.download('punkt')
    nltk.download('punkt_tab')
    nltk.download('stopwords')
    print("NLTK resources downloaded successfully")
except Exception as e:
    print(f"Error downloading NLTK resources: {str(e)}")

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-brand-voice-codifier')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # Session lifetime in seconds (1 hour)
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize Flask-Session
Session(app)

# Register blueprints
from app.routes.web_scraper import web_scraper_bp
app.register_blueprint(web_scraper_bp, url_prefix='/web-scraper')

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Custom Jinja2 filters
@app.template_filter('nl2br')
def nl2br_filter(s):
    """Convert newlines to <br> tags"""
    if not s:
        return s
    from markupsafe import Markup
    return Markup(s.replace('\n', '<br>'))

# Initialize CSRF protection but disable it for testing
# csrf = CSRFProtect(app)
app.config['WTF_CSRF_ENABLED'] = False

# Personality traits dictionary
PERSONALITY_TRAITS = {
    "innovative": ["innovative", "creative", "cutting-edge", "pioneering", "inventive", "original", "groundbreaking"],
    "trustworthy": ["trustworthy", "reliable", "dependable", "honest", "credible", "authentic", "transparent"],
    "playful": ["playful", "fun", "lighthearted", "humorous", "witty", "amusing", "entertaining"],
    "sophisticated": ["sophisticated", "elegant", "refined", "polished", "cultured", "high-end", "premium"],
    "friendly": ["friendly", "approachable", "warm", "welcoming", "personable", "accessible", "conversational"],
    "authoritative": ["authoritative", "expert", "knowledgeable", "professional", "competent", "credible", "informed"],
    "bold": ["bold", "daring", "brave", "fearless", "confident", "assertive", "strong"],
    "empathetic": ["empathetic", "compassionate", "understanding", "caring", "supportive", "sensitive", "thoughtful"]
}

# Emotional tone dictionary
EMOTIONAL_TONES = {
    "optimistic": ["optimistic", "positive", "hopeful", "upbeat", "encouraging", "inspiring", "motivating"],
    "serious": ["serious", "solemn", "grave", "earnest", "sober", "formal", "no-nonsense"],
    "passionate": ["passionate", "enthusiastic", "excited", "energetic", "fervent", "ardent", "zealous"],
    "calm": ["calm", "peaceful", "serene", "tranquil", "relaxed", "composed", "steady"],
    "urgent": ["urgent", "pressing", "critical", "crucial", "vital", "essential", "immediate"],
    "reassuring": ["reassuring", "comforting", "soothing", "consoling", "encouraging", "supportive", "calming"]
}

# Helper functions
def initialize_session():
    """Initialize session variables if they don't exist"""
    # Make session permanent
    session.permanent = True
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

    if 'api_settings' not in session:
        session['api_settings'] = {
            "api_key": "",
            "api_provider": "",
            "integration_enabled": False,
            "last_sync_time": None
        }

    if 'brightdata_settings' not in session:
        session['brightdata_settings'] = {
            "api_key": "",
            "zone": "web_unlocker1",
            "enabled": False
        }

def analyze_text(text):
    """Analyze text to extract brand voice parameters"""
    # Tokenize text
    sentences = sent_tokenize(text)
    words = word_tokenize(text.lower())

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word.isalnum() and word not in stop_words]

    # Calculate basic metrics
    avg_sentence_length = sum(len(word_tokenize(sentence)) for sentence in sentences) / len(sentences) if sentences else 0

    # Analyze personality traits
    personality_matches = {}
    for trait, keywords in PERSONALITY_TRAITS.items():
        matches = sum(1 for word in filtered_words if word in keywords)
        for keyword in keywords:
            matches += sum(1 for sentence in sentences if keyword in sentence.lower())
        personality_matches[trait] = matches

    # Analyze emotional tone
    emotion_matches = {}
    for emotion, keywords in EMOTIONAL_TONES.items():
        matches = sum(1 for word in filtered_words if word in keywords)
        for keyword in keywords:
            matches += sum(1 for sentence in sentences if keyword in sentence.lower())
        emotion_matches[emotion] = matches

    # Analyze formality
    formality_indicators = {
        "formal": ["therefore", "consequently", "furthermore", "moreover", "thus", "hence", "regarding",
                  "concerning", "accordingly", "subsequently"],
        "informal": ["anyway", "basically", "actually", "so", "well", "you know", "kind of", "sort of",
                    "like", "stuff", "thing"]
    }

    formal_count = sum(text.lower().count(word) for word in formality_indicators["formal"])
    informal_count = sum(text.lower().count(word) for word in formality_indicators["informal"])

    formality_score = 5  # Default middle value
    if formal_count + informal_count > 0:
        formality_score = min(10, max(1, int(10 * formal_count / (formal_count + informal_count))))

    # Get most common words for vocabulary analysis
    word_freq = FreqDist(filtered_words)
    common_words = word_freq.most_common(50)

    # Analyze sentence structure
    sentence_lengths = [len(word_tokenize(sentence)) for sentence in sentences]
    short_sentences = sum(1 for length in sentence_lengths if length < 10)
    medium_sentences = sum(1 for length in sentence_lengths if 10 <= length < 20)
    long_sentences = sum(1 for length in sentence_lengths if length >= 20)

    sentence_complexity = 5  # Default middle value
    if short_sentences + medium_sentences + long_sentences > 0:
        sentence_complexity = min(10, max(1, int(10 * (medium_sentences + 2 * long_sentences) /
                                              (short_sentences + medium_sentences + long_sentences))))

    # Return analysis results
    return {
        "personality_traits": personality_matches,
        "emotional_tone": emotion_matches,
        "formality_score": formality_score,
        "common_vocabulary": common_words,
        "avg_sentence_length": avg_sentence_length,
        "sentence_complexity": sentence_complexity
    }

def update_brand_parameters(analysis_results):
    """Update brand parameters based on analysis results"""
    # Update personality traits
    personality = sorted(analysis_results["personality_traits"].items(), key=lambda x: x[1], reverse=True)
    if personality:
        session['brand_parameters']["personality"]["primary_traits"] = [trait for trait, _ in personality[:3]]
        session['brand_parameters']["personality"]["secondary_traits"] = [trait for trait, _ in personality[3:6]]

    # Update emotional tone
    emotions = sorted(analysis_results["emotional_tone"].items(), key=lambda x: x[1], reverse=True)
    if emotions:
        session['brand_parameters']["emotional_tone"]["primary_emotions"] = [emotion for emotion, _ in emotions[:2]]
        session['brand_parameters']["emotional_tone"]["secondary_emotions"] = [emotion for emotion, _ in emotions[2:4]]

    # Update formality
    session['brand_parameters']["formality"]["level"] = analysis_results["formality_score"]

    # Update vocabulary
    session['brand_parameters']["vocabulary"]["preferred_terms"] = [word for word, _ in analysis_results["common_vocabulary"][:20]]

    # Update communication style
    session['brand_parameters']["communication_style"]["sentence_structure"]["length_preference"] = min(10, max(1, int(analysis_results["avg_sentence_length"] / 3)))
    session['brand_parameters']["communication_style"]["sentence_structure"]["complexity_preference"] = analysis_results["sentence_complexity"]

    session.modified = True

def generate_example_copy(parameters):
    """Generate example copy based on the brand voice parameters and actual document content"""

    # Check if we have the original API response with key phrases
    if "original_api_response" in parameters:
        api_response = parameters["original_api_response"]

        # Use key phrases from the API response if available
        if "communication_style" in api_response and "key_phrases" in api_response["communication_style"]:
            key_phrases = api_response["communication_style"]["key_phrases"]
            if key_phrases and len(key_phrases) > 0:
                # Format the output using actual phrases from the document
                result = "Examples from your brand document:\n\n"
                for i, phrase in enumerate(key_phrases[:3], 1):
                    result += f"{i}. \"{phrase}\"\n"

                # Add preferred terms if available
                if "vocabulary" in api_response and "preferred_terms" in api_response["vocabulary"]:
                    preferred_terms = api_response["vocabulary"]["preferred_terms"]
                    if preferred_terms and len(preferred_terms) > 0:
                        result += "\nPreferred terms from your document:\n"
                        terms_list = ", ".join([f"\"{term}\"" for term in preferred_terms[:5]])
                        result += terms_list

                return result

    # Extract key parameters for fallback
    primary_traits = parameters["personality"]["primary_traits"]
    primary_emotions = parameters["emotional_tone"]["primary_emotions"]

    # Simple fallback if no API response is available
    if not primary_traits or not primary_emotions:
        return "Complete at least one input method to generate example copy based on your document."

    # Create a simple fallback message
    traits_str = ", ".join(primary_traits)
    emotions_str = ", ".join(primary_emotions)

    return f"Based on your document analysis, your brand voice is {traits_str} with a {emotions_str} tone.\n\nFor specific examples, please upload a document with clear brand voice guidelines."

# Routes
@app.route('/')
def home():
    initialize_session()

    # Debug session data
    print("\nHome route - Session data:")
    print(f"Document upload used: {session['input_methods']['document_upload'].get('used', False)}")
    print(f"Document upload timestamp: {session['input_methods']['document_upload'].get('timestamp', 'None')}")
    print(f"Web scraper used: {session['input_methods']['web_scraper'].get('used', False)}")
    print(f"Brand interview used: {session['input_methods']['brand_interview'].get('used', False)}")

    # Make sure session is saved
    session.modified = True

    return render_template('index.html', input_methods=session['input_methods'])

@app.route('/restart', methods=['POST'])
def restart():
    """Clear the session and restart the application"""
    # Clear the session
    session.clear()
    # Initialize a fresh session
    initialize_session()
    flash('Session restarted successfully. All data has been reset.', 'success')
    return redirect(url_for('home'))

@app.route('/document-upload', methods=['GET', 'POST'])
def document_upload():
    initialize_session()

    if request.method == 'POST':
        # Check if the post request has the file part
        if 'document' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)

        file = request.files['document']

        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            try:
                # Extract text based on file type
                text = ""
                if filename.endswith('.pdf'):
                    try:
                        with open(file_path, 'rb') as f:
                            pdf_reader = PyPDF2.PdfReader(f)
                            for page in pdf_reader.pages:
                                page_text = page.extract_text()
                                if page_text:
                                    text += page_text + "\n\n"  # Add spacing between pages

                        # Print the extracted text for debugging
                        print(f"Extracted PDF text (length: {len(text)} chars)")
                        print("First 500 chars:")
                        print(text[:500])
                        print("Last 500 chars:")
                        print(text[-500:] if len(text) > 500 else text)

                        # Save the extracted text to a debug file for inspection
                        try:
                            with open('debug_extracted_text.txt', 'w', encoding='utf-8') as f:
                                f.write(text)
                            print("Saved extracted text to debug_extracted_text.txt for inspection")
                        except Exception as e:
                            print(f"Error saving debug file: {str(e)}")
                    except Exception as e:
                        flash(f'Error reading PDF file: {str(e)}', 'danger')
                        print(f"PDF extraction error: {str(e)}")
                elif filename.endswith('.txt'):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            text = f.read()
                            # Print the extracted text for debugging
                            print(f"Extracted TXT text (length: {len(text)} chars)")
                            print("First 500 chars:")
                            print(text[:500])
                            print("Last 500 chars:")
                            print(text[-500:] if len(text) > 500 else text)

                            # Save the extracted text to a debug file for inspection
                            try:
                                with open('debug_extracted_text.txt', 'w', encoding='utf-8') as f:
                                    f.write(text)
                                print("Saved extracted text to debug_extracted_text.txt for inspection")
                            except Exception as e:
                                print(f"Error saving debug file: {str(e)}")
                    except UnicodeDecodeError:
                        # Try with different encoding if UTF-8 fails
                        with open(file_path, 'r', encoding='latin-1') as f:
                            text = f.read()
                            # Print the extracted text for debugging
                            print(f"Extracted TXT text with latin-1 encoding (length: {len(text)} chars)")
                            print("First 500 chars:")
                            print(text[:500])
                            print("Last 500 chars:")
                            print(text[-500:] if len(text) > 500 else text)

                            # Save the extracted text to a debug file for inspection
                            try:
                                with open('debug_extracted_text.txt', 'w', encoding='utf-8') as f:
                                    f.write(text)
                                print("Saved extracted text to debug_extracted_text.txt for inspection")
                            except Exception as e:
                                print(f"Error saving debug file: {str(e)}")
                    except Exception as e:
                        flash(f'Error reading text file: {str(e)}', 'danger')
                        print(f"Text file reading error: {str(e)}")
                else:
                    flash('Unsupported file format. Please upload a PDF or TXT file.', 'danger')

                # Save the extracted text to a debug file for inspection
                try:
                    with open('debug_extracted_text.txt', 'w', encoding='utf-8') as f:
                        f.write(text)
                    print("Saved extracted text to debug_extracted_text.txt for inspection")
                except Exception as e:
                    print(f"Error saving debug file: {str(e)}")

                # Remove the file after processing
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error removing temporary file: {str(e)}")

                if text:
                    try:
                        # Analyze the text
                        print(f"Analyzing text of length: {len(text)}")

                        # Check if API key is set
                        api_key = session['api_settings'].get('api_key', '')

                        # Always set these values
                        session['api_settings']['api_provider'] = 'openai'
                        session['api_settings']['integration_enabled'] = True
                        session.modified = True

                        if not api_key:
                            flash('API key is required for document analysis. Please enter your OpenAI API key.', 'danger')
                            return redirect(url_for('api_settings'))

                        # Import the text analyzer with API support
                        from app.utils.text_analyzer import analyze_text as api_analyze_text

                        try:
                            print(f"Using {session['api_settings']['api_provider']} API for text analysis")
                            analysis_results = api_analyze_text(text)
                        except Exception as e:
                            flash(f'API analysis failed: {str(e)}', 'danger')
                            return redirect(url_for('api_settings'))

                        # First update the parameters using the text analyzer function
                        from app.utils.text_analyzer import update_brand_parameters as update_params_from_analysis
                        from app.utils.session_manager import get_brand_parameters
                        brand_parameters = get_brand_parameters()
                        updated_parameters = update_params_from_analysis(brand_parameters, analysis_results)

                        # Then use the session manager function to merge with method name
                        from app.utils.session_manager import update_brand_parameters as update_session_parameters
                        update_session_parameters(updated_parameters, method_name="document_upload")

                        # Mark document upload as used
                        session['input_methods']['document_upload']['used'] = True
                        session['input_methods']['document_upload']['data'] = analysis_results

                        # Update the timestamp
                        session['input_methods']['document_upload']['timestamp'] = datetime.now().isoformat()

                        # Make sure the session is saved
                        session.modified = True

                        # Print confirmation for debugging
                        print("Document upload marked as used:", session['input_methods']['document_upload']['used'])
                        print("Document upload timestamp:", session['input_methods']['document_upload']['timestamp'])

                        flash('Document analyzed successfully! You can now view the results.', 'success')
                        return redirect(url_for('home'))
                    except Exception as e:
                        flash(f'Error analyzing document: {str(e)}', 'danger')
                        print(f"Text analysis error: {str(e)}")
                else:
                    flash('Could not extract text from the uploaded file.', 'danger')
            except Exception as e:
                flash(f'An unexpected error occurred: {str(e)}', 'danger')
                print(f"Unexpected error in document upload: {str(e)}")

    return render_template('document_upload.html')

@app.route('/brand-interview', methods=['GET', 'POST'])
def brand_interview():
    initialize_session()

    if request.method == 'POST':
        # Process form data
        # Personality traits
        primary_traits = request.form.getlist('primary_traits')
        secondary_traits = request.form.getlist('secondary_traits')
        traits_to_avoid = request.form.getlist('traits_to_avoid')

        # Handle "other" options
        if 'other' in primary_traits and request.form.get('primary_traits_other'):
            primary_traits.remove('other')
            primary_traits.append(request.form.get('primary_traits_other').lower())

        if 'other' in secondary_traits and request.form.get('secondary_traits_other'):
            secondary_traits.remove('other')
            secondary_traits.append(request.form.get('secondary_traits_other').lower())

        if 'other' in traits_to_avoid and request.form.get('traits_to_avoid_other'):
            traits_to_avoid.remove('other')
            traits_to_avoid.append(request.form.get('traits_to_avoid_other').lower())

        # Emotional tone
        primary_emotions = request.form.getlist('primary_emotions')
        secondary_emotions = request.form.getlist('secondary_emotions')
        emotional_intensity = int(request.form.get('emotional_intensity', 5))

        # Handle "other" options
        if 'other' in primary_emotions and request.form.get('primary_emotions_other'):
            primary_emotions.remove('other')
            primary_emotions.append(request.form.get('primary_emotions_other').lower())

        if 'other' in secondary_emotions and request.form.get('secondary_emotions_other'):
            secondary_emotions.remove('other')
            secondary_emotions.append(request.form.get('secondary_emotions_other').lower())

        # Formality
        formality_level = int(request.form.get('formality_level', 5))
        formality_varies = request.form.get('formality_varies') == 'yes'
        formality_context = request.form.get('formality_context', '')

        # Communication style
        storytelling_preference = int(request.form.get('storytelling_preference', 5))
        sentence_length = int(request.form.get('sentence_length', 5))
        sentence_complexity = int(request.form.get('sentence_complexity', 5))

        # Update brand parameters
        session['brand_parameters']['personality']['primary_traits'] = primary_traits
        session['brand_parameters']['personality']['secondary_traits'] = secondary_traits
        session['brand_parameters']['personality']['traits_to_avoid'] = traits_to_avoid

        session['brand_parameters']['emotional_tone']['primary_emotions'] = primary_emotions
        session['brand_parameters']['emotional_tone']['secondary_emotions'] = secondary_emotions
        session['brand_parameters']['emotional_tone']['intensity'] = emotional_intensity

        session['brand_parameters']['formality']['level'] = formality_level
        if formality_varies and formality_context:
            # Parse context variations from the text input
            # Simple parsing: split by commas or newlines
            contexts = [c.strip() for c in re.split(r'[,\n]', formality_context) if c.strip()]
            context_dict = {}
            for context in contexts:
                if ':' in context:
                    key, value = context.split(':', 1)
                    context_dict[key.strip().lower()] = value.strip()

            if context_dict:
                session['brand_parameters']['formality']['context_variations'] = context_dict

        session['brand_parameters']['communication_style']['storytelling_preference'] = storytelling_preference
        session['brand_parameters']['communication_style']['sentence_structure']['length_preference'] = sentence_length
        session['brand_parameters']['communication_style']['sentence_structure']['complexity_preference'] = sentence_complexity

        # Mark brand interview as used
        session['input_methods']['brand_interview']['used'] = True
        session['input_methods']['brand_interview']['data'] = {
            'timestamp': datetime.now().isoformat(),
            'primary_traits': primary_traits,
            'primary_emotions': primary_emotions,
            'formality_level': formality_level
        }

        session.modified = True

        flash('Brand interview completed successfully!', 'success')
        return redirect(url_for('results'))

    return render_template('brand_interview.html')

@app.route('/simple-form')
def simple_form():
    return render_template('simple_form.html')

@app.route('/web-scraper')
def web_scraper_redirect():
    """Redirect old web scraper URL to the new blueprint route"""
    return redirect(url_for('web_scraper_bp.index'))

@app.route('/results')
def results():
    initialize_session()

    # Check if any input method has been used
    if not any(method['used'] for method in session['input_methods'].values()):
        flash('You need to complete at least one input method first.', 'warning')
        return redirect(url_for('home'))

    # Make sure parameters are merged from all input methods
    from app.utils.session_manager import merge_brand_parameters
    merge_brand_parameters()

    # Get parameter sources for the template
    parameter_sources = session.get('parameter_sources', {})

    # Print the parameters being passed to the template
    print("\nParameters being passed to the results template:")
    print(f"Personality primary traits: {session['brand_parameters']['personality']['primary_traits']}")
    print(f"Personality secondary traits: {session['brand_parameters']['personality']['secondary_traits']}")
    print(f"Emotional tone primary: {session['brand_parameters']['emotional_tone']['primary_emotions']}")
    print(f"Emotional tone secondary: {session['brand_parameters']['emotional_tone']['secondary_emotions']}")
    print(f"Formality level: {session['brand_parameters']['formality']['level']}")
    print(f"Communication style - storytelling: {session['brand_parameters']['communication_style']['storytelling_preference']}")
    print(f"Communication style - length: {session['brand_parameters']['communication_style']['sentence_structure']['length_preference']}")
    print(f"Communication style - complexity: {session['brand_parameters']['communication_style']['sentence_structure']['complexity_preference']}")

    # Debug input methods
    print("\nInput methods status:")
    for method_name, method_data in session['input_methods'].items():
        print(f"{method_name}: used={method_data.get('used', False)}, timestamp={method_data.get('timestamp', 'None')}")

    # Generate brand voice summary
    from app.utils.text_analyzer import generate_brand_voice_summary

    # Get analysis results from the most recently used method
    analysis_results = None
    for method, data in session['input_methods'].items():
        if data.get('used', False) and 'data' in data:
            analysis_results = data['data']
            break

    # Generate the brand voice summary
    brand_voice_summary = generate_brand_voice_summary(
        session['brand_parameters'],
        analysis_results=analysis_results,
        input_methods=session['input_methods']
    )

    # Store the summary in the session for later use
    session['brand_voice_summary'] = brand_voice_summary
    session.modified = True

    # Check if the summary has been approved
    summary_approved = session.get('summary_approved', False)

    return render_template('results.html',
                          brand_parameters=session['brand_parameters'],
                          input_methods=session['input_methods'],
                          api_settings=session['api_settings'],
                          parameter_sources=parameter_sources,
                          example_copy=generate_example_copy(session['brand_parameters']),
                          brand_voice_summary=brand_voice_summary,
                          summary_approved=summary_approved)

@app.route('/approve-summary', methods=['POST'])
def approve_summary():
    """Handle approval or editing of the brand voice summary"""
    initialize_session()

    if request.method == 'POST':
        action = request.form.get('action', '')

        if action == 'approve':
            # Mark the summary as approved
            session['summary_approved'] = True
            flash('Brand voice summary approved!', 'success')

        elif action == 'edit':
            # Get the edited summary values
            tone_description = request.form.get('tone_description', '')
            example_phrases = request.form.getlist('example_phrases')
            frequently_used_words = request.form.getlist('frequently_used_words')
            words_to_avoid = request.form.getlist('words_to_avoid')

            # Update the summary in the session
            if 'brand_voice_summary' not in session:
                session['brand_voice_summary'] = {}

            session['brand_voice_summary']['tone_description'] = tone_description
            session['brand_voice_summary']['example_phrases'] = example_phrases
            session['brand_voice_summary']['frequently_used_words'] = frequently_used_words
            session['brand_voice_summary']['words_to_avoid'] = words_to_avoid

            # Mark as approved since it's been edited
            session['summary_approved'] = True
            flash('Brand voice summary updated and approved!', 'success')

        session.modified = True

    return redirect(url_for('results'))

@app.route('/export')
def export():
    initialize_session()

    # Check if any input method has been used
    if not any(method['used'] for method in session['input_methods'].values()):
        flash('You need to complete at least one input method first.', 'warning')
        return redirect(url_for('home'))

    # Get the requested format (default to HTML)
    export_format = request.args.get('format', 'html').lower()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    css_version = datetime.now().strftime("%Y%m%d%H%M%S")  # Add a version for cache busting

    # Get the brand voice summary
    brand_voice_summary = session.get('brand_voice_summary', {})

    if export_format == 'json':
        # Generate JSON with brand parameters and summary
        export_data = {
            'brand_parameters': session['brand_parameters'],
            'brand_voice_summary': brand_voice_summary
        }
        response = jsonify(export_data)
        response.headers.set('Content-Disposition', f'attachment; filename=brand_voice_parameters_{file_timestamp}.json')
        response.headers.set('Content-Type', 'application/json')
        return response

    elif export_format == 'pdf':
        # For now, we'll redirect to the HTML report with a message
        # In a production environment, you would use a PDF generation library
        flash('PDF export is not available in the demo version. Please use the print function instead.', 'info')
        return redirect(url_for('export', format='html'))

    else:  # HTML report (default)
        # Generate HTML report
        response = make_response(render_template('report.html',
                              brand_parameters=session['brand_parameters'],
                              example_copy=generate_example_copy(session['brand_parameters']),
                              brand_voice_summary=brand_voice_summary,
                              timestamp=timestamp,
                              css_version=css_version,
                              current_year=datetime.now().year))

        # Add cache control headers
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'

        return response

@app.route('/api_settings', methods=['GET', 'POST'])
def api_settings():
    initialize_session()

    if request.method == 'POST':
        # Get API key from form
        api_key = request.form.get('api_key', '')

        # Always use OpenAI and enable integration
        api_provider = 'openai'
        integration_enabled = True

        # Update session
        session['api_settings']['api_key'] = api_key
        session['api_settings']['api_provider'] = api_provider
        session['api_settings']['integration_enabled'] = integration_enabled
        session.modified = True

        print(f"API key saved: {'*' * len(api_key) if api_key else 'None'}")

        # Try to sync with API if we have a key
        if api_key:
            success, message = sync_with_api()
            if success:
                flash('API key saved and verified successfully!', 'success')
            else:
                flash(f'API key saved but verification failed: {message}', 'warning')
        else:
            flash('API settings cleared.', 'info')

        return redirect(url_for('api_settings'))

    return render_template('api_settings.html', api_settings=session['api_settings'])

@app.route('/brightdata_settings')
def brightdata_settings_redirect():
    """Redirect old brightdata settings URL to the new web scraper page"""
    return redirect(url_for('web_scraper_bp.index'))

@app.route('/reset')
def reset():
    """Reset the session and start fresh"""
    # Clear the session
    session.clear()

    # Initialize a new session
    initialize_session()

    flash('Session reset successfully. All previous analysis has been cleared.', 'success')
    return redirect(url_for('home'))

@app.route('/api/sync', methods=['POST'])
def api_sync():
    initialize_session()

    # Check if API integration is enabled and we have an API key
    if not session['api_settings']['integration_enabled'] or not session['api_settings']['api_key']:
        return jsonify({'success': False, 'error': 'API integration is not enabled or API key is missing'})

    # Check if any input method has been used
    if not any(method['used'] for method in session['input_methods'].values()):
        return jsonify({'success': False, 'error': 'You need to complete at least one input method first'})

    # Sync with API
    success, message = sync_with_api()

    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': message})

def sync_with_api():
    """Verify API connection for intelligent text analysis"""
    try:
        api_key = session['api_settings']['api_key']

        if not api_key:
            return False, "API key is missing. Please enter your API key."

        # Import the API client
        from app.utils.api_client import APIClient

        # Create a test message to verify API connectivity
        test_message = "This is a test message to verify API connectivity."

        # Create API client and test connection (always use OpenAI)
        api_client = APIClient('openai', api_key)

        # Test the API with a small sample text
        success, result = api_client.analyze_text(test_message)

        # Update last sync time
        if success:
            session['api_settings']['last_sync_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            session.modified = True
            return True, "API connection verified successfully."
        else:
            error_message = result.get('error', 'Unknown error')
            return False, f"API connection test failed: {error_message}"

    except Exception as e:
        return False, f"API connection error: {str(e)}"

if __name__ == '__main__':
    # Use environment variable for port if available (for Render compatibility)
    port = int(os.environ.get('PORT', 5001))  # Changed default port to 5001
    app.run(host='0.0.0.0', port=port, debug=True)
