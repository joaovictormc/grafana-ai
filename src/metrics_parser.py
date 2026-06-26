"""
Fase 2: Parser de Metricas
Extrai dados dos dashboards do Grafana e normaliza para analise IA.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import re
from src.config import config
from src.grafana_client import create_grafana_client

logger = logging.getLogger(__name__)


class MetricsParser:
    """Parseia e normaliza metricas dos dashboards Grafana"""

    def __init__(self):
        self.client = create_grafana_client()
        self.metrics_history: Dict[str, List[Dict]] = {}

    def fetch_dashboard_metrics(self, dashboard_uid: str) -> Dict[str, Any]:
        """
        Busca todos os dados de um dashboard.

        Args:
            dashboard_uid: UID do dashboard

        Returns:
            Dict com metricas estruturadas
        """
        dashboard = self.client.get_dashboard(dashboard_uid)
        if not dashboard:
            logger.error(f"Dashboard {dashboard_uid} nao encontrado")
            return {}

        dashboard_name = dashboard.get("dashboard", {}).get("title") or \
                        dashboard.get("spec", {}).get("title") or dashboard_uid

        panels = self.client.get_panels_from_dashboard(dashboard_uid)
        metrics = {
            "dashboard_uid": dashboard_uid,
            "dashboard_name": dashboard_name,
            "timestamp": datetime.now().isoformat(),
            "panels": []
        }

        for panel in panels:
            panel_data = self._parse_panel(panel, dashboard_uid)
            if panel_data:
                metrics["panels"].append(panel_data)

        return metrics

    def _parse_panel(self, panel: Dict[str, Any], dashboard_uid: str) -> Optional[Dict]:
        """
        Parseia um painel individual.

        Args:
            panel: Dados do painel
            dashboard_uid: UID do dashboard pai

        Returns:
            Dict com dados parseados ou None
        """
        panel_id = panel.get("id")
        panel_title = panel.get("title", f"Panel {panel_id}")
        panel_type = panel.get("type", "unknown")

        if panel_type == "row":
            return None

        return {
            "id": panel_id,
            "title": panel_title,
            "type": panel_type,
            "targets": panel.get("targets", []),
            "description": panel.get("description", ""),
        }

    def extract_critical_metrics(self, dashboard_uid: str) -> Dict[str, Any]:
        """
        Extrai apenas metricas criticas definidas em config.yaml.

        Args:
            dashboard_uid: UID do dashboard

        Returns:
            Dict com metricas criticas normalizadas
        """
        dashboard_config = config.get_dashboard(dashboard_uid)
        if not dashboard_config:
            logger.warning(f"Dashboard {dashboard_uid} nao configurado em config.yaml")
            return {}

        metrics = self.fetch_dashboard_metrics(dashboard_uid)
        critical_metrics_config = dashboard_config.get("critical_metrics", [])

        result = {
            "dashboard": dashboard_config.get("name"),
            "timestamp": metrics.get("timestamp"),
            "metrics": {},
            "status": "OK"
        }

        for metric_cfg in critical_metrics_config:
            metric_name = metric_cfg.get("metric")
            threshold_warning = metric_cfg.get("threshold_warning")
            threshold_critical = metric_cfg.get("threshold_critical")

            for panel in metrics.get("panels", []):
                if self._matches_metric(panel["title"], metric_name):
                    result["metrics"][metric_name] = {
                        "panel_id": panel["id"],
                        "panel_title": panel["title"],
                        "threshold_warning": threshold_warning,
                        "threshold_critical": threshold_critical,
                        "status": "UNKNOWN",
                    }
                    break

        return result

    def _matches_metric(self, panel_title: str, metric_pattern: str) -> bool:
        """
        Verifica se um painel matcheia com um padrao de metrica.

        Args:
            panel_title: Titulo do painel
            metric_pattern: Padrao de metrica (pode ter wildcards)

        Returns:
            True se ha match
        """
        regex_pattern = metric_pattern.replace("*", ".*")
        regex_pattern = f"(?i){regex_pattern}"

        try:
            return bool(re.search(regex_pattern, panel_title))
        except re.error:
            return metric_pattern.lower() in panel_title.lower()

    def normalize_metrics(self, raw_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Normaliza metricas brutas para formato padronizado"""
        return {
            "dashboard": raw_metrics.get("dashboard"),
            "timestamp": raw_metrics.get("timestamp"),
            "summary": {
                "total_metrics": len(raw_metrics.get("metrics", {})),
                "critical_count": 0,
                "warning_count": 0,
            },
            "metrics": raw_metrics.get("metrics", {}),
        }

    def format_for_llm(self, normalized_metrics: Dict[str, Any]) -> str:
        """Formata metricas normalizadas em texto legivel para LLM"""
        dashboard = normalized_metrics.get("dashboard", "Unknown")
        timestamp = normalized_metrics.get("timestamp", "Unknown")
        metrics = normalized_metrics.get("metrics", {})

        lines = [
            f"=== Dashboard: {dashboard} ===",
            f"Timestamp: {timestamp}",
            "",
            "Metricas Criticas:",
        ]

        for metric_name, metric_data in metrics.items():
            status = metric_data.get("status", "UNKNOWN")
            threshold_w = metric_data.get("threshold_warning", "N/A")
            threshold_c = metric_data.get("threshold_critical", "N/A")

            lines.append(f"  - {metric_name}")
            lines.append(f"    Status: {status}")
            lines.append(f"    Warning: {threshold_w}, Critical: {threshold_c}")

        return "\n".join(lines)


def create_metrics_parser() -> MetricsParser:
    """Factory para criar parser de metricas"""
    return MetricsParser()
