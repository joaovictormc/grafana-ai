#!/usr/bin/env python3
"""Teste Fase 4: Notificacoes"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from src.notification_router import create_notification_router

def test_phase_4():
    print("\n" + "="*60)
    print("TEST: FASE 4 - Notificacoes")
    print("="*60 + "\n")
    router = create_notification_router()
    print("[4.1] Testando canais...")
    channels = router.test_channels()
    for channel, success in channels.items():
        print(f"  {'[OK]' if success else '[FAIL]'} {channel}")
    print("\n[4.2] Testando envio alerta...")
    analysis = {"status": "WARNING", "severity": 6, "reason": "CPU alta", "affected": ["Servidor01"], "recommendation": "Investigar"}
    results = router.send_alert(analysis, "Infra")
    print(f"  Dashboard: {results.get('dashboard')}")
    print(f"  Status: {results.get('status')}")
    print(f"  Canais: {list(results.get('channels', {}).keys())}")
    print("\n" + "="*60)
    print("SUCCESS: FASE 4 OK")
    print("="*60 + "\n")
    return True

if __name__ == "__main__":
    sys.exit(0 if test_phase_4() else 1)
