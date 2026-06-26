#!/usr/bin/env python3
"""Validar servicos externos: Evolution API e GLPI"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import config
from src.notifiers.whatsapp_notifier import WhatsAppNotifier
from src.notifiers.glpi_notifier import GLPINotifier

print("\n" + "="*60)
print("VALIDACAO DE SERVICOS EXTERNOS")
print("="*60 + "\n")

print("[1] Testando Evolution API (WhatsApp)...")
whatsapp = WhatsAppNotifier()
if whatsapp.test():
    print("    [OK] Evolution API conectado")
else:
    print("    [FAIL] Evolution API nao respondeu")
    print(f"    URL: {config.evolution_api_url}")
    print(f"    Instance: {config.evolution_instance_name}")

print("\n[2] Testando GLPI...")
glpi = GLPINotifier()
if glpi.test():
    print("    [OK] GLPI conectado")
else:
    print("    [FAIL] GLPI nao respondeu")
    print(f"    URL atual: {config.glpi_url}")
    print("    Acao: Atualizar URL no .env com URL de producao")

print("\n" + "="*60)
print("Apos atualizar URLs, rode novamente: python validate_services.py")
print("="*60 + "\n")
