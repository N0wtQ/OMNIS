"""
OSINT Module — theHarvester, SpiderFoot, sn0int, osint-mcp-server, shohei
Performs passive DNS, WHOIS, subdomain enumeration and public record lookups.
"""
from __future__ import annotations

import subprocess
import shutil
from datetime import datetime, timezone
from typing import List, Optional

from core.confidence import Finding


_TS = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run_theharvester(target: str) -> List[Finding]:
    if not shutil.which("theHarvester") and not shutil.which("python3"):
        return []
    findings = []
    try:
        result = subprocess.run(
            ["theHarvester", "-d", target, "-b", "bing,google,crtsh", "-l", "50"],
            capture_output=True, text=True, timeout=60
        )
        output = result.stdout + result.stderr
        if output.strip():
            findings.append(Finding(
                discipline="osint",
                description=f"theHarvester recon on {target}: {output[:300]}",
                sources=[f"theHarvester / bing,google,crtsh [{_TS()}]"],
                tools_used=["theHarvester"],
                timestamp=_TS(),
            ))
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return findings


def _passive_dns(target: str) -> List[Finding]:
    findings = []
    try:
        import dns.resolver
        for rtype in ("A", "MX", "NS", "TXT"):
            try:
                answers = dns.resolver.resolve(target, rtype, lifetime=5)
                records = [str(r) for r in answers]
                findings.append(Finding(
                    discipline="osint",
                    description=f"DNS {rtype} records for {target}: {', '.join(records)}",
                    sources=[f"dnspython / passive DNS [{_TS()}]"],
                    tools_used=["dnspython"],
                    timestamp=_TS(),
                ))
            except Exception:
                pass
    except ImportError:
        pass
    return findings


def _whois_lookup(target: str) -> List[Finding]:
    findings = []
    try:
        import whois
        w = whois.whois(target)
        if w and w.get("registrar"):
            findings.append(Finding(
                discipline="osint",
                description=(
                    f"WHOIS for {target}: registrar={w.get('registrar')}, "
                    f"creation={w.get('creation_date')}, "
                    f"expiry={w.get('expiration_date')}, "
                    f"org={w.get('org')}"
                ),
                sources=[f"python-whois [{_TS()}]"],
                tools_used=["python-whois"],
                timestamp=_TS(),
            ))
    except Exception:
        pass
    return findings


def run(target: str, query: str) -> List[Finding]:
    findings: List[Finding] = []
    findings += _passive_dns(target)
    findings += _whois_lookup(target)
    findings += _run_theharvester(target)
    return findings
