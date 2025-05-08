import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from collections import Counter
import re
import time

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

def scrape_website(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract text from paragraphs, headings, and list items
        paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
        text = ' '.join([p.get_text().strip() for p in paragraphs])
        
        # Clean the text
        text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
        text = re.sub(r'[^\w\s.,!?;:]', '', text)  # Remove special characters except punctuation
        
        return text
    except Exception as e:
        st.error(f"Error scraping website: {str(e)}")
        return None

def get_internal_links(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract base URL
        base_url = url.split('//')[-1].split('/')[0]
        if not base_url.startswith('http'):
            base_url = 'https://' + base_url
        
        # Find all links
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            
            # Handle relative URLs
            if href.startswith('/'):
                href = base_url + href
            
            # Only include internal links
            if base_url in href and href not in links:
                links.append(href)
        
        return links[:5]  # Limit to 5 internal links for the POC
    except Exception as e:
        st.error(f"Error getting internal links: {str(e)}")
        return []

def analyze_text(text):
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
    # Update personality traits
    personality = sorted(analysis_results["personality_traits"].items(), key=lambda x: x[1], reverse=True)
    if personality:
        st.session_state.brand_parameters["personality"]["primary_traits"] = [trait for trait, _ in personality[:3]]
        st.session_state.brand_parameters["personality"]["secondary_traits"] = [trait for trait, _ in personality[3:6]]
    
    # Update emotional tone
    emotions = sorted(analysis_results["emotional_tone"].items(), key=lambda x: x[1], reverse=True)
    if emotions:
        st.session_state.brand_parameters["emotional_tone"]["primary_emotions"] = [emotion for emotion, _ in emotions[:2]]
        st.session_state.brand_parameters["emotional_tone"]["secondary_emotions"] = [emotion for emotion, _ in emotions[2:4]]
    
    # Update formality
    st.session_state.brand_parameters["formality"]["level"] = analysis_results["formality_score"]
    
    # Update vocabulary
    st.session_state.brand_parameters["vocabulary"]["preferred_terms"] = [word for word, _ in analysis_results["common_vocabulary"][:20]]
    
    # Update communication style
    st.session_state.brand_parameters["communication_style"]["sentence_structure"]["length_preference"] = min(10, max(1, int(analysis_results["avg_sentence_length"] / 3)))
    st.session_state.brand_parameters["communication_style"]["sentence_structure"]["complexity_preference"] = analysis_results["sentence_complexity"]
    
    # Mark web scraper as used
    st.session_state.input_methods["web_scraper"]["used"] = True
    st.session_state.input_methods["web_scraper"]["data"] = analysis_results

def show_web_scraper_page():
    st.title("Web Presence Scraper")
    
    st.markdown("""
    ## Analyze Your Web Presence
    
    Enter your website URL to analyze your existing public-facing content for voice consistency and patterns.
    
    Our system will:
    - Scrape text content from your website
    - Analyze the content for brand voice patterns
    - Extract key parameters from your real-world usage
    - Identify strong examples of your current brand voice
    
    For the best results, enter your main website URL. The system will automatically analyze multiple pages.
    """)
    
    website_url = st.text_input("Enter your website URL:", placeholder="https://example.com")
    
    if website_url:
        if not website_url.startswith(('http://', 'https://')):
            website_url = 'https://' + website_url
        
        if st.button("Analyze Website"):
            with st.spinner("Analyzing website content..."):
                # Scrape the main URL
                main_text = scrape_website(website_url)
                
                if main_text:
                    # Get internal links
                    internal_links = get_internal_links(website_url)
                    
                    # Scrape internal pages
                    all_text = main_text
                    
                    with st.expander("Scraping Progress"):
                        progress_bar = st.progress(0)
                        for i, link in enumerate(internal_links):
                            st.write(f"Scraping: {link}")
                            page_text = scrape_website(link)
                            if page_text:
                                all_text += " " + page_text
                            progress_bar.progress((i + 1) / len(internal_links))
                            time.sleep(0.5)  # Small delay to avoid overwhelming the server
                    
                    # Analyze the combined text
                    analysis_results = analyze_text(all_text)
                    
                    # Update brand parameters based on analysis
                    update_brand_parameters(analysis_results)
                    
                    # Display analysis results
                    st.success("Analysis complete! Here's what we found:")
                    
                    # Display personality traits
                    st.subheader("Brand Personality")
                    personality_df = pd.DataFrame({
                        'Trait': list(analysis_results["personality_traits"].keys()),
                        'Score': list(analysis_results["personality_traits"].values())
                    })
                    personality_df = personality_df.sort_values('Score', ascending=False).reset_index(drop=True)
                    st.bar_chart(personality_df.set_index('Trait')['Score'])
                    
                    # Display emotional tone
                    st.subheader("Emotional Tone")
                    emotion_df = pd.DataFrame({
                        'Emotion': list(analysis_results["emotional_tone"].keys()),
                        'Score': list(analysis_results["emotional_tone"].values())
                    })
                    emotion_df = emotion_df.sort_values('Score', ascending=False).reset_index(drop=True)
                    st.bar_chart(emotion_df.set_index('Emotion')['Score'])
                    
                    # Display formality score
                    st.subheader("Formality Level")
                    st.progress(analysis_results["formality_score"] / 10)
                    st.write(f"Formality Score: {analysis_results['formality_score']}/10")
                    
                    # Display common vocabulary
                    st.subheader("Common Vocabulary")
                    vocab_df = pd.DataFrame(analysis_results["common_vocabulary"], columns=['Word', 'Frequency'])
                    st.dataframe(vocab_df.head(20))
                    
                    # Display sentence structure
                    st.subheader("Sentence Structure")
                    st.write(f"Average Sentence Length: {analysis_results['avg_sentence_length']:.2f} words")
                    st.write(f"Sentence Complexity: {analysis_results['sentence_complexity']}/10")
                    
                    # Provide next steps
                    st.markdown("---")
                    st.success("Your brand voice parameters have been updated based on the web analysis.")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("View Brand Voice Dashboard"):
                            st.session_state.current_page = "parameter_dashboard"
                    with col2:
                        if st.button("Try Another Input Method"):
                            st.session_state.current_page = "home"
                else:
                    st.error("Could not extract text from the website. Please check the URL and try again.")
    else:
        st.info("Please enter a website URL to begin analysis.")
