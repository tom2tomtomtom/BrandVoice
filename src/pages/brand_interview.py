import streamlit as st
import pandas as pd

# Define interview questions
INTERVIEW_QUESTIONS = {
    "personality": [
        {
            "question": "If your brand were a person, how would you describe their personality? (Select up to 3)",
            "type": "multiselect",
            "options": ["Innovative", "Trustworthy", "Playful", "Sophisticated", "Friendly", "Authoritative", "Bold", "Empathetic"],
            "key": "primary_traits",
            "max_selections": 3
        },
        {
            "question": "What secondary personality traits would your brand have? (Select up to 3)",
            "type": "multiselect",
            "options": ["Innovative", "Trustworthy", "Playful", "Sophisticated", "Friendly", "Authoritative", "Bold", "Empathetic"],
            "key": "secondary_traits",
            "max_selections": 3
        },
        {
            "question": "Which personality traits would you specifically want to avoid?",
            "type": "multiselect",
            "options": ["Innovative", "Trustworthy", "Playful", "Sophisticated", "Friendly", "Authoritative", "Bold", "Empathetic"],
            "key": "traits_to_avoid"
        }
    ],
    "formality": [
        {
            "question": "How formal or casual should your brand voice be?",
            "type": "slider",
            "min": 1,
            "max": 10,
            "default": 5,
            "labels": {1: "Very Casual", 5: "Balanced", 10: "Very Formal"},
            "key": "formality_level"
        },
        {
            "question": "Does your brand's formality level change in different contexts? If so, please describe:",
            "type": "text_area",
            "key": "context_variations"
        }
    ],
    "emotional_tone": [
        {
            "question": "What primary emotions should your brand voice convey? (Select up to 2)",
            "type": "multiselect",
            "options": ["Optimistic", "Serious", "Passionate", "Calm", "Urgent", "Reassuring"],
            "key": "primary_emotions",
            "max_selections": 2
        },
        {
            "question": "What secondary emotions might your brand voice convey? (Select up to 2)",
            "type": "multiselect",
            "options": ["Optimistic", "Serious", "Passionate", "Calm", "Urgent", "Reassuring"],
            "key": "secondary_emotions",
            "max_selections": 2
        },
        {
            "question": "Which emotional tones should your brand specifically avoid?",
            "type": "multiselect",
            "options": ["Optimistic", "Serious", "Passionate", "Calm", "Urgent", "Reassuring"],
            "key": "emotions_to_avoid"
        },
        {
            "question": "How intense should your brand's emotional expression be?",
            "type": "slider",
            "min": 1,
            "max": 10,
            "default": 5,
            "labels": {1: "Subtle", 5: "Moderate", 10: "Intense"},
            "key": "emotional_intensity"
        }
    ],
    "vocabulary": [
        {
            "question": "List some key terms or phrases that your brand should use frequently:",
            "type": "text_area",
            "key": "preferred_terms"
        },
        {
            "question": "List any terms or phrases that your brand should avoid:",
            "type": "text_area",
            "key": "restricted_terms"
        },
        {
            "question": "How much industry jargon should your brand use?",
            "type": "slider",
            "min": 1,
            "max": 10,
            "default": 5,
            "labels": {1: "Minimal", 5: "Moderate", 10: "Extensive"},
            "key": "jargon_level"
        },
        {
            "question": "How technically complex should your language be?",
            "type": "slider",
            "min": 1,
            "max": 10,
            "default": 5,
            "labels": {1: "Simple", 5: "Moderate", 10: "Complex"},
            "key": "technical_complexity"
        }
    ],
    "communication_style": [
        {
            "question": "Should your brand favor direct communication or storytelling?",
            "type": "slider",
            "min": 1,
            "max": 10,
            "default": 5,
            "labels": {1: "Very Direct", 5: "Balanced", 10: "Narrative-focused"},
            "key": "storytelling_preference"
        },
        {
            "question": "What sentence length does your brand prefer?",
            "type": "slider",
            "min": 1,
            "max": 10,
            "default": 5,
            "labels": {1: "Very Short", 5: "Medium", 10: "Long"},
            "key": "sentence_length"
        },
        {
            "question": "What sentence complexity does your brand prefer?",
            "type": "slider",
            "min": 1,
            "max": 10,
            "default": 5,
            "labels": {1: "Very Simple", 5: "Moderate", 10: "Complex"},
            "key": "sentence_complexity"
        },
        {
            "question": "Which rhetorical devices should your brand use? (Select all that apply)",
            "type": "multiselect",
            "options": ["Questions", "Metaphors", "Analogies", "Repetition", "Alliteration", "Statistics", "Quotes"],
            "key": "rhetorical_devices"
        },
        {
            "question": "How would you describe your brand's call-to-action style?",
            "type": "text_area",
            "key": "cta_style"
        }
    ],
    "audience_adaptation": [
        {
            "question": "Does your brand voice change for different audience segments? If so, please describe:",
            "type": "text_area",
            "key": "audience_segments"
        },
        {
            "question": "Does your brand voice change across different channels? If so, please describe:",
            "type": "text_area",
            "key": "channel_adaptations"
        },
        {
            "question": "Does your brand voice change across different customer journey stages? If so, please describe:",
            "type": "text_area",
            "key": "journey_stages"
        }
    ]
}

