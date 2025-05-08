#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Downloading NLTK resources..."
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords')"

echo "Starting application with gunicorn..."
# Check if gunicorn is installed
if command -v gunicorn &> /dev/null; then
    gunicorn main:app --bind 0.0.0.0:$PORT
else
    echo "Error: gunicorn not found. Installing gunicorn..."
    pip install gunicorn
    gunicorn main:app --bind 0.0.0.0:$PORT
fi
