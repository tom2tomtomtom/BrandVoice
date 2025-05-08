# Brand Voice Codifier

## Overview
The Brand Voice Codifier is a tool designed to analyze, capture, and codify a client's brand tone of voice for integration with copywriting systems. This application demonstrates the core functionality through three input methods, parameter extraction, visualization, and export options.

## Features

### 1. Multiple Input Methods
- **Document Upload & Analysis**: Upload brand documents (PDF, TXT) to extract voice parameters
- **Conversational Brand Interview**: Answer questions to define your brand voice
- **Web Presence Scraper**: Analyze website content for voice patterns

### 2. Parameter Extraction & Classification
- Brand Personality Profile
- Formality Spectrum
- Emotional Tone Framework
- Vocabulary Profile
- Communication Style Parameters
- Audience Adaptation Guidelines

### 3. Visualization & Results
- Interactive dashboard for reviewing brand voice parameters
- Visual representations of brand voice characteristics
- Real-time example generation of meta ad headlines and taglines

### 4. Export Options
- Well-formatted HTML report with print functionality
- JSON export for integration with copywriting systems
- API integration with external AI systems

## Installation

1. Clone this repository
   ```
   git clone https://github.com/tom2tomtomtom/BrandVoice.git
   cd BrandVoice
   ```

2. Create and activate a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Download NLTK resources:
   ```python
   python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords')"
   ```

## Usage

1. Run the Flask application:
   ```
   python main.py
   ```

2. Open your web browser and navigate to http://localhost:5000

3. Choose one of the input methods:
   - Upload a document (PDF or TXT)
   - Complete the brand interview
   - Analyze a website

4. Review the results in the dashboard

5. Export your brand voice parameters as a formatted report or JSON

## Project Structure

```
Brand Voice Codifier/
├── main.py                 # Main Flask application
├── requirements.txt        # Dependencies
├── README.md               # This file
├── static/                 # Static assets
│   ├── css/                # CSS stylesheets
│   └── js/                 # JavaScript files
├── templates/              # HTML templates
│   ├── base.html           # Base template
│   ├── index.html          # Home page
│   ├── document_upload.html # Document upload page
│   ├── brand_interview.html # Brand interview page
│   ├── web_scraper.html    # Web scraper page
│   ├── results.html        # Results dashboard
│   ├── report.html         # Formatted report
│   └── api_settings.html   # API integration settings
├── uploads/                # Temporary storage for uploads
└── venv/                   # Virtual environment (not tracked in git)
```

## Key Features

### Document Analysis
- Upload PDF or TXT files
- Extract text content
- Analyze for brand voice parameters
- Identify personality traits, emotional tone, and formality

### Brand Interview
- Multi-step interview process
- Customizable options with "Other" fields
- Comprehensive coverage of brand voice aspects
- Real-time form validation

### Web Scraper
- Analyze any public website
- Extract text content from paragraphs, headings, and lists
- Process content for brand voice parameters
- Identify patterns in online presence

### Results Dashboard
- Visual representation of brand parameters
- Interactive charts
- Example ad copy generation
- Export options

### Formatted Reports
- Professional HTML report
- Print-friendly design
- Comprehensive brand voice documentation
- Visual elements for easy understanding

### API Integration
- Connect with OpenAI, Anthropic, Cohere, or custom systems
- Synchronize brand voice parameters
- Secure API key management
- Status tracking

## Future Enhancements

- PDF export functionality
- More sophisticated text analysis algorithms
- Additional input methods (e.g., competitor analysis)
- Enhanced visualization options
- User accounts and saved brand profiles
- Collaborative editing features

## License

This project is licensed under the MIT License - see the LICENSE file for details.
