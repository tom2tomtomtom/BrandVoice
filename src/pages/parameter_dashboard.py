import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime

def generate_example_copy(parameters):
    """Generate example copy based on the brand voice parameters"""
    
    # Extract key parameters
    primary_traits = parameters["personality"]["primary_traits"]
    primary_emotions = parameters["emotional_tone"]["primary_emotions"]
    formality_level = parameters["formality"]["level"]
    storytelling_pref = parameters["communication_style"]["storytelling_preference"]
    
    # Generate example based on parameters
    if not primary_traits or not primary_emotions:
        return "Complete at least one input method to generate example copy."
    
    # Base examples for different combinations
    examples = {
        # Innovative examples
        ("innovative", "optimistic", "high"): "Introducing our groundbreaking solution that transforms how businesses approach sustainability. Our innovative platform leverages cutting-edge technology to deliver unprecedented results while maintaining the highest environmental standards.",
        ("innovative", "optimistic", "low"): "Check this out! We've created something totally new that's going to change how you think about sustainability. Our cool new tech makes amazing things happen while keeping things green!",
        ("innovative", "serious", "high"): "We present a significant advancement in sustainability technology. Our proprietary solution addresses critical environmental challenges through methodical innovation and rigorous scientific application.",
        ("innovative", "serious", "low"): "We've made a big breakthrough in green tech. Our new solution tackles serious environmental problems with smart innovation and solid science.",
        
        # Trustworthy examples
        ("trustworthy", "optimistic", "high"): "With our proven methodology and transparent approach, we deliver consistently reliable results. Our clients trust us to maintain the highest standards of integrity while achieving positive outcomes.",
        ("trustworthy", "optimistic", "low"): "You can count on us to keep our promises and do things right. We're always straight with you, and we're here to help you win!",
        ("trustworthy", "serious", "high"): "Our established protocols ensure dependable performance in all circumstances. We maintain strict adherence to ethical standards and provide comprehensive documentation of all processes.",
        ("trustworthy", "serious", "low"): "We do what we say we'll do, every time. We don't cut corners, and we always tell you exactly what's happening.",
        
        # Playful examples
        ("playful", "optimistic", "high"): "Embark on a delightful journey with our whimsical yet effective solutions. We infuse joy into every interaction while delivering results that exceed expectations.",
        ("playful", "optimistic", "low"): "Let's have some fun with this! Our awesome solutions bring a smile to your face AND get amazing results. Win-win!",
        ("playful", "passionate", "high"): "Discover the exhilarating combination of creativity and performance. Our enthusiastic approach transforms ordinary processes into extraordinary experiences.",
        ("playful", "passionate", "low"): "We're super excited about making things fun! Our creative approach turns boring stuff into awesome experiences you'll love!",
        
        # Sophisticated examples
        ("sophisticated", "calm", "high"): "We offer refined solutions characterized by elegant simplicity and thoughtful design. Our measured approach ensures a seamless experience that reflects discerning taste.",
        ("sophisticated", "calm", "low"): "Our stylish solutions are simple yet smart. We take a cool, collected approach to give you a smooth experience that shows real class.",
        ("sophisticated", "reassuring", "high"): "Rest assured that our distinguished services provide both excellence and peace of mind. We attend to every detail with precision, ensuring a superior outcome.",
        ("sophisticated", "reassuring", "low"): "Don't worry - our premium service has got you covered. We pay attention to all the little details so you get great results without the stress.",
        
        # Default example
        ("default", "default", "default"): "Our company provides solutions designed to meet your needs. We focus on delivering quality results through our dedicated approach and attention to detail."
    }
    
    # Determine which example to use
    primary_trait = primary_traits[0] if primary_traits else "default"
    primary_emotion = primary_emotions[0] if primary_emotions else "default"
    formality = "high" if formality_level > 5 else "low"
    
    # Get the example
    example_key = (primary_trait, primary_emotion, formality)
    if example_key in examples:
        example = examples[example_key]
    else:
        example = examples[("default", "default", "default")]
    
    # Adjust for storytelling preference
    if storytelling_pref > 7:
        example = "Imagine this scenario: " + example
    
    return example

def export_parameters():
    """Export brand parameters as JSON"""
    params_json = json.dumps(st.session_state.brand_parameters, indent=2)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return params_json, f"brand_voice_parameters_{timestamp}.json"

