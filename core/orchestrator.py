"""
OMNIS Orchestrator — coordinates discipline modules under the AEAD framework.
"""
from __future__ import annotations

import importlib
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

from core.confidence import Finding
from core.ioc_extractor import IOCBundle, extract_iocs
from core.report import build_report


DISCIPLINE_MODULES = {
    "osint": "modules.osint",
    "socmint": "modules.socmint",
    "geoint": "modules.geoint",
    "darkint": "modules.darkint",
    "finint": "modules.finint",
    "cybint": "modules.cybint",
    "sigint": "modules.sigint",
    "techint": "modules.techint",
}


@dataclass
class InvestigationContext:
    query: str
    target: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    findings_by_discipline: Dict[str, List[Finding]] = field(default_factory=dict)
    ioc: IOCBundle = field(default_factory=IOCBundle)
    cross_correlation: str = ""
    recommendations: str = ""


class Orchestrator:
    def __init__(self, disciplines: Optional[List[str]] = None, verbose: bool = False):
        self.disciplines = disciplines or list(DISCIPLINE_MODULES.keys())
        self.verbose = verbose

    def _load_module(self, discipline: str):
        module_path = DISCIPLINE_MODULES.get(discipline)
        if not module_path:
            return None
        try:
            return importlib.import_module(module_path)
        except ImportError:
            return None

    def _run_discipline(self, discipline: str, ctx: InvestigationContext) -> List[Finding]:
        module = self._load_module(discipline)
        if module is None or not hasattr(module, "run"):
            return []
        try:
            return module.run(ctx.target, ctx.query) or []
        except Exception as e:
            if self.verbose:
                print(f"[WARN] {discipline}: {e}")
            return []

    def _cross_correlate(self, ctx: InvestigationContext) -> str:
        all_findings = [f for flist in ctx.findings_by_discipline.values() for f in flist]
        if not all_findings:
            return "Sin datos suficientes para correlación cruzada."

        disciplines_with_data = [
            d for d, fl in ctx.findings_by_discipline.items() if fl
        ]
        lines = [
            f"  Disciplinas con hallazgos: {', '.join(disciplines_with_data)}",
            f"  Total de hallazgos integrados: {len(all_findings)}",
        ]

        # Simple overlap detection: shared terms across disciplines
        term_counts: Dict[str, int] = {}
        for f in all_findings:
            for word in f.description.lower().split():
                if len(word) > 5:
                    term_counts[word] = term_counts.get(word, 0) + 1
        recurring = [t for t, c in term_counts.items() if c >= 2]
        if recurring:
            lines.append(f"  Términos recurrentes entre disciplinas: {', '.join(recurring[:10])}")

        return "\n".join(lines)

    def _generate_recommendations(self, ctx: InvestigationContext) -> str:
        disciplines_with_data = [
            d for d, fl in ctx.findings_by_discipline.items() if fl
        ]
        empty = [d for d in self.disciplines if d not in disciplines_with_data]
        recs = ["  Próximos pasos recomendados:"]
        if empty:
            recs.append(f"  • Ampliar investigación en: {', '.join(empty)}")
        if ctx.ioc.ips:
            recs.append("  • Realizar lookups de reputación para IPs identificadas")
        if ctx.ioc.domains:
            recs.append("  • Verificar historial DNS/WHOIS de los dominios extraídos")
        if ctx.ioc.wallets_btc or ctx.ioc.wallets_eth:
            recs.append("  • Rastrear flujos de transacciones en exploradores blockchain")
        if ctx.ioc.hashes_md5 or ctx.ioc.hashes_sha256:
            recs.append("  • Correlacionar hashes con bases de datos de malware (VirusTotal, MISP)")
        recs.append("  • Documentar y preservar evidencias para posible escalado legal")
        return "\n".join(recs)

    def investigate(self, query: str, target: str) -> str:
        ctx = InvestigationContext(query=query, target=target)

        # FASE 1 & 2: ACQUIRE + ENRICH — run each discipline module
        for discipline in self.disciplines:
            findings = self._run_discipline(discipline, ctx)
            ctx.findings_by_discipline[discipline] = findings
            # Extract IOCs from finding descriptions
            for f in findings:
                found = extract_iocs(f.description)
                ctx.ioc.merge(found)

        # FASE 3: ASSESS — cross-correlate
        ctx.cross_correlation = self._cross_correlate(ctx)
        ctx.recommendations = self._generate_recommendations(ctx)

        # Metodología GIJN — recursos periodísticos aplicables
        try:
            from modules import gijn
            gijn_section = gijn.construir_seccion(target, query, self.disciplines)
        except Exception:
            gijn_section = ""

        # FASE 4: DELIVER — build report
        return build_report(
            query=ctx.query,
            findings_by_discipline=ctx.findings_by_discipline,
            ioc=ctx.ioc,
            cross_correlation=ctx.cross_correlation,
            recommendations=ctx.recommendations,
            gijn_section=gijn_section,
        )
