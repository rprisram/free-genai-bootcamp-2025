import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Check if PERPLEXITY_API_KEY is set
api_key = os.environ.get('PERPLEXITY_API_KEY')
if api_key:
    print(f"API key found: {api_key[:5]}...{api_key[-5:]}")
else:
    print("API key not found in environment variables")
