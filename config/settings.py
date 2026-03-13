"""
Configurações da Aplicação - Syndra Agent v2.0
Totalmente genérica e configurável via variáveis de ambiente
"""

from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache

class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # ═══════════════════════════════════════════════════════════════
    # APLICAÇÃO
    # ═══════════════════════════════════════════════════════════════
    
    APP_NAME: str = "Syndra Agent"
    APP_VERSION: str = "2.0.0"
    APP_ENV: str = "development"  # development, staging, production
    DEBUG: bool = False
    
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    
    # ═══════════════════════════════════════════════════════════════
    # CONDOMÍNIO (CONFIGURÁVEL POR CLIENTE)
    # ═══════════════════════════════════════════════════════════════
    
    # ⭐ GENÉRICO - Sem hardcoding!
    CONDO_NAME: str = "Condomínio SaaS"
    CONDO_CNPJ: str = ""
    CONDO_ADDRESS: str = ""
    CONDO_ID: str = "default"  # Para multi-tenancy
    
    # ═══════════════════════════════════════════════════════════════
    # AGENTE IA
    # ═══════════════════════════════════════════════════════════════
    
    AGENT_NAME: str = "Syndra"
    AGENT_ROLE: str = "Assistente Virtual do Condomínio"
    LLM_MODEL: str = "gpt-4-turbo-preview"  # ou claude-3-opus, etc
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 1024
    
    # OpenRouter (recomendado para suportar múltiplos modelos)
    USE_OPENROUTER: bool = True
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "openai/gpt-4-turbo-preview"
    
    # Alternativa: OpenAI direto
    OPENAI_API_KEY: str = ""
    
    # ═══════════════════════════════════════════════════════════════
    # WHATSAPP - EVOLUTION API
    # ═══════════════════════════════════════════════════════════════
    
    EVOLUTION_API_URL: str = "http://localhost:8080"
    EVOLUTION_API_KEY: str = ""
    EVOLUTION_INSTANCE: str = "syndra"
    EVOLUTION_RECONNECT: bool = True
    
    # ═══════════════════════════════════════════════════════════════
    # SUPABASE
    # ═══════════════════════════════════════════════════════════════
    
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""  # Service role (backend only)
    SUPABASE_ANON_KEY: str = ""      # Anonymous key (frontend)
    SUPABASE_ACCESS_TOKEN: str = ""
    
    # ═══════════════════════════════════════════════════════════════
    # REDIS (Cache, Sessões, Filas)
    # ═══════════════════════════════════════════════════════════════
    
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    REDIS_TIMEOUT: int = 5
    REDIS_POOL_SIZE: int = 10
    
    # ═══════════════════════════════════════════════════════════════
    # SEGURANÇA
    # ═══════════════════════════════════════════════════════════════
    
    SECRET_KEY: str = ""  # CRÍTICO: Deve ser setado no .env
    WEBHOOK_TOKEN: str = ""  # Token para validar webhooks
    
    # JWT
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]  # Restringir em produção
    ALLOWED_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE"]
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # segundos
    
    # ═══════════════════════════════════════════════════════════════
    # LOGGING & MONITORING
    # ═══════════════════════════════════════════════════════════════
    
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json ou plain
    
    # Sentry (error tracking)
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENABLED: bool = False
    
    # ═══════════════════════════════════════════════════════════════
    # RECURSOS & QUOTAS
    # ═══════════════════════════════════════════════════════════════
    
    # RAG & Embeddings
    EMBEDDINGS_MODEL: str = "text-embedding-3-small"
    VECTOR_DIMENSION: int = 1536
    MAX_CONTEXT_CHUNKS: int = 5
    
    # Limites
    MAX_MESSAGE_LENGTH: int = 4096
    MAX_CONVERSATION_HISTORY: int = 50
    
    # ═══════════════════════════════════════════════════════════════
    # FEATURES FLAGS
    # ═══════════════════════════════════════════════════════════════
    
    ENABLE_RAG: bool = True
    ENABLE_MEMORY: bool = True
    ENABLE_TOOLS: bool = True
    ENABLE_AUDIT_LOG: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"  # Permitir variáveis extras do .env


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna instância única de Settings (cached)
    Usar: from config.settings import get_settings
          settings = get_settings()
    """
    return Settings()


# Exportar para uso direto
settings = get_settings()

# Validações críticas
if settings.APP_ENV == "production":
    assert settings.SECRET_KEY, "SECRET_KEY é obrigatório em produção"
    assert settings.SUPABASE_URL, "SUPABASE_URL é obrigatório em produção"
    assert settings.EVOLUTION_API_KEY, "EVOLUTION_API_KEY é obrigatório em produção"
    assert not settings.DEBUG, "DEBUG deve ser False em produção"

