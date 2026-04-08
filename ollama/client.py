"""Ollama client for Saulo v2."""
import httpx
from typing import List, Dict, Any, Optional

OLLAMA_BASE_URL = "http://localhost:11434"


class OllamaClient:
    """Client for Ollama API."""
    
    def __init__(self, base_url: str = OLLAMA_BASE_URL):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=120.0)
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models."""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            data = response.json()
            
            models = []
            for model in data.get("models", []):
                models.append({
                    "name": model.get("name"),
                    "size": model.get("size"),
                    "modified_at": model.get("modified_at")
                })
            return models
        except Exception as e:
            print(f"Error listing Ollama models: {e}")
            # Return default models if Ollama is not running
            return [
                {"name": "gpt-oss:latest", "size": 0, "modified_at": ""},
                {"name": "qwen2.5-coder:7b", "size": 0, "modified_at": ""},
                {"name": "qwen2.5:3b", "size": 0, "modified_at": ""}
            ]
    
    async def generate(
        self,
        prompt: str,
        model: str = "gpt-oss:latest",
        system: Optional[str] = None,
        context: Optional[List[Dict]] = None
    ) -> str:
        """Generate text with Ollama."""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            
            if system:
                payload["system"] = system
            
            if context:
                payload["context"] = context
            
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            
            data = response.json()
            return data.get("response", "Error: No response from model")
            
        except Exception as e:
            return f"Error conectando a Ollama: {str(e)}. ¿Está Ollama corriendo en {self.base_url}?"
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-oss:latest"
    ) -> str:
        """Chat completion with Ollama."""
        try:
            payload = {
                "model": model,
                "messages": messages,
                "stream": False
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json=payload
            )
            
            data = response.json()
            return data.get("message", {}).get("content", "Error: No response")
            
        except Exception as e:
            return f"Error en chat: {str(e)}"
    
    async def generate_stream(
        self,
        prompt: str,
        model: str = "gpt-oss:latest"
    ):
        """Generate text with streaming."""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": True
            }
            
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if "response" in data:
                                yield data["response"]
                        except:
                            pass
                            
        except Exception as e:
            yield f"Error: {str(e)}"