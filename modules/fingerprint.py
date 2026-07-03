"""
Módulo de Fingerprinting — identificación de software e infraestructura.

Detecta qué software usa un objetivo (servidor web, CDN, WAF, servidor DNS,
servidor de correo, CMS/framework) mediante técnicas gratuitas y pasivas:

  • Cabeceras HTTP (Server, X-Powered-By, Via, cookies)
  • Firmas de CDN/WAF (Cloudflare, Akamai, Fastly, Fortinet, Imperva, Sucuri…)
  • Consulta CHAOS `version.bind` al servidor DNS autoritativo
  • Banner SMTP del servidor de correo (MX)

No requiere API keys. Cada detección indica el método usado y su confianza.
"""
from __future__ import annotations

import socket
import ssl
from datetime import datetime, timezone
from typing import Dict, List, Optional

from core.confidence import Finding

_TS = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
_UA = {"User-Agent": "OMNIS-Intelligence/1.0 (research)"}

# ── Firmas de CDN / WAF por cabecera (clave de cabecera → producto) ──
# Se comprueba por presencia de la cabecera o por valor contenido.
_FIRMAS_CABECERA = {
    "cf-ray": "Cloudflare (CDN/WAF)",
    "cf-cache-status": "Cloudflare (CDN)",
    "x-amz-cf-id": "Amazon CloudFront (CDN)",
    "x-akamai-transformed": "Akamai (CDN)",
    "x-akamai-request-id": "Akamai (CDN)",
    "x-fastly-request-id": "Fastly (CDN)",
    "x-sucuri-id": "Sucuri (WAF)",
    "x-sucuri-cache": "Sucuri (WAF)",
    "x-iinfo": "Imperva Incapsula (WAF)",
    "x-cdn": "CDN genérico",
    "x-fortigate": "Fortinet FortiGate (Firewall)",
    "fortiwafsid": "Fortinet FortiWeb (WAF)",
    "x-sourdough": "Section.io (CDN)",
    "x-azure-ref": "Microsoft Azure Front Door (CDN/WAF)",
    "x-cache": "Caché/CDN (Varnish/CloudFront/Akamai)",
    "x-varnish": "Varnish (Caché)",
}

# Firmas por valor de la cabecera Server (subcadena → producto)
_FIRMAS_SERVER = {
    "cloudflare": "Cloudflare (CDN/WAF)",
    "nginx": "nginx (servidor web)",
    "apache": "Apache HTTP Server (servidor web)",
    "microsoft-iis": "Microsoft IIS (servidor web)",
    "litespeed": "LiteSpeed (servidor web)",
    "openresty": "OpenResty / nginx (servidor web)",
    "caddy": "Caddy (servidor web)",
    "gunicorn": "Gunicorn (WSGI Python)",
    "awselb": "AWS Elastic Load Balancer",
    "akamaighost": "Akamai (CDN)",
    "cloudfront": "Amazon CloudFront (CDN)",
    "fortiweb": "Fortinet FortiWeb (WAF)",
    "big-ip": "F5 BIG-IP (balanceador/WAF)",
    "squid": "Squid (proxy)",
}

# Firmas de CMS/framework por cookie o cabecera
_FIRMAS_TECH = {
    "wordpress": "WordPress (CMS)",
    "wp-": "WordPress (CMS)",
    "laravel_session": "Laravel (framework PHP)",
    "ci_session": "CodeIgniter (framework PHP)",
    "django": "Django (framework Python)",
    "csrftoken": "Django (framework Python)",
    "jsessionid": "Java (servlet/JSP)",
    "asp.net": "ASP.NET (framework Microsoft)",
    "phpsessid": "PHP",
    "x-drupal": "Drupal (CMS)",
}


def _http_headers(target: str) -> Dict[str, str]:
    """Obtiene las cabeceras HTTP(S) del objetivo."""
    import requests
    for esquema in ("https", "http"):
        try:
            r = requests.get(f"{esquema}://{target}", headers=_UA, timeout=10,
                             allow_redirects=True)
            # Normalizar a minúsculas
            h = {k.lower(): v for k, v in r.headers.items()}
            h["_set-cookie"] = "; ".join(r.cookies.keys())
            return h
        except Exception:
            continue
    return {}


