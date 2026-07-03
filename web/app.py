"""
O.M.N.I.S — Interfaz web con motor multi-agente (inspirado en MiroFish).
Cada disciplina es un agente autónomo que razona con un LLM gratuito (Groq).
"""
import os
import sys
import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)  # necesario para que Flask encuentre templates/

from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from core.orchestrator import Orchestrator, DISCIPLINE_MODULES
from modules.multiagent import MultiAgentEngine

app = Flask(__name__, template_folder="templates")
app.secret_key = os.environ.get("SECRET_KEY", "omnis-dev-secret")

# Almacén en memoria de investigaciones activas
_investigations: dict = {}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/disciplinas")
def disciplinas():
    return jsonify(list(DISCIPLINE_MODULES.keys()))


@app.route("/api/investigar", methods=["POST"])
def investigar():
    data = request.get_json(force=True)
    objetivo = (data.get("objetivo") or "").strip()
    consulta = (data.get("consulta") or "").strip()
    disciplinas = data.get("disciplinas") or list(DISCIPLINE_MODULES.keys())
    modo_agente = data.get("modo_agente", False)

    if not objetivo:
        return jsonify({"error": "El campo 'objetivo' es obligatorio."}), 400

    inv_id = str(uuid.uuid4())
    _investigations[inv_id] = {
        "estado": "en_progreso",
        "objetivo": objetivo,
        "consulta": consulta or f"O.M.N.I.S: Investiga {objetivo}",
        "disciplinas": disciplinas,
        "modo_agente": modo_agente,
        "inicio": datetime.now(timezone.utc).isoformat(),
        "informe": None,
        "agentes": [],
        "error": None,
        "coordenadas": [],
    }

    def ejecutar():
        try:
            llm_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GROQ_API_KEY")
            if modo_agente and llm_key:
                engine = MultiAgentEngine(
                    disciplinas=disciplinas,
                )
                resultado = engine.investigar(
                    objetivo=objetivo,
                    consulta=_investigations[inv_id]["consulta"],
                    progreso_cb=lambda msg: _investigations[inv_id]["agentes"].append(msg),
                )
            else:
                orquestador = Orchestrator(disciplines=disciplinas)
                resultado = orquestador.investigate(
                    query=_investigations[inv_id]["consulta"],
                    target=objetivo,
                )
            _investigations[inv_id]["informe"] = resultado

            # Si GEOINT está activo, geocodificar el objetivo para el globo 3D
            if "geoint" in disciplinas:
                try:
                    from modules.geoint import geocodificar
                    _investigations[inv_id]["coordenadas"] = geocodificar(objetivo, limit=5)
                except Exception:
                    pass

            _investigations[inv_id]["estado"] = "completado"
        except Exception as e:
            _investigations[inv_id]["error"] = str(e)
            _investigations[inv_id]["estado"] = "error"

    threading.Thread(target=ejecutar, daemon=True).start()
    return jsonify({"id": inv_id})


@app.route("/api/estado/<inv_id>")
def estado(inv_id):
    inv = _investigations.get(inv_id)
    if not inv:
        return jsonify({"error": "Investigación no encontrada."}), 404
    return jsonify({
        "estado": inv["estado"],
        "agentes": inv["agentes"],
        "informe": inv["informe"],
        "error": inv["error"],
    })


@app.route("/api/stream/<inv_id>")
def stream(inv_id):
    """SSE — envía actualizaciones en tiempo real al navegador."""
    def generar():
        ultimo_idx = 0
        while True:
            inv = _investigations.get(inv_id)
            if not inv:
                yield f"data: {json.dumps({'error': 'no encontrada'})}\n\n"
                return

            # Enviar nuevos mensajes de agentes
            agentes = inv["agentes"]
            if len(agentes) > ultimo_idx:
                for msg in agentes[ultimo_idx:]:
                    yield f"data: {json.dumps({'tipo': 'agente', 'msg': msg})}\n\n"
                ultimo_idx = len(agentes)

            if inv["estado"] == "completado":
                yield f"data: {json.dumps({'tipo': 'completado', 'informe': inv['informe']})}\n\n"
                return
            if inv["estado"] == "error":
                yield f"data: {json.dumps({'tipo': 'error', 'msg': inv['error']})}\n\n"
                return

            import time
            time.sleep(0.8)

    return Response(
        stream_with_context(generar()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.route("/api/historial")
def historial():
    resumen = []
    for inv_id, inv in _investigations.items():
        resumen.append({
            "id": inv_id,
            "objetivo": inv["objetivo"],
            "estado": inv["estado"],
            "inicio": inv["inicio"],
            "modo_agente": inv["modo_agente"],
        })
    return jsonify(sorted(resumen, key=lambda x: x["inicio"], reverse=True))


@app.route("/globo")
def globo():
    """Vista del globo terráqueo 3D (CesiumJS)."""
    return render_template("globo.html")


@app.route("/api/globo/geocodificar")
def globo_geocodificar():
    """Geocodifica un objetivo vía OpenStreetMap Nominatim (gratis, sin API key)."""
    import requests
    q = (request.args.get("q") or "").strip()
    if not q:
        return jsonify({"resultados": []})
    try:
        resp = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": q, "format": "json", "limit": 5},
            headers={"User-Agent": "OMNIS-Intelligence/1.0 (research)"},
            timeout=10,
        )
        data = resp.json()
        resultados = [
            {
                "nombre": d.get("display_name"),
                "lat": float(d["lat"]),
                "lon": float(d["lon"]),
            }
            for d in data
        ]
    except Exception as e:
        return jsonify({"resultados": [], "error": str(e)})
    return jsonify({"resultados": resultados})


@app.route("/api/globo/investigacion/<inv_id>")
def globo_investigacion(inv_id):
    """Devuelve las coordenadas GEOINT de una investigación para pintarlas en el globo."""
    inv = _investigations.get(inv_id)
    if not inv:
        return jsonify({"error": "Investigación no encontrada.", "coordenadas": []}), 404
    return jsonify({
        "objetivo": inv["objetivo"],
        "estado": inv["estado"],
        "coordenadas": inv.get("coordenadas", []),
    })


@app.route("/api/globo/vuelos")
def globo_vuelos():
    """Vuelos en vivo (ADS-B) vía OpenSky Network — feed público sin API key."""
    import requests
    try:
        resp = requests.get(
            "https://opensky-network.org/api/states/all",
            headers={"User-Agent": "OMNIS-Intelligence/1.0 (research)"},
            timeout=15,
        )
        data = resp.json()
        estados = data.get("states", []) or []
        vuelos = []
        for s in estados[:400]:
            # s[5]=lon, s[6]=lat, s[7]=alt geométrica, s[1]=callsign
            if s[5] is not None and s[6] is not None:
                vuelos.append({
                    "callsign": (s[1] or "").strip() or "N/A",
                    "lon": s[5],
                    "lat": s[6],
                    "alt": s[7] or 0,
                    "pais": s[2],
                })
        return jsonify({"vuelos": vuelos, "total": len(vuelos)})
    except Exception as e:
        return jsonify({"vuelos": [], "total": 0, "error": str(e)})


@app.route("/api/mirofish/status")
def mirofish_status():
    """Comprueba si MiroFish está activo en el puerto 3000."""
    import urllib.request
    mirofish_url = os.environ.get("MIROFISH_URL", "http://localhost:3000")
    try:
        req = urllib.request.urlopen(mirofish_url, timeout=2)
        activo = req.status < 500
    except Exception:
        activo = False
    return jsonify({"activo": activo, "url": mirofish_url})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
