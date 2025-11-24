from openai import OpenAI, AzureOpenAI
import os

# app/services/ai_client.py
from dotenv import load_dotenv
load_dotenv()

def get_ai_client():
    provider = os.getenv("AI_PROVIDER", "openai").lower()
    if provider == "azure":
        return AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        )
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    return OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)

def get_model():
    provider = os.getenv("AI_PROVIDER", "openai").lower()
    if provider == "azure":
        return os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
    return os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")