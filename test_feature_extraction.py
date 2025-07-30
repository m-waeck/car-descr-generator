# test_feature_extraction.py
import os
import json
from feature_extraction import extract_features, verify_features
from openai_api import get_response
import streamlit as st

def test_with_sample_data():
    """Test feature extraction with sample data"""
    print("Testing feature extraction with sample data...")
    
    # Load API key from streamlit secrets
    # Note: For testing outside of streamlit, you'll need to set this manually
    try:
        API_KEY = st.secrets['openai']['key']
    except:
        API_KEY = os.environ.get('OPENAI_API_KEY')
        if not API_KEY:
            print("Error: OPENAI_API_KEY not found. Please set it as an environment variable.")
            return
    
    # Load sample data
    sample_path = "sample_data/raw/BMW_x1_25i.txt"
    with open(sample_path, 'r', encoding='utf-8') as f:
        sample_text = f.read()
    
    print(f"Loaded sample data from {sample_path}")
    print(f"Sample text length: {len(sample_text)} characters")
    
    # Extract features
    print("Extracting features...")
    features = extract_features(sample_text, get_response, API_KEY, "gpt-3.5-turbo")
    
    # Verify extraction
    print("Verifying extraction...")
    is_complete, missing_features = verify_features(sample_text, features["all_features"])
    
    if not is_complete:
        print(f"Warning: Some features may have been missed: {', '.join(missing_features)}")
    else:
        print("All features were successfully extracted!")
    
    # Print categorized features
    print("\nCategorized features:")
    for category, features_list in features["categorized_features"].items():
        if features_list:
            print(f"\n{category.replace('_', ' ').title()}:")
            for feature in sorted(features_list):
                print(f"- {feature}")
    
    # Save results to file for comparison
    output_path = "sample_data/test_output.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(features, f, ensure_ascii=False, indent=2)
    
    print(f"\nResults saved to {output_path}")
    
    # Compare with expected output
    expected_path = "sample_data/categorized/BMW_x1_25i.json"
    try:
        with open(expected_path, 'r', encoding='utf-8') as f:
            expected = json.load(f)
        
        print(f"\nComparing with expected output from {expected_path}:")
        
        # Compare selected features
        expected_features = set(expected.get("selected_features", []))
        actual_features = set(features["all_features"])
        
        common_features = expected_features.intersection(actual_features)
        missing_from_actual = expected_features - actual_features
        extra_in_actual = actual_features - expected_features
        
        print(f"Common features: {len(common_features)}")
        print(f"Features in expected but not in actual: {len(missing_from_actual)}")
        if missing_from_actual:
            print(f"  {', '.join(missing_from_actual)}")
        
        print(f"Features in actual but not in expected: {len(extra_in_actual)}")
        if extra_in_actual and len(extra_in_actual) < 10:
            print(f"  {', '.join(extra_in_actual)}")
        
    except Exception as e:
        print(f"Error comparing with expected output: {e}")

if __name__ == "__main__":
    test_with_sample_data()