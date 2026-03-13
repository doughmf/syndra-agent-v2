# 🏠 Syndra Agent v2.0 - IA para Gestão Condominial

> Agente de IA inteligente para WhatsApp com memória persistente, RAG (Retrieval Augmented Generation) e integração completa com Supabase.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Beta-orange)

## 📚 Índice

- [Características](#características)
- [Arquitetura](#arquitetura)
- [Início Rápido](#início-rápido)
- [Instalação Completa](#instalação-completa)
- [Configuração](#configuração)
- [Uso](#uso)
- [API](#api)
- [Segurança](#segurança)
- [Testes](#testes)
- [Troubleshooting](#troubleshooting)
- [Contribuindo](#contribuindo)

## ✨ Características

- ✅ **SaaS Multi-Tenant**: Totalmente genérico, sem hardcoding de cliente
- ✅ **WhatsApp Native**: Integração via Evolution API
- ✅ **RAG (Retrieval Augmented Generation)**: Base de conhecimento inteligente com pgvector
- ✅ **Memória Persistente**: Histórico de conversas no Supabase
- ✅ **LLM Flexível**: Suporte a OpenRouter, OpenAI, Claude, etc
- ✅ **API REST**: FastAPI com documentação automática (Swagger)
- ✅ **Segurança**: Rate limiting, validação de webhook, logs de auditoria
- ✅ **Escalável**: Docker, Redis, Kubernetes-ready
- ✅ **Testado**: 80%+ de cobertura com pytest
- ✅ **CI/CD**: GitHub Actions com linting, testes e build automático

## 🏗️ Arquitetura

```
┌─────────────┐
│ WhatsApp    │ ← Usuário
└──────┬──────┘
       │
       ▼
┌──────────────────────────┐
│  Evolution API           │ ← Webhook para receber mensagens
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│  FastAPI (Port 8000)             │
├──────────────────────────────────┤
│  - Syndra Agent (LangChain)      │
│  - Message Processing            │
│  - WebHook Handler               │
│  - Rate Limiting                 │
└──────┬──────────────────┬────────┘
       │                  │
       ▼                  ▼
   ┌────────┐        ┌──────────────┐
   │ Redis  │        │  Supabase    │
   │(Cache) │        │ PostgreSQL   │
   └────────┘        │ pgvector RAG │
                     └──────────────┘
```

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.9+
- Docker & Docker Compose (para deployment)
- Conta Supabase
- Conta OpenRouter ou OpenAI
- Conta Evolution API (para WhatsApp)

### 1. Clone e Configure (2 minutos)

```bash
git clone https://github.com/seu-usuario/syndra-agent.git
cd syndra-agent

# Copiar template de configuração
cp config/.env.example .env
```

### 2. Configure Variáveis (3 minutos)

```bash
# Editar .env com suas credenciais
nano .env
```

**Mínimo necessário:**

```env
SECRET_KEY=gere-uma-chave-aleatoria-forte-aqui
CONDO_NAME="Seu Condomínio"
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_SERVICE_KEY=sua-chave-aqui
OPENROUTER_API_KEY=sk-or-v1-sua-chave
EVOLUTION_API_KEY=sua-chave-evolution
```

### 3. Instale Dependências (2 minutos)

```bash
python -m venv venv
source venv/bin/activate  # ou: venv\Scripts\activate (Windows)
pip install -r requirements.txt
```

### 4. Rode Localmente (1 minuto)

```bash
python -m uvicorn src.api.main:app --reload
```

Acesse: http://localhost:8000/docs (Swagger)

### 5. Docker (1 minuto)

```bash
docker-compose up -d
```

## 📖 Instalação Completa

### Supabase - Configuração do Banco

1. **Criar Projeto**
   - Acesse https://supabase.com
   - Clique em "New Project"
   - Copie `SUPABASE_URL` e `SERVICE_ROLE_KEY`

2. **Rodar Migrations**

```bash
python scripts/setup_supabase.py
```

Este script cria:
- Tabela `chats` - Histórico de conversas
- Tabela `residentes` - Dados dos moradores
- Tabela `documentos` - Base de conhecimento para RAG
- Índice pgvector para embeddings

### Redis - Para Cache e Sessões

**Local:**
```bash
docker run -d -p 6379:6379 redis:7
```

**Cloud (recomendado para produção):**
- [Upstash](https://upstash.com) - Redis serverless
- [AWS ElastiCache](https://aws.amazon.com/elasticache/)

### Evolution API - Para WhatsApp

**Opção 1: Cloud (Recomendado)**
- Registre em https://evolution-api.com
- Configure webhook para: `https://seu-dominio/api/v1/webhooks/whatsapp`

**Opção 2: Self-Hosted**
```bash
docker run -d -p 8080:8080 atendimento/evolution-api:latest
```

## 🔧 Configuração

### Variáveis de Ambiente Importantes

```env
# 🔒 Segurança (CRÍTICO)
SECRET_KEY=gere-aleatório-python-c-import-secrets
WEBHOOK_TOKEN=outro-token-aleatorio

# 🏢 Condomínio (Customizável)
CONDO_NAME="Seu Condomínio SaaS"
CONDO_ID="seu-condo-id"

# 🤖 LLM
OPENROUTER_API_KEY=sk-or-v1-...
LLM_MODEL=openai/gpt-4-turbo-preview

# 🗄️ Banco de Dados
SUPABASE_URL=https://...supabase.co
SUPABASE_SERVICE_KEY=...

# 💬 WhatsApp
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=...

# 💾 Cache
REDIS_URL=redis://localhost:6379

# 🌐 Aplicação
APP_ENV=development
DEBUG=false
```

Ver `.env.example` para lista completa.

## 💻 Uso

### API - Health Check

```bash
curl http://localhost:8000/health
```

Resposta:
```json
{
  "status": "ok",
  "app_name": "Syndra Agent",
  "version": "2.0.0",
  "condo_name": "Seu Condomínio",
  "environment": "development"
}
```

### API - Webhook WhatsApp

**POST** `/api/v1/webhooks/whatsapp`

```json
{
  "sender": "5511999999999",
  "message": "Olá! Qual é o horário da churrasqueira?",
  "message_id": "wamid.12345678"
}
```

Resposta:
```json
{
  "success": true,
  "message_id": "wamid.12345678",
  "response": "📍 A churrasqueira está disponível...",
  "escalated": false
}
```

### Documentação Interativa

Acesse: `http://localhost:8000/api/docs` (Swagger UI)

Ou: `http://localhost:8000/api/redoc` (ReDoc)

## 🔒 Segurança

### Autenticação de Webhook

Todos os webhooks validam `WEBHOOK_TOKEN`:

```python
from config.settings import settings

# No cabeçalho: Authorization: Bearer {WEBHOOK_TOKEN}
```

### Rate Limiting

```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60  # segundos
```

### HTTPS em Produção

```bash
# Gerar certificado auto-assinado (teste)
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Usar Nginx como reverse proxy com SSL
docker-compose -f docker-compose.yml --profile production up
```

### Logs de Auditoria

Todas as operações são registradas:

```bash
tail -f logs/audit.log
```

## 🧪 Testes

### Rodar Testes Unitários

```bash
pytest tests/unit -v
```

### Cobertura

```bash
pytest tests/unit --cov=src --cov-report=html
open htmlcov/index.html
```

### Testes de Integração

```bash
pytest tests/integration -v -m integration
```

### Lint & Format

```bash
# Formatar
black src tests config

# Verificar
flake8 src tests config
pylint src
mypy src
```

## 🔧 Troubleshooting

### Erro: Connection refused ao Supabase

```
❌ "Connection refused" para Supabase
```

**Solução:**
1. Verifique `SUPABASE_URL` (deve ser completo)
2. Verifique `SUPABASE_SERVICE_KEY` (deve ser válida)
3. Teste: `python -c "from src.supabase.client import supabase"`

### Erro: Evolution API não responde

```
❌ "Connection refused" para Evolution API
```

**Solução:**
1. Verifique se Evolution está rodando: `docker ps`
2. Verifique `EVOLUTION_API_URL` (default: `http://localhost:8080`)
3. Teste: `curl http://localhost:8080/health`

### Erro: Redis não conecta

```
❌ "Connection refused" para Redis
```

**Solução:**
1. Redis rodando? `docker ps | grep redis`
2. Verifique `REDIS_URL`
3. Teste: `redis-cli ping` (deve responder PONG)

### Performance: Respostas lentas

**Verificar:**
1. Logs: `tail -f logs/app.log`
2. LLM latência: Ajuste `LLM_MAX_TOKENS`
3. RAG: Reduza `MAX_CONTEXT_CHUNKS`

## 📚 Documentação Técnica

- [ARQUITETURA.md](docs/ARQUITETURA.md) - Detalhes de design
- [API.md](docs/API.md) - Documentação de endpoints
- [DEPLOYMENT.md](docs/DEPLOYMENT.md) - Deploy em produção
- [DEVELOPMENT.md](docs/DEVELOPMENT.md) - Setup de desenvolvimento

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add some AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Abra Pull Request

**Diretrizes:**
- Código limpo (Black + isort)
- Testes para novas features
- Documentação atualizada
- 80%+ de cobertura de testes

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes

## 📞 Suporte

- 📧 Email: support@syndra-agent.dev
- 💬 Discord: [Comunidade](https://discord.gg/syndra)
- 🐛 Issues: [GitHub Issues](https://github.com/seu-usuario/syndra-agent/issues)

## 🙏 Agradecimentos

- [FastAPI](https://fastapi.tiangolo.com/)
- [LangChain](https://langchain.com/)
- [Supabase](https://supabase.com/)
- [Evolution API](https://evolution-api.com/)

---

**Made with ❤️ by Syndra Team**

Última atualização: 13 de Março de 2025

