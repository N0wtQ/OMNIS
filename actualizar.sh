#!/usr/bin/env bash
# ============================================================
#  O.M.N.I.S — Actualizador (Linux Mint / Ubuntu / macOS)
#
#  Trae los últimos cambios fusionados en GitHub (main) y
#  actualiza las dependencias, sin tocar tu fichero .env.
#
#  Uso:
#     chmod +x actualizar.sh
#     ./actualizar.sh
# ============================================================
set -e

VERDE="\033[0;32m"; AZUL="\033[0;36m"; AMAR="\033[1;33m"; FIN="\033[0m"
paso()  { echo -e "\n${AZUL}==> $1${FIN}"; }
ok()    { echo -e "${VERDE}✔ $1${FIN}"; }
aviso() { echo -e "${AMAR}⚠ $1${FIN}"; }

cd "$(dirname "$0")"

# ── 1. Traer los últimos cambios de main ────────────────────
paso "Paso 1/3 — Descargando los últimos cambios de GitHub (main)"
git checkout main
git fetch origin main

# Si hay cambios locales sin guardar, avisar (el .env está ignorado y no cuenta)
if ! git diff --quiet || ! git diff --cached --quiet; then
    aviso "Tienes cambios locales sin guardar en archivos versionados."
    aviso "Se conservarán, pero si el pull da conflicto usa:  git reset --hard origin/main"
fi

git pull origin main
ok "Código actualizado a la última versión"

# ── 2. Actualizar dependencias de Python ────────────────────
paso "Paso 2/3 — Actualizando las librerías de Python"
if [ -d ".venv" ]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
    ok "Entorno virtual activado"
else
    aviso "No hay entorno .venv. Ejecuta primero ./instalar-mint.sh"
    exit 1
fi
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
ok "Dependencias al día"

# ── 3. Listo ────────────────────────────────────────────────
paso "Paso 3/3 — Comprobación rápida"
python -c "import web.app" 2>/dev/null && ok "La aplicación importa correctamente" \
    || aviso "Revisa posibles errores de importación tras la actualización"

VER=$(git rev-parse --short HEAD)
echo -e "\n${VERDE}════════════════════════════════════════════════════${FIN}"
echo -e "${VERDE}  O.M.N.I.S ACTUALIZADO  (versión ${VER})${FIN}"
echo -e "${VERDE}════════════════════════════════════════════════════${FIN}"
echo -e "\nTu fichero .env (con las claves) NO se ha tocado."
echo -e "Para arrancar:  ${AZUL}source .venv/bin/activate && python web/app.py${FIN}\n"

read -r -p "¿Arrancar O.M.N.I.S ahora? [s/N] " r
if [[ "$r" =~ ^[sSyY]$ ]]; then
    python web/app.py
fi
