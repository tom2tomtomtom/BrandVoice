import requests
from bs4 import BeautifulSoup
import ssl
import urllib3
import urllib.request
import traceback
from app.utils.web_unlocker import fetch_with_web_unlocker, web_unlocker

def scrape_website(url):
    """Scrape text content from a website using a simplified approach"""
    print(f"Attempting to scrape website: {url}")

    # Suppress all SSL warnings
    urllib3.disable_warnings()

    try:
        # Method 1: Simple requests with SSL verification disabled
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        print(f"Making request to {url} with SSL verification disabled")
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        print(f"Response status code: {response.status_code}")
        response.raise_for_status()
        print("Response successful")
    except Exception as e:
        print(f"Method 1 failed: {str(e)}")
        
        try:
            # Method 2: urllib with SSL context
            print("Trying with urllib and unverified SSL context")
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
            print("Method 2 successful")
        except Exception as urllib_e:
            print(f"Method 2 failed: {str(urllib_e)}")
            
            # Method 3: Try with Brightdata Web Unlocker API if configured
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
                        print("Method 3 successful")
                    else:
                        print(f"Method 3 failed: {content}")
                        raise Exception(f"All methods failed: {content}")
                except Exception as unlocker_e:
                    print(f"Method 3 failed: {str(unlocker_e)}")
                    raise Exception(f"All scraping methods failed for {url}")
            else:
                print("Brightdata Web Unlocker API is not configured or disabled.")
                raise Exception(f"All scraping methods failed for {url}")
    
    # Process the response
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
    import re
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
    text = re.sub(r'[^\w\s.,!?;:\'"-]', '', text)  # Remove special characters except common punctuation
    
    return text
