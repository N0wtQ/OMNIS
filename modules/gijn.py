"""
Módulo GIJN — Global Investigative Journalism Network.

Integra la metodología y los recursos del Centro de Recursos de GIJN
(https://gijn.org/es/recurso/) en las investigaciones de O.M.N.I.S:

  • Guías metodológicas de periodismo de investigación
  • Bases de datos abiertas por país (registros mercantiles, contratación...)
  • Técnicas de detección de contenido generado por IA

Es conocimiento curado (sin dependencias externas ni llamadas de red), por lo
que funciona siempre, incluso sin conexión. El módulo selecciona los recursos
más relevantes según el tipo de objetivo y las disciplinas empleadas, y produce
un bloque para el informe con ángulos de investigación al estilo GIJN.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class GuiaGIJN:
    titulo: str
    descripcion: str
    disciplinas: List[str] = field(default_factory=list)
    url: str = "https://gijn.org/es/recurso/"


# ── Guías metodológicas ─────────────────────────────────────────────
GUIAS: List[GuiaGIJN] = [
    GuiaGIJN(
        "Guía para investigar la rendición de cuentas de la IA",
        "Marco para examinar los aspectos técnicos fundamentales de la tecnología que sustenta la IA.",
        ["osint", "cybint", "techint"],
    ),
    GuiaGIJN(
        "Guía para detectar contenido generado por IA",
        "Siete técnicas avanzadas para identificar contenido probablemente generado por IA.",
        ["osint", "socmint"],
    ),
    GuiaGIJN(
        "Guía para investigar los algoritmos de las redes sociales",
        "Técnicas y buenas prácticas para investigar los algoritmos de Meta, TikTok y otras plataformas.",
        ["socmint"],
    ),
    GuiaGIJN(
        "Guía para investigar amenazas digitales",
        "Herramientas y recursos para investigar sitios web, campañas de desinformación y software espía.",
        ["cybint", "techint", "darkint"],
    ),
    GuiaGIJN(
        "Guía para investigar los combustibles fósiles",
        "Contexto y asesoramiento práctico para investigar la industria de los combustibles fósiles.",
        ["finint", "geoint"],
    ),
    GuiaGIJN(
        "Guía de fuente abierta para investigar a compañías chinas",
        "Fuentes valiosas y métodos prácticos para investigaciones centradas en China.",
        ["finint", "osint"],
    ),
    GuiaGIJN(
        "Guía para investigar emisiones de metano en vertederos",
        "Buenas prácticas, recursos clave y preguntas para investigar emisiones de metano.",
        ["geoint"],
    ),
    GuiaGIJN(
        "Rastreo de activos y estructuras societarias",
        "Metodología para seguir el rastro de propiedad de empresas y beneficiarios reales.",
        ["finint"],
    ),
]

# ── Bases de datos abiertas por país ────────────────────────────────
# Portales públicos de registros mercantiles, contratación y datos abiertos.
BASES_POR_PAIS: Dict[str, List[str]] = {
    "España": [
        "BORME — Boletín Oficial del Registro Mercantil (boe.es/borme)",
        "Plataforma de Contratación del Sector Público (contrataciondelestado.es)",
        "datos.gob.es — portal de datos abiertos",
    ],
    "Reino Unido": [
        "Companies House (find-and-update.company-information.service.gov.uk)",
        "Contracts Finder (gov.uk/contracts-finder)",
    ],
    "Estados Unidos": [
        "SEC EDGAR (sec.gov/edgar)",
        "USASpending.gov — contratación federal",
        "OpenCorporates (opencorporates.com)",
    ],
    "Internacional": [
        "OpenCorporates — base global de empresas",
        "OpenSanctions — sanciones y personas expuestas políticamente",
        "OCCRP Aleph — investigación de redes de corrupción",
        "Open Ownership — beneficiarios reales",
    ],
}

# ── Técnicas de detección de contenido generado por IA ──────────────
TECNICAS_DETECCION_IA: List[str] = [
    "Buscar inconsistencias anatómicas (manos, dientes, orejas) en imágenes",
    "Analizar metadatos EXIF y ausencia de datos de cámara",
    "Detectar patrones de iluminación y sombras físicamente imposibles",
    "Revisar texto de fondo distorsionado o carteles ilegibles",
    "Comprobar repetición de texturas y artefactos de difusión",
    "Verificar la fuente original mediante búsqueda inversa de imagen",
    "Contrastar la afirmación con fuentes primarias independientes",
]

# Heurística ligera: marcadores léxicos de posible texto generado por IA.
_MARCADORES_IA_TEXTO = [
    "as an ai language model", "como modelo de lenguaje", "i cannot provide",
    "no puedo proporcionar", "in conclusion,", "en conclusión,",
    "it is important to note", "es importante señalar",
]


def detectar_texto_ia(texto: str) -> Dict:
    """Heurística ligera para señalar posible texto generado por IA."""
    if not texto:
        return {"sospecha_ia": False, "marcadores": []}
    bajo = texto.lower()
    encontrados = [m for m in _MARCADORES_IA_TEXTO if m in bajo]
    return {"sospecha_ia": bool(encontrados), "marcadores": encontrados}


def _paises_relevantes(target: str, query: str) -> List[str]:
    """Detecta países mencionados para sugerir sus bases de datos."""
    texto = f"{target} {query}".lower()
    relevantes = []
    claves = {
        "España": ["españa", "spain", ".es", "madrid", "barcelona", "borme"],
        "Reino Unido": ["reino unido", "uk", "united kingdom", ".co.uk", "london", "londres"],
        "Estados Unidos": ["estados unidos", "usa", "eeuu", ".us", "sec", "washington"],
    }
    for pais, kws in claves.items():
        if any(k in texto for k in kws):
            relevantes.append(pais)
    relevantes.append("Internacional")  # siempre aplicable
    return list(dict.fromkeys(relevantes))


def guias_relevantes(disciplinas: List[str]) -> List[GuiaGIJN]:
    """Devuelve las guías cuyo ámbito cruza con las disciplinas usadas."""
    disc = set(disciplinas)
    return [g for g in GUIAS if disc.intersection(g.disciplinas)]


def construir_seccion(target: str, query: str, disciplinas: List[str]) -> str:
    """Genera el bloque GIJN para incrustar en el informe."""
    guias = guias_relevantes(disciplinas)
    paises = _paises_relevantes(target, query)

    lineas: List[str] = []

    lineas.append("  📚 Guías metodológicas aplicables:")
    if guias:
        for g in guias:
            lineas.append(f"    • {g.titulo}")
            lineas.append(f"      {g.descripcion}")
    else:
        lineas.append("    • (ninguna guía específica para estas disciplinas)")

    lineas.append("")
    lineas.append("  🗂️  Bases de datos abiertas recomendadas:")
    for pais in paises:
        lineas.append(f"    [{pais}]")
        for db in BASES_POR_PAIS.get(pais, []):
            lineas.append(f"      • {db}")

    lineas.append("")
    lineas.append("  🤖 Verificación de contenido (detección de IA):")
    for t in TECNICAS_DETECCION_IA[:5]:
        lineas.append(f"    • {t}")

    lineas.append("")
    lineas.append("  🔎 Ángulos de investigación sugeridos (enfoque periodístico):")
    lineas.append("    • ¿Quién se beneficia? Rastrea la propiedad última y los flujos de dinero.")
    lineas.append("    • Contrasta cada afirmación con al menos dos fuentes primarias independientes.")
    lineas.append("    • Documenta y preserva evidencias (capturas con fecha, hashes) para trazabilidad.")

    lineas.append("")
    lineas.append("  🌐 Centro de Recursos GIJN: https://gijn.org/es/recurso/")

    return "\n".join(lineas)


def recursos_json(target: str, query: str, disciplinas: List[str]) -> Dict:
    """Versión estructurada para la interfaz web / exportación."""
    return {
        "guias": [
            {"titulo": g.titulo, "descripcion": g.descripcion, "url": g.url}
            for g in guias_relevantes(disciplinas)
        ],
        "bases_datos": {p: BASES_POR_PAIS[p] for p in _paises_relevantes(target, query)},
        "tecnicas_deteccion_ia": TECNICAS_DETECCION_IA,
        "centro_recursos": "https://gijn.org/es/recurso/",
    }
