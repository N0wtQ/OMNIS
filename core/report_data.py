"""
Construcción de datos estructurados del informe, compartida por el orquestador
clásico y el motor multi-agente. Alimenta tanto el generador de PDF
(`core/pdf_report.py`) como cualquier exportación estructurada (JSON).
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Dict, List

from core.confidence import Finding, aggregate_confidence
from core.ioc_extractor import IOCBundle
from core.report import DISCIPLINE_EMOJIS


def construir_datos(
    objetivo: str,
    consulta: str,
    findings_by_discipline: Dict[str, List[Finding]],
    ioc: IOCBundle,
    correlacion: str = "",
    recomendaciones: str = "",
    gijn: str = "",
) -> dict:
    """Devuelve el diccionario estructurado que consumen el PDF y la API."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    all_findings = [f for fl in findings_by_discipline.values() for f in fl]

    disciplinas = []
    for clave, findings in findings_by_discipline.items():
        etiqueta = DISCIPLINE_EMOJIS.get(clave, clave.upper())
        disciplinas.append({
            "clave": clave,
            "etiqueta": etiqueta,
            "confianza": aggregate_confidence(findings).value if findings else "Bajo",
            "hallazgos": [f.description for f in findings],
            "herramientas": list(dict.fromkeys(t for f in findings for t in f.tools_used)),
        })

    # Cadena de custodia: hash SHA-256 del dato objetivo de cada evidencia
    fuentes = []
    for f in all_findings:
        sha = hashlib.sha256(f.description.encode("utf-8")).hexdigest()
        for src in f.sources:
            fuentes.append(
                f"[{f.timestamp or timestamp}] {src} — {f.description[:70]} "
                f"(SHA-256: {sha[:16]}…)"
            )

    return {
        "objetivo": objetivo,
        "consulta": consulta,
        "timestamp": timestamp,
        "confianza_general": aggregate_confidence(all_findings).value,
        "disciplinas_activas": [d["clave"] for d in disciplinas],
        "disciplinas": disciplinas,
        "ioc": ioc.to_dict(),
        "correlacion": correlacion,
        "recomendaciones": recomendaciones,
        "gijn": gijn,
        "fuentes": fuentes,
    }
