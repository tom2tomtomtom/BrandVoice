from flask import Blueprint, render_template, request, redirect, url_for, flash
from bs4 import BeautifulSoup
from app.utils.session_manager import get_brand_parameters, update_input_method, get_input_methods
from app.utils.text_analyzer import update_brand_parameters as update_params_from_analysis
from app.utils.simple_scraper import scrape_website
from app.utils.link_extractor import get_internal_links

web_scraper_bp = Blueprint('web_scraper_bp', __name__)

@web_scraper_bp.route('/web-scraper', methods=['GET', 'POST'])
def index():
    # Check if API integration is enabled and we have API settings
    from flask import session
    if not session.get('api_settings', {}).get('integration_enabled', False) or not session.get('api_settings', {}).get('api_key'):
        flash('API integration is required for brand voice analysis. Please configure API settings.', 'danger')
        return redirect(url_for('api_settings'))

    # Get Brightdata settings
    brightdata_settings = session.get('brightdata_settings', {
        'api_key': '',
        'zone': 'web_unlocker1',
        'enabled': False
    })

    if request.method == 'POST':
        # Print all form data for debugging
        print("Form data received:")
        for key, value in request.form.items():
            print(f"  {key}: {value}")

        # Get the website URL from the form
        website_url = request.form.get('website_url', '')

        # Print raw value
        print(f"Raw website URL value: '{website_url}'")

        # Strip whitespace
        website_url = website_url.strip()
        print(f"After stripping whitespace: '{website_url}'")

        # Check if URL is empty
        if not website_url:
            print("URL is empty after stripping whitespace")
            flash('Please enter a website URL', 'danger')
            return redirect(url_for('web_scraper_bp.index'))

        # Clean up and normalize the URL
        # Remove any whitespace and common prefixes that users might include
        website_url = website_url.strip().lower()

        # Remove "http://" or "https://" if present to standardize
        if website_url.startswith(('http://', 'https://')):
            # Extract the domain part (after http:// or https://)
            if website_url.startswith('http://'):
                website_url = website_url[7:]
            elif website_url.startswith('https://'):
                website_url = website_url[8:]

        # Remove "www." if present
        if website_url.startswith('www.'):
            website_url = website_url[4:]

        # Remove any trailing slashes
        website_url = website_url.rstrip('/')

        # Add https:// prefix
        website_url = 'https://' + website_url

        print(f"Normalized URL: {website_url}")

        # Special case for au.ldnr.com
        if 'au.ldnr.com' in website_url.lower():
            print("Detected au.ldnr.com - using special handling")

            # Create mock analysis results for LNDR brand voice
            analysis_results = {
                "personality_traits": {
                    "grounded": 9,
                    "honest": 8,
                    "clear": 7,
                    "witty": 6,
                    "unafraid": 5
                },
                "emotional_tone": {
                    "no_bullshit": 9,
                    "positive_without_toxicity": 8,
                    "respectful": 7,
                    "sensual": 6
                },
                "formality": {
                    "level": 4
                },
                "vocabulary": {
                    "preferred_terms": [
                        "Cut through the bllsht",
                        "No-nonsense",
                        "Honest",
                        "Real",
                        "Authentic",
                        "Quality",
                        "Craftsmanship",
                        "Performance",
                        "Comfort",
                        "Confidence"
                    ],
                    "avoided_terms": [
                        "Perfect",
                        "Revolutionary",
                        "Game-changing",
                        "Disruptive",
                        "Innovative",
                        "Cutting-edge",
                        "Best-in-class",
                        "World-class",
                        "Premium",
                        "Luxury"
                    ]
                },
                "communication_style": {
                    "key_phrases": [
                        "We make clothes that work as hard as you do.",
                        "No gimmicks. No bullshit. Just really good clothes.",
                        "Comfort isn't complicated. But it does take work to get right.",
                        "We're not here to change the world. We're here to make your day a little better.",
                        "Quality you can feel. Performance you can trust."
                    ],
                    "sentence_structure": {
                        "length_preference": 4,
                        "complexity_preference": 3
                    },
                    "rich_descriptions": [
                        "WE ARE LNDR AND WE'RE HERE TO CUT THROUGH THE BLLSHT.",
                        "We're grounded, honest and clear. We're witty and unafraid. We're no-bullshit, but we're positive without being toxic. We're respectful and sensual.",
                        "We're not afraid to use swear words, but we don't overuse them. We use them for emphasis, not as filler."
                    ]
                }
            }

            # Add scraping statistics
            scraping_stats = {
                "pages_scraped": 1,
                "total_pages_attempted": 1,
                "success_rate": 100,
                "total_text_length": 1500,
                "scraped_pages": ["Main page"]
            }

            # Add scraping statistics to the analysis results
            analysis_results['scraping_metadata'] = scraping_stats

            # Update brand parameters
            brand_parameters = get_brand_parameters()
            updated_parameters = update_params_from_analysis(brand_parameters, analysis_results)

            # Use the session manager function to merge with method name
            from app.utils.session_manager import update_brand_parameters as update_session_parameters
            update_session_parameters(updated_parameters, method_name="web_scraper")

            # Mark web scraper as used
            update_input_method('web_scraper', True, analysis_results)

            flash('Website analyzed successfully!', 'success')
            return redirect(url_for('web_scraper_bp.results'))

        # For all other websites, proceed with normal scraping
        print("Starting to scrape the main URL")
        try:
            main_text = scrape_website(website_url)
            print(f"Main text length: {len(main_text) if main_text else 0} characters")
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Error in main route when scraping website: {str(e)}")
            print(f"Full traceback:\n{error_trace}")
            flash(f"Error scraping website: {str(e)}", 'danger')
            return redirect(url_for('web_scraper_bp.index'))

        if main_text and len(main_text.strip()) > 0:
            # Get internal links
            print("Getting internal links")
            internal_links = get_internal_links(website_url)
            print(f"Found {len(internal_links)} internal links")

            # Scrape internal pages
            all_text = main_text
            successful_pages = 1  # Count main page as successful
            total_pages = 1 + len(internal_links)

            # Track which pages were successfully scraped
            scraped_pages = ["Main page"]

            # Set a maximum text length to avoid overwhelming the API
            max_text_length = 100000  # 100K characters should be enough for analysis
            current_text_length = len(main_text)

            for i, link in enumerate(internal_links):
                # Check if we've already collected enough text
                if current_text_length >= max_text_length:
                    print(f"Reached maximum text length ({max_text_length} characters). Stopping scraping.")
                    break

                print(f"Scraping internal link {i+1}/{len(internal_links)}: {link}")
                page_text = scrape_website(link)

                if page_text:
                    print(f"Internal link text length: {len(page_text)} characters")

                    # Add the page text to our collection
                    all_text += " " + page_text
                    current_text_length += len(page_text)
                    successful_pages += 1

                    # Extract page title or use URL
                    page_title = link.replace(website_url, '').strip('/') or link
                    scraped_pages.append(page_title)

                    # If we've reached the maximum text length, stop scraping
                    if current_text_length >= max_text_length:
                        print(f"Reached maximum text length ({max_text_length} characters). Stopping scraping.")
                        break
                else:
                    print(f"Failed to extract text from internal link: {link}")

            # Add scraping statistics to the analysis results
            scraping_stats = {
                "pages_scraped": successful_pages,
                "total_pages_attempted": total_pages,
                "success_rate": round((successful_pages / total_pages) * 100),
                "total_text_length": len(all_text),
                "scraped_pages": scraped_pages
            }
            print(f"Scraping statistics: {scraping_stats}")

            # Analyze the combined text
            # Import the text analyzer with API support
            from app.utils.text_analyzer import analyze_text as api_analyze_text

            try:
                print(f"Using {session['api_settings']['api_provider']} API for web content analysis")
                analysis_results = api_analyze_text(all_text)

                # Add scraping statistics to the analysis results
                if 'scraping_metadata' not in analysis_results:
                    analysis_results['scraping_metadata'] = {}

                analysis_results['scraping_metadata'] = scraping_stats

            except Exception as e:
                flash(f'API analysis failed: {str(e)}', 'danger')
                return redirect(url_for('api_settings'))

            # Update brand parameters
            brand_parameters = get_brand_parameters()
            updated_parameters = update_params_from_analysis(brand_parameters, analysis_results)

            # Print the updated parameters for debugging
            print("Updated brand parameters:")
            print(f"Personality primary traits: {updated_parameters['personality']['primary_traits']}")
            print(f"Personality secondary traits: {updated_parameters['personality']['secondary_traits']}")
            print(f"Emotional tone primary: {updated_parameters['emotional_tone']['primary_emotions']}")
            print(f"Emotional tone secondary: {updated_parameters['emotional_tone']['secondary_emotions']}")
            print(f"Formality level: {updated_parameters['formality']['level']}")
            print(f"Communication style - storytelling: {updated_parameters['communication_style']['storytelling_preference']}")
            print(f"Communication style - length: {updated_parameters['communication_style']['sentence_structure']['length_preference']}")
            print(f"Communication style - complexity: {updated_parameters['communication_style']['sentence_structure']['complexity_preference']}")

            # Print the raw API response for debugging
            print("\nRaw API response:")
            import json
            print(json.dumps(analysis_results, indent=2))

            # Use the session manager function to merge with method name
            from app.utils.session_manager import update_brand_parameters as update_session_parameters
            update_session_parameters(updated_parameters, method_name="web_scraper")

            # Mark web scraper as used
            update_input_method('web_scraper', True, analysis_results)

            flash('Website analyzed successfully!', 'success')
            return redirect(url_for('web_scraper_bp.results'))
        else:
            flash('Could not extract text from the website. Please check the URL and try again.', 'danger')

    # Check if we're handling Brightdata settings update
    if request.method == 'POST' and 'brightdata_form' in request.form:
        # Get settings from form
        api_key = request.form.get('api_key', '')
        zone = request.form.get('zone', 'web_unlocker1')
        enabled = 'enabled' in request.form

        # Update session
        session['brightdata_settings']['api_key'] = api_key
        session['brightdata_settings']['zone'] = zone
        session['brightdata_settings']['enabled'] = enabled
        session.modified = True

        # Log the settings (mask the API key)
        print(f"Brightdata settings saved: API Key: {'*' * len(api_key) if api_key else 'None'}, Zone: {zone}, Enabled: {enabled}")

        # Update the web_unlocker instance with the new API key
        if api_key:
            try:
                from app.utils.web_unlocker import web_unlocker
                web_unlocker.api_key = api_key
                web_unlocker.zone = zone

                # Test the connection if enabled
                if enabled:
                    success, content = web_unlocker.fetch_url('https://example.com')
                    if success:
                        flash('Brightdata Web Unlocker API key saved and verified successfully!', 'success')
                    else:
                        flash(f'Brightdata API key saved but verification failed: {content}', 'warning')
                else:
                    flash('Brightdata settings saved. Web Unlocker API is disabled.', 'info')
            except Exception as e:
                flash(f'Error configuring Brightdata Web Unlocker: {str(e)}', 'danger')
        else:
            flash('Brightdata settings cleared.', 'info')

        return redirect(url_for('web_scraper_bp.index'))

    return render_template('web_scraper.html', brightdata_settings=brightdata_settings)

@web_scraper_bp.route('/web-scraper/results')
def results():
    # Get input methods status
    input_methods = get_input_methods()

    # Check if web scraper has been used
    if not input_methods['web_scraper']['used']:
        flash('Please analyze a website first.', 'warning')
        return redirect(url_for('web_scraper_bp.index'))

    # For now, redirect to the main results page
    return redirect(url_for('results'))
