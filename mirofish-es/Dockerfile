# ============================================================
#  MiroFish-ES — Imagen con soporte en español
#
#  Replica FIELMENTE el Dockerfile oficial de MiroFish
#  (python:3.11 + Node + uv, arranque con `npm run dev`) y solo
#  añade la inyección de la traducción al español. No usa nginx
#  ni scripts propios: deja que MiroFish arranque como está
#  diseñado (frontend Vite en :3000 y backend en :5001).
# ============================================================
FROM python:3.11

# Node.js (>=18) + git para clonar MiroFish
RUN apt-get update \
  && apt-get install -y --no-install-recommends nodejs npm git curl \
  && rm -rf /var/lib/apt/lists/*

# uv (gestor de paquetes Python que usa MiroFish)
COPY --from=ghcr.io/astral-sh/uv:0.9.26 /uv /uvx /bin/

WORKDIR /app

# Clonar MiroFish (shallow)
RUN git clone --depth 1 https://github.com/666ghj/MiroFish.git .

# ── Inyectar la traducción al español ────────────────────────
COPY locales/es.json /app/locales/es.json
COPY locales/languages.json /app/locales/languages.json
# Copia también dentro del frontend por si el glob de Vite carga desde ahí
RUN mkdir -p /app/frontend/locales \
  && cp /app/locales/es.json /app/frontend/locales/es.json \
  && cp /app/locales/languages.json /app/frontend/locales/languages.json

# Español como idioma por defecto (si el patrón existe; no falla si no)
RUN sed -i "s/|| *'zh'/|| 'es'/g; s/|| *\"zh\"/|| \"es\"/g" \
      /app/frontend/src/i18n/index.js 2>/dev/null || true

# ── Instalar dependencias igual que el Dockerfile oficial ────
RUN npm ci \
  && npm ci --prefix frontend \
  && cd backend && uv sync --frozen

EXPOSE 3000 5001

# Arranca frontend (Vite :3000) y backend (:5001) en modo desarrollo
CMD ["npm", "run", "dev"]
