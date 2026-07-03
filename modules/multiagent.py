"""
Motor Multi-Agente — inspirado en MiroFish.
Cada disciplina de O.M.N.I.S se convierte en un agente autónomo que:
  1. Recibe el objetivo e historial de hallazgos previos
  2. Razona usando un LLM gratuito (Groq — llama-3.3-70b-versatile)
  3. Propone hipótesis y extrae IOC
  4. Pasa el contexto al siguiente agente

Al final, un AgenteSíntesis fusiona todos los hallazgos en el informe AEAD.
Usa la API de Groq (gratis, compatible con OpenAI SDK).
"""
from __future__ import annotations

import os
import json
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional

try:
    from openai import OpenAI
    _OPENAI_AVAILABLE = True
except ImportError:
    _OPENAI_AVAILABLE = False

from core.confidence import Finding
from core.ioc_extractor import IOCBundle, extract_iocs
from core.report import build_report


_TS = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_MODEL = "llama-3.3-70b-versatile"

DISCIPLINE_PERSONAS = {
    "osint": (
        "Eres un especialista en OSINT (Open-Source Intelligence). "
        "Analizas registros DNS, WHOIS, certificados TLS y datos públicos. "
        "Identificas subdominios, IPs, registradores y patrones de infraestructura."
    ),
    "socmint": (
        "Eres un analista de SOCMINT (Social Media Intelligence). "
        "Buscas perfiles, nombres de usuario, actividad en redes sociales "
        "y huellas digitales del objetivo en plataformas públicas."
    ),
    "geoint": (
        "Eres un analista de GEOINT/IMINT. "
        "Interpretas datos geoespaciales, rutas de vuelo, actividad marítima "
        "y coordenadas asociadas al objetivo."
    ),
    "darkint": (
        "Eres un analista de DARKINT. "
        "Investigas presencia en la dark web, filtraciones, foros clandestinos "
        "y menciones en pastes o mercados ilegales. Mantienes OPSEC estricto."
    ),
    "finint": (
        "Eres un analista de FININT/BLOCKINT. "
        "Rastreas transacciones blockchain, wallets, estructuras corporativas, "
        "sanciones OFAC y flujos financieros sospechosos."
    ),
    "cybint": (
        "Eres un analista de CTI/CYBINT (Cyber Threat Intelligence). "
        "Correlacionas IOC con amenazas conocidas, campañas de malware, "
        "actores APT y vulnerabilidades explotadas."
    ),
    "sigint": (
        "Eres un analista de SIGINT/ELINT. "
        "Analizas infraestructura de red, ASNs, prefijos BGP, certificados TLS, "
        "cabeceras HTTP y huellas de protocolos."
    ),
    "techint": (
        "Eres un analista de TECHINT. "
        "Examinas tecnologías usadas, versiones de software, historial en Wayback Machine, "
        "logs de Certificate Transparency y cabeceras de servidor."
    ),
}

SYNTHESIS_PERSONA = (
    "Eres el Agente Síntesis de O.M.N.I.S — Operational Multi-Node Intelligence System. "
    "Tu misión es fusionar los hallazgos de todos los agentes disciplinares en un único "
    "informe de inteligencia estructurado, identificar correlaciones cruzadas, "
    "contradicciones y generar recomendaciones accionables. "
    "Responde siempre en español. Sé preciso, conciso y objetivo."
)


