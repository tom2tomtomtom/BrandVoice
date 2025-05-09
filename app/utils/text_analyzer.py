import nltk
import logging
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from flask import session

from app.utils.api_client import APIClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download necessary NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

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

def analyze_text(text):
    """
    Analyze text to extract brand voice parameters using AI API.
    Will only perform analysis if API integration is enabled and a valid API key is provided.
    """
    # Check if API key is set
    if 'api_settings' not in session:
        logger.error("API settings not found in session")
        raise Exception("API settings not found. Please configure API settings.")

    # Get API key
    api_key = session['api_settings'].get('api_key', '')

    # Always set these values
    session['api_settings']['api_provider'] = 'openai'
    session['api_settings']['integration_enabled'] = True
    session.modified = True

    if not api_key:
        logger.error("API key is missing")
        raise Exception("API key is missing. Please enter your OpenAI API key in the API settings page.")

    logger.info("Using OpenAI API for text analysis")

    # Create API client and analyze text (always use OpenAI)
    api_client = APIClient('openai', api_key)
    success, results = api_client.analyze_text(text)

    if success:
        logger.info("API analysis successful")

        # Process and standardize the API response
        try:
            # Extract and standardize the results
            standardized_results = standardize_api_results(results)
            return standardized_results
        except Exception as e:
            logger.error(f"Error standardizing API results: {str(e)}")
            raise Exception(f"Error processing API results: {str(e)}")
    else:
        error_msg = results.get('error', 'Unknown error')
        logger.error(f"API analysis failed: {error_msg}")
        raise Exception(f"API analysis failed: {error_msg}")

