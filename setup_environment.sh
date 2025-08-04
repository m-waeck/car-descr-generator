#!/bin/bash

# Create a new conda environment
echo "Creating conda environment 'car-descr-generator'..."
conda create -n car-descr-generator python=3.9 -y

# Activate the environment
echo "Activating environment..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate car-descr-generator

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

echo "Environment setup complete!"
echo "To activate the environment, run: conda activate car-descr-generator"
echo "To run the application, run: streamlit run app.py"