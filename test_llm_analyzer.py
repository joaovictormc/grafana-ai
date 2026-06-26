#!/usr/bin/env python3
"""Teste Fase 3: LLM Analyzer"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.metrics_parser import create_metrics_parser
from src.llm_analyzer import create_llm_analyzer
from src.config import config


def test_phase_3():
    """Testa LLM Analyzer"""
    print("\n" + "="*60)
    print("TEST: FASE 3 - LLM Analyzer")
    print("="*60 + "\n")

    parser = create_metrics_parser()
    analyzer = create_llm_analyzer()

    dashboard_cfg = config.yaml_config.get("dashboards", [])[0]
    uid = dashboard_cfg.get("uid")

    print("[3.1] Extraindo metricas...")
    raw = parser.extract_critical_metrics(uid)
    normalized = parser.normalize_metrics(raw)
    llm_text = parser.format_for_llm(normalized)
    print("[OK] Metricas formatadas")

    print("\n[3.2] Analisando com Claude...")
    analysis = analyzer.analyze_metrics(llm_text)
    print("[OK] Analise recebida")

    print("\n[3.3] Formatando resultado...")
    formatted = analyzer.format_analysis(analysis)
    print(f"\n{formatted}")

    print("\n" + "="*60)
    print("SUCCESS: FASE 3 OK")
    print("="*60 + "\n")
    return True


if __name__ == "__main__":
    success = test_phase_3()
    sys.exit(0 if success else 1)
