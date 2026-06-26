"""WhatsApp notifier via EvolutionAPI"""

import logging
from typing import Dict, Any
import requests
from src.config import config

logger = logging.getLogger(__name__)


class WhatsAppNotifier:
    """Envia notificacoes via WhatsApp (EvolutionAPI)"""

    def __init__(self):
        self.api_url = config.evolution_api_url.rstrip("/")
        self.api_token = config.evolution_api_token
        self.instance = config.evolution_instance_name
        self.recipients = config.whatsapp_notify_numbers

    def send(self, message: str, status: str, severity: int) -> Dict[str, Any]:
        """Envia mensagem WhatsApp"""
        if not self.recipients:
            return {"success": False, "error": "Nenhum numero configurado"}

        results = []
        for recipient in self.recipients:
            try:
                payload = {"number": recipient, "text": message}
                response = requests.post(
                    f"{self.api_url}/message/sendText/{self.instance}",
                    json=payload,
                    headers={"Authorization": f"Bearer {self.api_token}"},
                    timeout=10
                )

                if response.status_code == 200:
                    results.append({"number": recipient, "success": True})
                    logger.info(f"[WhatsApp] Enviado para {recipient}")
                else:
                    results.append({"number": recipient, "success": False, "error": response.text})

            except Exception as e:
                results.append({"number": recipient, "success": False, "error": str(e)})
                logger.error(f"[WhatsApp] Erro: {e}")

        return {"success": any(r["success"] for r in results), "results": results}

    def test(self) -> bool:
        """Testa conexao com EvolutionAPI"""
        try:
            response = requests.get(
                f"{self.api_url}/instance/fetchInstances",
                headers={"Authorization": f"Bearer {self.api_token}"},
                timeout=10
            )
            success = response.status_code == 200
            if success:
                logger.info("[WhatsApp] Conexao OK")
            return success
        except Exception as e:
            logger.error(f"[WhatsApp] Erro: {e}")
            return False
