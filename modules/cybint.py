"""
CTI / CYBINT Module — ThreatFox, URLhaus, MalwareBazaar, AbuseIPDB
All public/free APIs, no key required for basic queries.
"""
from __future__ import annotations

import requests
from datetime import datetime, timezone
from typing import List

from core.confidence import Finding


_TS = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
_HEADERS = {"User-Agent": "OMNIS-Intelligence/1.0 (research)"}


def _urlhaus_lookup(target: str) -> List[Finding]:
    findings = []
    try:
        resp = requests.post(
            "https://urlhaus-api.abuse.ch/v1/host/",
            data={"host": target},
            headers=_HEADERS,
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("query_status") == "is_host":
                urls = data.get("urls", [])[:5]
                desc = f"URLhaus: {len(urls)} malicious URLs for host '{target}'"
                if urls:
                    desc += ": " + "; ".join(u.get("url", "") for u in urls[:3])
                findings.append(Finding(
                    discipline="cybint",
                    description=desc,
                    sources=[f"URLhaus / abuse.ch [{_TS()}]"],
                    tools_used=["URLhaus"],
                    timestamp=_TS(),
                ))
    except Exception:
        pass
    return findings


def _malwarebazaar_lookup(target: str) -> List[Finding]:
    """Search MalwareBazaar for hash or tag."""
    findings = []
    try:
        payload = {"query": "get_taginfo", "tag": target, "limit": 5}
        resp = requests.post(
            "https://mb-api.abuse.ch/api/v1/",
            data=payload,
            headers=_HEADERS,
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("query_status") == "ok":
                samples = data.get("data", [])[:3]
                if samples:
                    desc = "; ".join(
                        f"sha256={s.get('sha256_hash','?')[:16]}... "
                        f"type={s.get('file_type')} sig={s.get('signature')}"
                        for s in samples
                    )
                    findings.append(Finding(
                        discipline="cybint",
                        description=f"MalwareBazaar tag '{target}': {desc}",
                        sources=[f"MalwareBazaar / abuse.ch [{_TS()}]"],
                        tools_used=["MalwareBazaar"],
                        timestamp=_TS(),
                    ))
    except Exception:
        pass
    return findings


def _abuseipdb_check(ip: str) -> List[Finding]:
    findings = []
    try:
        # Public endpoint without key returns limited data
        resp = requests.get(
            f"https://api.abuseipdb.com/api/v2/check",
            params={"ipAddress": ip, "maxAgeInDays": 90},
            headers={**_HEADERS, "Key": ""},
            timeout=8,
        )
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            score = data.get("abuseConfidenceScore", 0)
            total = data.get("totalReports", 0)
            findings.append(Finding(
                discipline="cybint",
                description=f"AbuseIPDB: IP {ip} — abuse score={score}%, reports={total}",
                sources=[f"AbuseIPDB [{_TS()}]"],
                tools_used=["AbuseIPDB"],
                timestamp=_TS(),
            ))
    except Exception:
        pass
    return findings


def run(target: str, query: str) -> List[Finding]:
    findings: List[Finding] = []
    findings += _urlhaus_lookup(target)
    findings += _malwarebazaar_lookup(target)
    # If target looks like an IP, also check AbuseIPDB
    import re
    if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", target):
        findings += _abuseipdb_check(target)
    return findings
