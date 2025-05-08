from flask import Blueprint, render_template, request, redirect, url_for, flash
import requests
from bs4 import BeautifulSoup
import re
from app.utils.session_manager import get_brand_parameters, update_brand_parameters, update_input_method
from app.utils.text_analyzer import analyze_text, update_brand_parameters as update_params_from_analysis

web_scraper_bp = Blueprint('web_scraper', __name__)

def scrape_website(url):
    """Scrape text content from a website"""
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
        flash(f"Error scraping website: {str(e)}", 'danger')
        return None

def get_internal_links(url):
    """Get internal links from a website"""
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
        flash(f"Error getting internal links: {str(e)}", 'danger')
        return []

@web_scraper_bp.route('/web-scraper', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        website_url = request.form.get('website_url', '').strip()
        
        if not website_url:
            flash('Please enter a website URL', 'danger')
            return redirect(url_for('web_scraper.index'))
        
        # Add http:// if not present
        if not website_url.startswith(('http://', 'https://')):
            website_url = 'https://' + website_url
        
        # Scrape the main URL
        main_text = scrape_website(website_url)
        
        if main_text:
            # Get internal links
            internal_links = get_internal_links(website_url)
            
            # Scrape internal pages
            all_text = main_text
            
            for link in internal_links:
                page_text = scrape_website(link)
                if page_text:
                    all_text += " " + page_text
            
            # Analyze the combined text
            analysis_results = analyze_text(all_text)
            
            # Update brand parameters
            brand_parameters = get_brand_parameters()
            updated_parameters = update_params_from_analysis(brand_parameters, analysis_results)
            update_brand_parameters(updated_parameters)
            
            # Mark web scraper as used
            update_input_method('web_scraper', True, analysis_results)
            
            flash('Website analyzed successfully!', 'success')
            return redirect(url_for('web_scraper.results'))
        else:
            flash('Could not extract text from the website. Please check the URL and try again.', 'danger')
    
    return render_template('web_scraper/index.html')

@web_scraper_bp.route('/web-scraper/results')
def results():
    # Get input methods status
    input_methods = get_input_methods()
    
    # Check if web scraper has been used
    if not input_methods['web_scraper']['used']:
        flash('Please analyze a website first.', 'warning')
        return redirect(url_for('web_scraper.index'))
    
    # Get analysis results
    analysis_results = input_methods['web_scraper']['data']
    
    return render_template('web_scraper/results.html', 
                          analysis_results=analysis_results)
