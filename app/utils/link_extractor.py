from bs4 import BeautifulSoup
from urllib.parse import urlparse
import traceback
from app.utils.simple_scraper import scrape_website

def get_internal_links(url):
    """Get internal links from a website"""
    try:
        # Get the page content using our simplified scraper
        print(f"Getting internal links from {url}")
        
        # Use the scrape_website function to get the page content
        # This will handle all the SSL and connection issues
        response_text = scrape_website(url)
        
        if not response_text:
            print("Failed to get page content")
            return []
        
        # Parse the HTML
        soup = BeautifulSoup(response_text, 'html.parser')
        
        # Extract base URL more reliably
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
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error getting internal links: {str(e)}")
        print(f"Full traceback:\n{error_trace}")
        return []
