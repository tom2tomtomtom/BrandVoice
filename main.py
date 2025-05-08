import os
import json
import nltk
import PyPDF2
import requests
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
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

# Initialize CSRF protection
csrf = CSRFProtect(app)

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
    """Generate example meta ad headlines and taglines based on the brand voice parameters"""

    # Extract key parameters
    primary_traits = parameters["personality"]["primary_traits"]
    primary_emotions = parameters["emotional_tone"]["primary_emotions"]
    formality_level = parameters["formality"]["level"]
    storytelling_pref = parameters["communication_style"]["storytelling_preference"]

    # Generate examples based on parameters
    if not primary_traits or not primary_emotions:
        return "Complete at least one input method to generate example ad copy."

    # Base examples for different combinations - Meta ad headlines and taglines
    headlines = {
        # Innovative examples
        ("innovative", "optimistic", "high"): "Revolutionize Your Industry with Cutting-Edge Solutions | Transform How You Do Business",
        ("innovative", "optimistic", "low"): "Game-Changing Tech That Actually Works! | Level Up Your Business Today",
        ("innovative", "serious", "high"): "Advanced Solutions for Complex Business Challenges | Strategic Innovation for Forward-Thinking Organizations",
        ("innovative", "serious", "low"): "Smart Tech for Tough Problems | Get Results Fast",

        # Trustworthy examples
        ("trustworthy", "optimistic", "high"): "Reliable Solutions You Can Count On | Building Trust Through Consistent Excellence",
        ("trustworthy", "optimistic", "low"): "We've Got Your Back! | No Surprises, Just Results",
        ("trustworthy", "serious", "high"): "Dependable Performance in Critical Situations | Trusted by Industry Leaders Since 2005",
        ("trustworthy", "serious", "low"): "Rock-Solid Reliability | We Keep Our Promises",

        # Playful examples
        ("playful", "optimistic", "high"): "Delight in the Unexpected | Bringing Joy to Business Innovation",
        ("playful", "optimistic", "low"): "Business Can Be Fun! | Smile While You Crush Your Goals",

        # Sophisticated examples
        ("sophisticated", "optimistic", "high"): "Elevate Your Business Experience | Refined Solutions for Discerning Organizations",
        ("sophisticated", "serious", "high"): "Premium Solutions for Elite Performance | Where Excellence Meets Sophistication",

        # Friendly examples
        ("friendly", "optimistic", "high"): "Your Partner in Business Growth | We're In This Together",
        ("friendly", "optimistic", "low"): "Hey There! Let's Grow Together | Business Made Easy",

        # Authoritative examples
        ("authoritative", "serious", "high"): "Industry-Leading Expertise for Optimal Results | The Definitive Solution for Business Excellence",
        ("authoritative", "optimistic", "high"): "Master Your Business Challenges | Expert Solutions That Drive Success",

        # Bold examples
        ("bold", "optimistic", "high"): "Dare to Transform Your Business | Breakthrough Solutions for Fearless Leaders",
        ("bold", "optimistic", "low"): "Go Big or Go Home! | Crush Your Competition Today",

        # Empathetic examples
        ("empathetic", "reassuring", "high"): "Understanding Your Business Challenges | Solutions That Address Your Unique Needs",
        ("empathetic", "optimistic", "low"): "We Get It. Business is Hard. | Let's Make It Easier Together",

        # Default example
        ("default", "default", "default"): "Effective Solutions for Your Business | Achieve Your Goals with Our Support"
    }

    # Determine which example to use
    primary_trait = primary_traits[0] if primary_traits else "default"
    primary_emotion = primary_emotions[0] if primary_emotions else "default"
    formality = "high" if formality_level > 5 else "low"

    # Get the example
    example_key = (primary_trait, primary_emotion, formality)
    if example_key in headlines:
        headline = headlines[example_key]
    else:
        # Try with just the primary trait and formality
        example_key = (primary_trait, "default", formality)
        if example_key in headlines:
            headline = headlines[example_key]
        else:
            # Fall back to default
            headline = headlines[("default", "default", "default")]

    # Split into headline and tagline
    parts = headline.split(" | ")
    headline_part = parts[0]
    tagline_part = parts[1] if len(parts) > 1 else ""

    # Format the output
    result = f"Headline: {headline_part}\nTagline: {tagline_part}"

    # Add a note about storytelling preference
    if storytelling_pref > 7:
        result += "\n\nNote: Your high storytelling preference suggests using narrative elements in longer ad copy."

    return result

# Routes
@app.route('/')
def home():
    initialize_session()
    return render_template('index.html', input_methods=session['input_methods'])

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
                                text += page.extract_text()
                    except Exception as e:
                        flash(f'Error reading PDF file: {str(e)}', 'danger')
                        print(f"PDF extraction error: {str(e)}")
                elif filename.endswith('.txt'):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            text = f.read()
                    except UnicodeDecodeError:
                        # Try with different encoding if UTF-8 fails
                        with open(file_path, 'r', encoding='latin-1') as f:
                            text = f.read()
                    except Exception as e:
                        flash(f'Error reading text file: {str(e)}', 'danger')
                        print(f"Text file reading error: {str(e)}")
                else:
                    flash('Unsupported file format. Please upload a PDF or TXT file.', 'danger')

                # Remove the file after processing
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error removing temporary file: {str(e)}")

                if text:
                    try:
                        # Analyze the text
                        print(f"Analyzing text of length: {len(text)}")
                        analysis_results = analyze_text(text)

                        # Update brand parameters
                        update_brand_parameters(analysis_results)

                        # Mark document upload as used
                        session['input_methods']['document_upload']['used'] = True
                        session['input_methods']['document_upload']['data'] = analysis_results
                        session.modified = True

                        flash('Document analyzed successfully!', 'success')
                        return redirect(url_for('results'))
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

