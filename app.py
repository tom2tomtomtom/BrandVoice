import streamlit as st
import os
import sys

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Import pages
from src.pages.home import show_home_page
from src.pages.document_upload import show_document_upload_page
from src.pages.brand_interview import show_brand_interview_page
from src.pages.web_scraper import show_web_scraper_page
from src.pages.parameter_dashboard import show_parameter_dashboard_page

# Set page configuration
st.set_page_config(
    page_title="Brand Voice Codifier",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "brand_parameters" not in st.session_state:
    st.session_state.brand_parameters = {
        "personality": {
            "primary_traits": [],
            "secondary_traits": [],
            "traits_to_avoid": []
        },
        "formality": {
            "level": 5,  # Scale of 1-10
            "context_variations": {}
        },
        "emotional_tone": {
            "primary_emotions": [],
            "secondary_emotions": [],
            "emotions_to_avoid": [],
            "intensity": 5  # Scale of 1-10
        },
        "vocabulary": {
            "preferred_terms": [],
            "restricted_terms": [],
            "jargon_level": 5,  # Scale of 1-10
            "technical_complexity": 5,  # Scale of 1-10
            "custom_terminology": {}
        },
        "communication_style": {
            "storytelling_preference": 5,  # Scale of 1-10 (direct to narrative)
            "sentence_structure": {
                "length_preference": 5,  # Scale of 1-10 (short to long)
                "complexity_preference": 5  # Scale of 1-10 (simple to complex)
            },
            "rhetorical_devices": [],
            "cta_style": ""
        },
        "audience_adaptation": {
            "audience_segments": {},
            "channel_adaptations": {},
            "journey_stage_adaptations": {}
        }
    }

if "input_methods" not in st.session_state:
    st.session_state.input_methods = {
        "document_upload": {"used": False, "data": {}},
        "brand_interview": {"used": False, "data": {}},
        "web_scraper": {"used": False, "data": {}}
    }

if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

# Sidebar navigation
st.sidebar.title("Brand Voice Codifier")
st.sidebar.subheader("Navigation")

# Navigation buttons
if st.sidebar.button("Home"):
    st.session_state.current_page = "home"
    
if st.sidebar.button("Document Upload & Analysis"):
    st.session_state.current_page = "document_upload"
    
if st.sidebar.button("Brand Interview"):
    st.session_state.current_page = "brand_interview"
    
if st.sidebar.button("Web Presence Scraper"):
    st.session_state.current_page = "web_scraper"
    
if st.sidebar.button("Parameter Dashboard"):
    st.session_state.current_page = "parameter_dashboard"

# Display the selected page
if st.session_state.current_page == "home":
    show_home_page()
elif st.session_state.current_page == "document_upload":
    show_document_upload_page()
elif st.session_state.current_page == "brand_interview":
    show_brand_interview_page()
elif st.session_state.current_page == "web_scraper":
    show_web_scraper_page()
elif st.session_state.current_page == "parameter_dashboard":
    show_parameter_dashboard_page()

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("Brand Voice Codifier POC v0.1")