def _detectar_web_cdn_waf(target: str) -> List[Finding]:
    findings: List[Finding] = []
    headers = _http_headers(target)
    if not headers:
        return findings

    detectados: Dict[str, str] = {}  # producto → método

    # Servidor web (cabecera Server)
    server = headers.get("server", "")
    if server:
        for firma, producto in _FIRMAS_SERVER.items():
            if firma in server.lower():
                detectados[f"{producto} [{server}]"] = "cabecera Server"
        if not any(f in server.lower() for f in _FIRMAS_SERVER):
            detectados[f"Servidor: {server}"] = "cabecera Server"

    # CDN / WAF por cabeceras específicas
    for cab, producto in _FIRMAS_CABECERA.items():
        if cab in headers:
            detectados[producto] = f"cabecera {cab}"

    # X-Powered-By y generador
    xpb = headers.get("x-powered-by")
    if xpb:
        detectados[f"X-Powered-By: {xpb}"] = "cabecera X-Powered-By"
    gen = headers.get("x-generator")
    if gen:
        detectados[f"Generador: {gen}"] = "cabecera X-Generator"

    # CMS/framework por cookies y cabeceras
    cookies = headers.get("_set-cookie", "").lower()
    blob = cookies + " " + " ".join(headers.keys())
    for firma, producto in _FIRMAS_TECH.items():
        if firma in blob:
            detectados.setdefault(producto, "cookie/cabecera")

    for producto, metodo in detectados.items():
        findings.append(Finding(
            discipline="techint",
            description=f"Software identificado en {target}: {producto} (detectado por {metodo})",
            sources=[f"Fingerprinting HTTP [{_TS()}]"],
            tools_used=["Fingerprinting de cabeceras HTTP"],
            timestamp=_TS(),
            raw_data={"componente": producto, "metodo": metodo},
        ))
    return findings


def _detectar_dns_software(target: str) -> List[Finding]:
    """Consulta CHAOS TXT version.bind al servidor DNS autoritativo."""
    findings: List[Finding] = []
    try:
        import dns.resolver
        import dns.query
        import dns.message

        # Obtener los NS del dominio
        try:
            ns_answers = dns.resolver.resolve(target, "NS", lifetime=5)
            servidores = [str(r).rstrip(".") for r in ns_answers]
        except Exception:
            servidores = []

        for ns in servidores[:2]:
            try:
                ns_ip = str(dns.resolver.resolve(ns, "A", lifetime=5)[0])
                consulta = dns.message.make_query("version.bind", "TXT",
                                                  rdclass=dns.rdataclass.CHAOS)
                resp = dns.query.udp(consulta, ns_ip, timeout=4)
                for rr in resp.answer:
                    version = " ".join(str(item).strip('"') for item in rr.items)
                    if version:
                        findings.append(Finding(
                            discipline="techint",
                            description=(
                                f"Servidor DNS {ns} ({ns_ip}) revela versión: '{version}' "
                                f"— identifica el software DNS (BIND/PowerDNS/Knot/etc.)"
                            ),
                            sources=[f"Consulta CHAOS version.bind [{_TS()}]"],
                            tools_used=["dnspython (version.bind CHAOS)"],
                            timestamp=_TS(),
                            raw_data={"componente": "Servidor DNS", "ns": ns, "version": version},
                        ))
            except Exception:
                continue
    except ImportError:
        pass
    return findings


def _detectar_mail_software(target: str) -> List[Finding]:
    """Lee el banner SMTP del servidor de correo (MX) para identificar el software."""
    findings: List[Finding] = []
    try:
        import dns.resolver
        mx = dns.resolver.resolve(target, "MX", lifetime=5)
        servidores = sorted(
            [(r.preference, str(r.exchange).rstrip(".")) for r in mx]
        )
    except Exception:
        return findings

    for _, host in servidores[:1]:  # solo el MX principal
        try:
            with socket.create_connection((host, 25), timeout=6) as s:
                s.settimeout(6)
                banner = s.recv(1024).decode(errors="ignore").strip()
            if banner:
                producto = "desconocido"
                low = banner.lower()
                for firma, nombre in {
                    "exchange": "Microsoft Exchange", "postfix": "Postfix",
                    "exim": "Exim", "sendmail": "Sendmail", "zimbra": "Zimbra",
                    "microsoft esmtp": "Microsoft Exchange", "haraka": "Haraka",
                    "google": "Google Workspace (Gmail)", "outlook": "Microsoft 365",
                }.items():
                    if firma in low:
                        producto = nombre
                        break
                findings.append(Finding(
                    discipline="techint",
                    description=(
                        f"Servidor de correo {host}: software {producto} "
                        f"— banner SMTP: '{banner[:120]}'"
                    ),
                    sources=[f"Banner SMTP puerto 25 [{_TS()}]"],
                    tools_used=["Banner grabbing SMTP"],
                    timestamp=_TS(),
                    raw_data={"componente": "Servidor de correo", "host": host,
                              "producto": producto, "banner": banner[:200]},
                ))
        except Exception:
            continue
    return findings


def run(target: str) -> List[Finding]:
    """Ejecuta todas las técnicas de fingerprinting sobre un dominio."""
    findings: List[Finding] = []
    findings += _detectar_web_cdn_waf(target)
    findings += _detectar_dns_software(target)
    findings += _detectar_mail_software(target)
    return findings
