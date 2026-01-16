import os
from typing import Optional
from functools import lru_cache
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings:
    """Application configuration loaded from environment variables."""
    
    # LLM Provider Configuration (ollama, gemini, or ondemand)
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ondemand")
    
    # Ollama Configuration (free, local)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "mistral")
    
    # Gemini Configuration (optional, for paid tier)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    
    # On-Demand Platform Configuration (supports GPT, Gita, Audio, Vision)
    ON_DEMAND_API_KEY: str = os.getenv("ON_DEMAND_API_KEY", "")
    ON_DEMAND_BASE_URL: str = os.getenv("ON_DEMAND_BASE_URL", "https://api.on-demand.io")
    ON_DEMAND_ENDPOINT_ID: str = os.getenv("ON_DEMAND_ENDPOINT_ID", "predefined-openai-gpt4o")
    
    # On-Demand Agent Configuration
    ON_DEMAND_GPT_AGENT: str = os.getenv("ON_DEMAND_GPT_AGENT", "predefined-openai-gpt4o")
    ON_DEMAND_GITA_AGENT: str = os.getenv("ON_DEMAND_GITA_AGENT", "gita-guide")
    ON_DEMAND_AUDIO_AGENT: str = os.getenv("ON_DEMAND_AUDIO_AGENT", "audio-transcription")
    ON_DEMAND_VISION_AGENT: str = os.getenv("ON_DEMAND_VISION_AGENT", "vision-analyzer")
    ON_DEMAND_MEMORY_AGENT: str = os.getenv("ON_DEMAND_MEMORY_AGENT", "predefined-openai-gpt4o")
    
    # Long-Term Memory Configuration
    ENABLE_LONG_TERM_MEMORY: bool = os.getenv("ENABLE_LONG_TERM_MEMORY", "true").lower() == "true"
    LONG_TERM_MEMORY_TYPE: str = os.getenv("LONG_TERM_MEMORY_TYPE", "ondemand")
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Frontend URL for CORS
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Debate Configuration
    CONFLICT_THRESHOLD: float = float(os.getenv("CONFLICT_THRESHOLD", "0.2"))
    MAX_DEBATE_ROUNDS: int = int(os.getenv("MAX_DEBATE_ROUNDS", "2"))
    
    # LLM Configuration
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "1500"))
    
    def __init__(self):
        if self.LLM_PROVIDER == "gemini" and not self.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable not set for Gemini provider")
        if self.LLM_PROVIDER == "ondemand" and not self.ON_DEMAND_API_KEY:
            raise ValueError("ON_DEMAND_API_KEY environment variable not set for On-Demand provider")

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Singleton settings instance."""
    return Settings()