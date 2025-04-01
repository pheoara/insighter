import os
from openai import OpenAI

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def get_client():
    """Get the OpenAI client instance"""
    return client