def standardize_api_results(api_results):
    """
    Standardize API results to match the expected format for brand parameters.
    Different APIs may return different formats, so we need to standardize them.
    """
    # Store the original API results for later use
    original_api_results = api_results.copy()

    standardized = {
        "personality_traits": {},
        "emotional_tone": {},
        "formality_score": 5,  # Default
        "common_vocabulary": [],
        "avg_sentence_length": 0,
        "sentence_complexity": 5,  # Default
        "original_api_response": original_api_results,  # Store the original response
        "rich_descriptions": []  # Store rich descriptions of the brand voice
    }

    # Extract rich descriptions if available
    if "communication_style" in api_results and "rich_descriptions" in api_results["communication_style"]:
        standardized["rich_descriptions"] = api_results["communication_style"]["rich_descriptions"]

    # Process personality traits
    if "personality_traits" in api_results:
        if isinstance(api_results["personality_traits"], dict):
            # Convert all values to numeric scores
            for trait, value in api_results["personality_traits"].items():
                if isinstance(value, bool):
                    standardized["personality_traits"][trait] = 10 if value else 0
                elif isinstance(value, (int, float)):
                    standardized["personality_traits"][trait] = int(value)  # Convert to integer
                elif isinstance(value, str) and value.isdigit():
                    standardized["personality_traits"][trait] = int(value)  # Convert string digits to integer
                else:
                    standardized["personality_traits"][trait] = 8  # Default to high score for any non-numeric value
                    print(f"Warning: Non-numeric value '{value}' for trait '{trait}' converted to 8")
        elif isinstance(api_results["personality_traits"], list):
            # Convert list to dict with scores
            for i, trait in enumerate(api_results["personality_traits"]):
                if isinstance(trait, str):
                    # Assign decreasing scores based on position
                    standardized["personality_traits"][trait] = 10 - i if i < 10 else 1
                elif isinstance(trait, dict) and "trait" in trait and "score" in trait:
                    standardized["personality_traits"][trait["trait"]] = trait["score"]

    # Process emotional tone
    if "emotional_tone" in api_results:
        if isinstance(api_results["emotional_tone"], dict):
            # Convert all values to numeric scores
            for emotion, value in api_results["emotional_tone"].items():
                if isinstance(value, bool):
                    standardized["emotional_tone"][emotion] = 10 if value else 0
                elif isinstance(value, (int, float)):
                    standardized["emotional_tone"][emotion] = int(value)  # Convert to integer
                elif isinstance(value, str) and value.isdigit():
                    standardized["emotional_tone"][emotion] = int(value)  # Convert string digits to integer
                else:
                    standardized["emotional_tone"][emotion] = 8  # Default to high score for any non-numeric value
                    print(f"Warning: Non-numeric value '{value}' for emotion '{emotion}' converted to 8")
        elif isinstance(api_results["emotional_tone"], list):
            # Convert list to dict with scores
            for i, emotion in enumerate(api_results["emotional_tone"]):
                if isinstance(emotion, str):
                    # Assign decreasing scores based on position
                    standardized["emotional_tone"][emotion] = 10 - i if i < 10 else 1
                elif isinstance(emotion, dict) and "emotion" in emotion and "score" in emotion:
                    standardized["emotional_tone"][emotion["emotion"]] = emotion["score"]

    # Process formality score
    if "formality" in api_results:
        if isinstance(api_results["formality"], dict) and "level" in api_results["formality"]:
            standardized["formality_score"] = api_results["formality"]["level"]
        elif isinstance(api_results["formality"], (int, float)):
            standardized["formality_score"] = api_results["formality"]
    elif "formality_score" in api_results:
        standardized["formality_score"] = api_results["formality_score"]

    # Process vocabulary
    if "vocabulary" in api_results:
        # Process preferred terms
        if "preferred_terms" in api_results["vocabulary"]:
            terms = api_results["vocabulary"]["preferred_terms"]
            if isinstance(terms, list):
                # Convert to format [(term, frequency)] for compatibility
                # Assign decreasing frequency values to emphasize the first terms
                standardized["common_vocabulary"] = []
                for i, term in enumerate(terms):
                    # Assign frequency value from 10 down to 1, with a minimum of 1
                    freq = max(1, 10 - i) if i < 10 else 1
                    standardized["common_vocabulary"].append((term, freq))

        # Process avoided terms if available
        if "avoided_terms" in api_results["vocabulary"]:
            avoided_terms = api_results["vocabulary"]["avoided_terms"]
            if isinstance(avoided_terms, list):
                standardized["avoided_terms"] = avoided_terms

    elif "common_vocabulary" in api_results:
        standardized["common_vocabulary"] = api_results["common_vocabulary"]

    # Print vocabulary for debugging
    print("\nExtracted vocabulary:")
    print(f"Preferred terms: {[term for term, _ in standardized['common_vocabulary'][:10] if standardized['common_vocabulary']]}")
    if "avoided_terms" in standardized:
        print(f"Avoided terms: {standardized['avoided_terms'][:10]}")

    # Process sentence structure
    if "communication_style" in api_results and "sentence_structure" in api_results["communication_style"]:
        sentence_structure = api_results["communication_style"]["sentence_structure"]
        if "length_preference" in sentence_structure:
            standardized["avg_sentence_length"] = sentence_structure["length_preference"] * 3  # Scale to match basic analysis
        if "complexity_preference" in sentence_structure:
            standardized["sentence_complexity"] = sentence_structure["complexity_preference"]
    elif "avg_sentence_length" in api_results:
        standardized["avg_sentence_length"] = api_results["avg_sentence_length"]
    if "sentence_complexity" in api_results:
        standardized["sentence_complexity"] = api_results["sentence_complexity"]

    # Print the standardized results for debugging
    print("\nStandardized API results:")
    import json
    print(json.dumps(standardized, indent=2))

    return standardized

def basic_analyze_text(text):
    """Basic text analysis using NLTK (fallback method)"""
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

