#!/usr/bin/env python3
"""
Script de teste: Fase 2 - Parser de Metricas
Executar: python test_metrics_parser.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.config import config
from src.metrics_parser import create_metrics_parser


def test_phase_2():
    """Testa parser de metricas"""

    print("\n" + "="*60)
    print("TEST: FASE 2 - Parser de Metricas")
    print("="*60 + "\n")

    parser = create_metrics_parser()
    dashboards_config = config.yaml_config.get("dashboards", [])

    if not dashboards_config:
        print("[FAIL] Nenhum dashboard configurado")
        return False

    print("[2.1] Testando fetch de paineis...")
    for dashboard_cfg in dashboards_config:
        uid = dashboard_cfg.get("uid")
        name = dashboard_cfg.get("name")

        print(f"\n  Dashboard: {name} ({uid})")
        metrics = parser.fetch_dashboard_metrics(uid)

        if not metrics:
            print("    [FAIL] Nao conseguiu buscar metricas")
            return False

        panels = metrics.get("panels", [])
        print(f"    [OK] {len(panels)} paineis encontrados")

        if panels:
            for i, panel in enumerate(panels[:3]):
                print(f"      [{i+1}] {panel.get('title')} ({panel.get('type')})")
            if len(panels) > 3:
                print(f"      ... e mais {len(panels) - 3}")

    print("\n[2.2] Testando extracao de metricas criticas...")
    for dashboard_cfg in dashboards_config:
        uid = dashboard_cfg.get("uid")
        name = dashboard_cfg.get("name")

        print(f"\n  Dashboard: {name}")
        critical = parser.extract_critical_metrics(uid)

        if not critical:
            print("    [WARN] Nenhuma metrica critica encontrada")
            continue

        metrics = critical.get("metrics", {})
        print(f"    [OK] {len(metrics)} metricas criticas mapeadas")

        for metric_name, metric_data in list(metrics.items())[:3]:
            panel_title = metric_data.get("panel_title")
            print(f"      - {metric_name}")
            print(f"        Painel: {panel_title}")
            print(f"        Warning: {metric_data.get('threshold_warning')}")
            print(f"        Critical: {metric_data.get('threshold_critical')}")

    print("\n[2.3] Testando normalizacao...")
    dashboard_cfg = dashboards_config[0]
    uid = dashboard_cfg.get("uid")
    raw = parser.extract_critical_metrics(uid)
    normalized = parser.normalize_metrics(raw)

    print(f"\n  Dashboard: {normalized.get('dashboard')}")
    summary = normalized.get("summary", {})
    print(f"  Total metricas: {summary.get('total_metrics')}")
    print(f"  Criticas: {summary.get('critical_count')}")
    print(f"  Avisos: {summary.get('warning_count')}")

    print("\n[2.4] Testando formatacao para LLM...")
    llm_text = parser.format_for_llm(normalized)
    print(f"\n{llm_text}")

    print("\n" + "="*60)
    print("SUCCESS: FASE 2 OK")
    print("="*60 + "\n")

    return True


if __name__ == "__main__":
    success = test_phase_2()
    sys.exit(0 if success else 1)
