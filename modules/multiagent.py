"""
Motor Multi-Agente — inspirado en MiroFish.
Cada disciplina de O.M.N.I.S se convierte en un agente autónomo que:
  1. Recibe el objetivo e historial de hallazgos previos
  2. Razona usando un LLM (Gemini o Groq)
  3. Propone hipótesis y extrae IOC
  4. Pasa el contexto al siguiente agente

Al final, un AgenteSíntesis fusiona todos los hallazgos en el informe AEAD.
Soporta Google Gemini (GEMINI_API_KEY) y Groq (GROQ_API_KEY).
"""
from __future__ import annotations

import os
import json
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional

try:
    import google.generativeai as genai
    _GEMINI_AVAILABLE = True
except ImportError:
    _GEMINI_AVAILABLE = False

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
DEFAULT_MODEL_GROQ = "llama-3.3-70b-versatile"
DEFAULT_MODEL_GEMINI = "gemini-2.0-flash"

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
        "Eres un analista de TECHINT especializado en fingerprinting. "
        "Para CADA servicio identifica el SOFTWARE y la VERSIÓN concretos: servidor "
        "web (nginx, Apache, IIS, LiteSpeed), CDN/WAF (Cloudflare, Akamai, Fastly, "
        "Imperva, Fortinet FortiWeb, Sucuri, F5 BIG-IP), servidor DNS (BIND, PowerDNS, "
        "Knot), servidor de correo (Exchange, Postfix, Exim) y CMS/framework "
        "(WordPress, Laravel, Drupal). Indica el método de detección y evalúa si hay "
        "versiones obsoletas o vulnerables."
    ),
}

SYNTHESIS_PERSONA = (
    "Eres el Agente Síntesis de O.M.N.I.S, un analista de inteligencia profesional que "
    "redacta según los estándares de agencias (NSA/CNI/FBI) y del método OSINT investigativo. "
    "Reglas de redacción OBLIGATORIAS:\n"
    "1. SEPARA hecho de inferencia: primero el dato objetivo, después su interpretación.\n"
    "2. LENGUAJE NARRATIVO DE CONFIANZA (no uses solo Alto/Medio/Bajo): "
    "'Las evidencias establecen con elevada confianza que…', 'Los datos sugieren que…', "
    "'Los datos son compatibles con varios escenarios, resultando en confianza baja…'.\n"
    "3. HIPÓTESIS EN COMPETENCIA: plantea 2-3 hipótesis y evalúa cuál soporta mejor la "
    "convergencia de evidencias independientes.\n"
    "4. EVIDENCIA NEGATIVA: declara qué búsquedas no dieron resultados y qué límite imponen.\n"
    "5. Markdown puro, sin HTML. Responde en español, tono sobrio y defendible."
)


def _llamar_llm(client, model: str, sistema: str, usuario: str,
                json_mode: bool = False, max_tokens: int = 1024) -> str:
    """Capa de abstracción para Gemini y Groq/OpenAI."""
    if hasattr(client, "generate_content"):
        # Cliente Gemini
        instruccion_json = "\nResponde ÚNICAMENTE con JSON válido, sin markdown." if json_mode else ""
        prompt = f"{sistema}\n\n{usuario}{instruccion_json}"
        resp = client.generate_content(prompt)
        return resp.text
    else:
        # Cliente OpenAI / Groq
        kwargs: dict = dict(
            model=model,
            messages=[
                {"role": "system", "content": sistema},
                {"role": "user", "content": usuario},
            ],
            temperature=0.3,
            max_tokens=max_tokens,
        )
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        resp = client.chat.completions.create(**kwargs)
        return resp.choices[0].message.content


