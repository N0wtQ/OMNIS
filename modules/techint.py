"""
TECHINT / CRIMINT / VEHINT / MASINT / FISINT Module
Technology stack fingerprinting, Wayback Machine, Shodan community data.
"""
from __future__ import annotations

import requests
from datetime import datetime, timezone
from typing import List

from core.confidence import Finding


_TS = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
_HEADERS = {"User-Agent": "OMNIS-Intelligence/1.0 (research)"}


def _wayback_machine(target: str) -> List[Finding]:
    findings = []
    try:
        resp = requests.get(
            f"https://archive.org/wayback/available?url={target}",
            headers=_HEADERS,
            timeout=10,
        )
        if resp.status_code == 200:
            snap = resp.json().get("archived_snapshots", {}).get("closest", {})
            if snap:
                findings.append(Finding(
                    discipline="techint",
                    description=(
                        f"Wayback Machine: {target} — latest snapshot "
                        f"at {snap.get('timestamp')}: {snap.get('url')}"
                    ),
                    sources=[f"archive.org Wayback API [{_TS()}]"],
                    tools_used=["Wayback Machine"],
                    timestamp=_TS(),
                ))
    except Exception:
        pass
    return findings


def _crt_sh(target: str) -> List[Finding]:
    """Certificate transparency logs via crt.sh."""
    findings = []
    try:
        resp = requests.get(
            f"https://crt.sh/?q={target}&output=json",
            headers=_HEADERS,
            timeout=15,
        )
        if resp.status_code == 200:
            certs = resp.json()[:10]
            names = list(dict.fromkeys(c.get("name_value", "") for c in certs))[:10]
            if names:
                findings.append(Finding(
                    discipline="techint",
                    description=(
                        f"crt.sh Certificate Transparency for '{target}': "
                        f"{len(certs)} certs found. Names: {', '.join(names[:5])}"
                    ),
                    sources=[f"crt.sh CT logs [{_TS()}]"],
                    tools_used=["crt.sh"],
                    timestamp=_TS(),
                ))
    except Exception:
        pass
    return findings


def _http_headers(target: str) -> List[Finding]:
    findings = []
    try:
        resp = requests.head(
            f"https://{target}",
            headers=_HEADERS,
            timeout=8,
            allow_redirects=True,
        )
        interesting = {
            k: v for k, v in resp.headers.items()
            if k.lower() in (
                "server", "x-powered-by", "x-generator", "via",
                "x-frame-options", "content-security-policy", "strict-transport-security",
            )
        }
        if interesting:
            findings.append(Finding(
                discipline="techint",
                description=f"HTTP headers for {target}: " + "; ".join(f"{k}={v}" for k, v in interesting.items()),
                sources=[f"HTTP HEAD request [{_TS()}]"],
                tools_used=["requests (HTTP fingerprinting)"],
                timestamp=_TS(),
            ))
    except Exception:
        pass
    return findings


def run(target: str, query: str) -> List[Finding]:
    findings: List[Finding] = []
    findings += _wayback_machine(target)
    findings += _crt_sh(target)
    findings += _http_headers(target)
    return findings
