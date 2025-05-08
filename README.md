# Brand Voice Codifier: Proof of Concept

## Overview
The Brand Voice Codifier is a tool designed to analyze, capture, and codify a client's brand tone of voice for integration with a copywriting agent in an ad creation platform. This POC demonstrates the core functionality through three input methods, parameter extraction, and visualization.

## Features

### 1. Multiple Input Methods
- **Document Upload & Analysis**: Upload brand documents to extract voice parameters
- **Conversational Brand Interview**: Answer questions to define your brand voice
- **Web Presence Scraper**: Analyze website content for voice patterns

### 2. Parameter Extraction & Classification
- Brand Personality Profile
- Formality Spectrum
- Emotional Tone Framework
- Vocabulary Profile
- Communication Style Parameters
- Audience Adaptation Guidelines

### 3. Visualization & Parameter Adjustment
- Interactive dashboard for reviewing and adjusting parameters
- Visual representations of brand voice characteristics
- Real-time example generation based on parameters

### 4. Parameter Export
- Export parameters in JSON format for integration with copywriting systems

## Installation

1. Clone this repository
2. Create and activate a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install the required packages:
   ```
   pip install streamlit pandas nltk scikit-learn matplotlib plotly beautifulsoup4 requests PyPDF2
   ```

## Usage

1. Run the Streamlit application:
   ```
   streamlit run app.py
   ```
2. Open your web browser and navigate to the URL displayed in the terminal (typically http://localhost:8501)
3. Use the sidebar to navigate between different sections of the application
4. Complete at least one input method to generate brand voice parameters
5. Review and adjust parameters in the dashboard
6. Export the parameters for integration with copywriting systems

## Project Structure

```
Brand Voice Codifier/
├── app.py                  # Main application file
├── README.md               # This file
├── venv/                   # Virtual environment (not tracked in git)
└── src/                    # Source code
    ├── components/         # UI components
    ├── data/               # Data storage
    ├── pages/              # Application pages
    │   ├── home.py         # Home page
    │   ├── document_upload.py  # Document upload page
    │   ├── brand_interview.py  # Brand interview page
    │   ├── web_scraper.py      # Web scraper page
    │   └── parameter_dashboard.py  # Parameter dashboard page
    └── utils/              # Utility functions
```

## Future Enhancements

- Integration with AI copywriting systems
- More sophisticated text analysis algorithms
- Additional input methods (e.g., competitor analysis)
- Enhanced visualization options
- User accounts and saved brand profiles
- Collaborative editing features

## License

This project is a proof of concept and is not licensed for commercial use.
