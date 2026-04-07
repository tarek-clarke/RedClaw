import base64
from typing import List, Dict, Any, Optional
from openai import OpenAI
from config import LM_STUDIO_HOST, LM_STUDIO_API_KEY, DEFAULT_MODEL_VISION

class LLMManager:
    """Wrapper for LM Studio's OpenAI-compatible API."""
    
    def __init__(self, api_key: str = LM_STUDIO_API_KEY, base_url: str = LM_STUDIO_HOST):
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def encode_image(self, image_path: str) -> str:
        """Encode image to base64 for multimodal input."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str = DEFAULT_MODEL_VISION,
        max_tokens: int = 1000,
        temperature: float = 0.0
    ) -> str:
        """Standard chat completion (text-only)."""
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content

    def multimodal_completion(
        self, 
        prompt: str, 
        image_path: str, 
        model: str = DEFAULT_MODEL_VISION,
        max_tokens: int = 1000
    ) -> str:
        """Multimodal completion (text + image)."""
        base64_image = self.encode_image(image_path)
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
        
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
