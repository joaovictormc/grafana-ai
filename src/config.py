"""
Configuração centralizada da aplicação.
Carrega variáveis de ambiente (.env) e arquivo YAML (config.yaml)
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
import yaml

# Carregar .env
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


def load_yaml_config(config_path: Optional[str] = None) -> dict:
    """
    Carrega arquivo YAML de configuração.

    Args:
        config_path: Caminho customizado (padrão: ./config.yaml)

    Returns:
        Dicionário com configuração YAML
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config.yaml"

    if not Path(config_path).exists():
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class Config:
    """Configuração centralizada da aplicação - acessa variáveis de ambiente"""

    def __init__(self):
        # Grafana
        self.grafana_url = os.getenv("GRAFANA_URL", "")
        self.grafana_api_token = os.getenv("GRAFANA_API_TOKEN", "")

        # Claude
        self.claude_api_key = os.getenv("CLAUDE_API_KEY", "")
        self.claude_model = "claude-3-5-haiku-20241022"

        # EvolutionAPI (WhatsApp)
        self.evolution_api_url = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
        self.evolution_api_token = os.getenv("EVOLUTION_API_TOKEN", "")
        self.evolution_instance_name = os.getenv("EVOLUTION_INSTANCE_NAME", "")
        whatsapp_numbers = os.getenv("WHATSAPP_NOTIFY_NUMBERS", "")
        self.whatsapp_notify_numbers = [n.strip() for n in whatsapp_numbers.split(",") if n.strip()]

        # Telegram
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        telegram_ids = os.getenv("TELEGRAM_CHAT_IDS", "")
        self.telegram_chat_ids = [int(n.strip()) for n in telegram_ids.split(",") if n.strip()]

        # GLPI
        self.glpi_url = os.getenv("GLPI_URL", "")
        self.glpi_api_token = os.getenv("GLPI_API_TOKEN", "")
        self.glpi_app_token = os.getenv("GLPI_APP_TOKEN", "")
        self.glpi_user_id = int(os.getenv("GLPI_USER_ID", "2"))

        # Email
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.email_from = os.getenv("EMAIL_FROM", "")
        self.email_to = os.getenv("EMAIL_TO", "")

        # App
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.scheduler_interval_minutes = int(os.getenv("SCHEDULER_INTERVAL_MINUTES", "5"))

        # Carregar YAML
        try:
            self.yaml_config = load_yaml_config()
        except FileNotFoundError as e:
            print(f"⚠️  {e}")
            self.yaml_config = {}

    def get_dashboard(self, uid: str) -> Optional[dict]:
        """Obtém configuração de um dashboard pelo UID"""
        for dashboard in self.yaml_config.get("dashboards", []):
            if dashboard.get("uid") == uid:
                return dashboard
        return None

    def get_thresholds(self) -> dict:
        """Obtém limites críticos globais"""
        return self.yaml_config.get("thresholds", {})

    def validate(self) -> bool:
        """Valida configurações necessárias"""
        errors = []

        if not self.grafana_url:
            errors.append("GRAFANA_URL é obrigatório")
        if not self.grafana_api_token:
            errors.append("GRAFANA_API_TOKEN é obrigatório")
        if not self.claude_api_key:
            errors.append("CLAUDE_API_KEY é obrigatório")

        if errors:
            print("❌ Erros de configuração:")
            for error in errors:
                print(f"  - {error}")
            return False

        return True


# Instância global
config = Config()
