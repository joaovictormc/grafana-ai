# Deployment - Servidor Linux com Docker Compose

## 📋 Pré-requisitos
- Docker + Docker Compose
- SSH ao servidor Linux
- Credenciais: Grafana, Claude API, Telegram, GLPI, Email

---

## 🚀 Passo 1: Transferir arquivos

```bash
# Via SCP
scp -r /seu/diretorio/ usuario@servidor:/home/usuario/monitoring

# Ou via Git
git clone <seu-repo> /home/usuario/monitoring
cd /home/usuario/monitoring
```

---

## 🔧 Passo 2: Configurar .env

```bash
ssh usuario@servidor
cd monitoring
cp .env.example .env
nano .env
```

**Variáveis obrigatórias:**
```
GRAFANA_URL=https://seu-grafana.com
GRAFANA_API_TOKEN=glc_xxxx
CLAUDE_API_KEY=sk-ant-xxxx
TELEGRAM_BOT_TOKEN=123:ABC...
TELEGRAM_CHAT_IDS=-123456
GLPI_URL=https://seu-glpi-producao.com
GLPI_API_TOKEN=xxxx
GLPI_APP_TOKEN=xxxx
SMTP_SERVER=mail.dominio.com
SMTP_USER=email@dominio.com
SMTP_PASSWORD=senha
EMAIL_FROM=monitoramento@dominio.com
EMAIL_TO=seu-email@dominio.com
```

---

## 🐳 Passo 3: Deploy

```bash
# Build
docker-compose build

# Testar (foreground)
docker-compose up

# Produção (background)
docker-compose up -d

# Logs
docker-compose logs -f monitoring
```

---

## ✅ Passo 4: Validar

```bash
docker-compose ps
docker-compose exec monitoring python validate_services.py
docker-compose logs monitoring
```

---

## 🔄 Operações

```bash
# Parar
docker-compose down

# Reiniciar
docker-compose restart

# Ver logs
docker-compose logs -f

# Atualizar código
git pull
docker-compose build
docker-compose up -d
```

---

## 📊 Monitoramento

- Logs em `/home/usuario/monitoring/monitoring.log`
- Container rodando 24/7
- Intervalo: 5 min (configurável em .env)
- Alertas via: Telegram, Email, GLPI (tickets críticos)

---

## 🐛 Troubleshooting

```bash
# Ver erros
docker-compose logs monitoring

# Testar GLPI
docker-compose exec monitoring python validate_services.py

# Testar Grafana
docker-compose exec monitoring python test_grafana.py
```

---

**Pronto! Sistema 24/7 rodando em Docker.**
