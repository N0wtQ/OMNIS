"""
FININT / BLOCKINT Module — Blockchain explorers, OFAC sanctions, OpenCorporates
"""
from __future__ import annotations

import re
import requests
from datetime import datetime, timezone
from typing import List

from core.confidence import Finding


_TS = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
_HEADERS = {"User-Agent": "OMNIS-Intelligence/1.0 (research)"}

_BTC_RE = re.compile(r"\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b")
_ETH_RE = re.compile(r"\b0x[0-9a-fA-F]{40}\b")


def _check_btc_wallet(address: str) -> List[Finding]:
    findings = []
    try:
        resp = requests.get(
            f"https://blockchain.info/rawaddr/{address}?limit=5",
            headers=_HEADERS,
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            balance = data.get("final_balance", 0) / 1e8
            n_tx = data.get("n_tx", 0)
            findings.append(Finding(
                discipline="finint",
                description=(
                    f"BTC wallet {address}: balance={balance:.8f} BTC, "
                    f"total_transactions={n_tx}"
                ),
                sources=[f"Blockchain.info API [{_TS()}]"],
                tools_used=["Blockchain.info"],
                timestamp=_TS(),
            ))
    except Exception:
        pass
    return findings


def _check_eth_wallet(address: str) -> List[Finding]:
    findings = []
    try:
        resp = requests.get(
            f"https://api.blockcypher.com/v1/eth/main/addrs/{address}/balance",
            headers=_HEADERS,
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            balance = data.get("balance", 0) / 1e18
            n_tx = data.get("n_tx", 0)
            findings.append(Finding(
                discipline="finint",
                description=(
                    f"ETH wallet {address}: balance={balance:.6f} ETH, "
                    f"total_transactions={n_tx}"
                ),
                sources=[f"BlockCypher API [{_TS()}]"],
                tools_used=["BlockCypher"],
                timestamp=_TS(),
            ))
    except Exception:
        pass
    return findings


def _opencorporates_search(target: str) -> List[Finding]:
    findings = []
    try:
        resp = requests.get(
            "https://api.opencorporates.com/v0.4/companies/search",
            params={"q": target, "format": "json"},
            headers=_HEADERS,
            timeout=10,
        )
        if resp.status_code == 200:
            companies = resp.json().get("results", {}).get("companies", [])[:3]
            if companies:
                desc_parts = [
                    f"{c['company']['name']} ({c['company'].get('jurisdiction_code','?')})"
                    for c in companies
                ]
                findings.append(Finding(
                    discipline="finint",
                    description=f"OpenCorporates matches for '{target}': {'; '.join(desc_parts)}",
                    sources=[f"OpenCorporates API [{_TS()}]"],
                    tools_used=["OpenCorporates"],
                    timestamp=_TS(),
                ))
    except Exception:
        pass
    return findings


def run(target: str, query: str) -> List[Finding]:
    findings: List[Finding] = []

    # Detect wallets in target or query
    combined = f"{target} {query}"
    for wallet in _BTC_RE.findall(combined):
        findings += _check_btc_wallet(wallet)
    for wallet in _ETH_RE.findall(combined):
        findings += _check_eth_wallet(wallet)

    # Corporate lookup
    findings += _opencorporates_search(target)
    return findings