def update_brand_parameters_from_interview(responses):
    # Update personality traits
    if "primary_traits" in responses:
        st.session_state.brand_parameters["personality"]["primary_traits"] = responses["primary_traits"]
    if "secondary_traits" in responses:
        st.session_state.brand_parameters["personality"]["secondary_traits"] = responses["secondary_traits"]
    if "traits_to_avoid" in responses:
        st.session_state.brand_parameters["personality"]["traits_to_avoid"] = responses["traits_to_avoid"]
    
    # Update formality
    if "formality_level" in responses:
        st.session_state.brand_parameters["formality"]["level"] = responses["formality_level"]
    if "context_variations" in responses:
        st.session_state.brand_parameters["formality"]["context_variations"] = {"general": responses["context_variations"]}
    
    # Update emotional tone
    if "primary_emotions" in responses:
        st.session_state.brand_parameters["emotional_tone"]["primary_emotions"] = responses["primary_emotions"]
    if "secondary_emotions" in responses:
        st.session_state.brand_parameters["emotional_tone"]["secondary_emotions"] = responses["secondary_emotions"]
    if "emotions_to_avoid" in responses:
        st.session_state.brand_parameters["emotional_tone"]["emotions_to_avoid"] = responses["emotions_to_avoid"]
    if "emotional_intensity" in responses:
        st.session_state.brand_parameters["emotional_tone"]["intensity"] = responses["emotional_intensity"]
    
    # Update vocabulary
    if "preferred_terms" in responses:
        terms = [term.strip() for term in responses["preferred_terms"].split(",") if term.strip()]
        st.session_state.brand_parameters["vocabulary"]["preferred_terms"] = terms
    if "restricted_terms" in responses:
        terms = [term.strip() for term in responses["restricted_terms"].split(",") if term.strip()]
        st.session_state.brand_parameters["vocabulary"]["restricted_terms"] = terms
    if "jargon_level" in responses:
        st.session_state.brand_parameters["vocabulary"]["jargon_level"] = responses["jargon_level"]
    if "technical_complexity" in responses:
        st.session_state.brand_parameters["vocabulary"]["technical_complexity"] = responses["technical_complexity"]
    
    # Update communication style
    if "storytelling_preference" in responses:
        st.session_state.brand_parameters["communication_style"]["storytelling_preference"] = responses["storytelling_preference"]
    if "sentence_length" in responses:
        st.session_state.brand_parameters["communication_style"]["sentence_structure"]["length_preference"] = responses["sentence_length"]
    if "sentence_complexity" in responses:
        st.session_state.brand_parameters["communication_style"]["sentence_structure"]["complexity_preference"] = responses["sentence_complexity"]
    if "rhetorical_devices" in responses:
        st.session_state.brand_parameters["communication_style"]["rhetorical_devices"] = responses["rhetorical_devices"]
    if "cta_style" in responses:
        st.session_state.brand_parameters["communication_style"]["cta_style"] = responses["cta_style"]
    
    # Update audience adaptation
    if "audience_segments" in responses:
        st.session_state.brand_parameters["audience_adaptation"]["audience_segments"] = {"general": responses["audience_segments"]}
    if "channel_adaptations" in responses:
        st.session_state.brand_parameters["audience_adaptation"]["channel_adaptations"] = {"general": responses["channel_adaptations"]}
    if "journey_stages" in responses:
        st.session_state.brand_parameters["audience_adaptation"]["journey_stage_adaptations"] = {"general": responses["journey_stages"]}
    
    # Mark brand interview as used
    st.session_state.input_methods["brand_interview"]["used"] = True
    st.session_state.input_methods["brand_interview"]["data"] = responses

