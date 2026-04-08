"""Chat service for Saulo v2."""
import uuid
import json
from datetime import datetime
from typing import Optional, Callable, Dict, Any

from ollama.client import OllamaClient
from medical.searcher import MedicalSearcher
from medical.formatter import MedicalFormatter
from openclaw.bridge import OpenClawBridge


class ChatService:
    """Service for processing chat messages."""
    
    def __init__(self):
        self.ollama = OllamaClient()
        self.medical_searcher = MedicalSearcher()
        self.medical_formatter = MedicalFormatter()
        self.openclaw = OpenClawBridge()
        
        # In-memory storage (replace with DB in production)
        self.conversations: Dict[str, Dict] = {}
        self.messages: Dict[str, list] = {}
    
    def _detect_intent(self, content: str) -> str:
        """Detect user intent from message."""
        content_lower = content.lower()
        
        # Check for admin commands
        if content_lower.startswith("@langosta") or content_lower.startswith("/admin"):
            return "admin"
        
        # Check for medical queries
        medical_keywords = [
            "estudio", "evidencia", "tratamiento", "fármaco", "medicamento",
            "meta-análisis", "rct", "ensayo clínico", "mortalidad",
            "odds ratio", "riesgo relativo", "intervalo de confianza",
            "pubmed", "literatura médica", "guía clínica", "recomendación",
            "sepsis", "shock", "insuficiencia", "falla", "síndrome",
            "diagnóstico", "pronóstico", "terapia", "intervención"
        ]
        
        if any(kw in content_lower for kw in medical_keywords):
            return "medical"
        
        # Check for code
        code_keywords = ["código", "python", "javascript", "programar", "bug", "error", "función", "class", "import"]
        if any(kw in content_lower for kw in code_keywords):
            return "code"
        
        return "general"
    
    async def process_message(
        self,
        user_id: str,
        content: str,
        model: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a message and return response."""
        
        # Create conversation if needed
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            self.conversations[conversation_id] = {
                "id": conversation_id,
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "title": content[:50] + "..." if len(content) > 50 else content
            }
            self.messages[conversation_id] = []
        
        # Store user message
        self.messages[conversation_id].append({
            "role": "user",
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Detect intent
        intent = self._detect_intent(content)
        
        # Process based on intent
        if intent == "admin":
            response_text = await self._handle_admin_request(content, user_id)
        elif intent == "medical":
            response_text = await self._handle_medical_query(content)
        elif intent == "code":
            response_text = await self._handle_code_query(content, model)
        else:
            response_text = await self._handle_general_query(content, model)
        
        # Store assistant message
        self.messages[conversation_id].append({
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "conversation_id": conversation_id,
            "text": response_text,
            "intent": intent,
            "model_used": model or "auto"
        }
    
    async def process_message_stream(
        self,
        user_id: str,
        content: str,
        model: Optional[str] = None,
        conversation_id: Optional[str] = None,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """Process a message with streaming updates."""
        
        if progress_callback:
            await progress_callback("Analizando tu consulta...")
        
        result = await self.process_message(user_id, content, model, conversation_id)
        return result
    
    async def _handle_admin_request(self, content: str, user_id: str) -> str:
        """Handle admin request via OpenClaw."""
        # Remove command prefix
        clean_content = content
        for prefix in ["@langosta", "/admin"]:
            if content.lower().startswith(prefix):
                clean_content = content[len(prefix):].strip()
                break
        
        return await self.openclaw.send_request(clean_content, user_id)
    
    async def _handle_medical_query(self, content: str) -> str:
        """Handle medical research query."""
        # Search for medical evidence
        search_results = await self.medical_searcher.search(content)
        
        # Format in Langosta style
        formatted = await self.medical_formatter.format_summary(search_results)
        
        return formatted
    
    async def _handle_code_query(self, content: str, model: Optional[str]) -> str:
        """Handle coding query."""
        # Use code-optimized model
        code_model = model or "qwen2.5-coder:7b"
        return await self.ollama.generate(content, model=code_model)
    
    async def _handle_general_query(self, content: str, model: Optional[str]) -> str:
        """Handle general query."""
        general_model = model or "qwen2.5:7b"
        return await self.ollama.generate(content, model=general_model)
    
    async def get_conversation_history(self, user_id: str, conversation_id: str) -> list:
        """Get conversation history."""
        return self.messages.get(conversation_id, [])
    
    async def create_conversation(self, user_id: str) -> str:
        """Create new conversation."""
        conversation_id = str(uuid.uuid4())
        self.conversations[conversation_id] = {
            "id": conversation_id,
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "title": "Nueva conversación"
        }
        self.messages[conversation_id] = []
        return conversation_id
    
    async def list_conversations(self, user_id: str) -> list:
        """List user's conversations."""
        return [
            conv for conv in self.conversations.values()
            if conv["user_id"] == user_id
        ]