class AgenteDisiplinar:
    def __init__(self, disciplina: str, client, model: str):
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
            '{"hallazgos": ["DATO OBSERVADO: <hecho objetivo>. INTERPRETACIÓN: <qué implica y '
            'por qué, separando hecho de inferencia>."], '
            '"ioc": {"ips": [], "dominios": [], "emails": [], "hashes": [], "wallets": []}, '
            '"hipotesis": [{"enunciado": "hipótesis que explica los datos", '
            '"confianza": "Muy Alta|Alta|Media|Baja", '
            '"fundamento": "por qué, según la convergencia de evidencias"}], '
            '"evidencia_negativa": ["búsqueda que no dio resultados y el límite que impone"], '
            '"confianza": "Alto|Medio|Bajo", '
            '"herramientas": ["herramienta1"]}'
        )
        usuario = (
            f"OBJETIVO DE INVESTIGACIÓN: {objetivo}\n"
            f"CONSULTA: {consulta}\n"
            f"{ctx_bloque}\n\n"
            f"Analiza el objetivo desde tu disciplina ({self.disciplina.upper()}) como un "
            f"analista profesional. Para CADA hallazgo separa el DATO OBSERVADO (hecho) de la "
            f"INTERPRETACIÓN (inferencia). Plantea hipótesis en competencia con confianza "
            f"narrativa y declara la evidencia negativa (búsquedas sin resultado). "
            f"Responde ÚNICAMENTE con JSON válido con este formato exacto:\n{formato_json}"
        )

        try:
            contenido = _llamar_llm(self.client, self.model, self.persona, usuario, json_mode=True)
            # Limpiar markdown si el modelo lo incluye
            if "```" in contenido:
                contenido = contenido.split("```")[1]
                if contenido.startswith("json"):
                    contenido = contenido[4:]
            resultado = json.loads(contenido.strip())
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
    def __init__(self, client, model: str):
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

        def _fmt_hip(res):
            hip = res.get("hipotesis", [])
            if isinstance(hip, list):
                return " | ".join(
                    f"{h.get('enunciado','')} ({h.get('confianza','')})"
                    if isinstance(h, dict) else str(h) for h in hip
                ) or "N/A"
            return str(hip) or "N/A"

        resumen_agentes = "\n\n".join(
            f"=== {disc.upper()} ===\n"
            f"Datos e interpretación: {' || '.join(res.get('hallazgos', []))}\n"
            f"Hipótesis: {_fmt_hip(res)}\n"
            f"Evidencia negativa: {'; '.join(res.get('evidencia_negativa', [])) or 'no declarada'}\n"
            f"Confianza: {res.get('confianza', 'N/A')}\n"
            f"Herramientas: {', '.join(res.get('herramientas', []))}"
            for disc, res in resultados_por_disciplina.items()
        )

        usuario = (
            f"OBJETIVO: {objetivo}\nCONSULTA: {consulta}\n\n"
            f"MATERIAL DE LOS AGENTES:\n{resumen_agentes}\n\n"
            f"Redacta un INFORME DE INTELIGENCIA PROFESIONAL en español, Markdown puro (sin "
            f"HTML), con esta estructura de 7 secciones EXACTA:\n\n"
            f"## 1. Encabezado y datos del mandato\n"
            f"(objetivo, pregunta clave de inteligencia, fecha, disciplinas ejecutadas)\n\n"
            f"## 2. Resumen ejecutivo\n"
            f"(respuesta sintética a la pregunta clave, hallazgos principales, hipótesis "
            f"dominante y confianza global en lenguaje narrativo — máx. una página)\n\n"
            f"## 3. Metodología\n"
            f"(herramientas y fuentes consultadas, alcance y limitaciones del método)\n\n"
            f"## 4. Evidencias recopiladas\n"
            f"(lista de datos objetivos observados, agrupados por disciplina)\n\n"
            f"## 5. Análisis\n"
            f"(por disciplina: **Datos observados** → **Interpretación** [separa hecho de "
            f"inferencia] → **Hipótesis en competencia** evaluadas por convergencia de "
            f"evidencias, con confianza narrativa)\n\n"
            f"## 6. Límites y recomendaciones\n"
            f"(evidencia negativa y lo que NO se pudo verificar; próximos pasos accionables "
            f"con enfoque periodístico GIJN)\n\n"
            f"## 7. Apéndices\n"
            f"(fuentes/URLs consultadas y nota de cadena de custodia)\n\n"
            f"Usa SIEMPRE lenguaje narrativo de confianza, nunca 'Alto/Medio/Bajo' a secas."
        )

        try:
            sintesis = _llamar_llm(self.client, self.model, SYNTHESIS_PERSONA, usuario,
                                   json_mode=False, max_tokens=4096)
        except Exception as e:
            sintesis = f"Error en síntesis: {e}"

        if progreso_cb:
            progreso_cb("📄 Síntesis completada — generando informe final...")

        return sintesis


class MultiAgentEngine:
    """
    Orquestador multi-agente al estilo MiroFish.
    Detecta automáticamente GEMINI_API_KEY (prioridad) o GROQ_API_KEY.
    """

    def __init__(
        self,
        disciplinas: Optional[List[str]] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: str = GROQ_BASE_URL,
    ):
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
