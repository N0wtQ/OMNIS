"""
Generador de informes PDF profesionales para O.M.N.I.S — basado en reportlab.

reportlab es Python puro (se instala con pip, sin librerías de sistema), por lo
que funciona en Linux, Windows, móvil y despliegues en la nube sin configuración
extra. Produce un PDF con portada, gráfico de confianza, tablas por disciplina,
tabla de IOC, sección GIJN y recomendaciones.

La función principal `construir_pdf(datos, mapa_png=None)` recibe un diccionario
estructurado (ver estructura en `core/report_data.py`) y devuelve los bytes del
PDF listos para descargar.
"""
from __future__ import annotations

import io
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, HRFlowable, PageBreak,
)
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart

# ── Paleta O.M.N.I.S ────────────────────────────────────────────────
AZUL = colors.HexColor("#0a0f1e")
ACENTO = colors.HexColor("#0088aa")
ORO = colors.HexColor("#b8860b")
GRIS = colors.HexColor("#555555")

_CONF_NUM = {"Alto": 3, "Medio": 2, "Bajo": 1}
_CONF_COLOR = {"Alto": colors.green, "Medio": colors.orange, "Bajo": colors.red}


def _estilos():
    ss = getSampleStyleSheet()
    ss.add(ParagraphStyle("OmnisTitulo", parent=ss["Title"], textColor=AZUL,
                          fontSize=26, spaceAfter=6))
    ss.add(ParagraphStyle("OmnisSub", parent=ss["Normal"], textColor=ACENTO,
                          fontSize=11, alignment=TA_CENTER, spaceAfter=2))
    ss.add(ParagraphStyle("OmnisSeccion", parent=ss["Heading2"], textColor=AZUL,
                          fontSize=13, spaceBefore=14, spaceAfter=6))
    ss.add(ParagraphStyle("OmnisTexto", parent=ss["Normal"], fontSize=9,
                          leading=13))
    ss.add(ParagraphStyle("OmnisMono", parent=ss["Code"], fontSize=8, leading=11,
                          textColor=colors.HexColor("#222222")))
    ss.add(ParagraphStyle("OmnisPie", parent=ss["Normal"], fontSize=7,
                          textColor=GRIS, alignment=TA_CENTER))
    return ss


def _grafico_confianza(disciplinas) -> Optional[Drawing]:
    """Gráfico de barras del nivel de confianza por disciplina."""
    datos = [(d["etiqueta"].split()[0], _CONF_NUM.get(d["confianza"], 0))
             for d in disciplinas if d.get("hallazgos")]
    if not datos:
        return None
    etiquetas = [d[0] for d in datos]
    valores = [d[1] for d in datos]

    dib = Drawing(460, 180)
    bc = VerticalBarChart()
    bc.x, bc.y, bc.width, bc.height = 30, 30, 400, 130
    bc.data = [valores]
    bc.strokeColor = colors.white
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = 3
    bc.valueAxis.valueStep = 1
    bc.categoryAxis.categoryNames = etiquetas
    bc.categoryAxis.labels.angle = 30
    bc.categoryAxis.labels.fontSize = 7
    bc.categoryAxis.labels.dy = -6
    bc.bars[0].fillColor = ACENTO
    dib.add(bc)
    return dib


