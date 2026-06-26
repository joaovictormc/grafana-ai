"""Telegram notifier"""

import logging
from typing import Dict, Any
from telegram import Bot
from telegram.error import TelegramError
from src.config import config

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Envia notificacoes via Telegram"""

    def __init__(self):
        self.bot = Bot(token=config.telegram_bot_token)
        self.chat_ids = config.telegram_chat_ids

    def send(self, message: str, status: str, severity: int) -> Dict[str, Any]:
        """Envia mensagem Telegram"""
        if not self.chat_ids:
            return {"success": False, "error": "Nenhum chat configurado"}

        results = []
        for chat_id in self.chat_ids:
            try:
                emoji = {"CRITICAL": "[CRITICO]", "WARNING": "[AVISO]", "OK": "[OK]"}.get(status, "")
                formatted = f"{emoji}\n{message}"
                self.bot.send_message(chat_id=chat_id, text=formatted)
                results.append({"chat_id": chat_id, "success": True})
                logger.info(f"[Telegram] Enviado para chat {chat_id}")

            except TelegramError as e:
                results.append({"chat_id": chat_id, "success": False, "error": str(e)})
                logger.error(f"[Telegram] Erro: {e}")

        return {"success": any(r["success"] for r in results), "results": results}

    def test(self) -> bool:
        """Testa conexao com Telegram"""
        try:
            self.bot.get_me()
            logger.info("[Telegram] Conexao OK")
            return True
        except TelegramError as e:
            logger.error(f"[Telegram] Erro: {e}")
            return False
