"""
Fase 4: Notification Router
Roteia alertas para multiplos canais: WhatsApp, Telegram, GLPI, Email
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
from src.config import config
from src.notifiers.whatsapp_notifier import WhatsAppNotifier
from src.notifiers.telegram_notifier import TelegramNotifier
from src.notifiers.glpi_notifier import GLPINotifier
from src.notifiers.email_notifier import EmailNotifier

logger = logging.getLogger(__name__)


class NotificationRouter:
    """Roteia alertas para multiplos canais baseado em severidade"""

    def __init__(self):
        self.whatsapp = WhatsAppNotifier() if config.evolution_api_token else None
        self.telegram = TelegramNotifier() if config.telegram_bot_token else None
        self.glpi = GLPINotifier() if config.glpi_api_token else None
        self.email = EmailNotifier() if config.smtp_user else None

    def send_alert(self, analysis: Dict[str, Any], dashboard: str) -> Dict[str, Any]:
        """
        Envia alerta para canais apropriados baseado na severidade.

        Args:
            analysis: Dict com {status, severity, reason, affected, recommendation}
            dashboard: Nome do dashboard

        Returns:
            Dict com resultado de envio para cada canal
        """
        status = analysis.get("status", "UNKNOWN")
        severity = analysis.get("severity", 0)
        reason = analysis.get("reason", "")
        affected = analysis.get("affected", [])
        recommendation = analysis.get("recommendation")

        results = {
            "timestamp": datetime.now().isoformat(),
            "dashboard": dashboard,
            "status": status,
            "severity": severity,
            "channels": {}
        }

        message = self._format_message(dashboard, status, severity, reason, affected, recommendation)

        if self.telegram:
            results["channels"]["telegram"] = self.telegram.send(message, status, severity)

        if self.email:
            results["channels"]["email"] = self.email.send(message, dashboard, status, severity)

        if status == "CRITICAL":
            if self.glpi:
                results["channels"]["glpi"] = self.glpi.create_ticket(
                    dashboard=dashboard,
                    status=status,
                    severity=severity,
                    reason=reason,
                    affected=affected,
                    recommendation=recommendation
                )

        return results

    def _format_message(self, dashboard: str, status: str, severity: int, reason: str, affected: List[str], recommendation: str) -> str:
        """Formata mensagem para notificacao"""
        lines = [
            f"[{status}] Dashboard: {dashboard}",
            f"Severidade: {severity}/10",
            f"Motivo: {reason}",
        ]

        if affected:
            lines.append(f"Afetados: {', '.join(affected)}")
        if recommendation:
            lines.append(f"Acao: {recommendation}")

        return "\n".join(lines)

    def test_channels(self) -> Dict[str, bool]:
        """Testa conexao com todos os canais"""
        results = {
            "telegram": self.telegram.test() if self.telegram else False,
            "glpi": self.glpi.test() if self.glpi else False,
            "email": self.email.test() if self.email else False,
        }
        return results


def create_notification_router() -> NotificationRouter:
    """Factory para criar roteador de notificacoes"""
    return NotificationRouter()