def show_brand_interview_page():
    st.title("Brand Voice Interview")
    
    st.markdown("""
    ## Brand Voice Discovery Interview
    
    Answer the following questions to help us understand your brand's voice and personality.
    This structured interview will guide you through defining your brand's unique voice characteristics.
    
    Take your time to consider each question carefully - your answers will directly shape the brand voice parameters.
    """)
    
    # Initialize responses dictionary if not already in session state
    if "interview_responses" not in st.session_state:
        st.session_state.interview_responses = {}
    
    # Initialize current section if not already in session state
    if "current_section" not in st.session_state:
        st.session_state.current_section = "personality"
    
    # Display progress
    sections = list(INTERVIEW_QUESTIONS.keys())
    current_index = sections.index(st.session_state.current_section)
    progress = (current_index) / len(sections)
    
    st.progress(progress)
    st.write(f"Section {current_index + 1} of {len(sections)}: {st.session_state.current_section.title()}")
    
    # Display current section questions
    st.subheader(f"{st.session_state.current_section.title()} Questions")
    
    responses = {}
    
    for question in INTERVIEW_QUESTIONS[st.session_state.current_section]:
        if question["type"] == "multiselect":
            max_selections = question.get("max_selections", None)
            help_text = f"Select up to {max_selections} options" if max_selections else "Select all that apply"
            
            value = st.multiselect(
                question["question"],
                options=question["options"],
                help=help_text,
                key=f"{st.session_state.current_section}_{question['key']}"
            )
            
            # Enforce max selections if specified
            if max_selections and len(value) > max_selections:
                st.warning(f"Please select at most {max_selections} options.")
                value = value[:max_selections]
            
            responses[question["key"]] = value
            
        elif question["type"] == "slider":
            value = st.slider(
                question["question"],
                min_value=question["min"],
                max_value=question["max"],
                value=question.get("default", (question["min"] + question["max"]) // 2),
                help="Drag the slider to indicate your preference",
                key=f"{st.session_state.current_section}_{question['key']}"
            )
            responses[question["key"]] = value
            
        elif question["type"] == "text_area":
            value = st.text_area(
                question["question"],
                help="Enter your response",
                key=f"{st.session_state.current_section}_{question['key']}"
            )
            responses[question["key"]] = value
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if current_index > 0:
            if st.button("Previous Section"):
                # Save responses to session state
                for key, value in responses.items():
                    st.session_state.interview_responses[key] = value
                
                # Go to previous section
                st.session_state.current_section = sections[current_index - 1]
                st.experimental_rerun()
    
    with col2:
        if current_index < len(sections) - 1:
            if st.button("Next Section"):
                # Save responses to session state
                for key, value in responses.items():
                    st.session_state.interview_responses[key] = value
                
                # Go to next section
                st.session_state.current_section = sections[current_index + 1]
                st.experimental_rerun()
        else:
            if st.button("Complete Interview"):
                # Save final section responses
                for key, value in responses.items():
                    st.session_state.interview_responses[key] = value
                
                # Update brand parameters
                update_brand_parameters_from_interview(st.session_state.interview_responses)
                
                # Show completion message
                st.success("Interview completed! Your brand voice parameters have been updated.")
                
                # Provide next steps
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("View Brand Voice Dashboard"):
                        st.session_state.current_page = "parameter_dashboard"
                with col2:
                    if st.button("Try Another Input Method"):
                        st.session_state.current_page = "home"
