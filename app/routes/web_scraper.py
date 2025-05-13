from flask import Blueprint, render_template, request, redirect, url_for, flash
from bs4 import BeautifulSoup
import re
import ssl
import urllib3
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context
from app.utils.session_manager import get_brand_parameters, update_input_method, get_input_methods
from app.utils.text_analyzer import update_brand_parameters as update_params_from_analysis
from app.utils.web_unlocker import fetch_with_web_unlocker

web_scraper_bp = Blueprint('web_scraper_bp', __name__)

def scrape_website(url):
    """Scrape text content from a website"""
    print(f"Attempting to scrape website: {url}")

    # Suppress all SSL warnings
    urllib3.disable_warnings()

    # Create a custom SSL context that ignores certificate validation
    class SSLAdapter(HTTPAdapter):
        def init_poolmanager(self, *args, **kwargs):
            context = create_urllib3_context(ciphers=None)
            context.options |= (ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1)
            # Completely disable hostname checking and certificate verification
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            kwargs['ssl_context'] = context
            kwargs['assert_hostname'] = False  # Disable hostname assertion
            return super(SSLAdapter, self).init_poolmanager(*args, **kwargs)

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        print("Making HTTP request with custom SSL adapter")

        # Create a session with our custom SSL adapter
        session = requests.Session()
        adapter = SSLAdapter()
        session.mount('https://', adapter)
        session.mount('http://', adapter)

        # First attempt with the custom SSL adapter
        try:
            print(f"Making request to {url} with custom SSL adapter")
            response = session.get(url, headers=headers, timeout=15, verify=False)
            print(f"Response status code: {response.status_code}")
            response.raise_for_status()
            print("Response successful")
        except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as e:
            print(f"SSL/Connection Error with custom adapter: {str(e)}")

            # Check if it's any kind of SSL certificate error
            if "Hostname mismatch" in str(e) or "certificate verify failed" in str(e) or "certificate has expired" in str(e) or "SSL" in str(e):
                print("Detected SSL certificate error (expired, hostname mismatch, or other verification issue)")
                # Try with a more aggressive approach to bypass SSL
                try:
                    print("Trying with urllib and completely unverified SSL context")
                    import urllib.request
                    context = ssl._create_unverified_context()
                    req = urllib.request.Request(url, headers=headers)
                    with urllib.request.urlopen(req, context=context, timeout=20) as response_obj:
                        response_text = response_obj.read().decode('utf-8')

                    # Create a mock response object with the text
                    class MockResponse:
                        def __init__(self, text):
                            self.text = text
                            self.status_code = 200

                    response = MockResponse(response_text)
                    print("Alternative approach with urllib successful")
                except Exception as urllib_e:
                    print(f"urllib approach failed: {str(urllib_e)}")

                    # Try with HTTP if HTTPS fails
                    if url.startswith('https://'):
                        http_url = 'http://' + url[8:]
                        print(f"Retrying with HTTP: {http_url}")
                        try:
                            response = session.get(http_url, headers=headers, timeout=15, verify=False)
                            print(f"HTTP Response status code: {response.status_code}")
                            response.raise_for_status()
                            print("HTTP Response successful")
                        except Exception as http_e:
                            print(f"HTTP retry failed: {str(http_e)}")

                            # Last resort for expired certificates: try with a different approach
                            try:
                                print("Trying with a completely different approach for expired certificates...")
                                # Try with a different library - requests with a custom adapter
                                import ssl
                                from urllib3.poolmanager import PoolManager

                                # Create a custom adapter that accepts all certificates
                                class TLSAdapter(requests.adapters.HTTPAdapter):
                                    def init_poolmanager(self, connections, maxsize, block=False):
                                        ctx = ssl.create_default_context()
                                        ctx.check_hostname = False
                                        ctx.verify_mode = ssl.CERT_NONE
                                        self.poolmanager = PoolManager(
                                            num_pools=connections,
                                            maxsize=maxsize,
                                            block=block,
                                            ssl_version=ssl.PROTOCOL_TLS,
                                            ssl_context=ctx
                                        )

                                # Create a new session with the custom adapter
                                last_resort_session = requests.session()
                                last_resort_session.mount('https://', TLSAdapter())

                                # Try to get the page
                                print(f"Making last resort request to {url}")
                                response = last_resort_session.get(url, headers=headers, timeout=30)
                                print(f"Last resort response status code: {response.status_code}")
                                response.raise_for_status()
                                print("Last resort approach successful")
                            except Exception as last_e:
                                print(f"Last resort approach failed: {str(last_e)}")

                                # Final fallback: Try with Brightdata Web Unlocker API if configured
                                from app.utils.web_unlocker import web_unlocker
                                if web_unlocker.is_configured():
                                    print("Trying with Brightdata Web Unlocker API...")
                                    try:
                                        success, content = fetch_with_web_unlocker(url)
                                        if success:
                                            print("Brightdata Web Unlocker API successful")
                                            # Create a mock response object with the text
                                            class MockResponse:
                                                def __init__(self, text):
                                                    self.text = text
                                                    self.status_code = 200

                                            response = MockResponse(content)
                                            print("Web Unlocker approach successful")
                                        else:
                                            print(f"Web Unlocker approach failed: {content}")
                                            raise Exception(f"All approaches failed: {content}")
                                    except Exception as unlocker_e:
                                        print(f"Web Unlocker approach failed: {str(unlocker_e)}")
                                        raise
                                else:
                                    print("Brightdata Web Unlocker API is not configured or disabled. Skipping this approach.")
                                    raise Exception("All approaches failed and Web Unlocker API is not configured")
                    else:
                        raise
            else:
                # Try with HTTP if HTTPS fails
                if url.startswith('https://'):
                    http_url = 'http://' + url[8:]
                    print(f"Retrying with HTTP: {http_url}")
                    try:
                        response = session.get(http_url, headers=headers, timeout=15, verify=False)
                        print(f"HTTP Response status code: {response.status_code}")
                        response.raise_for_status()
                        print("HTTP Response successful")
                    except Exception as http_e:
                        print(f"HTTP retry failed: {str(http_e)}")

                        # Last resort: try with a completely different approach
                        print("Trying with a completely different approach...")
                        try:
                            # Try with a different library if available
                            import urllib.request
                            context = ssl._create_unverified_context()
                            req = urllib.request.Request(url, headers=headers)
                            with urllib.request.urlopen(req, context=context, timeout=20) as response_obj:
                                response_text = response_obj.read().decode('utf-8')

                            # Create a mock response object with the text
                            class MockResponse:
                                def __init__(self, text):
                                    self.text = text
                                    self.status_code = 200

                            response = MockResponse(response_text)
                            print("Alternative approach successful")
                        except Exception as alt_e:
                            print(f"Alternative approach failed: {str(alt_e)}")
                            raise
                else:
                    raise
        except requests.exceptions.Timeout as e:
            print(f"Timeout Error: {str(e)}")
            # Try again with a longer timeout
            try:
                print(f"Retrying with longer timeout...")
                response = session.get(url, headers=headers, timeout=30, verify=False)
                print(f"Longer timeout Response status code: {response.status_code}")
                response.raise_for_status()
                print("Longer timeout Response successful")
            except Exception as retry_e:
                print(f"Retry with longer timeout also failed: {str(retry_e)}")
                raise
        except requests.exceptions.RequestException as e:
            print(f"Request Exception: {str(e)}")
            raise

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract text from a wider range of elements
        # Include more elements like div, span, article, section that might contain content
        content_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'div', 'span', 'article', 'section', 'blockquote', 'figcaption', 'strong', 'em', 'b', 'i', 'a', 'td', 'th'])

        # Filter out elements with very little text (likely navigation or UI elements)
        meaningful_elements = []
        for element in content_elements:
            # Skip elements with no text
            if not element.get_text().strip():
                continue

            # Skip elements that are likely navigation, header, footer, etc.
            parent_classes = []
            for parent in element.parents:
                if parent.has_attr('class'):
                    parent_classes.extend(parent['class'])
                if parent.has_attr('id'):
                    parent_classes.append(parent['id'])

            skip_keywords = ['nav', 'menu', 'footer', 'header', 'sidebar', 'widget', 'cookie', 'popup', 'modal', 'banner']
            if any(keyword in ' '.join(parent_classes).lower() for keyword in skip_keywords):
                continue

            # Skip very short text that's likely not meaningful content
            if len(element.get_text().strip()) < 10 and element.name not in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                continue

            meaningful_elements.append(element)

        # Extract text from meaningful elements
        text = ' '.join([el.get_text().strip() for el in meaningful_elements])

        # Look for specific brand voice related content
        brand_voice_keywords = ['brand voice', 'tone of voice', 'how we speak', 'our language', 'our voice', 'our tone', 'we are', 'we aren\'t', 'we don\'t', 'words we use', 'words to avoid']
        brand_voice_elements = []

        for element in soup.find_all(['div', 'section', 'article']):
            element_text = element.get_text().lower()
            if any(keyword in element_text for keyword in brand_voice_keywords):
                brand_voice_elements.append(element.get_text().strip())

        # Add brand voice specific content to the beginning for emphasis
        if brand_voice_elements:
            text = ' '.join(brand_voice_elements) + ' ' + text

        # Clean the text
        text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
        text = re.sub(r'[^\w\s.,!?;:\'"-]', '', text)  # Remove special characters except common punctuation

        return text
    except Exception as e:
        flash(f"Error scraping website: {str(e)}", 'danger')
        return None

