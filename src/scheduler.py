"""
Fase 5: Scheduler
Executa pipeline: Grafana → Parser → LLM → Notificacoes (a cada 5 min)
"""

import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from src.config import config
from src.metrics_parser import create_metrics_parser
from src.llm_analyzer import create_llm_analyzer
from src.notification_router import create_notification_router

logger = logging.getLogger(__name__)


class MonitoringScheduler:
    """Scheduler do pipeline de monitoramento"""

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.parser = create_metrics_parser()
        self.analyzer = create_llm_analyzer()
        self.router = create_notification_router()
        self.interval_minutes = config.scheduler_interval_minutes

    def start(self):
        """Inicia o scheduler"""
        if self.scheduler.running:
            logger.warning("Scheduler ja rodando")
            return

        self.scheduler.add_job(
            self.run_monitoring_cycle,
            trigger=IntervalTrigger(minutes=self.interval_minutes),
            id="monitoring_cycle",
            name="Monitoring Cycle",
            replace_existing=True
        )

        self.scheduler.start()
        logger.info(f"Scheduler iniciado - ciclo a cada {self.interval_minutes} min")

    def stop(self):
        """Para o scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler parado")

    def run_monitoring_cycle(self):
        """Executa ciclo completo: metrics → analyze → notify"""
        cycle_start = datetime.now().isoformat()
        logger.info(f"[{cycle_start}] Iniciando monitoramento...")

        dashboards_config = config.yaml_config.get("dashboards", [])
        if not dashboards_config:
            logger.error("Nenhum dashboard configurado")
            return

        for dashboard_cfg in dashboards_config:
            try:
                uid = dashboard_cfg.get("uid")
                name = dashboard_cfg.get("name")

                logger.info(f"  Processando: {name}")

                raw = self.parser.extract_critical_metrics(uid)
                if not raw:
                    logger.warning(f"  Nenhuma metrica para {name}")
                    continue

                normalized = self.parser.normalize_metrics(raw)
                llm_text = self.parser.format_for_llm(normalized)
                analysis = self.analyzer.analyze_metrics(llm_text)
                result = self.router.send_alert(analysis, name)

                status = analysis.get("status", "UNKNOWN")
                severity = analysis.get("severity", 0)
                channels = list(result.get("channels", {}).keys())

                logger.info(f"  {name}: {status} (Sev {severity}/10) - {channels}")

            except Exception as e:
                logger.error(f"  Erro {name}: {e}", exc_info=True)

        logger.info(f"[{datetime.now().isoformat()}] Ciclo concluido")


def create_scheduler() -> MonitoringScheduler:
    """Factory para criar scheduler"""
    return MonitoringScheduler()
