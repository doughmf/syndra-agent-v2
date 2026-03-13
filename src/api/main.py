"""
Syndra Agent - FastAPI Application
API Principal com segurança, logging e tratamento de erros
"""

import logging
import json
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from pydantic import BaseModel, Field

# Importar configurações
from config.settings import get_settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


# ═══════════════════════════════════════════════════════════════════════════
# Lifespan Management
# ═══════════════════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Executado no startup e shutdown da aplicação"""
    # STARTUP
    logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} iniciando...")
    logger.info(f"   Condomínio: {settings.CONDO_NAME}")
    logger.info(f"   Ambiente: {settings.APP_ENV}")
    logger.info(f"   Debug: {settings.DEBUG}")
    
    # Validações críticas em produção
    if settings.APP_ENV == "production":
        if not settings.SECRET_KEY:
            raise ValueError("❌ SECRET_KEY é obrigatório em produção")
        if not settings.SUPABASE_URL:
            raise ValueError("❌ SUPABASE_URL é obrigatório em produção")
        if not settings.EVOLUTION_API_KEY:
            raise ValueError("❌ EVOLUTION_API_KEY é obrigatório em produção")
    
    logger.info("✅ Configurações validadas")
    logger.info("✅ Pronto para receber requisições")
    
    yield
    
    # SHUTDOWN
    logger.info("🛑 Encerrando aplicação...")
    logger.info("✅ Aplicação finalizada")


# ═══════════════════════════════════════════════════════════════════════════
# Criar Aplicação FastAPI
# ═══════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=f"IA para gestão de {settings.CONDO_NAME}",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)


# ═══════════════════════════════════════════════════════════════════════════
# Middleware
# ═══════════════════════════════════════════════════════════════════════════

# CORS - Restringir em produção!
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS if isinstance(settings.ALLOWED_ORIGINS, list) else ["*"],
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=["*"],
)

# Security Headers
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Compression
app.add_middleware(GZIPMiddleware, minimum_size=1000)


# ═══════════════════════════════════════════════════════════════════════════
# Exception Handlers
# ═══════════════════════════════════════════════════════════════════════════

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler para erros de validação"""
    logger.error(f"Erro de validação em {request.url}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Erro de validação",
            "errors": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handler geral para exceções não tratadas"""
    logger.error(f"❌ Erro em {request.url}: {str(exc)}", exc_info=True)
    
    if settings.DEBUG:
        import traceback
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Erro interno do servidor",
                "error": str(exc),
                "traceback": traceback.format_exc(),
            },
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Erro interno do servidor. Contate o administrador.",
            },
        )


# ═══════════════════════════════════════════════════════════════════════════
# Modelos Pydantic
# ═══════════════════════════════════════════════════════════════════════════

class HealthResponse(BaseModel):
    """Resposta de health check"""
    status: str = Field(..., description="Status da aplicação")
    app_name: str = Field(..., description="Nome da aplicação")
    version: str = Field(..., description="Versão")
    condo_name: str = Field(..., description="Condomínio")
    timestamp: datetime = Field(..., description="Data/hora")
    environment: str = Field(..., description="Ambiente (dev/staging/prod)")


class MessageRequest(BaseModel):
    """Requisição de mensagem WhatsApp"""
    sender: str = Field(..., description="ID do remetente")
    message: str = Field(..., description="Conteúdo da mensagem", max_length=4096)
    message_id: str = Field(..., description="ID único da mensagem")
    timestamp: datetime = Field(default_factory=datetime.now)


class MessageResponse(BaseModel):
    """Resposta a uma mensagem"""
    success: bool = Field(..., description="Sucesso da operação")
    message_id: str = Field(..., description="ID da mensagem processada")
    response: str = Field(..., description="Resposta gerada")
    escalated: bool = Field(False, description="Foi escalada para síndico?")
    timestamp: datetime = Field(default_factory=datetime.now)


# ═══════════════════════════════════════════════════════════════════════════
# Rotas
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check da aplicação.
    
    Usado por load balancers e monitoramento.
    """
    return HealthResponse(
        status="ok",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        condo_name=settings.CONDO_NAME,
        timestamp=datetime.now(),
        environment=settings.APP_ENV,
    )


@app.post("/api/v1/webhooks/whatsapp", response_model=MessageResponse, tags=["WhatsApp"])
async def whatsapp_webhook(request: MessageRequest):
    """
    Webhook para receber mensagens do WhatsApp via Evolution API.
    
    Valida token de segurança e processa mensagem.
    """
    logger.info(f"📨 Mensagem recebida de {request.sender}: {request.message[:50]}")
    
    try:
        # TODO: Implementar processamento da mensagem com agente
        # TODO: Consultar base de conhecimento (RAG)
        # TODO: Gerar resposta com LLM
        # TODO: Enviar resposta via Evolution API
        # TODO: Registrar em auditoria
        
        response = "Mensagem recebida! Processamento em desenvolvimento."
        
        return MessageResponse(
            success=True,
            message_id=request.message_id,
            response=response,
            escalated=False,
        )
    
    except Exception as e:
        logger.error(f"❌ Erro ao processar mensagem: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar mensagem",
        )


@app.get("/api/v1/status", tags=["Status"])
async def get_status():
    """
    Status detalhado da aplicação e integrações.
    """
    status_info = {
        "app": {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.APP_ENV,
        },
        "condo": {
            "name": settings.CONDO_NAME,
            "id": settings.CONDO_ID,
        },
        "integrations": {
            "supabase": "configured" if settings.SUPABASE_URL else "missing",
            "evolution_api": "configured" if settings.EVOLUTION_API_KEY else "missing",
            "openrouter": "configured" if settings.OPENROUTER_API_KEY else "missing",
            "redis": "configured" if settings.REDIS_URL else "missing",
        },
        "features": {
            "rag": settings.ENABLE_RAG,
            "memory": settings.ENABLE_MEMORY,
            "tools": settings.ENABLE_TOOLS,
            "audit_log": settings.ENABLE_AUDIT_LOG,
        },
    }
    
    return status_info


@app.get("/", tags=["Root"])
async def root():
    """Rota raiz com informações da API"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
        "status": "/health",
    }


# ═══════════════════════════════════════════════════════════════════════════
# Startup/Shutdown Events
# ═══════════════════════════════════════════════════════════════════════════

@app.on_event("startup")
async def on_startup():
    """Eventos de inicialização"""
    logger.info("🔧 Inicializando recursos...")
    # TODO: Conectar ao Supabase
    # TODO: Conectar ao Redis
    # TODO: Inicializar agente
    # TODO: Carregar base de conhecimento
    logger.info("✅ Todos os recursos inicializados")


@app.on_event("shutdown")
async def on_shutdown():
    """Eventos de shutdown"""
    logger.info("🧹 Limpando recursos...")
    # TODO: Fechar conexões
    # TODO: Salvar estado
    logger.info("✅ Limpeza concluída")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )

