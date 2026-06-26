"""
Cliente para interagir com a API Grafana.
Extrai dados de painéis e séries temporais.
"""

import logging
from typing import Optional, List, Dict, Any
import requests
from requests.exceptions import RequestException, ConnectionError, Timeout
from src.config import config

logger = logging.getLogger(__name__)


class GrafanaClient:
    """Cliente para a API REST do Grafana"""

    def __init__(self, base_url: str, api_token: str):
        """
        Inicializa o cliente Grafana.

        Args:
            base_url: URL base do Grafana (ex: https://grafana.seu-site.com)
            api_token: Token de API com permissões de leitura
        """
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        })

    def get_dashboard(self, uid: str) -> Optional[Dict[str, Any]]:
        """
        Obtém um dashboard pelo UID.

        Args:
            uid: UID único do dashboard

        Returns:
            Dict com dashboard ou None se não encontrado
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/dashboards/uid/{uid}",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except (RequestException, ConnectionError, Timeout) as e:
            logger.error(f"Erro ao buscar dashboard {uid}: {e}")
            return None

    def get_panels_from_dashboard(self, uid: str) -> List[Dict[str, Any]]:
        """
        Extrai todos os painéis de um dashboard.

        Args:
            uid: UID do dashboard

        Returns:
            Lista de painéis
        """
        dashboard = self.get_dashboard(uid)
        if not dashboard:
            return []

        if "dashboard" in dashboard:
            return dashboard.get("dashboard", {}).get("panels", [])

        if "spec" in dashboard:
            elements = dashboard.get("spec", {}).get("elements", {})
            panels = []
            for element in elements.values():
                if element.get("kind") == "Panel":
                    panels.append(element.get("spec", {}))
            return panels

        return []

    def get_datasources(self) -> List[Dict[str, Any]]:
        """
        Lista todos os datasources disponíveis.

        Returns:
            Lista de datasources
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/datasources",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except (RequestException, ConnectionError, Timeout) as e:
            logger.error(f"Erro ao listar datasources: {e}")
            return []

    def test_connection(self) -> bool:
        """
        Testa a conexão com o Grafana.

        Returns:
            True se conexão bem-sucedida
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/health",
                timeout=10
            )
            response.raise_for_status()
            logger.info("✓ Conexão com Grafana bem-sucedida")
            return True
        except (RequestException, ConnectionError, Timeout) as e:
            logger.error(f"✗ Conexão com Grafana falhou: {e}")
            return False


def create_grafana_client() -> GrafanaClient:
    """Factory para criar cliente Grafana com config global"""
    return GrafanaClient(
        base_url=config.grafana_url,
        api_token=config.grafana_api_token
    )