def update_brand_parameters(brand_parameters, analysis_results):
    """Update brand parameters based on analysis results"""
    # Print the raw analysis results for debugging
    print("\nRaw analysis results in update_brand_parameters:")
    import json
    print(json.dumps(analysis_results, indent=2))

    # Check if we have the original API response
    if "original_api_response" in analysis_results:
        # Store the original API response in the brand parameters for later use
        brand_parameters["original_api_response"] = analysis_results["original_api_response"]
        print("Stored original API response in brand parameters")

    # Check if personality_traits contains numerical values
    print("\nChecking personality_traits values:")
    for trait, value in analysis_results["personality_traits"].items():
        print(f"{trait}: {value} (type: {type(value).__name__})")

    # Update personality traits
    personality = sorted(analysis_results["personality_traits"].items(), key=lambda x: x[1], reverse=True)
    if personality:
        print("\nSorted personality traits:")
        for trait, score in personality:
            print(f"{trait}: {score}")
        brand_parameters["personality"]["primary_traits"] = [trait for trait, _ in personality[:3]]
        brand_parameters["personality"]["secondary_traits"] = [trait for trait, _ in personality[3:6]]

    # Check if emotional_tone contains numerical values
    print("\nChecking emotional_tone values:")
    for emotion, value in analysis_results["emotional_tone"].items():
        print(f"{emotion}: {value} (type: {type(value).__name__})")

    # Update emotional tone
    emotions = sorted(analysis_results["emotional_tone"].items(), key=lambda x: x[1], reverse=True)
    if emotions:
        print("\nSorted emotional tones:")
        for emotion, score in emotions:
            print(f"{emotion}: {score}")
        brand_parameters["emotional_tone"]["primary_emotions"] = [emotion for emotion, _ in emotions[:2]]
        brand_parameters["emotional_tone"]["secondary_emotions"] = [emotion for emotion, _ in emotions[2:4]]

    # Update formality
    brand_parameters["formality"]["level"] = analysis_results["formality_score"]
    print(f"\nFormality score: {analysis_results['formality_score']}")

    # Update vocabulary
    brand_parameters["vocabulary"]["preferred_terms"] = [word for word, _ in analysis_results["common_vocabulary"][:20]]

    # Update avoided terms if available
    if "avoided_terms" in analysis_results:
        brand_parameters["vocabulary"]["avoided_terms"] = analysis_results["avoided_terms"][:20]
        print(f"\nAvoided terms: {brand_parameters['vocabulary']['avoided_terms']}")

    # Update communication style
    length_pref = min(10, max(1, int(analysis_results["avg_sentence_length"] / 3)))
    complexity_pref = analysis_results["sentence_complexity"]
    print(f"\nCommunication style:")
    print(f"Length preference: {length_pref}")
    print(f"Complexity preference: {complexity_pref}")
    brand_parameters["communication_style"]["sentence_structure"]["length_preference"] = length_pref
    brand_parameters["communication_style"]["sentence_structure"]["complexity_preference"] = complexity_pref

    # If we have key phrases from the original API response, store them
    if "original_api_response" in analysis_results and "communication_style" in analysis_results["original_api_response"] and "key_phrases" in analysis_results["original_api_response"]["communication_style"]:
        key_phrases = analysis_results["original_api_response"]["communication_style"]["key_phrases"]
        brand_parameters["communication_style"]["key_phrases"] = key_phrases
        print(f"\nKey phrases: {key_phrases}")

    # Print the updated brand parameters
    print("\nUpdated brand parameters in update_brand_parameters:")
    print(f"Personality primary traits: {brand_parameters['personality']['primary_traits']}")
    print(f"Personality secondary traits: {brand_parameters['personality']['secondary_traits']}")
    print(f"Emotional tone primary: {brand_parameters['emotional_tone']['primary_emotions']}")
    print(f"Emotional tone secondary: {brand_parameters['emotional_tone']['secondary_emotions']}")
    print(f"Formality level: {brand_parameters['formality']['level']}")
    print(f"Communication style - storytelling: {brand_parameters['communication_style']['storytelling_preference']}")
    print(f"Communication style - length: {brand_parameters['communication_style']['sentence_structure']['length_preference']}")
    print(f"Communication style - complexity: {brand_parameters['communication_style']['sentence_structure']['complexity_preference']}")

    return brand_parameters

