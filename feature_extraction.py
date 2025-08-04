# feature_extraction.py
import json
from datetime import datetime

def extract_features(text, get_response_func, api_key, model):
    """
    Extract and categorize car features from unstructured text using an LLM.
    
    Args:
        text (str): Unstructured text containing car specifications
        get_response_func (function): Function to call the LLM API
        api_key (str): API key for the selected LLM provider
        model (str): Model name for the selected LLM provider
        
    Returns:
        dict: Dictionary containing categorized features and all features
    """
    # Create prompt for the LLM
    prompt = """
    Du bist ein hilfreiches System zur Extraktion von Fahrzeugmerkmalen.
    Extrahiere und kategorisiere alle Fahrzeugmerkmale aus dem folgenden Text. 
    Kategorisiere jedes Merkmal in eine der folgenden Kategorien: 
    - Motor & Getriebe & Fahrwerk & Lenkung (z.B. Motor, Sportfahrwerk, etc.)
    - Ausstattung (Sitze, Klimaanlage, etc.)
    - Pakete (z.B. Sportpaket, Komfortpaket, etc.)
    - Sicherheit (z.B. Airbags, Assistenzsysteme, etc.)
    - Audio & Kommunikation (z.B. Audio, Navigation, etc.)
    - Komfort (z.B. Sitzheizung, etc.)
    - Interieur (z.B. Materialien, etc.)
    - Exterieur (z.B. Farbe, Felgen, etc.)
    - Weiteres (alles andere, was nicht in die obigen Kategorien passt)

    Gib die Ausgabe **ausschließlich als gültiges JSON-Objekt** mit folgender Struktur zurück:
    {
        "motor_getriebe_fahrwerk_lenkung": ["merkmal1", "merkmal2", ...],
        "ausstattung": ["merkmal1", "merkmal2", ...],
        "pakete": ["merkmal1", "merkmal2", ...],
        "sicherheit": ["merkmal1", "merkmal2", ...],
        "audio_kommunikation": ["merkmal1", "merkmal2", ...],
        "komfort": ["merkmal1", "merkmal2", ...],
        "interieur": ["merkmal1", "merkmal2", ...],
        "exterieur": ["merkmal1", "merkmal2", ...],
        "weiteres": ["merkmal1", "merkmal2", ...]
    }

    Stelle sicher, dass ALLE im Text erwähnten Merkmale enthalten sind und innerhalb jeder Kategorie alphabetisch sortiert werden.

    Text:
    """

    
    # Get response from LLM
    response = get_response_func(prompt + text, False, api_key, model)
    
    try:
        # Parse JSON response
        categorized_features = json.loads(response)
        
        # Ensure all categories exist
        for category in ["motor_getriebe_fahrwerk_lenkung", "ausstattung", "pakete", "sicherheit", 
                         "audio_kommunikation", "komfort", "interieur", "exterieur", "weiteres"]:
            if category not in categorized_features:
                categorized_features[category] = []
            
            # Sort features alphabetically within each category
            categorized_features[category] = sorted(categorized_features[category])
        
        # Create a list of all features
        all_features = []
        for category in categorized_features.values():
            all_features.extend(category)
        all_features.sort()
        
        return {
            "categorized_features": categorized_features,
            "all_features": all_features
        }
    except json.JSONDecodeError:
        # Handle case where LLM doesn't return valid JSON
        return {
            "categorized_features": {
                "motor_getriebe_fahrwerk_lenkung": [],
                "ausstattung": [],
                "pakete": [],
                "sicherheit": [],
                "audio_kommunikation": [],
                "komfort": [],
                "interieur": [],
                "exterieur": [],
                "weiteres": []
            },
            "all_features": []
        }

def verify_features(text, extracted_features):
    """
    Verify that all features in the text are included in the extracted features.
    
    Args:
        text (str): Original text
        extracted_features (list): List of all extracted features
        
    Returns:
        tuple: (bool, list) - (is_complete, missing_features)
    """
    # Simple verification: check if each line in the text is represented in the extracted features
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    potential_features = []
    
    for line in lines:
        # Skip headers or non-feature lines
        if line.endswith(':') or len(line) < 3:
            continue
        
        # Split by commas if multiple features per line
        features = [f.strip() for f in line.split(',')]
        potential_features.extend(features)
    
    # Check if each potential feature is represented in the extracted features
    missing_features = []
    for feature in potential_features:
        found = False
        for extracted in extracted_features:
            if feature.lower() in extracted.lower() or extracted.lower() in feature.lower():
                found = True
                break
        
        if not found:
            missing_features.append(feature)
    
    return len(missing_features) == 0, missing_features