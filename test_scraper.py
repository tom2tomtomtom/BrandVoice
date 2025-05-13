import requests
from bs4 import BeautifulSoup
import ssl
import urllib3
import urllib.request
import traceback

def test_scrape(url):
    """Test scraping a website with different methods"""
    print(f"Testing scraping for URL: {url}")

    # Method 1: Simple requests
    try:
        print("\nMethod 1: Simple requests")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status code: {response.status_code}")
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
        text = ' '.join([p.get_text().strip() for p in paragraphs])
        print(f"Extracted text length: {len(text)}")
        print(f"First 100 chars: {text[:100]}")
        print("Method 1 SUCCESS")
    except Exception as e:
        print(f"Method 1 FAILED: {str(e)}")
        print(traceback.format_exc())

    # Method 2: Requests with SSL verification disabled
    try:
        print("\nMethod 2: Requests with SSL verification disabled")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        print(f"Status code: {response.status_code}")
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
        text = ' '.join([p.get_text().strip() for p in paragraphs])
        print(f"Extracted text length: {len(text)}")
        print(f"First 100 chars: {text[:100]}")
        print("Method 2 SUCCESS")
    except Exception as e:
        print(f"Method 2 FAILED: {str(e)}")
        print(traceback.format_exc())

    # Method 3: urllib with SSL context
    try:
        print("\nMethod 3: urllib with SSL context")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        context = ssl._create_unverified_context()
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=context, timeout=20) as response_obj:
            response_text = response_obj.read().decode('utf-8')

        soup = BeautifulSoup(response_text, 'html.parser')
        paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
        text = ' '.join([p.get_text().strip() for p in paragraphs])
        print(f"Extracted text length: {len(text)}")
        print(f"First 100 chars: {text[:100]}")
        print("Method 3 SUCCESS")
    except Exception as e:
        print(f"Method 3 FAILED: {str(e)}")
        print(traceback.format_exc())

if __name__ == "__main__":
    # Test with a few different URLs
    test_urls = [
        "https://www.apple.com",
        "https://www.google.com",
        "https://www.example.com",
        "https://lndr.com"  # This is the URL that's failing
    ]

    for url in test_urls:
        test_scrape(url)
        print("\n" + "="*50 + "\n")
