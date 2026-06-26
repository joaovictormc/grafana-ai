"""
Fase 3: LLM Analyzer
Integra Claude API para analise inteligente de metricas.
"""

import logging
import json
from typing import Dict, Any, Optional
import os
from anthropic import Anthropic
from src.config import config

logger = logging.getLogger(__name__)


class LLMAnalyzer:
    """Analisa metricas usando Claude API"""

    def __init__(self):
        os.environ["ANTHROPIC_API_KEY"] = config.claude_api_key
        self.client = Anthropic(api_key=config.claude_api_key)
        self.model = config.claude_model

    def analyze_metrics(self, metrics_text: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Analisa metricas usando Claude. Retorna JSON com status, severity, reason."""
        system_prompt = """Voce eh um especialista em infraestrutura de rede.
Analise as metricas e responda em JSON: {status, severity, reason, affected, recommendation}
Status: OK | WARNING | CRITICAL
Severity: 1-10 (numerico)"""

        user_prompt = metrics_text
        if context:
            user_prompt += f"\n\nContexto:\n{context}"

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=300,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            response_text = message.content[0].text

            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                logger.warning("Claude nao retornou JSON valido")
                return {
                    "status": "WARNING",
                    "severity": 5,
                    "reason": "Parse error",
                    "affected": [],
                    "recommendation": "Revisar manualmente"
                }

        except Exception as e:
            logger.error(f"Erro Claude API: {e}")
            return {"status": "ERROR", "severity": 0, "reason": str(e), "affected": [], "recommendation": None}

    def format_analysis(self, analysis: Dict[str, Any]) -> str:
        """Formata analise em texto legivel"""
        status = analysis.get("status", "UNKNOWN")
        severity = analysis.get("severity", 0)
        reason = analysis.get("reason", "N/A")
        affected = analysis.get("affected", [])
        recommendation = analysis.get("recommendation")

        lines = [
            f"Status: {status}",
            f"Severidade: {severity}/10",
            f"Motivo: {reason}",
        ]

        if affected:
            lines.append(f"Afetados: {', '.join(affected)}")
        if recommendation:
            lines.append(f"Recomendacao: {recommendation}")

        return "\n".join(lines)


def create_llm_analyzer() -> LLMAnalyzer:
    return LLMAnalyzer()
