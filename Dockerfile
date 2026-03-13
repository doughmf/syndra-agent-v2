# Multi-stage build para imagem otimizada

# ═══════════════════════════════════════════════════════════════════════════
# Stage 1: Builder
# ═══════════════════════════════════════════════════════════════════════════

FROM python:3.11-slim as builder

# Labels
LABEL maintainer="Syndra Agent Development"
LABEL description="Syndra Agent - IA para Gestão Condominial"
LABEL version="2.0.0"

# Variáveis de ambiente do builder
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Instalar dependências de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# ═══════════════════════════════════════════════════════════════════════════
# Stage 2: Runtime
# ═══════════════════════════════════════════════════════════════════════════

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/root/.local/bin:$PATH \
    APP_HOME=/app

WORKDIR $APP_HOME

# Instalar apenas runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root para segurança
RUN useradd -m -u 1000 syndra && \
    mkdir -p $APP_HOME && \
    chown -R syndra:syndra $APP_HOME

# Copiar dependências instaladas do builder
COPY --from=builder /root/.local /root/.local
COPY --from=builder /root/.local/bin /usr/local/bin

# Copiar código da aplicação
COPY --chown=syndra:syndra . .

# Trocar para usuário não-root
USER syndra

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Porta da aplicação
EXPOSE 8000

# Comando de inicialização
CMD ["python", "-m", "uvicorn", "src.api.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4"]

