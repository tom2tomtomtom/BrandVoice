#!/bin/bash
# Download NLTK resources
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords')"

# Start the application with gunicorn
gunicorn main:app
