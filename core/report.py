from datetime import datetime, timezone
from typing import Dict, List, Optional

from core.confidence import ConfidenceLevel, Finding, aggregate_confidence
from core.ioc_extractor import IOCBundle


REPORT_TEMPLATE = """\
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄  INFORME DE INTELIGENCIA — O.M.N.I.S
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Fecha              : {timestamp}
Consulta           : {query}
Nivel de confianza : {confidence}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔹 RESUMEN EJECUTIVO
{executive_summary}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔹 ANÁLISIS POR DISCIPLINA
{discipline_analysis}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔹 CORRELACIÓN CRUZADA
{cross_correlation}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔹 RECURSOS Y METODOLOGÍA GIJN
{gijn_section}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔹 EXTRACCIÓN DE IOC Y ACTIVOS
{ioc_section}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔹 RECOMENDACIONES
{recommendations}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔹 FUENTES
{sources}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

DISCIPLINE_EMOJIS = {
    "osint": "🌐 OSINT",
    "socmint": "📱 SOCMINT",
    "geoint": "🛰️  GEOINT / IMINT / ORBINT",
    "darkint": "🌑 DARKINT / DARKWEBINT",
    "finint": "💰 FININT / BLOCKINT",
    "cybint": "⚔️  CTI / CYBINT",
    "sigint": "📡 SIGINT / ELINT / COMINT",
    "techint": "🔧 TECHINT / CRIMINT / VEHINT / MASINT",
}


def _format_ioc_section(ioc: IOCBundle) -> str:
    d = ioc.to_dict()
    if not d:
        return "  No se identificaron IOC en esta investigación."
    labels = {
        "ips": "IPs",
        "domains": "Dominios",
        "emails": "Emails",
        "hashes_md5": "Hashes MD5",
        "hashes_sha256": "Hashes SHA-256",
        "urls": "URLs",
        "usernames": "Usuarios",
        "wallets_btc": "Wallets BTC",
        "wallets_eth": "Wallets ETH",
        "companies": "Empresas / Activos",
        "other": "Otros",
    }
    lines = []
    for key, label in labels.items():
        values = d.get(key, [])
        if values:
            lines.append(f"  {label}:\n" + "\n".join(f"    • {v}" for v in values))
    return "\n".join(lines)


def build_report(
    query: str,
    findings_by_discipline: Dict[str, List[Finding]],
    ioc: IOCBundle,
    cross_correlation: str = "",
    recommendations: str = "",
    gijn_section: str = "",
) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    all_findings = [f for flist in findings_by_discipline.values() for f in flist]
    overall_confidence = aggregate_confidence(all_findings)

    # Executive summary
    disciplines_used = [k for k, v in findings_by_discipline.items() if v]
    tools_used = list(
        dict.fromkeys(t for f in all_findings for t in f.tools_used)
    )
    exec_summary = (
        f"  Disciplinas utilizadas : {', '.join(disciplines_used) or 'N/A'}\n"
        f"  Herramientas utilizadas: {', '.join(tools_used) or 'N/A'}\n"
        f"  Total de hallazgos     : {len(all_findings)}\n"
        f"  Nivel de confianza     : {overall_confidence.value}\n"
    )
    if all_findings:
        exec_summary += "\n  Hallazgos clave:\n"
        for f in all_findings[:5]:
            exec_summary += f"    • [{f.confidence.value}] {f.description}\n"

    # Discipline analysis
    discipline_blocks = []
    for disc_key, label in DISCIPLINE_EMOJIS.items():
        findings = findings_by_discipline.get(disc_key, [])
        block = f"#### {label}\n"
        if not findings:
            block += "  Sin hallazgos para esta disciplina.\n"
        else:
            tools = list(dict.fromkeys(t for f in findings for t in f.tools_used))
            block += f"  Herramientas: {', '.join(tools) or 'N/A'}\n"
            for f in findings:
                block += f"  [{f.confidence.value}] {f.description}\n"
                if f.sources:
                    block += "    Fuentes: " + ", ".join(f.sources) + "\n"
        discipline_blocks.append(block)

    # Sources
    source_lines = []
    for f in all_findings:
        for src in f.sources:
            source_lines.append(f"  • [{f.timestamp or timestamp}] {src} — {f.description[:60]}")
    sources_text = "\n".join(source_lines) if source_lines else "  Sin fuentes registradas."

    return REPORT_TEMPLATE.format(
        timestamp=timestamp,
        query=query,
        confidence=overall_confidence.value,
        executive_summary=exec_summary,
        discipline_analysis="\n".join(discipline_blocks),
        cross_correlation=cross_correlation or "  Sin correlaciones cruzadas identificadas.",
        gijn_section=gijn_section or "  Sin recursos GIJN aplicados.",
        ioc_section=_format_ioc_section(ioc),
        recommendations=recommendations or "  Sin recomendaciones adicionales.",
        sources=sources_text,
    )
