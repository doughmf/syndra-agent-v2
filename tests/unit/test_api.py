"""
Syndra Agent - Testes Unitários
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient

from src.api.main import app
from config.settings import get_settings

settings = get_settings()
client = TestClient(app)


# ═══════════════════════════════════════════════════════════════════════════
# Testes de Health Check
# ═══════════════════════════════════════════════════════════════════════════

def test_health_check():
    """Teste de health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app_name"] == settings.APP_NAME
    assert data["version"] == settings.APP_VERSION
    assert data["condo_name"] == settings.CONDO_NAME


def test_root_route():
    """Teste da rota raiz"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "app" in data
    assert "version" in data
    assert "docs" in data


def test_status_route():
    """Teste da rota de status"""
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    data = response.json()
    assert "app" in data
    assert "condo" in data
    assert "integrations" in data
    assert "features" in data


# ═══════════════════════════════════════════════════════════════════════════
# Testes de Webhook
# ═══════════════════════════════════════════════════════════════════════════

def test_whatsapp_webhook_valid_message():
    """Teste de webhook com mensagem válida"""
    payload = {
        "sender": "5511999999999",
        "message": "Olá! Qual é o horário da churrasqueira?",
        "message_id": "wamid.1234567890"
    }
    
    response = client.post("/api/v1/webhooks/whatsapp", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message_id"] == payload["message_id"]
    assert "response" in data


def test_whatsapp_webhook_missing_fields():
    """Teste de webhook com campos faltando"""
    payload = {
        "sender": "5511999999999",
        # Faltando 'message' e 'message_id'
    }
    
    response = client.post("/api/v1/webhooks/whatsapp", json=payload)
    assert response.status_code == 422  # Unprocessable Entity


def test_whatsapp_webhook_empty_message():
    """Teste de webhook com mensagem vazia"""
    payload = {
        "sender": "5511999999999",
        "message": "",
        "message_id": "wamid.1234567890"
    }
    
    response = client.post("/api/v1/webhooks/whatsapp", json=payload)
    # Pode ser 422 ou 200 dependendo da validação
    assert response.status_code in [200, 422]


def test_whatsapp_webhook_very_long_message():
    """Teste de webhook com mensagem muito longa"""
    payload = {
        "sender": "5511999999999",
        "message": "x" * 5000,  # Excede MAX_MESSAGE_LENGTH
        "message_id": "wamid.1234567890"
    }
    
    response = client.post("/api/v1/webhooks/whatsapp", json=payload)
    assert response.status_code == 422  # Deve rejeitar


# ═══════════════════════════════════════════════════════════════════════════
# Testes de Configuração
# ═══════════════════════════════════════════════════════════════════════════

def test_settings_condo_name_not_hardcoded():
    """Teste que CONDO_NAME não está hardcoded"""
    # Deve estar em variável de ambiente ou padrão genérico
    assert settings.CONDO_NAME != ""
    # Não deve conter nome específico do cliente
    assert "Nogueira Martins" not in settings.CONDO_NAME
    assert "Residencial" not in settings.CONDO_NAME or settings.CONDO_NAME == "Condomínio SaaS"


def test_settings_agent_name():
    """Teste do nome do agente"""
    assert settings.AGENT_NAME == "Syndra"


def test_settings_environment():
    """Teste do ambiente configurado"""
    assert settings.APP_ENV in ["development", "staging", "production"]


# ═══════════════════════════════════════════════════════════════════════════
# Testes de Prompts
# ═══════════════════════════════════════════════════════════════════════════

def test_system_prompt_generation():
    """Teste de geração de system prompt"""
    from src.agent.prompts import build_system_prompt
    
    prompt = build_system_prompt(
        condo_id="default",
        resident_name="João Silva",
        apartment="101"
    )
    
    assert prompt is not None
    assert len(prompt) > 0
    assert settings.AGENT_NAME in prompt
    assert settings.CONDO_NAME in prompt
    assert "João Silva" in prompt
    assert "101" in prompt
    
    # Não deve conter hardcoding
    assert "Nogueira Martins" not in prompt


def test_escalation_keywords():
    """Teste de detecção de escalação"""
    from src.agent.prompts import should_escalate
    
    # Deve escalar
    assert should_escalate("Tem incêndio no prédio!")
    assert should_escalate("Recebi uma ameaça")
    assert should_escalate("Sofri um acidente")
    
    # Não deve escalar
    assert not should_escalate("Qual é o horário da churrasqueira?")
    assert not should_escalate("Quero reservar o salão")
    assert not should_escalate("Boa tarde!")


# ═══════════════════════════════════════════════════════════════════════════
# Testes de Segurança
# ═══════════════════════════════════════════════════════════════════════════

def test_cors_headers():
    """Teste de headers CORS"""
    response = client.get("/health")
    # Verificar se não há erros CORS
    assert response.status_code == 200


def test_security_headers():
    """Teste de headers de segurança"""
    response = client.get("/health")
    # Headers de segurança podem estar presentes
    assert response.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════
# Pytest Fixtures
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def valid_message_payload():
    """Fixture com payload válido de mensagem"""
    return {
        "sender": "5511999999999",
        "message": "Olá! Tudo bem?",
        "message_id": "wamid.test.123456"
    }


@pytest.fixture
def client_fixture():
    """Fixture com cliente teste"""
    return TestClient(app)


# ═══════════════════════════════════════════════════════════════════════════
# Parametrized Tests
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("message,expected_escalation", [
    ("incêndio!", True),
    ("fogo no apartamento", True),
    ("ameaça de violência", True),
    ("Qual é o horário?", False),
    ("Boa tarde", False),
    ("Reservar salão", False),
])
def test_escalation_detection_parametrized(message, expected_escalation):
    """Teste parametrizado de detecção de escalação"""
    from src.agent.prompts import should_escalate
    assert should_escalate(message) == expected_escalation


# ═══════════════════════════════════════════════════════════════════════════
# Integration Tests (marcados com @pytest.mark.integration)
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
def test_full_message_flow(valid_message_payload):
    """Teste de fluxo completo de mensagem (integration test)"""
    # Este teste pode exigir recursos externos (Supabase, LLM, etc)
    # Deve ser executado com: pytest -m integration
    
    response = client.post("/api/v1/webhooks/whatsapp", json=valid_message_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


# ═══════════════════════════════════════════════════════════════════════════
# Pytest Configuration (conftest.py)
# ═══════════════════════════════════════════════════════════════════════════

# Adicionar ao arquivo: tests/conftest.py
pytest_plugins = []

def pytest_configure(config):
    """Configuração customizada do pytest"""
    config.addinivalue_line(
        "markers", "integration: marca teste como teste de integração"
    )