def show_parameter_dashboard_page():
    st.title("Brand Voice Parameter Dashboard")
    
    # Check if any input methods have been used
    if not any(method["used"] for method in st.session_state.input_methods.values()):
        st.warning("You haven't completed any input methods yet. Please use at least one input method to generate brand voice parameters.")
        if st.button("Return to Home"):
            st.session_state.current_page = "home"
        return
    
    # Display input methods used
    st.subheader("Input Methods Used")
    
    method_col1, method_col2, method_col3 = st.columns(3)
    
    with method_col1:
        if st.session_state.input_methods["document_upload"]["used"]:
            st.success("✅ Document Analysis")
        else:
            st.error("❌ Document Analysis")
    
    with method_col2:
        if st.session_state.input_methods["brand_interview"]["used"]:
            st.success("✅ Brand Interview")
        else:
            st.error("❌ Brand Interview")
    
    with method_col3:
        if st.session_state.input_methods["web_scraper"]["used"]:
            st.success("✅ Web Analysis")
        else:
            st.error("❌ Web Analysis")
    
    st.markdown("---")
    
    # Display and allow adjustment of parameters
    st.subheader("Brand Voice Parameters")
    st.markdown("Review and adjust your brand voice parameters below.")
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Personality", "Formality", "Emotional Tone", 
        "Vocabulary", "Communication Style", "Audience Adaptation"
    ])
    
    with tab1:
        st.subheader("Brand Personality")
        
        # Primary traits
        st.write("Primary Personality Traits")
        primary_traits = st.multiselect(
            "Select up to 3 primary traits",
            options=["Innovative", "Trustworthy", "Playful", "Sophisticated", "Friendly", "Authoritative", "Bold", "Empathetic"],
            default=[trait.capitalize() for trait in st.session_state.brand_parameters["personality"]["primary_traits"]],
            max_selections=3
        )
        st.session_state.brand_parameters["personality"]["primary_traits"] = [trait.lower() for trait in primary_traits]
        
        # Secondary traits
        st.write("Secondary Personality Traits")
        secondary_traits = st.multiselect(
            "Select up to 3 secondary traits",
            options=["Innovative", "Trustworthy", "Playful", "Sophisticated", "Friendly", "Authoritative", "Bold", "Empathetic"],
            default=[trait.capitalize() for trait in st.session_state.brand_parameters["personality"]["secondary_traits"]],
            max_selections=3
        )
        st.session_state.brand_parameters["personality"]["secondary_traits"] = [trait.lower() for trait in secondary_traits]
        
        # Traits to avoid
        st.write("Traits to Avoid")
        avoid_traits = st.multiselect(
            "Select traits to avoid",
            options=["Innovative", "Trustworthy", "Playful", "Sophisticated", "Friendly", "Authoritative", "Bold", "Empathetic"],
            default=[trait.capitalize() for trait in st.session_state.brand_parameters["personality"]["traits_to_avoid"]]
        )
        st.session_state.brand_parameters["personality"]["traits_to_avoid"] = [trait.lower() for trait in avoid_traits]
        
        # Visualize personality traits
        if primary_traits or secondary_traits:
            st.subheader("Personality Profile")
            
            trait_data = {}
            for trait in primary_traits:
                trait_data[trait] = 10
            for trait in secondary_traits:
                if trait not in trait_data:
                    trait_data[trait] = 5
            
            df = pd.DataFrame({
                'Trait': list(trait_data.keys()),
                'Value': list(trait_data.values())
            })
            
            fig = px.bar(df, x='Trait', y='Value', color='Value',
                        color_continuous_scale='Viridis', title='Brand Personality Profile')
            st.plotly_chart(fig)
    
    with tab2:
        st.subheader("Formality Level")
        
        # Formality slider
        formality = st.slider(
            "How formal or casual should your brand voice be?",
            min_value=1, max_value=10, 
            value=st.session_state.brand_parameters["formality"]["level"],
            help="1 = Very Casual, 10 = Very Formal"
        )
        st.session_state.brand_parameters["formality"]["level"] = formality
        
        # Formality visualization
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = formality,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Formality Level"},
            gauge = {
                'axis': {'range': [1, 10]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [1, 3], 'color': "lightgreen"},
                    {'range': [3, 7], 'color': "lightyellow"},
                    {'range': [7, 10], 'color': "lightcoral"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': formality
                }
            }
        ))
        st.plotly_chart(fig)
        
        # Context variations
        st.write("Formality Context Variations")
        context_variations = st.text_area(
            "Describe how formality varies across different contexts:",
            value=next(iter(st.session_state.brand_parameters["formality"]["context_variations"].values()), "")
        )
        st.session_state.brand_parameters["formality"]["context_variations"] = {"general": context_variations}
    
    with tab3:
        st.subheader("Emotional Tone")
        
        # Primary emotions
        st.write("Primary Emotional Tones")
        primary_emotions = st.multiselect(
            "Select up to 2 primary emotional tones",
            options=["Optimistic", "Serious", "Passionate", "Calm", "Urgent", "Reassuring"],
            default=[emotion.capitalize() for emotion in st.session_state.brand_parameters["emotional_tone"]["primary_emotions"]],
            max_selections=2
        )
        st.session_state.brand_parameters["emotional_tone"]["primary_emotions"] = [emotion.lower() for emotion in primary_emotions]
        
        # Secondary emotions
        st.write("Secondary Emotional Tones")
        secondary_emotions = st.multiselect(
            "Select up to 2 secondary emotional tones",
            options=["Optimistic", "Serious", "Passionate", "Calm", "Urgent", "Reassuring"],
            default=[emotion.capitalize() for emotion in st.session_state.brand_parameters["emotional_tone"]["secondary_emotions"]],
            max_selections=2
        )
        st.session_state.brand_parameters["emotional_tone"]["secondary_emotions"] = [emotion.lower() for emotion in secondary_emotions]
        
        # Emotions to avoid
        st.write("Emotional Tones to Avoid")
        avoid_emotions = st.multiselect(
            "Select emotional tones to avoid",
            options=["Optimistic", "Serious", "Passionate", "Calm", "Urgent", "Reassuring"],
            default=[emotion.capitalize() for emotion in st.session_state.brand_parameters["emotional_tone"]["emotions_to_avoid"]]
        )
        st.session_state.brand_parameters["emotional_tone"]["emotions_to_avoid"] = [emotion.lower() for emotion in avoid_emotions]
        
        # Emotional intensity
        intensity = st.slider(
            "How intense should your brand's emotional expression be?",
            min_value=1, max_value=10, 
            value=st.session_state.brand_parameters["emotional_tone"]["intensity"],
            help="1 = Subtle, 10 = Intense"
        )
        st.session_state.brand_parameters["emotional_tone"]["intensity"] = intensity
        
        # Visualize emotional tone
        if primary_emotions or secondary_emotions:
            st.subheader("Emotional Tone Profile")
            
            emotion_data = {}
            for emotion in primary_emotions:
                emotion_data[emotion] = 10
            for emotion in secondary_emotions:
                if emotion not in emotion_data:
                    emotion_data[emotion] = 5
            
            df = pd.DataFrame({
                'Emotion': list(emotion_data.keys()),
                'Value': list(emotion_data.values())
            })
            
            fig = px.pie(df, values='Value', names='Emotion', title='Emotional Tone Distribution')
            st.plotly_chart(fig)
    
    with tab4:
        st.subheader("Vocabulary Profile")
        
        # Preferred terms
        st.write("Preferred Terminology")
        preferred_terms = st.text_area(
            "Enter preferred terms or phrases (comma-separated):",
            value=", ".join(st.session_state.brand_parameters["vocabulary"]["preferred_terms"])
        )
        st.session_state.brand_parameters["vocabulary"]["preferred_terms"] = [term.strip() for term in preferred_terms.split(",") if term.strip()]
        
        # Restricted terms
        st.write("Restricted Terminology")
        restricted_terms = st.text_area(
            "Enter terms or phrases to avoid (comma-separated):",
            value=", ".join(st.session_state.brand_parameters["vocabulary"]["restricted_terms"])
        )
        st.session_state.brand_parameters["vocabulary"]["restricted_terms"] = [term.strip() for term in restricted_terms.split(",") if term.strip()]
        
        # Jargon level
        jargon_level = st.slider(
            "How much industry jargon should your brand use?",
            min_value=1, max_value=10, 
            value=st.session_state.brand_parameters["vocabulary"]["jargon_level"],
            help="1 = Minimal, 10 = Extensive"
        )
        st.session_state.brand_parameters["vocabulary"]["jargon_level"] = jargon_level
        
        # Technical complexity
        technical_complexity = st.slider(
            "How technically complex should your language be?",
            min_value=1, max_value=10, 
            value=st.session_state.brand_parameters["vocabulary"]["technical_complexity"],
            help="1 = Simple, 10 = Complex"
        )
        st.session_state.brand_parameters["vocabulary"]["technical_complexity"] = technical_complexity
        
        # Visualize vocabulary parameters
        st.subheader("Vocabulary Parameters")
        
        vocab_data = {
            'Parameter': ['Jargon Level', 'Technical Complexity'],
            'Value': [jargon_level, technical_complexity]
        }
        
        df = pd.DataFrame(vocab_data)
        fig = px.bar(df, x='Parameter', y='Value', color='Value',
                    color_continuous_scale='Blues', title='Vocabulary Parameters')
        st.plotly_chart(fig)
    
    with tab5:
        st.subheader("Communication Style")
        
        # Storytelling preference
        storytelling_pref = st.slider(
            "Should your brand favor direct communication or storytelling?",
            min_value=1, max_value=10, 
            value=st.session_state.brand_parameters["communication_style"]["storytelling_preference"],
            help="1 = Very Direct, 10 = Narrative-focused"
        )
        st.session_state.brand_parameters["communication_style"]["storytelling_preference"] = storytelling_pref
        
        # Sentence length
        sentence_length = st.slider(
            "What sentence length does your brand prefer?",
            min_value=1, max_value=10, 
            value=st.session_state.brand_parameters["communication_style"]["sentence_structure"]["length_preference"],
            help="1 = Very Short, 10 = Long"
        )
        st.session_state.brand_parameters["communication_style"]["sentence_structure"]["length_preference"] = sentence_length
        
        # Sentence complexity
        sentence_complexity = st.slider(
            "What sentence complexity does your brand prefer?",
            min_value=1, max_value=10, 
            value=st.session_state.brand_parameters["communication_style"]["sentence_structure"]["complexity_preference"],
            help="1 = Very Simple, 10 = Complex"
        )
        st.session_state.brand_parameters["communication_style"]["sentence_structure"]["complexity_preference"] = sentence_complexity
        
        # Rhetorical devices
        st.write("Rhetorical Devices")
        rhetorical_devices = st.multiselect(
            "Which rhetorical devices should your brand use?",
            options=["Questions", "Metaphors", "Analogies", "Repetition", "Alliteration", "Statistics", "Quotes"],
            default=st.session_state.brand_parameters["communication_style"]["rhetorical_devices"]
        )
        st.session_state.brand_parameters["communication_style"]["rhetorical_devices"] = rhetorical_devices
        
        # CTA style
        cta_style = st.text_area(
            "How would you describe your brand's call-to-action style?",
            value=st.session_state.brand_parameters["communication_style"]["cta_style"]
        )
        st.session_state.brand_parameters["communication_style"]["cta_style"] = cta_style
        
        # Visualize communication style
        st.subheader("Communication Style Parameters")
        
        comm_data = {
            'Parameter': ['Storytelling vs. Direct', 'Sentence Length', 'Sentence Complexity'],
            'Value': [storytelling_pref, sentence_length, sentence_complexity]
        }
        
        df = pd.DataFrame(comm_data)
        fig = px.bar(df, x='Parameter', y='Value', color='Value',
                    color_continuous_scale='Greens', title='Communication Style Parameters')
        st.plotly_chart(fig)
    
    with tab6:
        st.subheader("Audience Adaptation")
        
        # Audience segments
        st.write("Audience Segment Adaptations")
        audience_segments = st.text_area(
            "Describe how your brand voice changes for different audience segments:",
            value=next(iter(st.session_state.brand_parameters["audience_adaptation"]["audience_segments"].values()), "")
        )
        st.session_state.brand_parameters["audience_adaptation"]["audience_segments"] = {"general": audience_segments}
        
        # Channel adaptations
        st.write("Channel Adaptations")
        channel_adaptations = st.text_area(
            "Describe how your brand voice changes across different channels:",
            value=next(iter(st.session_state.brand_parameters["audience_adaptation"]["channel_adaptations"].values()), "")
        )
        st.session_state.brand_parameters["audience_adaptation"]["channel_adaptations"] = {"general": channel_adaptations}
        
        # Journey stage adaptations
        st.write("Customer Journey Stage Adaptations")
        journey_stages = st.text_area(
            "Describe how your brand voice changes across different customer journey stages:",
            value=next(iter(st.session_state.brand_parameters["audience_adaptation"]["journey_stage_adaptations"].values()), "")
        )
        st.session_state.brand_parameters["audience_adaptation"]["journey_stage_adaptations"] = {"general": journey_stages}
    
    st.markdown("---")
    
    # Example copy based on parameters
    st.subheader("Example Copy")
    st.markdown("Here's an example of copy that reflects your brand voice parameters:")
    
    example_copy = generate_example_copy(st.session_state.brand_parameters)
    st.info(example_copy)
    
    # Export parameters
    st.markdown("---")
    st.subheader("Export Brand Voice Parameters")
    
    params_json, filename = export_parameters()
    st.download_button(
        label="Download Brand Voice Parameters (JSON)",
        data=params_json,
        file_name=filename,
        mime="application/json"
    )
    
    # Display raw parameters for debugging
    with st.expander("View Raw Parameters"):
        st.json(st.session_state.brand_parameters)
