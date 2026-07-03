#!/usr/bin/env bash
# ============================================================
#  O.M.N.I.S — Instalador automático para Linux Mint / Ubuntu
#
#  Uso:
#     chmod +x instalar-mint.sh
#     ./instalar-mint.sh
#
#  Hace todo de una vez: instala Python, crea el entorno,
#  instala dependencias y prepara la configuración.
# ============================================================
set -e  # detenerse si algo falla

# ── Colores para que se lea bien ────────────────────────────
VERDE="\033[0;32m"; AZUL="\033[0;36m"; AMAR="\033[1;33m"; ROJO="\033[0;31m"; FIN="\033[0m"
paso()  { echo -e "\n${AZUL}==> $1${FIN}"; }
ok()    { echo -e "${VERDE}✔ $1${FIN}"; }
aviso() { echo -e "${AMAR}⚠ $1${FIN}"; }

echo -e "${AZUL}"
echo "   ██████╗ ███╗   ███╗███╗   ██╗██╗███████╗"
echo "  ██║   ██║██╔████╔██║██╔██╗ ██║██║███████╗"
echo "   ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝╚══════╝"
echo -e "  Instalador para Linux Mint / Ubuntu${FIN}\n"

# ── 1. Dependencias del sistema ─────────────────────────────
paso "Paso 1/5 — Instalando Python, pip, venv y git (pedirá tu contraseña)"
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git
ok "Dependencias del sistema instaladas"

# ── 2. Entorno virtual ──────────────────────────────────────
paso "Paso 2/5 — Creando entorno virtual aislado (.venv)"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    ok "Entorno virtual creado"
else
    aviso "El entorno .venv ya existía, se reutiliza"
fi
# shellcheck disable=SC1091
source .venv/bin/activate
ok "Entorno virtual activado"

# ── 3. Dependencias de Python ───────────────────────────────
paso "Paso 3/5 — Instalando las librerías de Python (puede tardar unos minutos)"
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
ok "Librerías instaladas"

# ── 4. Configuración (.env) ─────────────────────────────────
paso "Paso 4/5 — Preparando el fichero de configuración .env"
if [ ! -f ".env" ]; then
    cp .env.example .env
    ok "Fichero .env creado a partir de .env.example"
    aviso "Edita .env y añade tu clave de API (Gemini o Groq) si quieres el modo multi-agente."
    aviso "Comando para editarlo:  xed .env    (o:  nano .env )"
else
    aviso "Ya existía un .env, no se toca"
fi

# ── 5. Carpeta de informes ──────────────────────────────────
paso "Paso 5/5 — Últimos ajustes"
mkdir -p reports
ok "Todo listo"

# ── Resumen final ───────────────────────────────────────────
echo -e "\n${VERDE}════════════════════════════════════════════════════${FIN}"
echo -e "${VERDE}  INSTALACIÓN COMPLETADA${FIN}"
echo -e "${VERDE}════════════════════════════════════════════════════${FIN}"
echo -e "\nPara ARRANCAR O.M.N.I.S ahora mismo:\n"
echo -e "   ${AZUL}source .venv/bin/activate${FIN}"
echo -e "   ${AZUL}python web/app.py${FIN}\n"
echo -e "Luego abre el navegador en:  ${AMAR}http://localhost:5001${FIN}"
echo -e "El globo 3D está en el botón  ${AMAR}🛰️ Globo 3D${FIN}  (arriba a la derecha)\n"
echo -e "Para PARAR el servidor:  pulsa ${AMAR}Ctrl + C${FIN}\n"

# ── Preguntar si arrancar ya ────────────────────────────────
read -r -p "¿Quieres arrancar O.M.N.I.S ahora? [s/N] " respuesta
if [[ "$respuesta" =~ ^[sSyY]$ ]]; then
    paso "Arrancando O.M.N.I.S en http://localhost:5001 (Ctrl+C para parar)"
    python web/app.py
fi