def _pie_pagina(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(GRIS)
    canvas.drawCentredString(
        A4[0] / 2, 1.0 * cm,
        "O.M.N.I.S — Operational Multi-Node Intelligence System   ·   "
        "Inteligencia para todos, con la metodología de los mejores periodistas   ·   "
        f"Página {doc.page}",
    )
    canvas.restoreState()


def _p(texto, estilo):
    """Paragraph seguro: escapa < > & para no romper el marcado de reportlab."""
    seguro = (str(texto).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    return Paragraph(seguro, estilo)


def construir_pdf(datos: dict, mapa_png: Optional[bytes] = None) -> bytes:
    ss = _estilos()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=1.8 * cm, bottomMargin=1.8 * cm,
        title=f"Informe O.M.N.I.S — {datos.get('objetivo', '')}",
        author="O.M.N.I.S",
    )
    el = []

    # ── PORTADA ─────────────────────────────────────────────────────
    el.append(Spacer(1, 3 * cm))
    el.append(_p("O.M.N.I.S", ss["OmnisTitulo"]))
    el.append(_p("Operational Multi-Node Intelligence System", ss["OmnisSub"]))
    el.append(_p("Informe de Inteligencia de Fuentes Múltiples", ss["OmnisSub"]))
    el.append(Spacer(1, 1 * cm))
    el.append(HRFlowable(width="100%", color=ACENTO, thickness=1.5))
    el.append(Spacer(1, 0.6 * cm))

    conf = datos.get("confianza_general", "N/A")
    tabla_meta = Table([
        ["Objetivo", datos.get("objetivo", "N/A")],
        ["Consulta", datos.get("consulta", "N/A")],
        ["Fecha", datos.get("timestamp", "N/A")],
        ["Confianza general", conf],
        ["Disciplinas", ", ".join(datos.get("disciplinas_activas", [])) or "N/A"],
    ], colWidths=[4 * cm, 11 * cm])
    tabla_meta.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (0, -1), AZUL),
        ("TEXTCOLOR", (1, 3), (1, 3), _CONF_COLOR.get(conf, colors.black)),
        ("FONTNAME", (1, 3), (1, 3), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, colors.HexColor("#dddddd")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    el.append(tabla_meta)
    el.append(PageBreak())

    # ── RESUMEN EJECUTIVO + GRÁFICO ─────────────────────────────────
    el.append(_p("Resumen ejecutivo", ss["OmnisSeccion"]))
    total = sum(len(d.get("hallazgos", [])) for d in datos.get("disciplinas", []))
    usadas = [d["etiqueta"] for d in datos.get("disciplinas", []) if d.get("hallazgos")]
    el.append(_p(f"Total de hallazgos: <b>{total}</b>. "
                 f"Disciplinas con datos: {', '.join(usadas) or 'ninguna'}. "
                 f"Nivel de confianza general: <b>{conf}</b>.", ss["OmnisTexto"]))
    el.append(Spacer(1, 0.3 * cm))
    grafico = _grafico_confianza(datos.get("disciplinas", []))
    if grafico:
        el.append(_p("Nivel de confianza por disciplina (3=Alto, 2=Medio, 1=Bajo):",
                     ss["OmnisTexto"]))
        el.append(grafico)

    # ── MAPA (si hay captura del globo 3D) ──────────────────────────
    if mapa_png:
        try:
            el.append(_p("Vista geoespacial (GEOINT)", ss["OmnisSeccion"]))
            el.append(Image(io.BytesIO(mapa_png), width=15 * cm, height=8 * cm))
        except Exception:
            pass

    # ── ANÁLISIS POR DISCIPLINA ─────────────────────────────────────
    el.append(_p("Análisis por disciplina", ss["OmnisSeccion"]))
    for d in datos.get("disciplinas", []):
        hallazgos = d.get("hallazgos", [])
        if not hallazgos:
            continue
        el.append(_p(f"<b>{d['etiqueta']}</b> — confianza {d.get('confianza','N/A')} "
                     f"· herramientas: {', '.join(d.get('herramientas', [])) or 'N/A'}",
                     ss["OmnisTexto"]))
        filas = [[_p(f"• {h}", ss["OmnisTexto"])] for h in hallazgos]
        t = Table(filas, colWidths=[15 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f4f6fa")),
            ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#dfe4ee")),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        el.append(t)
        el.append(Spacer(1, 0.25 * cm))

    # ── CORRELACIÓN CRUZADA ─────────────────────────────────────────
    if datos.get("correlacion"):
        el.append(_p("Correlación cruzada", ss["OmnisSeccion"]))
        for linea in datos["correlacion"].split("\n"):
            if linea.strip():
                el.append(_p(linea, ss["OmnisTexto"]))

    # ── IOC ─────────────────────────────────────────────────────────
    ioc = datos.get("ioc", {})
    if ioc:
        el.append(_p("Extracción de IOC y activos", ss["OmnisSeccion"]))
        etiquetas = {
            "ips": "IPs", "domains": "Dominios", "emails": "Emails",
            "hashes_md5": "Hashes MD5", "hashes_sha256": "Hashes SHA-256",
            "urls": "URLs", "usernames": "Usuarios", "wallets_btc": "Wallets BTC",
            "wallets_eth": "Wallets ETH", "companies": "Empresas", "other": "Otros",
        }
        filas = [[_p("<b>Tipo</b>", ss["OmnisTexto"]), _p("<b>Valores</b>", ss["OmnisTexto"])]]
        for clave, etiqueta in etiquetas.items():
            valores = ioc.get(clave, [])
            if valores:
                filas.append([_p(etiqueta, ss["OmnisTexto"]),
                              _p(", ".join(valores), ss["OmnisMono"])])
        if len(filas) > 1:
            t = Table(filas, colWidths=[3.5 * cm, 11.5 * cm])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), AZUL),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#dfe4ee")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            el.append(t)

    # ── GIJN ────────────────────────────────────────────────────────
    if datos.get("gijn"):
        el.append(_p("Recursos y metodología GIJN", ss["OmnisSeccion"]))
        for linea in datos["gijn"].split("\n"):
            if linea.strip():
                el.append(_p(linea, ss["OmnisTexto"]))

    # ── RECOMENDACIONES ─────────────────────────────────────────────
    if datos.get("recomendaciones"):
        el.append(_p("Recomendaciones", ss["OmnisSeccion"]))
        for linea in datos["recomendaciones"].split("\n"):
            if linea.strip():
                el.append(_p(linea, ss["OmnisTexto"]))

    # ── FUENTES ─────────────────────────────────────────────────────
    fuentes = datos.get("fuentes", [])
    if fuentes:
        el.append(_p("Fuentes", ss["OmnisSeccion"]))
        for f in fuentes:
            el.append(_p(f"• {f}", ss["OmnisMono"]))

    doc.build(el, onFirstPage=_pie_pagina, onLaterPages=_pie_pagina)
    return buf.getvalue()
