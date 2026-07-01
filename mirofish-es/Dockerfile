# ============================================================
#  MiroFish-ES — Imagen con soporte en español
#  Clona MiroFish, inyecta las traducciones al español
#  y construye el frontend Vue.js con el locale incluido.
# ============================================================

# ── Etapa 1: clonar y construir el frontend ──────────────────
FROM node:18-alpine AS frontend-builder

RUN apk add --no-cache git

WORKDIR /app

# Clonar MiroFish (shallow para velocidad)
RUN git clone --depth 1 https://github.com/666ghj/MiroFish.git .

# Inyectar locale español en ambas ubicaciones posibles
COPY locales/es.json /app/locales/es.json
COPY locales/languages.json /app/locales/languages.json

# Algunos builds esperan las traducciones también en frontend/locales/
RUN mkdir -p /app/frontend/locales && \
    cp /app/locales/es.json /app/frontend/locales/es.json && \
    cp /app/locales/languages.json /app/frontend/locales/languages.json

# Establecer español como locale por defecto en el arranque del frontend
RUN sed -i "s/localStorage.getItem('locale') || 'zh'/localStorage.getItem('locale') || 'es'/" \
    /app/frontend/src/i18n/index.js || true

WORKDIR /app/frontend
RUN npm install --legacy-peer-deps
RUN npm run build


# ── Etapa 2: backend Python ───────────────────────────────────
FROM python:3.11-slim AS backend

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git && rm -rf /var/lib/apt/lists/*

# Instalar uv (gestor de paquetes rápido)
RUN pip install uv --quiet

WORKDIR /app

# Copiar backend de la etapa anterior
COPY --from=frontend-builder /app/backend ./backend
COPY --from=frontend-builder /app/locales ./locales

# Instalar dependencias Python
RUN cd backend && \
    uv pip install --system -r requirements.txt --quiet 2>/dev/null || \
    pip install -r requirements.txt --quiet

# Crear directorio de uploads
RUN mkdir -p /app/backend/uploads


# ── Etapa 3: imagen final con nginx para servir el frontend ───
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Backend
COPY --from=backend /app/backend ./backend
COPY --from=backend /app/locales ./locales
COPY --from=backend /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend /usr/local/bin /usr/local/bin

# Frontend construido
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Configuración nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Script de arranque
COPY start.sh /start.sh
RUN chmod +x /start.sh

RUN mkdir -p /app/backend/uploads

EXPOSE 3000 5001

CMD ["/start.sh"]
