"""
DARKINT / DARKWEBINT Module
Checks public breach indexes and paste sites (no direct dark web access).
OPSEC note: this module does NOT connect to .onion addresses directly.
"""
from __future__ import annotations

import requests
from datetime import datetime, timezone
from typing import List

from core.confidence import Finding


_TS = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
_HEADERS = {"User-Agent": "OMNIS-Intelligence/1.0 (research)"}


def _check_paste_search(target: str) -> List[Finding]:
    """Search psbdmp.ws for pastes mentioning the target (public API)."""
    findings = []
    try:
        resp = requests.get(
            f"https://psbdmp.ws/api/search/{target}",
            headers=_HEADERS,
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            count = data.get("count", 0)
            if count:
                findings.append(Finding(
                    discipline="darkint",
                    description=f"Paste search for '{target}': {count} pastes found on psbdmp.ws",
                    sources=[f"psbdmp.ws public API [{_TS()}]"],
                    tools_used=["psbdmp.ws"],
                    timestamp=_TS(),
                ))
    except Exception:
        pass
    return findings


def _threat_fox_ioc(target: str) -> List[Finding]:
    """Query ThreatFox (abuse.ch) for IOC matches — free public API."""
    findings = []
    try:
        resp = requests.post(
            "https://threatfox-api.abuse.ch/api/v1/",
            json={"query": "search_ioc", "search_term": target},
            headers=_HEADERS,
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("query_status") == "ok":
                iocs = data.get("data", [])[:5]
                if iocs:
                    desc = "; ".join(
                        f"ioc={i.get('ioc')} type={i.get('ioc_type')} malware={i.get('malware')}"
                        for i in iocs
                    )
                    findings.append(Finding(
                        discipline="darkint",
                        description=f"ThreatFox IOC hits for '{target}': {desc}",
                        sources=[f"ThreatFox / abuse.ch [{_TS()}]"],
                        tools_used=["ThreatFox"],
                        timestamp=_TS(),
                    ))
    except Exception:
        pass
    return findings


def run(target: str, query: str) -> List[Finding]:
    findings: List[Finding] = []
    findings += _check_paste_search(target)
    findings += _threat_fox_ioc(target)
    return findings
