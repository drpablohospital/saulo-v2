"""OpenClaw bridge for Saulo v2."""
import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class OpenClawBridge:
    """Bridge to communicate with Langosta via file-based protocol."""
    
    def __init__(self):
        self.workspace = Path("C:/Users/xiute/.openclaw/workspace/langosta")
        self.inbox = self.workspace / "bridge" / "inbox"
        self.outbox = self.workspace / "bridge" / "outbox"
        
        # Ensure directories exist
        self.inbox.mkdir(parents=True, exist_ok=True)
        self.outbox.mkdir(parents=True, exist_ok=True)
    
    async def send_request(
        self,
        content: str,
        user_id: str,
        request_type: str = "query"
    ) -> str:
        """Send request to Langosta via file bridge."""
        
        request_id = f"saulo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(content) % 10000}"
        
        request_data = {
            "id": request_id,
            "source": "saulo",
            "user_id": user_id,
            "type": request_type,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        # Write request
        request_file = self.inbox / f"{request_id}.json"
        try:
            with open(request_file, 'w', encoding='utf-8') as f:
                json.dump(request_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"❌ Error enviando a Langosta: {str(e)}"
        
        # Wait for response (with timeout)
        response_file = self.outbox / f"{request_id}_response.json"
        timeout = 60  # seconds
        check_interval = 0.5
        
        elapsed = 0
        while elapsed < timeout:
            if response_file.exists():
                try:
                    with open(response_file, 'r', encoding='utf-8') as f:
                        response_data = json.load(f)
                    
                    # Clean up files
                    request_file.unlink(missing_ok=True)
                    response_file.unlink(missing_ok=True)
                    
                    return response_data.get("response", "⚠️ Respuesta vacía de Langosta")
                    
                except Exception as e:
                    return f"⚠️ Error leyendo respuesta: {str(e)}"
            
            await asyncio.sleep(check_interval)
            elapsed += check_interval
        
        # Timeout
        request_file.unlink(missing_ok=True)
        return "⏱️ Tiempo de espera agotado. Langosta no respondió. Intenta por WhatsApp directamente."
    
    async def check_langosta_med_summaries(self) -> Dict[str, Any]:
        """Check for latest Langosta-Med summaries."""
        daily_path = self.workspace / "agents" / "med-pub-monitor" / "data" / "daily"
        
        if not daily_path.exists():
            return {
                "status": "no_data",
                "message": "No hay datos de Langosta-Med"
            }
        
        # Get most recent search file
        files = sorted(
            [f for f in daily_path.glob("search_*.json")],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if not files:
            return {
                "status": "no_files",
                "message": "No hay archivos de búsqueda"
            }
        
        try:
            with open(files[0], 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return {
                "status": "success",
                "timestamp": data.get("timestamp", ""),
                "query": data.get("query", ""),
                "articles_count": len(data.get("articles", [])),
                "articles": data.get("articles", [])[:5]  # Top 5
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }