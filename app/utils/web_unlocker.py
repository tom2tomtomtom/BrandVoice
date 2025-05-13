"""
Brightdata Web Unlocker API integration for handling difficult-to-scrape websites.
This module provides a fallback mechanism when regular scraping methods fail.
"""

import requests
import json
import logging
import os
from flask import current_app, session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebUnlocker:
    """Client for making API calls to Brightdata Web Unlocker API."""

    def __init__(self, api_key=None):
        """
        Initialize the Web Unlocker client.

        Args:
            api_key: The API key for Brightdata Web Unlocker API
        """
        self.api_key = api_key or os.environ.get('BRIGHTDATA_API_KEY')
        self.api_endpoint = "https://api.brightdata.com/request"
        self.zone = "web_unlocker1"  # Default zone, can be configured

    def fetch_url(self, url, format="raw", data_format=None):
        """
        Fetch a URL using Brightdata Web Unlocker API.

        Args:
            url: The URL to fetch
            format: Response format (raw, json)
            data_format: Optional data format (markdown, screenshot)

        Returns:
            Tuple containing:
                - Success flag (True/False)
                - Response content or error message
        """
        if not self.api_key:
            logger.error("Brightdata API key is missing")
            return False, "API key is missing. Please configure the Brightdata API key."

        try:
            logger.info(f"Fetching URL with Web Unlocker API: {url}")

            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            # Prepare payload
            payload = {
                "zone": self.zone,
                "url": url,
                "format": format
            }

            # Add data_format if specified
            if data_format:
                payload["data_format"] = data_format

            # Make the API request
            response = requests.post(
                self.api_endpoint,
                headers=headers,
                json=payload,
                timeout=60  # Longer timeout for complex pages
            )

            logger.info(f"Web Unlocker API response status code: {response.status_code}")

            if response.status_code == 200:
                logger.info("Web Unlocker API request successful")

                # Handle different response formats
                if format == "raw":
                    if data_format == "screenshot":
                        return True, response.content  # Binary content for screenshots
                    else:
                        return True, response.text
                elif format == "json":
                    return True, response.json()
                else:
                    return True, response.content
            else:
                error_msg = f"API request failed with status code {response.status_code}: {response.text}"
                logger.error(error_msg)
                return False, error_msg

        except Exception as e:
            error_msg = f"Error fetching URL with Web Unlocker API: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def get_settings_from_session(self):
        """Get the Brightdata settings from the session if available."""
        try:
            # Try to get from session
            if 'brightdata_settings' in session:
                settings = session['brightdata_settings']
                return {
                    'api_key': settings.get('api_key', ''),
                    'zone': settings.get('zone', 'web_unlocker1'),
                    'enabled': settings.get('enabled', False)
                }
            return None
        except Exception:
            return None

    def is_configured(self):
        """Check if the Web Unlocker API is configured with a valid API key and enabled."""
        settings = self.get_settings_from_session()
        if settings:
            return bool(settings['api_key'] and settings['enabled'])
        return bool(self.api_key)

# Create a singleton instance
web_unlocker = WebUnlocker()

def fetch_with_web_unlocker(url, format="raw", data_format=None):
    """
    Utility function to fetch a URL using the Web Unlocker API.

    Args:
        url: The URL to fetch
        format: Response format (raw, json)
        data_format: Optional data format (markdown, screenshot)

    Returns:
        Tuple containing:
            - Success flag (True/False)
            - Response content or error message
    """
    # Get settings from session
    settings = web_unlocker.get_settings_from_session()

    if settings:
        # Check if enabled
        if not settings['enabled']:
            return False, "Brightdata Web Unlocker API is disabled in settings"

        # Check if API key is configured
        if not settings['api_key']:
            return False, "Brightdata API key is not configured"

        # Create a new instance with the settings
        unlocker = WebUnlocker(settings['api_key'])
        unlocker.zone = settings['zone']
        return unlocker.fetch_url(url, format, data_format)

    # Fallback to instance settings
    if not web_unlocker.api_key:
        return False, "Brightdata API key is not configured"

    # Use the singleton instance
    return web_unlocker.fetch_url(url, format, data_format)
