#!/usr/bin/env python3
"""
Script de teste: Fase 1 - Validar conexao e fetch de dados Grafana
Executar: python test_grafana.py
"""

import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.config import config
from src.grafana_client import create_grafana_client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_phase_1():
    """Testa todos os passos da Fase 1"""

    print("\n" + "="*60)
    print("TEST: FASE 1 - Setup & Integracao Grafana")
    print("="*60 + "\n")

    print("[1.1] Validando configuracoes...")
    if not config.validate():
        print("[FAIL] Configuracoes invalidas. Preencha .env")
        return False

    print("[OK] Configuracoes carregadas")
    print(f"  - Grafana: {config.grafana_url}")
    print(f"  - Dashboards: {len(config.yaml_config.get('dashboards', []))}")

    print("\n[1.2] Testando conexao Grafana...")
    client = create_grafana_client()
    if not client.test_connection():
        print("[FAIL] Conexao falhou")
        print("  Verifique GRAFANA_URL e GRAFANA_API_TOKEN")
        return False

    print("[OK] Conexao com Grafana estabelecida")

    print("\n[1.3] Listando datasources...")
    datasources = client.get_datasources()
    if datasources:
        print(f"[OK] {len(datasources)} datasource(s):")
        for ds in datasources:
            print(f"  - {ds.get('name')} ({ds.get('type')})")
    else:
        print("[WARN] Nenhum datasource encontrado")

    print("\n[1.4] Validando dashboards...")
    dashboards_config = config.yaml_config.get("dashboards", [])
    if not dashboards_config:
        print("[FAIL] Nenhum dashboard em config.yaml")
        return False

    success_count = 0
    for dashboard_cfg in dashboards_config:
        uid = dashboard_cfg.get("uid")
        name = dashboard_cfg.get("name")
        print(f"  Buscando: {name}...")

        dashboard = client.get_dashboard(uid)
        if not dashboard:
            print(f"    [FAIL] Nao encontrado")
            continue

        success_count += 1
        panels = client.get_panels_from_dashboard(uid)
        print(f"    [OK] Encontrado ({len(panels)} paineis)")

    if success_count == 0:
        print("[FAIL] Nenhum dashboard encontrado")
        return False

    print(f"\n[OK] {success_count}/{len(dashboards_config)} dashboards validados")

    print("\n" + "="*60)
    print("SUCCESS: FASE 1 OK")
    print("="*60 + "\n")

    return True


if __name__ == "__main__":
    success = test_phase_1()
    sys.exit(0 if success else 1)
