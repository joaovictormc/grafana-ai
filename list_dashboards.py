#!/usr/bin/env python3
"""
Script auxiliar: Listar todos os dashboards e seus UIDs
Executar: python list_dashboards.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.grafana_client import create_grafana_client


def list_dashboards():
    """Lista todos os dashboards"""
    client = create_grafana_client()

    print("\nListando dashboards no Grafana...\n")

    try:
        response = client.session.get(
            f"{client.base_url}/api/search?type=dash-db",
            timeout=10
        )
        response.raise_for_status()
        dashboards = response.json()

        if not dashboards:
            print("[WARN] Nenhum dashboard encontrado")
            return

        print(f"[OK] {len(dashboards)} dashboard(s) encontrados:\n")
        for i, dash in enumerate(dashboards, 1):
            uid = dash.get("uid", "N/A")
            title = dash.get("title", "Sem titulo")
            print(f"{i}. Title: {title}")
            print(f"   UID:   {uid}")
            print(f"   URL:   /d/{uid}/")
            print()

    except Exception as e:
        print(f"[ERROR] Erro ao listar dashboards: {e}")


if __name__ == "__main__":
    list_dashboards()
