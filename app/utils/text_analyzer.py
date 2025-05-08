import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
import re
from collections import Counter

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

def update_brand_parameters(brand_parameters, analysis_results):
    """Update brand parameters based on analysis results"""
    # Update personality traits
    personality = sorted(analysis_results["personality_traits"].items(), key=lambda x: x[1], reverse=True)
    if personality:
        brand_parameters["personality"]["primary_traits"] = [trait for trait, _ in personality[:3]]
        brand_parameters["personality"]["secondary_traits"] = [trait for trait, _ in personality[3:6]]
    
    # Update emotional tone
    emotions = sorted(analysis_results["emotional_tone"].items(), key=lambda x: x[1], reverse=True)
    if emotions:
        brand_parameters["emotional_tone"]["primary_emotions"] = [emotion for emotion, _ in emotions[:2]]
        brand_parameters["emotional_tone"]["secondary_emotions"] = [emotion for emotion, _ in emotions[2:4]]
    
    # Update formality
    brand_parameters["formality"]["level"] = analysis_results["formality_score"]
    
    # Update vocabulary
    brand_parameters["vocabulary"]["preferred_terms"] = [word for word, _ in analysis_results["common_vocabulary"][:20]]
    
    # Update communication style
    brand_parameters["communication_style"]["sentence_structure"]["length_preference"] = min(10, max(1, int(analysis_results["avg_sentence_length"] / 3)))
    brand_parameters["communication_style"]["sentence_structure"]["complexity_preference"] = analysis_results["sentence_complexity"]
    
    return brand_parameters
