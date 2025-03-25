import google.generativeai as genai
import os

genai.configure(api_key= os.getenv("GEMINI_API_KEY"))

for model in genai.list_models():
    print(f"Model: {model.name}")
    print(f"  Description: {model.description}")
    print(f"  Supported generation methods: {model.supported_generation_methods}")
    print()