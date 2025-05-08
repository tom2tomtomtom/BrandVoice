import streamlit as st

def show_home_page():
    st.title("Brand Voice Codifier: Proof of Concept")
    
    st.markdown("""
    ## Welcome to the Brand Voice Codifier
    
    This tool is designed to analyze, capture, and codify your brand's tone of voice for integration with a copywriting agent in an ad creation platform.
    
    ### How It Works
    
    The Brand Voice Codifier offers three different methods to capture your brand voice:
    
    1. **Document Upload & Analysis**: Upload your existing brand documents (guidelines, mission statements, marketing materials) and let our system extract key brand voice elements.
    
    2. **Conversational Brand Interview**: Answer a series of questions about your brand's personality, voice, and style to help us understand your brand voice preferences.
    
    3. **Web Presence Scraper**: Provide your website URL and social media channels to analyze your existing public-facing content for voice consistency and patterns.
    
    ### What You'll Get
    
    After using one or more of these methods, you'll receive:
    
    - A comprehensive brand voice parameter set
    - Visual representation of your brand voice characteristics
    - Adjustable parameters to fine-tune your brand voice
    - Exportable format for integration with copywriting systems
    
    ### Getting Started
    
    Choose one of the input methods from the sidebar to begin capturing your brand voice.
    """)
    
    # Display cards for each input method
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("### Document Upload & Analysis")
        st.markdown("Upload brand documents to extract voice parameters.")
        if st.button("Start Document Analysis", key="doc_button"):
            st.session_state.current_page = "document_upload"
    
    with col2:
        st.info("### Brand Interview")
        st.markdown("Answer questions to define your brand voice.")
        if st.button("Start Brand Interview", key="interview_button"):
            st.session_state.current_page = "brand_interview"
    
    with col3:
        st.info("### Web Presence Scraper")
        st.markdown("Analyze your website and social media content.")
        if st.button("Start Web Analysis", key="web_button"):
            st.session_state.current_page = "web_scraper"
    
    # Show progress if any methods have been used
    st.markdown("---")
    st.subheader("Your Progress")
    
    progress_col1, progress_col2, progress_col3 = st.columns(3)
    
    with progress_col1:
        if st.session_state.input_methods["document_upload"]["used"]:
            st.success("✅ Document Analysis Complete")
        else:
            st.warning("⏳ Document Analysis Not Started")
    
    with progress_col2:
        if st.session_state.input_methods["brand_interview"]["used"]:
            st.success("✅ Brand Interview Complete")
        else:
            st.warning("⏳ Brand Interview Not Started")
    
    with progress_col3:
        if st.session_state.input_methods["web_scraper"]["used"]:
            st.success("✅ Web Analysis Complete")
        else:
            st.warning("⏳ Web Analysis Not Started")
    
    # Show dashboard button if at least one method is complete
    if any(method["used"] for method in st.session_state.input_methods.values()):
        st.markdown("---")
        st.success("You've completed at least one input method. View your brand voice parameters in the dashboard.")
        if st.button("View Brand Voice Dashboard", key="dashboard_button"):
            st.session_state.current_page = "parameter_dashboard"
