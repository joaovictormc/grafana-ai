#!/usr/bin/env python3
"""
Aplicacao Principal - Inicia monitoramento 24/7
Executar: python run.py
"""

import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.config import config
from src.scheduler import create_scheduler

logging.basicConfig(
    level=getattr(logging, config.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("monitoring.log")]
)

logger = logging.getLogger(__name__)


def main():
    """Funcao principal"""
    print("\n" + "="*60)
    print("MONITORAMENTO INTELIGENTE COM IA")
    print("="*60 + "\n")

    if not config.validate():
        print("Erro: Configuracoes invalidas")
        return 1

    logger.info("Configuracoes validadas")
    logger.info(f"Dashboards: {len(config.yaml_config.get('dashboards', []))}")

    scheduler = create_scheduler()

    try:
        scheduler.start()
        print("\nMonitoramento iniciado! (Ctrl+C para parar)\n")
        scheduler.scheduler.start()
        return 0

    except KeyboardInterrupt:
        print("\n\nParando monitoramento...")
        scheduler.stop()
        logger.info("Parado pelo usuario")
        return 0

    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