class AgenteDisiplinar:
    def __init__(
        self,
        disciplina: str,
        client: "OpenAI",
        model: str = DEFAULT_MODEL,
    ):
        self.disciplina = disciplina
        self.client = client
        self.model = model
        self.persona = DISCIPLINE_PERSONAS.get(disciplina, "Eres un analista de inteligencia.")

    def analizar(
        self,
        objetivo: str,
        consulta: str,
        contexto_previo: str = "",
        progreso_cb: Optional[Callable] = None,
    ) -> Dict:
        if progreso_cb:
            progreso_cb(f"🔍 Agente {self.disciplina.upper()} analizando '{objetivo}'...")

        ctx_bloque = ("CONTEXTO DE AGENTES ANTERIORES:\n" + contexto_previo) if contexto_previo else ""
        formato_json = (
            '{"hallazgos": ["hallazgo 1", "hallazgo 2"], '
            '"ioc": {"ips": [], "dominios": [], "emails": [], "hashes": [], "wallets": []}, '
            '"hipotesis": "hipotesis principal", '
            '"confianza": "Alto|Medio|Bajo", '
            '"herramientas": ["herramienta1"]}'
        )
        mensajes = [
            {"role": "system", "content": self.persona},
            {
                "role": "user",
                "content": (
                    f"OBJETIVO DE INVESTIGACIÓN: {objetivo}\n"
                    f"CONSULTA: {consulta}\n"
                    f"{ctx_bloque}\n\n"
                    f"Analiza el objetivo desde tu disciplina ({self.disciplina.upper()}). "
                    f"Estructura tu respuesta en JSON con este formato exacto:\n{formato_json}"
                ),
            },
        ]

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=mensajes,
                temperature=0.3,
                max_tokens=1024,
                response_format={"type": "json_object"},
            )
            contenido = resp.choices[0].message.content
            resultado = json.loads(contenido)
        except Exception as e:
            resultado = {
                "hallazgos": [f"Error en agente {self.disciplina}: {e}"],
                "ioc": {},
                "hipotesis": "",
                "confianza": "Bajo",
                "herramientas": [],
            }

        if progreso_cb:
            n = len(resultado.get("hallazgos", []))
            progreso_cb(f"✅ Agente {self.disciplina.upper()} completado — {n} hallazgo(s) encontrado(s)")

        return resultado


class AgenteSintesis:
    def __init__(self, client: "OpenAI", model: str = DEFAULT_MODEL):
        self.client = client
        self.model = model

    def sintetizar(
        self,
        objetivo: str,
        consulta: str,
        resultados_por_disciplina: Dict[str, Dict],
        progreso_cb: Optional[Callable] = None,
    ) -> str:
        if progreso_cb:
            progreso_cb("🧠 Agente Síntesis fusionando hallazgos de todos los agentes...")

        resumen_agentes = "\n\n".join(
            f"=== {disc.upper()} ===\n"
            f"Hallazgos: {', '.join(res.get('hallazgos', []))}\n"
            f"Hipótesis: {res.get('hipotesis', 'N/A')}\n"
            f"Confianza: {res.get('confianza', 'N/A')}\n"
            f"Herramientas: {', '.join(res.get('herramientas', []))}"
            for disc, res in resultados_por_disciplina.items()
        )

        mensajes = [
            {"role": "system", "content": SYNTHESIS_PERSONA},
            {
                "role": "user",
                "content": (
                    f"OBJETIVO: {objetivo}\nCONSULTA: {consulta}\n\n"
                    f"HALLAZGOS DE TODOS LOS AGENTES:\n{resumen_agentes}\n\n"
                    f"Genera:\n"
                    f"1. Correlación cruzada entre disciplinas (patrones, contradicciones)\n"
                    f"2. Nivel de confianza general (Alto/Medio/Bajo) con justificación\n"
                    f"3. Top 5 hallazgos más relevantes\n"
                    f"4. Recomendaciones de próximos pasos\n"
                    f"Responde en español, formato de texto estructurado."
                ),
            },
        ]

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=mensajes,
                temperature=0.2,
                max_tokens=2048,
            )
            sintesis = resp.choices[0].message.content
        except Exception as e:
            sintesis = f"Error en síntesis: {e}"

        if progreso_cb:
            progreso_cb("📄 Síntesis completada — generando informe final...")

        return sintesis


