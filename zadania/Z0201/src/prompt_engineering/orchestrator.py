import requests
import logging

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "anthropic/claude-3.5-sonnet" # Można dostosować w zależności od potrzeb

    def get_classification(self, prompt: str) -> str:
        """Wysyła prompt do modelu LLM i zwraca klasyfikację."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0 # Wymagamy determinizmu dla klasyfikacji
        }
        
        try:
            response = requests.post(self.url, headers=headers, json=data)
            response.raise_for_status()
            content = response.json()['choices'][0]['message']['content'].strip()
            # Upewnienie się, że model zwrócił tylko etykietę (NEU lub DNG)
            if "NEU" in content: return "NEU"
            if "DNG" in content: return "DNG"
            return content
        except Exception as e:
            logger.error(f"Błąd podczas wywołania LLM: {e}")
            return ""

def update_prompt_template(feedback: str, current_prompt: str, api_key: str) -> str:
    """Agent inżynierii promptów. Poprawia prompt na podstawie błędów."""
    
    system_instruction = (
        "You are an expert Prompt Engineer. Your task is to update a prompt used for "
        "classifying items as dangerous (DNG) or neutral (NEU). You will receive the current prompt "
        "and feedback from a system showing errors it made. "
        "Update the prompt to prevent these errors in the future. "
        "Keep the prompt structured with static instructions at the top and maintain the "
        "critical override rule for reactor components. Make it concise and in English to minimize tokens. "
        "Output ONLY the new raw prompt text. Do not add explanations or formatting tags like ```."
    )
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "anthropic/claude-3.5-sonnet",
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"CURRENT PROMPT:\n{current_prompt}\n\nFEEDBACK:\n{feedback}"}
        ],
        "temperature": 0.2
    }
    
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        new_prompt = response.json()['choices'][0]['message']['content'].strip()
        return new_prompt
    except Exception as e:
        logger.error(f"Błąd podczas poprawiania promptu przez LLM: {e}")
        return current_prompt