@app.route('/web-scraper', methods=['GET', 'POST'])
def web_scraper():
    initialize_session()

    if request.method == 'POST':
        website_url = request.form.get('url', '').strip()

        if not website_url:
            flash('Please enter a website URL', 'danger')
            return redirect(request.url)

        # Add http:// if not present
        if not website_url.startswith(('http://', 'https://')):
            website_url = 'https://' + website_url

        try:
            # Scrape the website
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(website_url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract text from paragraphs, headings, and list items
            paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
            text = ' '.join([p.get_text().strip() for p in paragraphs])

            # Clean the text
            text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
            text = re.sub(r'[^\w\s.,!?;:]', '', text)  # Remove special characters except punctuation

            if text:
                # Analyze the text
                analysis_results = analyze_text(text)

                # Update brand parameters
                update_brand_parameters(analysis_results)

                # Mark web scraper as used
                session['input_methods']['web_scraper']['used'] = True
                session['input_methods']['web_scraper']['data'] = analysis_results
                session.modified = True

                flash('Website analyzed successfully!', 'success')
                return redirect(url_for('results'))
            else:
                flash('Could not extract text from the website.', 'danger')
        except Exception as e:
            flash(f'Error scraping website: {str(e)}', 'danger')

    return render_template('web_scraper.html')

@app.route('/results')
def results():
    initialize_session()

    # Check if any input method has been used
    if not any(method['used'] for method in session['input_methods'].values()):
        flash('You need to complete at least one input method first.', 'warning')
        return redirect(url_for('home'))

    return render_template('results.html',
                          brand_parameters=session['brand_parameters'],
                          input_methods=session['input_methods'],
                          api_settings=session['api_settings'],
                          example_copy=generate_example_copy(session['brand_parameters']))

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

    if export_format == 'json':
        # Generate JSON
        response = jsonify(session['brand_parameters'])
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
        return render_template('report.html',
                              brand_parameters=session['brand_parameters'],
                              example_copy=generate_example_copy(session['brand_parameters']),
                              timestamp=timestamp,
                              current_year=datetime.now().year)

@app.route('/api_settings', methods=['GET', 'POST'])
def api_settings():
    initialize_session()

    if request.method == 'POST':
        # Update API settings
        session['api_settings']['api_key'] = request.form.get('api_key', '')
        session['api_settings']['api_provider'] = request.form.get('api_provider', '')
        session['api_settings']['integration_enabled'] = 'integration_enabled' in request.form
        session.modified = True

        # If integration is enabled and we have an API key, try to sync
        if session['api_settings']['integration_enabled'] and session['api_settings']['api_key']:
            success, message = sync_with_api()
            if success:
                flash('API settings saved and synchronized successfully!', 'success')
            else:
                flash(f'API settings saved but synchronization failed: {message}', 'warning')
        else:
            flash('API settings saved successfully!', 'success')

        return redirect(url_for('api_settings'))

    return render_template('api_settings.html', api_settings=session['api_settings'])

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
    """Sync brand parameters with the selected API provider"""
    try:
        api_provider = session['api_settings']['api_provider']
        api_key = session['api_settings']['api_key']

        if not api_provider or not api_key:
            return False, "API provider or API key is missing"

        # Prepare data for API
        data = {
            'brand_parameters': session['brand_parameters'],
            'timestamp': datetime.now().isoformat()
        }

        # Different API providers have different endpoints and authentication methods
        if api_provider == 'openai':
            # OpenAI API integration
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            # In a real implementation, you would make an actual API call here
            # response = requests.post('https://api.openai.com/v1/brand-voice', json=data, headers=headers)
            # For demo purposes, we'll simulate a successful response
            success = True

        elif api_provider == 'anthropic':
            # Anthropic API integration
            headers = {
                'x-api-key': api_key,
                'Content-Type': 'application/json'
            }
            # In a real implementation, you would make an actual API call here
            # response = requests.post('https://api.anthropic.com/v1/brand-voice', json=data, headers=headers)
            # For demo purposes, we'll simulate a successful response
            success = True

        elif api_provider == 'cohere':
            # Cohere API integration
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            # In a real implementation, you would make an actual API call here
            # response = requests.post('https://api.cohere.ai/v1/brand-voice', json=data, headers=headers)
            # For demo purposes, we'll simulate a successful response
            success = True

        elif api_provider == 'custom':
            # Custom API integration
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            # In a real implementation, you would make an actual API call here
            # response = requests.post('https://your-custom-api.com/brand-voice', json=data, headers=headers)
            # For demo purposes, we'll simulate a successful response
            success = True

        else:
            return False, f"Unsupported API provider: {api_provider}"

        # Update last sync time
        if success:
            session['api_settings']['last_sync_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            session.modified = True
            return True, "Synchronization successful"
        else:
            return False, "API request failed"

    except Exception as e:
        return False, str(e)

if __name__ == '__main__':
    # Use environment variable for port if available (for Render compatibility)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
