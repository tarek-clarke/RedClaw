import base64
from typing import List, Dict, Any, Optional
from openai import OpenAI
from config import LM_STUDIO_HOST, LM_STUDIO_API_KEY, DEFAULT_MODEL_VISION

class LLMManager:
    """Wrapper for LM Studio's OpenAI-compatible API."""
    
    def __init__(self, api_key: str = LM_STUDIO_API_KEY, base_url: str = LM_STUDIO_HOST):
        # V5.1: Added explicit timeouts to the client itself to prevent OS-level hangs
        from httpx import Timeout
        timeout = Timeout(10.0, connect=5.0) # 10s total, 5s for connection
        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)
        print(f"[REDCLAW] AI Connection configured for {base_url}")

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
        """Standard chat completion (text-only) with graceful error handling."""
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=10 # Short timeout for local checks
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"\n[REDCLAW] ERROR: Could not connect to LM Studio at {self.client.base_url}")
            print(f"[REDCLAW] TIP: 1. Is LM Studio open? 2. Is the 'Local Server' started? 3. Is the port 1234?")
            if "10061" in str(e):
                print(f"[REDCLAW] DETAIL: The target machine actively refused the connection.")
            raise e

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
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                timeout=30 # 30s timeout for vision tasks
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[REDCLAW] Vision Brain Communication Error: {str(e)}")
            return "ESC_HUMAN(\"Vision AI timed out. Switching to manual control.\")"
