"""
GEOINT / IMINT / ORBINT Module — Leafmap, public flight/maritime APIs
"""
from __future__ import annotations

import requests
from datetime import datetime, timezone
from typing import List

from core.confidence import Finding


_TS = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
_HEADERS = {"User-Agent": "OMNIS-Intelligence/1.0 (research)"}


def _openstreetmap_nominatim(target: str) -> List[Finding]:
    findings = []
    try:
        resp = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": target, "format": "json", "limit": 3},
            headers=_HEADERS,
            timeout=10,
        )
        data = resp.json()
        if data:
            locs = [f"{d.get('display_name')} (lat={d.get('lat')}, lon={d.get('lon')})" for d in data[:3]]
            findings.append(Finding(
                discipline="geoint",
                description=f"OSM Nominatim geocoding for '{target}': {'; '.join(locs)}",
                sources=[f"OpenStreetMap Nominatim [{_TS()}]"],
                tools_used=["Nominatim / OSM"],
                timestamp=_TS(),
            ))
    except Exception:
        pass
    return findings


def _opensky_flights(target: str) -> List[Finding]:
    """Query OpenSky Network for flights related to the target ICAO/callsign."""
    findings = []
    try:
        resp = requests.get(
            "https://opensky-network.org/api/states/all",
            params={"time": 0},
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json()
            states = data.get("states", []) or []
            matches = [
                s for s in states
                if s[1] and target.lower() in str(s[1]).lower()
            ][:5]
            if matches:
                desc = "; ".join(
                    f"callsign={s[1].strip()} origin={s[2]} alt={s[7]}m" for s in matches
                )
                findings.append(Finding(
                    discipline="geoint",
                    description=f"OpenSky flights matching '{target}': {desc}",
                    sources=[f"OpenSky Network API [{_TS()}]"],
                    tools_used=["OpenSky Network"],
                    timestamp=_TS(),
                ))
    except Exception:
        pass
    return findings


def run(target: str, query: str) -> List[Finding]:
    findings: List[Finding] = []
    findings += _openstreetmap_nominatim(target)
    findings += _opensky_flights(target)
    return findings
