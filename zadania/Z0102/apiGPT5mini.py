import requests
import json
import os
from dotenv import load_dotenv


def call_openrouter_api(api_key, model, messages, site_url="", site_name=""):
    """
    Call OpenRouter API with provided parameters.
    
    Args:
        api_key: OpenRouter API key
        model: Model name (e.g., "openai/gpt-5-mini")
        messages: List of message objects
        site_url: Optional site URL for rankings
        site_name: Optional site name for rankings
    
    Returns:
        Response object from the API call
    """
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": site_url,
            "X-OpenRouter-Title": site_name,
        },
        data=json.dumps({
            "model": model,
            "messages": messages
        })
    )
    return response

def message(role, content):
    """
    Helper function to create a message object.
    
    Args:
        role: Role of the message (e.g., "system", "user", "assistant")
        content: Content of the message

    Returns:
        Message object
    """
    return {"role": role, "content": content}

# def main():
#     API_KEY = "tutaj-twój-klucz-api"  # Replace with your actual API key
#     model = "openai/gpt-5-mini" # Specify the model you want to use 
#     messages = [
#         message("system", "You are a helpful assistant."),
#         message("user", "What is the capital of France?")
#     ]

#     response = call_openrouter_api(API_KEY, model, messages)
#     print(response.json())

if __name__ == "__main__":
    # Example usage
    # main()
    load_dotenv('./zadania/Z0102/.config')
    API_KEY = os.getenv("LLM_APIKEY")
    model = "openai/gpt-5-mini" # Specify the model you want to use 
    messages = [
        message("system", "You are a helpful assistant."),
        message("user", "What is the capital of France?")
    ]
    print(API_KEY)
    response = call_openrouter_api(API_KEY, model, messages)
    print(response.json())
