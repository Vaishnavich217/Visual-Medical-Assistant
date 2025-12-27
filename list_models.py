import google.generativeai as genai
from google_api_key import google_api_key  # or load from .env

# Configure the API key
genai.configure(api_key=google_api_key)

# List available models
models = genai.list_models()

# Print model names and supported methods
for model in models:
    print("Model Name:", model.name)
    print("Supported Methods:", model.supported_generation_methods)
    print("---")
