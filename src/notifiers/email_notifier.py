"""Email notifier"""

import logging
from typing import Dict, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.config import config

logger = logging.getLogger(__name__)


class EmailNotifier:
    """Envia notificacoes via Email"""

    def __init__(self):
        self.smtp_server = config.smtp_server
        self.smtp_port = config.smtp_port
        self.user = config.smtp_user
        self.password = config.smtp_password
        self.sender = config.email_from
        self.recipients = [config.email_to]

    def send(self, message: str, dashboard: str, status: str, severity: int) -> Dict[str, Any]:
        """Envia notificacao por email"""
        try:
            subject = f"[{status}] Alerta: {dashboard} (Sev {severity}/10)"
            msg = MIMEMultipart()
            msg["From"] = self.sender
            msg["To"] = ", ".join(self.recipients)
            msg["Subject"] = subject

            body = f"Dashboard: {dashboard}\nStatus: {status}\nSeveridade: {severity}/10\n\n{message}"
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.send_message(msg)

            logger.info(f"[Email] Enviado para {', '.join(self.recipients)}")
            return {"success": True, "recipients": self.recipients}

        except Exception as e:
            logger.error(f"[Email] Erro: {e}")
            return {"success": False, "error": str(e)}

    def test(self) -> bool:
        """Testa conexao SMTP"""
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.user, self.password)
            logger.info("[Email] Conexao OK")
            return True
        except Exception as e:
            logger.error(f"[Email] Erro: {e}")
            return False