def generate_brand_voice_summary(brand_parameters, analysis_results=None, input_methods=None):
    """
    Generate a comprehensive brand voice summary with:
    1. Tone description in prose
    2. Example phrases
    3. Words frequently used
    4. Words to avoid

    Each section is supported by specific examples from the brand's material
    or derived from analysis data if no formal brand guide was provided.
    """
    summary = {}

    # Check if we have the raw API response with key phrases
    if analysis_results and "communication_style" in analysis_results and "key_phrases" in analysis_results["communication_style"]:
        # Use the key phrases from the API response
        key_phrases = analysis_results["communication_style"]["key_phrases"]
        if key_phrases and len(key_phrases) > 0:
            # Create a tone description directly using the content from the document
            tone_description = "From your brand voice document:\n\n"

            # Check if we have rich descriptions from the API response
            if "rich_descriptions" in analysis_results and analysis_results["rich_descriptions"]:
                rich_descriptions = analysis_results["rich_descriptions"]

                # Look for "We are..." and "We aren't..." sections
                we_are_section = None
                we_arent_section = None
                how_we_speak_section = None

                for desc in rich_descriptions:
                    if "We are" in desc or "We're" in desc:
                        we_are_section = desc
                    if "We aren't" in desc or "We don't" in desc:
                        we_arent_section = desc
                    if "How we speak" in desc or "Our language" in desc:
                        how_we_speak_section = desc

                # Add the "We are..." section if found
                if we_are_section:
                    tone_description += f"WE ARE:\n{we_are_section}\n\n"

                # Add the "We aren't..." section if found
                if we_arent_section:
                    tone_description += f"WE AREN'T:\n{we_arent_section}\n\n"

                # Add the "How we speak" section if found
                if how_we_speak_section:
                    tone_description += f"HOW WE SPEAK:\n{how_we_speak_section}\n\n"

                # If we didn't find specific sections, use all rich descriptions
                if not (we_are_section or we_arent_section or how_we_speak_section):
                    for desc in rich_descriptions[:3]:
                        tone_description += f"{desc}\n\n"

            # If no rich descriptions, fall back to using traits and emotions
            if "rich_descriptions" not in analysis_results or not analysis_results["rich_descriptions"]:
                # Add personality traits
                primary_traits = brand_parameters["personality"]["primary_traits"]
                if primary_traits:
                    trait_str = ", ".join(primary_traits[:-1])
                    if len(primary_traits) > 1:
                        trait_str += f" and {primary_traits[-1]}"
                    else:
                        trait_str = primary_traits[0]
                    tone_description += f"WE ARE: {trait_str}. "

                # Add emotional tone
                primary_emotions = brand_parameters["emotional_tone"]["primary_emotions"]
                if primary_emotions:
                    emotion_str = ", ".join(primary_emotions[:-1])
                    if len(primary_emotions) > 1:
                        emotion_str += f" and {primary_emotions[-1]}"
                    else:
                        emotion_str = primary_emotions[0]
                    tone_description += f"Our tone is {emotion_str}. "

            # Add key phrases from the document
            if "communication_style" in analysis_results and "key_phrases" in analysis_results["communication_style"]:
                key_phrases = analysis_results["communication_style"]["key_phrases"]
                if key_phrases and len(key_phrases) > 0:
                    tone_description += "\nKEY PHRASES:\n"
                    for phrase in key_phrases[:5]:
                        tone_description += f"• \"{phrase}\"\n"

            # Add vocabulary characteristics
            if "vocabulary" in analysis_results and "preferred_terms" in analysis_results["vocabulary"]:
                preferred_terms = analysis_results["vocabulary"]["preferred_terms"]
                if preferred_terms and len(preferred_terms) > 0:
                    tone_description += "\nWORDS AND PHRASES WE USE:\n"
                    terms_list = ", ".join([f"\"{term}\"" for term in preferred_terms[:10]])
                    tone_description += f"{terms_list}"

            # Add key phrases
            tone_description += ".\n\nSignature brand phrases include: "
            tone_description += f"\"{key_phrases[0]}\""
            if len(key_phrases) > 1:
                tone_description += f" and \"{key_phrases[1]}\""

            # Add avoided terms if available - show more terms
            if "vocabulary" in analysis_results and "avoided_terms" in analysis_results["vocabulary"]:
                avoided_terms = analysis_results["vocabulary"]["avoided_terms"]
                if avoided_terms and len(avoided_terms) > 0:
                    # Show more avoided terms (up to 5)
                    display_terms = avoided_terms[:5]
                    if len(display_terms) == 1:
                        tone_description += f".\n\nThe brand deliberately avoids terms like \"{display_terms[0]}\""
                    elif len(display_terms) == 2:
                        tone_description += f".\n\nThe brand deliberately avoids terms like \"{display_terms[0]}\" and \"{display_terms[1]}\""
                    else:
                        terms_list = ", ".join([f"\"{term}\"" for term in display_terms[:-1]])
                        tone_description += f".\n\nThe brand deliberately avoids terms like {terms_list}, and \"{display_terms[-1]}\""

            # Add rich descriptions if available
            if "rich_descriptions" in analysis_results and analysis_results["rich_descriptions"]:
                rich_descriptions = analysis_results["rich_descriptions"]
                if rich_descriptions:
                    tone_description += "\n\nFrom the brand voice document:"
                    for desc in rich_descriptions[:3]:  # Include up to 3 rich descriptions
                        tone_description += f"\n\n\"{desc}\""

            summary["tone_description"] = tone_description

            # Use the key phrases as example phrases
            summary["example_phrases"] = key_phrases[:3]

            # Use the preferred terms from the API response - show all available terms
            if "vocabulary" in analysis_results and "preferred_terms" in analysis_results["vocabulary"]:
                # Get all preferred terms from the API response
                summary["frequently_used_words"] = analysis_results["vocabulary"]["preferred_terms"]

            # Use the avoided terms from the API response - show all available terms
            if "vocabulary" in analysis_results and "avoided_terms" in analysis_results["vocabulary"]:
                # Get all avoided terms from the API response
                summary["words_to_avoid"] = analysis_results["vocabulary"]["avoided_terms"]

            # Add source information
            if input_methods:
                used_methods = []
                for method, data in input_methods.items():
                    if data.get('used', False):
                        used_methods.append(method)

                if used_methods:
                    source_text = "This summary is based on analysis from: " + ", ".join(used_methods).replace("_", " ").title()
                    summary["source_info"] = source_text
                else:
                    summary["source_info"] = "This summary is based on the brand voice document analysis."
            else:
                summary["source_info"] = "This summary is based on the brand voice document analysis."

            return summary

    # Fall back to the original method if we don't have key phrases
    # 1. Tone description in prose
    primary_traits = brand_parameters["personality"]["primary_traits"]
    primary_emotions = brand_parameters["emotional_tone"]["primary_emotions"]
    formality_level = brand_parameters["formality"]["level"]
    storytelling_pref = brand_parameters["communication_style"]["storytelling_preference"]

    # Create tone description
    tone_description = f"The brand voice is characterized as "

    # Add personality traits
    if primary_traits:
        tone_description += f"{', '.join(primary_traits[:-1])}"
        if len(primary_traits) > 1:
            tone_description += f" and {primary_traits[-1]}"
        else:
            tone_description += f"{primary_traits[0]}"

    # Add emotional tone
    if primary_emotions:
        tone_description += f", conveying a {', '.join(primary_emotions[:-1])}"
        if len(primary_emotions) > 1:
            tone_description += f" and {primary_emotions[-1]} emotional tone"
        else:
            tone_description += f" {primary_emotions[0]} emotional tone"

    # Add formality
    formality_desc = "balanced formality"
    if formality_level >= 8:
        formality_desc = "highly formal tone"
    elif formality_level >= 6:
        formality_desc = "moderately formal tone"
    elif formality_level <= 3:
        formality_desc = "casual, conversational tone"
    elif formality_level <= 5:
        formality_desc = "slightly casual tone"

    tone_description += f". The communication maintains a {formality_desc}"

    # Add storytelling preference
    if storytelling_pref >= 8:
        tone_description += " with a strong emphasis on narrative and storytelling elements."
    elif storytelling_pref >= 6:
        tone_description += " with occasional use of storytelling to illustrate points."
    elif storytelling_pref <= 3:
        tone_description += " focusing on direct, straightforward communication."
    else:
        tone_description += " balancing direct information with illustrative examples when appropriate."

    # Add sentence structure information
    length_pref = brand_parameters["communication_style"]["sentence_structure"]["length_preference"]
    complexity_pref = brand_parameters["communication_style"]["sentence_structure"]["complexity_preference"]

    if length_pref >= 7 and complexity_pref >= 7:
        tone_description += " Sentences tend to be longer and more complex, allowing for nuanced expression."
    elif length_pref <= 4 and complexity_pref <= 4:
        tone_description += " Sentences are typically short and simple, ensuring clarity and impact."
    elif length_pref >= 7 and complexity_pref <= 4:
        tone_description += " While sentences may be longer, they maintain a simple structure for clarity."
    elif length_pref <= 4 and complexity_pref >= 7:
        tone_description += " Sentences are concise but may employ complex structures to convey sophisticated ideas."
    else:
        tone_description += " Sentence structure balances length and complexity to maintain engagement while ensuring clarity."

    summary["tone_description"] = tone_description

    # 2. Example phrases
    # Generate example phrases based on brand parameters
    example_phrases = []

    # Combine traits and emotions to generate appropriate phrases
    trait_emotion_pairs = []
    for trait in primary_traits[:2]:
        for emotion in primary_emotions[:2]:
            trait_emotion_pairs.append((trait, emotion))

    # Phrase templates based on trait-emotion combinations
    phrase_templates = {
        ("innovative", "optimistic"): [
            "Discover the future of [industry] with our groundbreaking solutions.",
            "Reimagine what's possible with our forward-thinking approach."
        ],
        ("innovative", "passionate"): [
            "We're relentlessly pursuing innovation that transforms [industry].",
            "Our passion for innovation drives us to create solutions that matter."
        ],
        ("innovative", "empowering"): [
            "Take control of your [outcome] with our innovative tools.",
            "Our cutting-edge solutions empower you to achieve more."
        ],
        ("trustworthy", "optimistic"): [
            "Build a brighter future with a partner you can trust.",
            "Reliable solutions for a better tomorrow."
        ],
        ("trustworthy", "passionate"): [
            "We're deeply committed to earning your trust every day.",
            "Our passion for excellence is matched only by our dedication to reliability."
        ],
        ("trustworthy", "empowering"): [
            "Make confident decisions with a trusted partner by your side.",
            "We provide the reliable foundation you need to reach new heights."
        ],
        ("sophisticated", "optimistic"): [
            "Elevate your experience with our refined approach to [solution].",
            "A more elegant solution for a brighter future."
        ],
        ("sophisticated", "passionate"): [
            "We bring an uncompromising commitment to sophistication in everything we do.",
            "Our passion for excellence creates a truly refined experience."
        ],
        ("sophisticated", "empowering"): [
            "Command attention with our sophisticated solutions.",
            "Elevate your position with our refined approach to [industry]."
        ],
        ("direct", "optimistic"): [
            "Clear solutions for better outcomes. No complications.",
            "Straightforward paths to a better future."
        ],
        ("direct", "passionate"): [
            "We're passionate about cutting through complexity to deliver real results.",
            "No fluff, just powerful solutions driven by genuine commitment."
        ],
        ("direct", "empowering"): [
            "Take control with clear, straightforward solutions.",
            "We give you the direct path to success. You make it happen."
        ],
        ("friendly", "optimistic"): [
            "Let's create something amazing together!",
            "We're here to help you succeed with a smile."
        ],
        ("friendly", "passionate"): [
            "We love what we do, and it shows in how we work with you.",
            "Our enthusiasm for your success makes us the friendly partner you need."
        ],
        ("friendly", "empowering"): [
            "We're in your corner, providing the support you need to succeed.",
            "Consider us your friendly guide to achieving your goals."
        ],
        ("bold", "optimistic"): [
            "Dare to reimagine what's possible.",
            "Break boundaries and create a better tomorrow."
        ],
        ("bold", "passionate"): [
            "We're not afraid to challenge conventions to deliver extraordinary results.",
            "Our passion drives us to take bold steps where others won't venture."
        ],
        ("bold", "empowering"): [
            "Take bold action with confidence, knowing we've got your back.",
            "Empower yourself to make the bold moves that drive success."
        ],
        ("witty", "optimistic"): [
            "Smart solutions for a brighter future (and fewer headaches).",
            "We're seriously good at what we do, but we don't take ourselves too seriously."
        ],
        ("witty", "passionate"): [
            "We're ridiculously passionate about solving your problems. Some might call it obsessive. We call it Tuesday.",
            "We put the 'fun' in 'functional solutions'. (We also put the 'al solutions', but that's less catchy.)"
        ],
        ("witty", "empowering"): [
            "Give yourself the power to succeed. And maybe a cape. Capes are cool.",
            "You bring the challenges. We'll bring the solutions. Someone else can bring the coffee."
        ],
        ("playful", "optimistic"): [
            "Let's make success fun again!",
            "Who says achieving your goals can't be a blast?"
        ],
        ("playful", "passionate"): [
            "We're serious about results, but we believe the journey should be enjoyable!",
            "Our passion comes with a playful spirit that makes working together a joy."
        ],
        ("playful", "empowering"): [
            "Take control of your future – and have a good time doing it!",
            "We put the power in your hands and a smile on your face."
        ]
    }

    # Default phrases if no matches found
    default_phrases = [
        "We deliver exceptional solutions tailored to your unique needs.",
        "Our approach combines innovation with reliability to ensure your success.",
        "Partner with us to transform your challenges into opportunities."
    ]

    # Get phrases based on trait-emotion pairs
    for trait, emotion in trait_emotion_pairs:
        if (trait, emotion) in phrase_templates:
            example_phrases.extend(phrase_templates[(trait, emotion)])

    # If no matches or not enough phrases, add default phrases
    if len(example_phrases) < 2:
        example_phrases.extend(default_phrases)

    # Limit to 3 phrases
    summary["example_phrases"] = example_phrases[:3]

    # 3. Words frequently used
    frequently_used = []

    # Use common vocabulary from analysis if available
    if analysis_results and "common_vocabulary" in analysis_results:
        frequently_used = [word for word, _ in analysis_results["common_vocabulary"][:10]]

    # If not enough words, add words based on brand parameters
    if len(frequently_used) < 5:
        # Words associated with personality traits
        trait_words = {
            "innovative": ["innovative", "cutting-edge", "groundbreaking", "transformative", "pioneering"],
            "trustworthy": ["reliable", "trusted", "proven", "dependable", "consistent"],
            "sophisticated": ["refined", "elegant", "premium", "polished", "distinguished"],
            "friendly": ["approachable", "helpful", "supportive", "welcoming", "personable"],
            "bold": ["bold", "daring", "fearless", "confident", "decisive"],
            "direct": ["clear", "straightforward", "precise", "explicit", "uncomplicated"],
            "witty": ["clever", "smart", "insightful", "intelligent", "perceptive"],
            "playful": ["fun", "engaging", "lively", "dynamic", "energetic"]
        }

        # Words associated with emotional tones
        emotion_words = {
            "optimistic": ["positive", "hopeful", "promising", "bright", "uplifting"],
            "passionate": ["passionate", "enthusiastic", "dedicated", "committed", "driven"],
            "empowering": ["empowering", "enabling", "strengthening", "boosting", "enhancing"],
            "serious": ["focused", "important", "significant", "substantial", "meaningful"],
            "sensual": ["appealing", "attractive", "desirable", "enticing", "alluring"],
            "humorous": ["amusing", "entertaining", "enjoyable", "delightful", "pleasant"]
        }

        # Add words based on primary traits and emotions
        for trait in primary_traits:
            if trait in trait_words and len(frequently_used) < 10:
                frequently_used.extend(trait_words[trait][:2])

        for emotion in primary_emotions:
            if emotion in emotion_words and len(frequently_used) < 10:
                frequently_used.extend(emotion_words[emotion][:2])

    # Remove duplicates and limit to 10 words
    frequently_used = list(dict.fromkeys(frequently_used))[:10]
    summary["frequently_used_words"] = frequently_used

    # 4. Words to avoid
    words_to_avoid = []

    # Use avoided terms from analysis if available
    if analysis_results and "avoided_terms" in analysis_results:
        words_to_avoid = analysis_results["avoided_terms"][:10]

    # If not enough words, add words based on brand parameters
    if len(words_to_avoid) < 5:
        # Words that contradict the brand's personality
        opposite_traits = {
            "innovative": ["traditional", "conventional", "outdated", "old-fashioned", "standard"],
            "trustworthy": ["unreliable", "questionable", "dubious", "unproven", "inconsistent"],
            "sophisticated": ["basic", "crude", "unsophisticated", "simple", "plain"],
            "friendly": ["distant", "cold", "aloof", "detached", "unapproachable"],
            "bold": ["timid", "cautious", "hesitant", "uncertain", "indecisive"],
            "direct": ["vague", "ambiguous", "unclear", "roundabout", "indirect"],
            "witty": ["dull", "boring", "tedious", "humorless", "dry"],
            "playful": ["serious", "stern", "rigid", "formal", "stiff"]
        }

        # Add words that contradict primary traits
        for trait in primary_traits:
            opposite = None
            for key in opposite_traits.keys():
                if trait.lower() == key.lower():
                    opposite = key
                    break

            if opposite and opposite in opposite_traits and len(words_to_avoid) < 10:
                words_to_avoid.extend(opposite_traits[opposite][:2])

    # Words to avoid based on brand parameters
    avoid_traits = brand_parameters["personality"].get("traits_to_avoid", [])

    # Add words to avoid from traits to avoid if we don't have enough
    if len(words_to_avoid) < 5 and avoid_traits:
        for trait in avoid_traits:
            if trait in opposite_traits and len(words_to_avoid) < 10:
                words_to_avoid.extend(opposite_traits[trait][:1])

    # Remove duplicates and limit to 10 words
    words_to_avoid = list(dict.fromkeys(words_to_avoid))[:10]
    summary["words_to_avoid"] = words_to_avoid

    # Words associated with traits to avoid
    avoid_trait_words = {
        "boring": ["dull", "tedious", "monotonous", "uninteresting", "bland"],
        "arrogant": ["superior", "condescending", "patronizing", "pompous", "pretentious"],
        "unprofessional": ["sloppy", "careless", "haphazard", "disorganized", "amateur"],
        "complicated": ["convoluted", "confusing", "complex", "intricate", "perplexing"],
        "timid": ["hesitant", "uncertain", "doubtful", "indecisive", "reluctant"],
        "aggressive": ["hostile", "forceful", "pushy", "domineering", "intimidating"],
        "generic": ["common", "ordinary", "standard", "typical", "conventional"],
        "insincere": ["fake", "artificial", "disingenuous", "phony", "pretend"]
    }

    # Add words to avoid based on traits to avoid
    for trait in avoid_traits:
        if trait in avoid_trait_words:
            words_to_avoid.extend(avoid_trait_words[trait][:3])

    # If not enough words to avoid, add words that contrast with primary traits
    if len(words_to_avoid) < 5:
        contrast_traits = {
            "innovative": ["outdated", "conventional", "traditional", "old-fashioned", "stagnant"],
            "trustworthy": ["unreliable", "questionable", "dubious", "untrustworthy", "suspicious"],
            "sophisticated": ["crude", "unsophisticated", "basic", "simplistic", "rudimentary"],
            "friendly": ["unfriendly", "cold", "distant", "aloof", "detached"],
            "bold": ["timid", "cautious", "hesitant", "uncertain", "indecisive"],
            "direct": ["vague", "ambiguous", "indirect", "unclear", "confusing"],
            "witty": ["dull", "boring", "unimaginative", "literal", "humorless"],
            "playful": ["serious", "stern", "rigid", "formal", "stiff"]
        }

        for trait in primary_traits:
            if trait in contrast_traits and len(words_to_avoid) < 10:
                words_to_avoid.extend(contrast_traits[trait][:2])

    # Remove duplicates and limit to 10 words
    words_to_avoid = list(dict.fromkeys(words_to_avoid))[:10]
    summary["words_to_avoid"] = words_to_avoid

    # Add source information
    if input_methods:
        used_methods = []
        for method, data in input_methods.items():
            if data.get('used', False):
                used_methods.append(method)

        if used_methods:
            source_text = "This summary is based on analysis from: " + ", ".join(used_methods).replace("_", " ").title()
            summary["source_info"] = source_text
        else:
            summary["source_info"] = "This summary is based on default brand voice parameters."
    else:
        summary["source_info"] = "This summary is based on the provided brand parameters."

    # Generate tone of voice prompt and campaign taglines using API
    try:
        # Check if API key is set
        if 'api_settings' in session:
            api_key = session['api_settings'].get('api_key', '')

            if api_key:
                # Create API client
                api_client = APIClient('openai', api_key)

                # Generate tone of voice assets
                success, assets = api_client.generate_tone_of_voice_assets(summary)

                if success:
                    # Add tone of voice prompt and campaign taglines to summary
                    summary["tone_of_voice_prompt"] = assets.get("tone_of_voice_prompt", "")
                    summary["campaign_taglines"] = assets.get("campaign_taglines", [])
                    logger.info("Successfully generated tone of voice prompt and campaign taglines")
                else:
                    # If API call fails, create a basic tone of voice prompt
                    error_msg = assets.get('error', 'Unknown error')
                    logger.error(f"Failed to generate tone of voice assets: {error_msg}")
                    summary["tone_of_voice_prompt"] = f"Write in a {', '.join(primary_traits)} voice that conveys a {', '.join(primary_emotions)} tone. Use {formality_desc} and {frequently_used[:5] if frequently_used else 'appropriate industry terminology'}. Avoid {words_to_avoid[:5] if words_to_avoid else 'generic or clichéd language'}."
                    summary["campaign_taglines"] = example_phrases[:2]
    except Exception as e:
        logger.error(f"Error generating tone of voice assets: {str(e)}")
        # Create a basic tone of voice prompt as fallback
        summary["tone_of_voice_prompt"] = f"Write in a {', '.join(primary_traits)} voice that conveys a {', '.join(primary_emotions)} tone. Use {formality_desc} and {frequently_used[:5] if frequently_used else 'appropriate industry terminology'}. Avoid {words_to_avoid[:5] if words_to_avoid else 'generic or clichéd language'}."
        summary["campaign_taglines"] = example_phrases[:2]

    return summary
