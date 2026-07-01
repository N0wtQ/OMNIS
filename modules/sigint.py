"""
SIGINT / ELINT / COMINT Module — DNS, TLS, BGP, RDAP infrastructure analysis
"""
from __future__ import annotations

import socket
import ssl
import requests
from datetime import datetime, timezone
from typing import List

from core.confidence import Finding


_TS = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
_HEADERS = {"User-Agent": "OMNIS-Intelligence/1.0 (research)"}


def _tls_fingerprint(target: str) -> List[Finding]:
    """Grab TLS certificate details from the target host."""
    findings = []
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.create_connection((target, 443), timeout=8), server_hostname=target) as s:
            cert = s.getpeercert()
            subject = dict(x[0] for x in cert.get("subject", []))
            issuer = dict(x[0] for x in cert.get("issuer", []))
            san = cert.get("subjectAltName", [])
            findings.append(Finding(
                discipline="sigint",
                description=(
                    f"TLS cert for {target}: CN={subject.get('commonName')}, "
                    f"issuer={issuer.get('organizationName')}, "
                    f"expires={cert.get('notAfter')}, "
                    f"SANs={[v for _, v in san[:5]]}"
                ),
                sources=[f"SSL/TLS handshake direct [{_TS()}]"],
                tools_used=["ssl (Python stdlib)"],
                timestamp=_TS(),
            ))
    except Exception:
        pass
    return findings


def _bgp_prefix_lookup(target: str) -> List[Finding]:
    """Query BGPView API for ASN/prefix data."""
    findings = []
    try:
        resp = requests.get(
            f"https://api.bgpview.io/search?query_term={target}",
            headers=_HEADERS,
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            asns = data.get("asns", [])[:3]
            prefixes = data.get("ipv4_prefixes", [])[:3]
            parts = []
            if asns:
                parts.append("ASNs: " + ", ".join(f"AS{a.get('asn')} {a.get('name')}" for a in asns))
            if prefixes:
                parts.append("Prefixes: " + ", ".join(p.get("prefix", "") for p in prefixes))
            if parts:
                findings.append(Finding(
                    discipline="sigint",
                    description=f"BGPView for '{target}': {'; '.join(parts)}",
                    sources=[f"BGPView API [{_TS()}]"],
                    tools_used=["BGPView"],
                    timestamp=_TS(),
                ))
    except Exception:
        pass
    return findings


def _rdap_lookup(target: str) -> List[Finding]:
    findings = []
    try:
        resp = requests.get(
            f"https://rdap.org/domain/{target}",
            headers=_HEADERS,
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            name = data.get("ldhName", target)
            status = data.get("status", [])
            entities = [e.get("vcardArray", [[]])[1] for e in data.get("entities", [])[:2] if e.get("vcardArray")]
            findings.append(Finding(
                discipline="sigint",
                description=f"RDAP for {name}: status={status}, entities_count={len(data.get('entities', []))}",
                sources=[f"RDAP.org [{_TS()}]"],
                tools_used=["RDAP"],
                timestamp=_TS(),
            ))
    except Exception:
        pass
    return findings


def run(target: str, query: str) -> List[Finding]:
    findings: List[Finding] = []
    findings += _tls_fingerprint(target)
    findings += _bgp_prefix_lookup(target)
    findings += _rdap_lookup(target)
    return findings
