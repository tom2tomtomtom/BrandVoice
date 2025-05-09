"""
API Client for intelligent text analysis.
This module handles communication with various AI APIs for text analysis.
"""

import requests
import json
import os
from typing import Dict, Any, Tuple, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIClient:
    """Client for making API calls to various AI services for text analysis."""

    def __init__(self, api_provider: str, api_key: str):
        """
        Initialize the API client.

        Args:
            api_provider: The API provider to use ('openai', 'anthropic', 'cohere', or 'custom')
            api_key: The API key for authentication
        """
        self.api_provider = api_provider
        self.api_key = api_key

        # API endpoints and configurations
        self.endpoints = {
            'openai': {
                'base_url': 'https://api.openai.com/v1',
                'analyze_endpoint': '/chat/completions',
                'model': 'gpt-4o',
                'headers': {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
            },
            'anthropic': {
                'base_url': 'https://api.anthropic.com/v1',
                'analyze_endpoint': '/messages',
                'model': 'claude-3-opus-20240229',
                'headers': {
                    'x-api-key': api_key,
                    'anthropic-version': '2023-06-01',
                    'Content-Type': 'application/json'
                }
            },
            'cohere': {
                'base_url': 'https://api.cohere.ai/v1',
                'analyze_endpoint': '/generate',
                'model': 'command-r-plus',
                'headers': {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
            },
            'custom': {
                'base_url': os.environ.get('CUSTOM_API_BASE_URL', 'https://api.example.com'),
                'analyze_endpoint': os.environ.get('CUSTOM_API_ENDPOINT', '/analyze'),
                'model': os.environ.get('CUSTOM_API_MODEL', 'default'),
                'headers': {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
            }
        }

    def analyze_text(self, text: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Analyze text using the configured API provider.

        Args:
            text: The text to analyze

        Returns:
            Tuple containing:
                - Success flag (True/False)
                - Analysis results or error message
        """
        # Add debug logging
        logger.info(f"Starting API analysis with provider: {self.api_provider}")
        logger.info(f"Text length: {len(text)} characters")

        # Save the text to a debug file before sending to API
        try:
            with open('debug_api_input.txt', 'w', encoding='utf-8') as f:
                f.write(text)
            logger.info("Saved API input text to debug_api_input.txt for inspection")
        except Exception as e:
            logger.error(f"Error saving API input debug file: {str(e)}")

        # For debugging purposes, let's add a deliberate delay to simulate API call time
        import time
        time.sleep(3)  # Add a 3-second delay to make it obvious when API is being used

        if not self.api_provider or not self.api_key:
            logger.error("API provider or API key is missing")
            return False, {"error": "API provider or API key is missing"}

        if self.api_provider not in self.endpoints:
            logger.error(f"Unsupported API provider: {self.api_provider}")
            return False, {"error": f"Unsupported API provider: {self.api_provider}"}

        try:
            endpoint_config = self.endpoints[self.api_provider]
            url = f"{endpoint_config['base_url']}{endpoint_config['analyze_endpoint']}"
            logger.info(f"Making API request to: {url}")

            # Prepare the request based on the API provider
            if self.api_provider == 'openai':
                logger.info("Using OpenAI API for analysis")
                return self._analyze_with_openai(url, text, endpoint_config)
            elif self.api_provider == 'anthropic':
                logger.info("Using Anthropic API for analysis")
                return self._analyze_with_anthropic(url, text, endpoint_config)
            elif self.api_provider == 'cohere':
                logger.info("Using Cohere API for analysis")
                return self._analyze_with_cohere(url, text, endpoint_config)
            elif self.api_provider == 'custom':
                logger.info("Using Custom API for analysis")
                return self._analyze_with_custom(url, text, endpoint_config)

        except Exception as e:
            logger.error(f"API request failed: {str(e)}")
            return False, {"error": f"API request failed: {str(e)}"}

    def _analyze_with_openai(self, url: str, text: str, config: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Make an API call to OpenAI for text analysis."""
        logger.info("Preparing OpenAI API request payload")
        payload = {
            "model": config['model'],
            "messages": [
                {"role": "system", "content": "You are a brand voice analysis expert. Your task is to analyze the provided document and extract ALL brand voice characteristics directly from the text. DO NOT generate generic descriptions - only use what's explicitly stated in the document. If the document contains sections like 'Words and phrases we use', 'Words and phrases we avoid', 'We are...', 'We aren't...', 'How we speak', 'Our language toolkit', or any other brand voice guidelines, INCLUDE THEM ALL COMPLETELY. Capture the FULL RICHNESS of the brand voice descriptions. If the document is rich with brand voice information, include ALL of it. If it's sparse, extract whatever brand voice information you can find."},
                {"role": "user", "content": f"""Analyze the following document and extract ALL brand voice characteristics directly from the text. INCLUDE COMPLETE SECTIONS from the document that describe the brand voice. If the document contains rich brand voice guidelines, preserve ALL of this content in your analysis.

The response should follow this format:
```json
{{
  "personality_traits": {{
    "trait1": 9,
    "trait2": 8,
    "trait3": 7,
    "trait4": 6,
    "trait5": 5
  }},
  "emotional_tone": {{
    "tone1": 9,
    "tone2": 8,
    "tone3": 7,
    "tone4": 6
  }},
  "formality": {{
    "level": 7
  }},
  "vocabulary": {{
    "preferred_terms": ["exact term1", "exact term2", "exact term3", "exact term4", "exact term5", "exact term6", "exact term7", "exact term8", "exact term9", "exact term10", "exact term11", "exact term12", "exact term13", "exact term14", "exact term15"],
    "avoided_terms": ["avoided term1", "avoided term2", "avoided term3", "avoided term4", "avoided term5", "avoided term6", "avoided term7", "avoided term8", "avoided term9", "avoided term10"]
  }},
  "communication_style": {{
    "key_phrases": ["exact phrase1", "exact phrase2", "exact phrase3", "exact phrase4", "exact phrase5"],
    "sentence_structure": {{
      "length_preference": 7,
      "complexity_preference": 6
    }},
    "rich_descriptions": [
      "Full sentence or paragraph describing the brand voice exactly as stated in the document",
      "Another rich description from the document that captures the brand's unique voice",
      "Additional descriptive text that provides context and nuance to the brand voice"
    ]
  }}
}}
```

CRITICAL INSTRUCTIONS:
1. ONLY use traits, tones, terms, and phrases that are EXPLICITLY mentioned in the document.
2. For personality_traits, use the EXACT traits mentioned in the "Words and phrases we use", "We are...", or similar sections.
3. For emotional_tone, extract tones directly from sections describing the brand's tone or emotional qualities.
4. For preferred_terms, use the EXACT words and phrases listed in the "Words and phrases we use", "Superlatives", "Adjectives", or similar sections. Include ALL terms mentioned, not just a few.
5. For avoided_terms, use the EXACT words and phrases listed in the "Words and phrases we avoid", "Words and phrases we're not into", or similar sections. Include ALL terms mentioned, not just a few.
6. For key_phrases, extract direct quotes or taglines that represent the brand's voice. Include the most distinctive and representative phrases.
7. For rich_descriptions, extract COMPLETE sentences, paragraphs, or entire sections that describe the brand voice. Include ALL relevant content from the document verbatim.
8. DO NOT invent or generalize - only use what's explicitly in the document.
9. Assign numeric scores (1-10) based on the emphasis placed on each trait/tone in the document.
10. If the document contains a section like "How we speak", "Our language toolkit", "We are/We aren't", or any other brand voice guidelines, INCLUDE THESE SECTIONS COMPLETELY in rich_descriptions.
11. Include ALL sections that explicitly list words to use or avoid - these are critical to include in full.
12. Capture the FULL RICHNESS of the brand voice - don't summarize or simplify the descriptions provided in the document.
13. If the document is rich with brand voice information, include ALL of it. If it's sparse, extract whatever brand voice information you can find.
14. PRESERVE THE EXACT WORDING from the document - don't paraphrase or rewrite.

Here's the document to analyze:

{text}"""}
            ],
            "response_format": {"type": "json_object"}
        }

        logger.info(f"Sending POST request to OpenAI API: {url}")
        try:
            # Disable SSL verification for development purposes
            # In production, this should be set to True for security
            response = requests.post(url, json=payload, headers=config['headers'], verify=False)

            # Suppress only the InsecureRequestWarning from urllib3
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            logger.info(f"OpenAI API response status code: {response.status_code}")

            if response.status_code == 200:
                logger.info("OpenAI API request successful")
                result = response.json()
                try:
                    # Extract the JSON content from the response
                    content = result['choices'][0]['message']['content']
                    analysis_results = json.loads(content)
                    logger.info("Successfully parsed OpenAI API response")

                    # Save the API response to a debug file
                    try:
                        with open('debug_api_response.json', 'w', encoding='utf-8') as f:
                            f.write(json.dumps(analysis_results, indent=2))
                        logger.info("Saved API response to debug_api_response.json for inspection")
                    except Exception as e:
                        logger.error(f"Error saving API response debug file: {str(e)}")

                    return True, analysis_results
                except (KeyError, json.JSONDecodeError) as e:
                    logger.error(f"Failed to parse OpenAI API response: {str(e)}")
                    return False, {"error": f"Failed to parse API response: {str(e)}"}
            else:
                logger.error(f"OpenAI API request failed with status code {response.status_code}: {response.text}")
                return False, {"error": f"API request failed with status code {response.status_code}: {response.text}"}
        except Exception as e:
            logger.error(f"Exception during OpenAI API request: {str(e)}")
            return False, {"error": f"API request failed: {str(e)}"}

    def _analyze_with_anthropic(self, url: str, text: str, config: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Make an API call to Anthropic for text analysis."""
        payload = {
            "model": config['model'],
            "max_tokens": 4000,
            "messages": [
                {"role": "user", "content": f"Analyze the following text and provide a structured JSON response with brand voice parameters including personality traits, emotional tone, formality level, vocabulary characteristics, and communication style:\n\n{text}"}
            ],
            "system": "You are a brand voice analysis expert. Provide your analysis as a valid JSON object with no additional text.",
        }

        # Disable SSL verification for development purposes
        response = requests.post(url, json=payload, headers=config['headers'], verify=False)

        if response.status_code == 200:
            result = response.json()
            try:
                # Extract the JSON content from the response
                content = result['content'][0]['text']
                analysis_results = json.loads(content)
                return True, analysis_results
            except (KeyError, json.JSONDecodeError) as e:
                return False, {"error": f"Failed to parse API response: {str(e)}"}
        else:
            return False, {"error": f"API request failed with status code {response.status_code}: {response.text}"}

    def _analyze_with_cohere(self, url: str, text: str, config: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Make an API call to Cohere for text analysis."""
        payload = {
            "model": config['model'],
            "max_tokens": 4000,
            "prompt": f"Analyze the following text and provide a structured JSON response with brand voice parameters including personality traits, emotional tone, formality level, vocabulary characteristics, and communication style:\n\n{text}\n\nProvide your analysis as a valid JSON object with no additional text."
        }

        # Disable SSL verification for development purposes
        response = requests.post(url, json=payload, headers=config['headers'], verify=False)

        if response.status_code == 200:
            result = response.json()
            try:
                # Extract the JSON content from the response
                content = result['generations'][0]['text']
                # Find the JSON part in the response
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_content = content[json_start:json_end]
                    analysis_results = json.loads(json_content)
                    return True, analysis_results
                else:
                    return False, {"error": "Could not find valid JSON in the response"}
            except (KeyError, json.JSONDecodeError) as e:
                return False, {"error": f"Failed to parse API response: {str(e)}"}
        else:
            return False, {"error": f"API request failed with status code {response.status_code}: {response.text}"}

    def _analyze_with_custom(self, url: str, text: str, config: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Make an API call to a custom API for text analysis."""
        payload = {
            "text": text,
            "model": config['model'],
            "analysis_type": "brand_voice"
        }

        # Disable SSL verification for development purposes
        response = requests.post(url, json=payload, headers=config['headers'], verify=False)

        if response.status_code == 200:
            try:
                analysis_results = response.json()
                return True, analysis_results
            except json.JSONDecodeError as e:
                return False, {"error": f"Failed to parse API response: {str(e)}"}
        else:
            return False, {"error": f"API request failed with status code {response.status_code}: {response.text}"}

    def generate_tone_of_voice_assets(self, brand_voice_summary: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Generate tone of voice prompt and campaign taglines based on brand voice summary.

        Args:
            brand_voice_summary: The brand voice summary containing tone description, example phrases, etc.

        Returns:
            Tuple containing:
                - Success flag (True/False)
                - Generated assets or error message
        """
        logger.info("Generating tone of voice assets using API")

        if not self.api_provider or not self.api_key:
            logger.error("API provider or API key is missing")
            return False, {"error": "API provider or API key is missing"}

        if self.api_provider not in self.endpoints:
            logger.error(f"Unsupported API provider: {self.api_provider}")
            return False, {"error": f"Unsupported API provider: {self.api_provider}"}

        try:
            endpoint_config = self.endpoints[self.api_provider]
            url = f"{endpoint_config['base_url']}{endpoint_config['analyze_endpoint']}"
            logger.info(f"Making API request to: {url}")

            # Format the brand voice summary for the prompt
            tone_description = brand_voice_summary.get('tone_description', '')
            example_phrases = brand_voice_summary.get('example_phrases', [])
            frequently_used_words = brand_voice_summary.get('frequently_used_words', [])
            words_to_avoid = brand_voice_summary.get('words_to_avoid', [])

            # Create a comprehensive prompt with all brand voice elements
            prompt = f"""Based on the following brand voice summary, create:
1. A comprehensive tone of voice prompt that copywriters can use to write in this brand's voice
2. Two compelling campaign taglines/headlines that exemplify this brand voice

BRAND VOICE SUMMARY:
-------------------
TONE DESCRIPTION:
{tone_description}

KEY BRAND PHRASES:
{', '.join(example_phrases)}

WORDS & PHRASES WE USE:
{', '.join(frequently_used_words)}

WORDS & PHRASES WE AVOID:
{', '.join(words_to_avoid)}
-------------------

The tone of voice prompt should be thorough, specific, and actionable, providing clear guidance on:
- The brand's personality and character
- How to structure sentences and paragraphs
- Word choice and vocabulary preferences
- Emotional tone to convey
- Specific dos and don'ts
- Examples of good copy in this voice

The campaign taglines should be memorable, aligned with the brand voice, and showcase the distinctive style described above.

Format your response as a JSON object with these keys:
- tone_of_voice_prompt: A comprehensive guide for copywriters (at least 300 words)
- campaign_taglines: An array of two compelling taglines/headlines
"""

            # Make the API call based on the provider
            if self.api_provider == 'openai':
                logger.info("Using OpenAI API for generating tone of voice assets")

                payload = {
                    "model": endpoint_config['model'],
                    "messages": [
                        {"role": "system", "content": "You are an expert copywriter and brand strategist who creates precise, actionable tone of voice guidelines and compelling campaign taglines."},
                        {"role": "user", "content": prompt}
                    ],
                    "response_format": {"type": "json_object"}
                }

                response = requests.post(url, json=payload, headers=endpoint_config['headers'], verify=False)

                if response.status_code == 200:
                    result = response.json()
                    try:
                        content = result['choices'][0]['message']['content']
                        assets = json.loads(content)
                        logger.info("Successfully generated tone of voice assets")
                        return True, assets
                    except (KeyError, json.JSONDecodeError) as e:
                        logger.error(f"Failed to parse API response: {str(e)}")
                        return False, {"error": f"Failed to parse API response: {str(e)}"}
                else:
                    logger.error(f"API request failed with status code {response.status_code}: {response.text}")
                    return False, {"error": f"API request failed with status code {response.status_code}: {response.text}"}

            # Add support for other API providers as needed
            else:
                logger.error(f"Tone of voice asset generation not implemented for {self.api_provider}")
                return False, {"error": f"Tone of voice asset generation not implemented for {self.api_provider}"}

        except Exception as e:
            logger.error(f"Failed to generate tone of voice assets: {str(e)}")
            return False, {"error": f"Failed to generate tone of voice assets: {str(e)}"}
