"""GLPI ticket notifier"""

import logging
from typing import Dict, Any, List
import requests
from src.config import config

logger = logging.getLogger(__name__)


class GLPINotifier:
    """Cria tickets GLPI para alertas criticos"""

    def __init__(self):
        url = config.glpi_url.rstrip("/")
        if url.startswith("http://http://"):
            url = "http://" + url.split("http://http://")[1]
        elif url.startswith("https://https://"):
            url = "https://" + url.split("https://https://")[1]
        self.api_url = url
        self.api_token = config.glpi_api_token
        self.app_token = config.glpi_app_token
        self.user_id = config.glpi_user_id

    def create_ticket(self, dashboard: str, status: str, severity: int, reason: str, affected: List[str], recommendation: str) -> Dict[str, Any]:
        """Cria ticket GLPI"""
        if status != "CRITICAL":
            return {"success": False, "error": "Apenas alertas CRITICAL"}

        try:
            headers = {
                "Content-Type": "application/json",
                "Session-Token": self._get_session(),
                "App-Token": self.app_token
            }

            payload = {
                "input": {
                    "name": f"[{dashboard}] ALERTA CRITICO - Sev {severity}/10",
                    "content": self._format_ticket_content(dashboard, status, severity, reason, affected, recommendation),
                    "urgency": 5,
                    "priority": 5,
                    "type": 2,
                    "_users_id_requester": self.user_id,
                    "status": 1,
                }
            }

            response = requests.post(
                f"{self.api_url}/apirest.php/Ticket",
                json=payload,
                headers=headers,
                timeout=10
            )

            if response.status_code == 201:
                ticket_id = response.json().get("id")
                logger.info(f"[GLPI] Ticket {ticket_id} criado")
                return {"success": True, "ticket_id": ticket_id}
            else:
                return {"success": False, "error": f"Status {response.status_code}"}

        except Exception as e:
            logger.error(f"[GLPI] Erro: {e}")
            return {"success": False, "error": str(e)}

    def _format_ticket_content(self, dashboard: str, status: str, severity: int, reason: str, affected: List[str], recommendation: str) -> str:
        lines = [f"Dashboard: {dashboard}", f"Status: {status}", f"Severidade: {severity}/10", "", f"Motivo: {reason}"]
        if affected:
            lines.append(f"Afetados: {', '.join(affected)}")
        if recommendation:
            lines.append(f"Recomendacao: {recommendation}")
        return "\n".join(lines)

    def _get_session(self) -> str:
        """Obtém session token GLPI"""
        response = requests.get(
            f"{self.api_url}/apirest.php/initSession",
            headers={"Content-Type": "application/json", "Authorization": f"user_token {self.api_token}", "App-Token": self.app_token},
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get("session_token")
        raise Exception(f"Erro GLPI: {response.status_code}")

    def test(self) -> bool:
        """Testa conexao GLPI"""
        try:
            self._get_session()
            logger.info("[GLPI] Conexao OK")
            return True
        except Exception as e:
            logger.error(f"[GLPI] Erro: {e}")
            return False
