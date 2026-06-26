# 🚀 Fase 1: Setup & Integração Grafana

## Checklist de Configuração

### ✅ 1.1 - Copiar `.env.example` → `.env` e preencher

```bash
cp .env.example .env
```

Abra `.env` e preencha **OBRIGATORIAMENTE**:

```bash
# Grafana (OBRIGATÓRIO)
GRAFANA_URL=https://seu-grafana.com
GRAFANA_API_TOKEN=glc_XXXX

# Claude API (OBRIGATÓRIO)
CLAUDE_API_KEY=sk-ant-XXXX

# Opcional inicialmente
TELEGRAM_BOT_TOKEN=123456:ABC...
TELEGRAM_CHAT_IDS=-123456789
```

### ✅ 1.2 - Instalar dependências Python

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### ✅ 1.3 - Gerar API Token no Grafana

1. Grafana → **Admin > API Keys**
2. **Create API Key**
3. Name: `monitoring-bot`, Role: `Viewer`
4. Copy token → `.env` como `GRAFANA_API_TOKEN`

### ✅ 1.4 - Testar conexão

```bash
python test_grafana.py
```

**Esperado:**
```
✓ Configurações OK
✓ Conexão OK
✓ 2/2 dashboards validados
✅ FASE 1 OK
```

## 🎯 Próximo

Quando passar: **Fase 2 - Parser de Métricas**

