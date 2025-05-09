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

web_scraper_bp = Blueprint('web_scraper', __name__)

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
                                raise
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
                                raise
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
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']

            # Handle relative URLs
            if href.startswith('/'):
                href = base_domain + href
            # Handle URLs without protocol
            elif not href.startswith(('http://', 'https://')) and not href.startswith('#'):
                href = base_domain + '/' + href.lstrip('/')

            # Only include internal links
            if base_url in href and href not in links:
                links.append(href)

        return links[:5]  # Limit to 5 internal links for the POC
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

            for i, link in enumerate(internal_links):
                print(f"Scraping internal link {i+1}/{len(internal_links)}: {link}")
                page_text = scrape_website(link)
                if page_text:
                    print(f"Internal link text length: {len(page_text)} characters")
                    all_text += " " + page_text
                else:
                    print(f"Failed to extract text from internal link: {link}")

            # Analyze the combined text
            # Import the text analyzer with API support
            from app.utils.text_analyzer import analyze_text as api_analyze_text

            try:
                print(f"Using {session['api_settings']['api_provider']} API for web content analysis")
                analysis_results = api_analyze_text(all_text)
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
