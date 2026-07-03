"""
Módulo de escaneo de correos — obligatorio al investigar dominios.

Combina tres fuentes gratuitas y las fusiona en una tabla con fuente, fiabilidad
y rol de cada correo:

  1. theHarvester  — recolección pasiva en buscadores (requiere el binario)
  2. Hunter.io     — búsqueda por dominio (requiere HUNTER_API_KEY; tier gratuito)
  3. Holehe        — en qué servicios está registrado cada correo (requiere binario)

Todas las fuentes degradan con elegancia: si una herramienta no está instalada o
no hay API key, se omite y se anota en el resumen, sin romper la investigación.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from typing import Dict, List

from core.confidence import Finding

_TS = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")

# Clasificación de rol según la parte local del correo
_ROLES = {
    "admin": ["admin", "administrator", "administrador", "webmaster", "root", "sysadmin"],
    "info": ["info", "informacion", "hello", "hola"],
    "contacto": ["contact", "contacto", "contacta"],
    "soporte": ["support", "soporte", "help", "ayuda", "sac"],
    "ventas": ["sales", "ventas", "comercial", "s"],
    "prensa": ["press", "prensa", "media", "comunicacion"],
    "rrhh": ["hr", "rrhh", "jobs", "empleo", "talento", "recruit"],
    "facturación": ["billing", "facturacion", "invoice", "pagos"],
    "seguridad": ["security", "seguridad", "abuse", "soc", "csirt"],
    "legal": ["legal", "dpo", "privacy", "privacidad"],
    "no-reply": ["noreply", "no-reply", "donotreply"],
}


def _clasificar_rol(email: str) -> str:
    local = email.split("@", 1)[0].lower()
    for rol, claves in _ROLES.items():
        if any(local == c or local.startswith(c) for c in claves):
            return rol
    return "personal/otro"


def _theharvester(dominio: str) -> Dict[str, str]:
    """Devuelve {email: fiabilidad} desde theHarvester."""
    encontrados: Dict[str, str] = {}
    if not shutil.which("theHarvester"):
        return encontrados
    try:
        res = subprocess.run(
            ["theHarvester", "-d", dominio, "-b", "bing,google,crtsh,duckduckgo", "-l", "100"],
            capture_output=True, text=True, timeout=90,
        )
        for m in _EMAIL_RE.findall(res.stdout + res.stderr):
            if m.lower().endswith(dominio.lower()):
                encontrados[m.lower()] = "Media"
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return encontrados


def _hunter(dominio: str) -> Dict[str, str]:
    """Devuelve {email: fiabilidad} desde Hunter.io (requiere HUNTER_API_KEY)."""
    encontrados: Dict[str, str] = {}
    api_key = os.environ.get("HUNTER_API_KEY")
    if not api_key:
        return encontrados
    try:
        import requests
        r = requests.get(
            "https://api.hunter.io/v2/domain-search",
            params={"domain": dominio, "api_key": api_key},
            timeout=15,
        )
        if r.status_code == 200:
            for e in r.json().get("data", {}).get("emails", []):
                valor = (e.get("value") or "").lower()
                if valor:
                    # Hunter marca el estado de verificación
                    verif = (e.get("verification", {}) or {}).get("status")
                    encontrados[valor] = "Alta" if verif == "valid" else "Media"
    except Exception:
        pass
    return encontrados


def _holehe(email: str) -> List[str]:
    """Servicios en los que el correo está registrado (Holehe)."""
    if not shutil.which("holehe"):
        return []
    servicios = []
    try:
        res = subprocess.run(
            ["holehe", "--only-used", email],
            capture_output=True, text=True, timeout=60,
        )
        for linea in res.stdout.splitlines():
            linea = linea.strip()
            # Holehe marca los usados con '[+]'
            if linea.startswith("[+]"):
                servicios.append(linea.replace("[+]", "").strip())
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return servicios


def escanear_correos(dominio: str, max_holehe: int = 5) -> dict:
    """
    Escanea correos de un dominio y devuelve una estructura con la tabla de
    correos (fuente, fiabilidad, rol, servicios) y un resumen de cobertura.
    """
    fuentes_usadas = []
    fuentes_omitidas = []

    th = _theharvester(dominio)
    (fuentes_usadas if shutil.which("theHarvester") else fuentes_omitidas).append("theHarvester")

    hu = _hunter(dominio)
    if os.environ.get("HUNTER_API_KEY"):
        fuentes_usadas.append("Hunter.io")
    else:
        fuentes_omitidas.append("Hunter.io (falta HUNTER_API_KEY)")

    # Fusionar correos y su fuente/fiabilidad
    correos: Dict[str, dict] = {}
    for email, fiab in th.items():
        correos.setdefault(email, {"fuentes": [], "fiabilidad": fiab})
        correos[email]["fuentes"].append("theHarvester")
    for email, fiab in hu.items():
        d = correos.setdefault(email, {"fuentes": [], "fiabilidad": fiab})
        d["fuentes"].append("Hunter.io")
        # Hunter verificado eleva la fiabilidad
        if fiab == "Alta":
            d["fiabilidad"] = "Alta"

    tiene_holehe = bool(shutil.which("holehe"))
    (fuentes_usadas if tiene_holehe else fuentes_omitidas).append(
        "Holehe" if tiene_holehe else "Holehe (no instalado)"
    )

    tabla = []
    for i, (email, d) in enumerate(sorted(correos.items())):
        servicios = _holehe(email) if (tiene_holehe and i < max_holehe) else []
        tabla.append({
            "email": email,
            "fuente": ", ".join(dict.fromkeys(d["fuentes"])),
            "fiabilidad": d["fiabilidad"],
            "rol": _clasificar_rol(email),
            "servicios": servicios,
        })

    resumen = (
        f"{len(tabla)} correo(s) encontrado(s). "
        f"Fuentes activas: {', '.join(fuentes_usadas) or 'ninguna'}. "
        + (f"Omitidas: {', '.join(fuentes_omitidas)}." if fuentes_omitidas else "")
    )

    return {"correos": tabla, "resumen": resumen,
            "fuentes_usadas": fuentes_usadas, "fuentes_omitidas": fuentes_omitidas}


def tabla_markdown(resultado: dict) -> str:
    """Renderiza la tabla de correos en Markdown plano (sin HTML)."""
    correos = resultado.get("correos", [])
    if not correos:
        return ("No se encontraron correos asociados. Puede indicar protección de "
                "privacidad WHOIS, escasa huella pública, o que las herramientas de "
                "escaneo (theHarvester/Hunter.io/Holehe) no están disponibles.")
    filas = ["| Correo | Rol | Fuente | Fiabilidad | Servicios (Holehe) |",
             "|--------|-----|--------|------------|--------------------|"]
    for c in correos:
        serv = ", ".join(c["servicios"][:6]) or "—"
        filas.append(f"| {c['email']} | {c['rol']} | {c['fuente']} | {c['fiabilidad']} | {serv} |")
    return "\n".join(filas)


def run_como_findings(dominio: str) -> List[Finding]:
    """Integración con el orquestador: convierte el escaneo en Finding(s)."""
    resultado = escanear_correos(dominio)
    correos = resultado.get("correos", [])
    if not correos:
        return []
    lista = "; ".join(f"{c['email']} ({c['rol']}, {c['fiabilidad']})" for c in correos)
    return [Finding(
        discipline="osint",
        description=f"Correos asociados a {dominio}: {lista}",
        sources=[f"Escaneo de correos (theHarvester/Hunter/Holehe) [{_TS()}]"],
        tools_used=["theHarvester", "Hunter.io", "Holehe"],
        timestamp=_TS(),
        raw_data={"escaneo_correos": resultado},
    )]
