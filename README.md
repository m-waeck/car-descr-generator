# Car Description Generator

A Streamlit web application that leverages MongoDB and LLMs to generate descriptive texts for specific cars and extract car features from unstructured text.

## Features

### Text Generation
- Generate descriptive texts for specific cars using different LLM providers (ChatGPT, Mistral, DeepSeek)
- Customize the description by providing car model, year, and special features
- Store generated descriptions in MongoDB

### Feature Extraction (New)
- Extract car features from unstructured text using LLMs
- Categorize features into technical specifications, performance metrics, comfort features, and safety systems
- Display features in alphabetical order within each category
- Verify that all features from the text are extracted and displayed
- Save extracted features to MongoDB, linked to car descriptions

## Setup

### Prerequisites
- Python 3.9+
- Conda
- MongoDB Atlas account
- API keys for OpenAI, Mistral, and DeepSeek (optional, depending on which LLMs you want to use)

### Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd car-descr-generator
```

2. Set up the conda environment:
```bash
chmod +x setup_environment.sh
./setup_environment.sh
```

3. Activate the environment:
```bash
conda activate car-descr-generator
```

4. Create a `.streamlit/secrets.toml` file with your API keys and MongoDB connection string:
```toml
[mongodb]
mongoURI = "your-mongodb-connection-string"

[openai]
key = "your-openai-api-key"

[mistral]
key = "your-mistral-api-key"

[deepseek]
key = "your-deepseek-api-key"
```

### Running the Application

```bash
streamlit run app.py
```

## Usage

### Text Generation
1. Select the LLM provider from the sidebar
2. Enter the car model, year, and any special features
3. Click "Generieren" to generate a description
4. The generated description will be displayed and saved to MongoDB

### Feature Extraction
1. Navigate to the "Feature Extraction" tab
2. Select the LLM provider for feature extraction
3. Paste the car specification text into the text area
4. Click "Merkmale extrahieren" to extract and categorize features
5. Review the extracted features, categorized into technical specifications, performance, comfort, and safety
6. Enter the car model and year to save the extracted features
7. Click "Extrahierte Merkmale speichern" to save the features to MongoDB

## Testing

To test the feature extraction functionality with sample data:

```bash
python test_feature_extraction.py
```

This will:
1. Load sample data from `sample_data/raw/BMW_x1_25i.txt`
2. Extract and categorize features using the selected LLM
3. Verify that all features are extracted
4. Compare the results with the expected output in `sample_data/categorized/BMW_x1_25i.json`
5. Save the results to `sample_data/test_output.json` for review

## Project Structure

- `app.py`: Main Streamlit application
- `feature_extraction.py`: Functions for extracting and categorizing car features
- `db_operations.py`: MongoDB integration for feature extraction
- `openai_api.py`, `mistral_api.py`, `deepseek_api.py`: API integrations for different LLM providers
- `setup_environment.sh`: Script to set up the conda environment
- `test_feature_extraction.py`: Script to test feature extraction with sample data
- `sample_data/`: Sample data for testing
  - `raw/`: Raw car specification texts
  - `cleaned/`: Cleaned and alphabetically sorted features
  - `categorized/`: Categorized features in JSON format

## Data Structure

### Cars Collection
```json
{
  "_id": "ObjectId",
  "date": "string",
  "time": "string",
  "model": "string",
  "year": "number",
  "specials": "string",
  "descr": "string",
  "ai_model": "string",
  "features_id": "ObjectId"  // Reference to Features Collection
}
```

### Features Collection (New)
```json
{
  "_id": "ObjectId",
  "car_id": "ObjectId",  // Reference to Cars Collection
  "raw_text": "string",  // Original pasted text
  "extraction_date": "string",
  "extraction_time": "string",
  "ai_model": "string",  // LLM used for extraction
  "categorized_features": {
    "technical_specs": ["feature1", "feature2", ...],
    "performance": ["feature1", "feature2", ...],
    "comfort": ["feature1", "feature2", ...],
    "safety": ["feature1", "feature2", ...]
  },
  "all_features": ["feature1", "feature2", ...]  // All features in alphabetical order
}