class MultiAgentEngine:
    """
    Orquestador multi-agente al estilo MiroFish.
    Cada agente disciplinar analiza el objetivo de forma secuencial,
    compartiendo contexto con el siguiente agente.
    """

    def __init__(
        self,
        disciplinas: Optional[List[str]] = None,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        base_url: str = GROQ_BASE_URL,
    ):
        if not _OPENAI_AVAILABLE:
            raise ImportError("Instala openai: pip install openai")

        self.disciplinas = disciplinas or list(DISCIPLINE_PERSONAS.keys())
        self.model = model
        self.ultimos_datos = None
        self.client = OpenAI(
            api_key=api_key or os.environ.get("GROQ_API_KEY", ""),
            base_url=base_url,
        )

    def investigar(
        self,
        objetivo: str,
        consulta: str,
        progreso_cb: Optional[Callable] = None,
    ) -> str:
        timestamp = _TS()
        resultados: Dict[str, Dict] = {}
        contexto_acumulado = ""
        ioc_global = IOCBundle()

        if progreso_cb:
            progreso_cb(f"🚀 Motor multi-agente iniciado — {len(self.disciplinas)} agente(s) activo(s)")

        # Fase 1 & 2: cada agente disciplinar analiza y pasa contexto
        for disciplina in self.disciplinas:
            agente = AgenteDisiplinar(disciplina, self.client, self.model)
            resultado = agente.analizar(
                objetivo=objetivo,
                consulta=consulta,
                contexto_previo=contexto_acumulado,
                progreso_cb=progreso_cb,
            )
            resultados[disciplina] = resultado

            # Acumular contexto para el siguiente agente
            contexto_acumulado += (
                f"\n[{disciplina.upper()}] "
                + "; ".join(resultado.get("hallazgos", [])[:3])
            )

            # Extraer IOC del texto de hallazgos
            texto = " ".join(resultado.get("hallazgos", []))
            ioc_global.merge(extract_iocs(texto))

            # IOC estructurados del agente
            ioc_agente = resultado.get("ioc", {})
            if ioc_agente.get("ips"):
                ioc_global.ips = list(dict.fromkeys(ioc_global.ips + ioc_agente["ips"]))
            if ioc_agente.get("dominios"):
                ioc_global.domains = list(dict.fromkeys(ioc_global.domains + ioc_agente["dominios"]))
            if ioc_agente.get("emails"):
                ioc_global.emails = list(dict.fromkeys(ioc_global.emails + ioc_agente["emails"]))
            if ioc_agente.get("wallets"):
                ioc_global.wallets_btc = list(dict.fromkeys(ioc_global.wallets_btc + ioc_agente["wallets"]))

        # Fase 3: síntesis
        agente_sintesis = AgenteSintesis(self.client, self.model)
        sintesis = agente_sintesis.sintetizar(
            objetivo=objetivo,
            consulta=consulta,
            resultados_por_disciplina=resultados,
            progreso_cb=progreso_cb,
        )

        # Fase 4: construir findings para el generador de informes estándar
        findings_by_discipline: Dict[str, List[Finding]] = {}
        for disciplina, res in resultados.items():
            findings = []
            for hallazgo in res.get("hallazgos", []):
                findings.append(Finding(
                    discipline=disciplina,
                    description=hallazgo,
                    sources=[f"Agente LLM {disciplina.upper()} [{timestamp}]"],
                    tools_used=res.get("herramientas", ["LLM Multi-Agente"]),
                    timestamp=timestamp,
                ))
            findings_by_discipline[disciplina] = findings

        try:
            from modules import gijn
            gijn_section = gijn.construir_seccion(objetivo, consulta, self.disciplinas)
        except Exception:
            gijn_section = ""

        recomendaciones = (
            "  Generado por el motor multi-agente O.M.N.I.S.\n"
            "  Revisa la sección de correlación cruzada para recomendaciones detalladas."
        )

        texto = build_report(
            query=consulta,
            findings_by_discipline=findings_by_discipline,
            ioc=ioc_global,
            cross_correlation=sintesis,
            recommendations=recomendaciones,
            gijn_section=gijn_section,
        )

        # Datos estructurados para exportación a PDF
        try:
            from core.report_data import construir_datos
            self.ultimos_datos = construir_datos(
                objetivo=objetivo,
                consulta=consulta,
                findings_by_discipline=findings_by_discipline,
                ioc=ioc_global,
                correlacion=sintesis,
                recomendaciones=recomendaciones,
                gijn=gijn_section,
            )
        except Exception:
            self.ultimos_datos = None

        return texto
