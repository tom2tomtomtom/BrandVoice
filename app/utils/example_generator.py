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
