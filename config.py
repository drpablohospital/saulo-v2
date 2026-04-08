"""Configuration for Saulo v2."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    app_name: str = "Saulo v2"
    debug: bool = True
    
    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    
    # Auth
    secret_key: str = "saulo-secret-key-change-in-production"
    
    class Config:
        env_file = ".env"


settings = Settings()