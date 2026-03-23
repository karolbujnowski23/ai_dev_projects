import os
import base64
import mimetypes
from pathlib import Path
import requests
from dotenv import load_dotenv

class GeminiConnector:
    """
    A connector class to interact with the Google Gemini API for vision analysis.
    """
    def __init__(self, model: str = "gemini-3-pro-image-preview"):
        """
        Initializes the connector, loads the API key from the environment,
        and sets the model for vision analysis.

        Args:
            model (str): The Gemini model to use. Defaults to "gemini-2.5-flash"
                         as it's suitable for multimodal tasks.
        """
        # Construct the path to the .config file relative to the script location
        # Script is in 'zadania/sandbox', config is in 'zadania'
        config_path = ".\zadania\.config"
        
        # Load environment variables from the specified .config file
        load_dotenv(dotenv_path=config_path)
        
        self.api_key = os.getenv("GEMINI_LLM_APIKEY")
        if not self.api_key:
            raise ValueError("GEMINI_LLM_APIKEY not found in the .config file.")
            
        self.model = model
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    def _encode_image(self, image_path: str) -> str:
        """
        Encodes the image at the given path to a base64 string.

        Args:
            image_path (str): The path to the image file.

        Returns:
            str: The base64 encoded string representation of the image.
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def _get_mime_type(self, image_path: str) -> str:
        """
        Determines the MIME type of the image file.

        Args:
            image_path (str): The path to the image file.

        Returns:
            str: The MIME type of the image.
        """
        mime_type, _ = mimetypes.guess_type(image_path)
        if mime_type is None:
            raise ValueError(f"Could not determine MIME type for {image_path}")
        return mime_type

    def analyze_image(self, prompt: str, image_path: str = None, image_url: str = None) -> str:
        """
        Sends an image (either local file or URL) and a text prompt to the Gemini API for analysis.

        Args:
            prompt (str): The text prompt to accompany the image.
            image_path (str, optional): The local path to the image file. Defaults to None.
            image_url (str, optional): The URL of the image file. Defaults to None.

        Returns:
            str: The text response from the model.
        """
        if not (image_path or image_url):
            raise ValueError("Either image_path or image_url must be provided.")
        if image_path and image_url:
            raise ValueError("Only one of image_path or image_url can be provided.")

        image_part = {}
        if image_path:
            if not Path(image_path).is_file():
                return f"Error: Image file not found at '{image_path}'"
            encoded_image = self._encode_image(image_path)
            mime_type = self._get_mime_type(image_path)
            image_part = {
                "inline_data": {
                    "mime_type": mime_type,
                    "data": encoded_image
                }
            }
        elif image_url:
            # Assuming the API can infer MIME type from URL, or it's implicitly image/jpeg or image/png
            # For specific requirements, a mime_type could be added here if known.
            # The documentation mentions "video URI", implying direct URI use for media.
            image_part = {
                "file_data": { # This is an educated guess based on the documentation
                    "file_uri": image_url,
                    "mime_type": mimetypes.guess_type(image_url)[0] or "application/octet-stream" # Attempt to guess, fallback to generic
                }
            }

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }

        payload = {
            "contents": [{
                "parts": [
                    image_part,
                    {
                        "text": prompt
                    },
                ]
            }]
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()  # Raises an exception for bad status codes (4xx or 5xx)
            
            response_json = response.json()
            
            # Extract the text from the response based on the documentation structure
            if "candidates" in response_json and len(response_json["candidates"]) > 0:
                content = response_json["candidates"][0].get("content", {})
                if "parts" in content and len(content["parts"]) > 0:
                    return content["parts"][0].get("text", "No text found in response part.")
            return "Error: Could not parse the response from the API."

        except requests.exceptions.RequestException as e:
            return f"An error occurred: {e}"
        except (KeyError, IndexError) as e:
            return f"Error parsing API response: {e}. Full response: {response.text}"


if __name__ == "__main__":
    try:
        # --- USAGE EXAMPLE ---
        
        # 1. Initialize the connector
        gemini = GeminiConnector()

        # 2. Define your prompt and either a local image path or an image URL
        # !!! IMPORTANT !!! 
        # Choose ONE of the following: image_to_analyze (local) OR image_url_to_analyze (remote)
        # For local image: 
        # image_to_analyze = "path/to/your/image.jpg" 
        # For remote image:
        klucz = os.getenv('APIKEY') # Replace with your actual key for the URL
        image_url_to_analyze = f"https://hub.ag3nts.org/data/{klucz}/drone.png" # Example URL for the drone map
        
        text_prompt = "Analyze this image and tell me how many rows and columns it has. The image rows and columns are separated by red web of vertical and horizontal lines.  Then, identify the sector (column, row) that contains the dam with the blue water. Use 1-based indexing for columns and rows, starting from the top-left corner. format: (x,y) -no spaces. try to assess the altitude of the point the picture was made. format: (100m) - no spaces!" # Using the problem's specific prompt

        # 3. Call the analysis method with either image_path or image_url
        print(f"Analyzing with prompt: {text_prompt}")
        
        # Uncomment the line below if you are using a local image file
        # result = gemini.analyze_image(prompt=text_prompt, image_path=image_to_analyze)

        # Uncomment the line below if you are using an image URL
        result = gemini.analyze_image(prompt=text_prompt, image_url=image_url_to_analyze)
        
        # 4. Print the result
        print("--- Gemini API Response ---")
        print(result)

    except ValueError as e:
        print(f"Configuration Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")