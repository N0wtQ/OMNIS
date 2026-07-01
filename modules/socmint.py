"""
SOCMINT Module — Sherlock, Maigret
Username enumeration across social platforms.
"""
from __future__ import annotations

import subprocess
import shutil
from datetime import datetime, timezone
from typing import List

from core.confidence import Finding


_TS = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run_sherlock(username: str) -> List[Finding]:
    if not shutil.which("sherlock"):
        return []
    findings = []
    try:
        result = subprocess.run(
            ["sherlock", username, "--print-found", "--timeout", "10"],
            capture_output=True, text=True, timeout=120
        )
        hits = [line for line in result.stdout.splitlines() if line.startswith("[+]")]
        if hits:
            findings.append(Finding(
                discipline="socmint",
                description=f"Sherlock found {len(hits)} profiles for '{username}': " + "; ".join(hits[:5]),
                sources=[f"Sherlock [{_TS()}]"],
                tools_used=["Sherlock"],
                timestamp=_TS(),
            ))
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return findings


def _run_maigret(username: str) -> List[Finding]:
    if not shutil.which("maigret"):
        return []
    findings = []
    try:
        result = subprocess.run(
            ["maigret", username, "--print-found", "--timeout", "10"],
            capture_output=True, text=True, timeout=120
        )
        hits = [line for line in result.stdout.splitlines() if "[+]" in line]
        if hits:
            findings.append(Finding(
                discipline="socmint",
                description=f"Maigret found {len(hits)} profiles for '{username}': " + "; ".join(hits[:5]),
                sources=[f"Maigret 2000+ sites [{_TS()}]"],
                tools_used=["Maigret"],
                timestamp=_TS(),
            ))
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return findings


def run(target: str, query: str) -> List[Finding]:
    # target is treated as a potential username for SOCMINT
    username = target.split("@")[0].replace(" ", "").lower()
    findings: List[Finding] = []
    findings += _run_sherlock(username)
    findings += _run_maigret(username)
    if not findings:
        findings.append(Finding(
            discipline="socmint",
            description=f"No SOCMINT tools (Sherlock/Maigret) found installed. "
                        f"Install with: pip install sherlock-project maigret",
            sources=["OMNIS internal check"],
            tools_used=[],
            timestamp=_TS(),
        ))
    return findings
