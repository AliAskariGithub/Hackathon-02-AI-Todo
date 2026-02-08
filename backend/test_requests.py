"""
Test script using synchronous requests library.
"""
import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("GROQ_MODEL", "meta-llama/llama-3.2-3b-instruct:free")

print(f"Testing OpenRouter API with requests library...")
print(f"API Key: {api_key[:20]}..." if api_key else "API Key: NOT FOUND")
print(f"Model: {model}")
print()

try:
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8001",
            "X-Title": "AI Todo App"
        },
        json={
            "model": model,
            "messages": [
                {"role": "user", "content": "Say hello in one sentence"}
            ],
            "temperature": 0.7,
            "max_tokens": 100
        },
        timeout=30.0
    )
    
    print(f"Response Status: {response.status_code}")
    print()
    
    if response.status_code == 200:
        result = response.json()
        print("SUCCESS! Response:")
        print(result)
        print()
        print("Assistant message:")
        print(result["choices"][0]["message"]["content"])
    else:
        print(f"ERROR! Status {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"EXCEPTION: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
