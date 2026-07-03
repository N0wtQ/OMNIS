"""
Código Admiralty (OTAN) de fiabilidad de fuentes.

Asigna a cada evidencia un código de dos caracteres:
  • Letra (fiabilidad de la FUENTE): A (fiable) … F (no evaluable)
  • Número (credibilidad del CONTENIDO): 1 (confirmado) … 6 (no evaluable)

O.M.N.I.S clasifica automáticamente cada hallazgo según la herramienta/fuente
empleada, de forma determinista y transparente.
"""
from __future__ import annotations

from typing import List

# Descripción legible de cada código usado
DESCRIPCIONES = {
    "A1": "Fuente fiable, contenido confirmado (registros oficiales, DNS/WHOIS/TLS)",
    "A2": "Fuente fiable, contenido probablemente cierto (APIs de referencia)",
    "B2": "Fuente normalmente fiable, contenido probablemente cierto (recolección OSINT)",
    "B3": "Fuente normalmente fiable, contenido posiblemente cierto (redes sociales)",
    "C3": "Fuente no siempre fiable, contenido posiblemente cierto (dark web, pastes)",
    "F6": "Fiabilidad y credibilidad no evaluables",
}

# Reglas por palabras clave en las herramientas/fuentes (orden = prioridad)
_REGLAS = [
    # A1 — registros oficiales y protocolos verificables directamente
    (["dnspython", "passive dns", "whois", "rdap", "crt.sh", "certificate", "tls",
      "ssl", "borme", "opencorporates", "sec edgar", "version.bind", "bgpview"], "A1"),
    # A2 — APIs de referencia y feeds reputados
    (["virustotal", "abuseipdb", "shodan", "urlhaus", "malwarebazaar", "threatfox",
      "opensanctions", "blockchain", "blockcypher", "opensky", "nominatim",
      "wayback", "hunter.io", "fingerprinting"], "A2"),
    # B2 — recolección OSINT / correo
    (["theharvester", "spiderfoot", "recon-ng", "amass", "subfinder", "holehe",
      "escaneo de correos", "banner smtp", "http"], "B2"),
    # B3 — redes sociales / enumeración de usuarios
    (["sherlock", "maigret", "namechk", "socmint", "twitter", "linkedin",
      "instagram", "social"], "B3"),
    # C3 — dark web / pastes / filtraciones sin verificar
    (["dark", "onion", "paste", "psbdmp", "dehashed", "leak", "ahmia"], "C3"),
]


def codigo_admiralty(tools_used: List[str], sources: List[str]) -> str:
    """Devuelve el código Admiralty (p. ej. 'A1') para una evidencia."""
    blob = " ".join((tools_used or []) + (sources or [])).lower()
    for claves, codigo in _REGLAS:
        if any(k in blob for k in claves):
            return codigo
    return "F6"