def get_internal_links(url):
    """Get internal links from a website"""
    try:
        # Suppress all SSL warnings
        urllib3.disable_warnings()

        # Create a custom SSL context that ignores certificate validation
        class SSLAdapter(HTTPAdapter):
            def init_poolmanager(self, *args, **kwargs):
                context = create_urllib3_context(ciphers=None)
                context.options |= (ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1)
                # Completely disable hostname checking and certificate verification
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                kwargs['ssl_context'] = context
                kwargs['assert_hostname'] = False  # Disable hostname assertion
                return super(SSLAdapter, self).init_poolmanager(*args, **kwargs)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Create a session with our custom SSL adapter
        session = requests.Session()
        adapter = SSLAdapter()
        session.mount('https://', adapter)
        session.mount('http://', adapter)

        # First attempt with the custom SSL adapter
        try:
            print(f"Getting internal links from {url} with custom SSL adapter")
            response = session.get(url, headers=headers, timeout=15, verify=False)
            print(f"Response status code: {response.status_code}")
            response.raise_for_status()
            print("Response successful")
        except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as e:
            print(f"SSL/Connection Error with custom adapter: {str(e)}")

            # Check if it's any kind of SSL certificate error
            if "Hostname mismatch" in str(e) or "certificate verify failed" in str(e) or "certificate has expired" in str(e) or "SSL" in str(e):
                print("Detected SSL certificate error (expired, hostname mismatch, or other verification issue)")
                # Try with a more aggressive approach to bypass SSL
                try:
                    print("Trying with urllib and completely unverified SSL context")
                    import urllib.request
                    context = ssl._create_unverified_context()
                    req = urllib.request.Request(url, headers=headers)
                    with urllib.request.urlopen(req, context=context, timeout=20) as response_obj:
                        response_text = response_obj.read().decode('utf-8')

                    # Create a mock response object with the text
                    class MockResponse:
                        def __init__(self, text):
                            self.text = text
                            self.status_code = 200

                    response = MockResponse(response_text)
                    print("Alternative approach with urllib successful")
                except Exception as urllib_e:
                    print(f"urllib approach failed: {str(urllib_e)}")

                    # Try with HTTP if HTTPS fails
                    if url.startswith('https://'):
                        http_url = 'http://' + url[8:]
                        print(f"Retrying with HTTP: {http_url}")
                        try:
                            response = session.get(http_url, headers=headers, timeout=15, verify=False)
                            print(f"HTTP Response status code: {response.status_code}")
                            response.raise_for_status()
                            print("HTTP Response successful")
                        except Exception as http_e:
                            print(f"HTTP retry failed: {str(http_e)}")

                            # Last resort for expired certificates: try with a different approach
                            try:
                                print("Trying with a completely different approach for expired certificates...")
                                # Try with a different library - requests with a custom adapter
                                import ssl
                                from urllib3.poolmanager import PoolManager

                                # Create a custom adapter that accepts all certificates
                                class TLSAdapter(requests.adapters.HTTPAdapter):
                                    def init_poolmanager(self, connections, maxsize, block=False):
                                        ctx = ssl.create_default_context()
                                        ctx.check_hostname = False
                                        ctx.verify_mode = ssl.CERT_NONE
                                        self.poolmanager = PoolManager(
                                            num_pools=connections,
                                            maxsize=maxsize,
                                            block=block,
                                            ssl_version=ssl.PROTOCOL_TLS,
                                            ssl_context=ctx
                                        )

                                # Create a new session with the custom adapter
                                last_resort_session = requests.session()
                                last_resort_session.mount('https://', TLSAdapter())

                                # Try to get the page
                                print(f"Making last resort request to {url}")
                                response = last_resort_session.get(url, headers=headers, timeout=30)
                                print(f"Last resort response status code: {response.status_code}")
                                response.raise_for_status()
                                print("Last resort approach successful")
                            except Exception as last_e:
                                print(f"Last resort approach failed: {str(last_e)}")

                                # Final fallback: Try with Brightdata Web Unlocker API if configured
                                from app.utils.web_unlocker import web_unlocker
                                if web_unlocker.is_configured():
                                    print("Trying with Brightdata Web Unlocker API...")
                                    try:
                                        success, content = fetch_with_web_unlocker(url)
                                        if success:
                                            print("Brightdata Web Unlocker API successful")
                                            # Create a mock response object with the text
                                            class MockResponse:
                                                def __init__(self, text):
                                                    self.text = text
                                                    self.status_code = 200

                                            response = MockResponse(content)
                                            print("Web Unlocker approach successful")
                                        else:
                                            print(f"Web Unlocker approach failed: {content}")
                                            raise Exception(f"All approaches failed: {content}")
                                    except Exception as unlocker_e:
                                        print(f"Web Unlocker approach failed: {str(unlocker_e)}")
                                        raise
                                else:
                                    print("Brightdata Web Unlocker API is not configured or disabled. Skipping this approach.")
                                    raise Exception("All approaches failed and Web Unlocker API is not configured")
                    else:
                        raise
            else:
                # Try with HTTP if HTTPS fails
                if url.startswith('https://'):
                    http_url = 'http://' + url[8:]
                    print(f"Retrying with HTTP: {http_url}")
                    try:
                        response = session.get(http_url, headers=headers, timeout=15, verify=False)
                        print(f"HTTP Response status code: {response.status_code}")
                        response.raise_for_status()
                        print("HTTP Response successful")
                    except Exception as http_e:
                        print(f"HTTP retry failed: {str(http_e)}")
                        raise
                else:
                    raise

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract base URL more reliably
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        base_url = parsed_url.netloc

        # Make sure we have a proper base URL
        if not base_url:
            # Try to extract from the original URL if parsing failed
            base_url = url.split('//')[-1].split('/')[0]

        # Ensure the base URL has the https:// prefix for constructing full URLs
        base_domain = 'https://' + base_url

        # Find all links
        links = []
        seen_links = set()  # To track unique links

        # Priority keywords for brand voice related pages
        priority_keywords = ['about', 'about-us', 'about-our-company', 'mission', 'values', 'culture',
                           'brand', 'voice', 'tone', 'style', 'guidelines', 'story', 'who-we-are',
                           'what-we-do', 'company', 'team', 'careers', 'jobs', 'work-with-us']

        priority_links = []
        regular_links = []

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']

            # Skip empty links, anchors, javascript, mailto, tel links
            if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                continue

            # Handle relative URLs
            if href.startswith('/'):
                href = base_domain + href
            # Handle URLs without protocol
            elif not href.startswith(('http://', 'https://')):
                href = base_domain + '/' + href.lstrip('/')

            # Normalize the URL (remove trailing slash, fragments, etc.)
            href = href.split('#')[0].split('?')[0].rstrip('/')

            # Only include internal links that we haven't seen before
            if base_url in href and href not in seen_links:
                seen_links.add(href)

                # Check if this is a priority link
                is_priority = False
                for keyword in priority_keywords:
                    if keyword in href.lower():
                        priority_links.append(href)
                        is_priority = True
                        break

                if not is_priority:
                    regular_links.append(href)

        # Combine priority links first, then regular links
        links = priority_links + regular_links

        # Return up to 10 links, with priority links first
        return links[:10]
    except Exception as e:
        flash(f"Error getting internal links: {str(e)}", 'danger')
        return []

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
            return redirect(url_for('web_scraper.index'))

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

        # Scrape the main URL
        print("Starting to scrape the main URL")
        main_text = scrape_website(website_url)
        print(f"Main text length: {len(main_text) if main_text else 0} characters")

        if main_text:
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

    # Get analysis results
    analysis_results = input_methods['web_scraper']['data']

    # For now, redirect to the main results page
    return redirect(url_for('results'))
