import os
import requests
import sys

# Configuration par défaut
API_URL = os.getenv("FREELLMAPI_URL", "http://localhost:3001/v1/chat/completions")
API_KEY = os.getenv("FREELLMAPI_KEY", "freellmapi-your-unified-key")


def chat_completion(messages, model="auto"):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": messages, "stream": False}

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Erreur lors de l'appel FreeLLMAPI : {str(e)}"


if __name__ == "__main__":
    # Lecture du prompt depuis stdin ou args
    if len(sys.argv) > 1:
        user_prompt = " ".join(sys.argv[1:])
    else:
        user_prompt = sys.stdin.read()

    messages = [{"role": "user", "content": user_prompt}]
    print(chat_completion(messages))
