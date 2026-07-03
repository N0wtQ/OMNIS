# O.M.N.I.S — Operational Multi-Node Intelligence System

```
   ██████╗ ███╗   ███╗███╗   ██╗██╗███████╗
  ██╔═══██╗████╗ ████║████╗  ██║██║██╔════╝
  ██║   ██║██╔████╔██║██╔██╗ ██║██║███████╗
  ██║   ██║██║╚██╔╝██║██║╚██╗██║██║╚════██║
  ╚██████╔╝██║ ╚═╝ ██║██║ ╚████║██║███████║
   ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝╚══════╝

    Operational Multi-Node Intelligence System
           "See all. Connect all. Understand all."
```

---

## ¿Qué es O.M.N.I.S?

O.M.N.I.S es un framework de fusión de inteligencia multidisciplinar de código abierto. Orquesta herramientas OSINT gratuitas, APIs públicas y un motor multi-agente con LLM bajo un único flujo de trabajo AEAD:

**Adquirir → Enriquecer → Evaluar → Entregar**

Dispone de **dos modos de operación**:

| Modo | Descripción | Requiere |
|------|-------------|----------|
| ⚙️ **Clásico** | APIs públicas gratuitas (DNS, WHOIS, Blockchain, etc.) | Solo Python |
| 🤖 **Multi-Agente** | Cada disciplina actúa como agente autónomo con LLM | API key de Gemini o Groq (gratis) |

### ✨ Funciones destacadas

- 🛰️ **Globo terráqueo 3D** (CesiumJS) con geocodificación y vuelos en vivo — pinta automáticamente las coordenadas GEOINT
- 📄 **Informes en PDF profesionales** con portada, gráficos, tablas y mapa incrustado
- 📚 **Metodología GIJN** integrada (guías, bases de datos por país, detección de contenido IA)
- 📱 **Multiplataforma (PWA)** — instalable en móvil, tablet y escritorio desde el navegador
- 🤖 Motor **multi-agente** con Google Gemini o Groq (ambos con tier gratuito)

---

## Disciplinas integradas

| Disciplina | Herramientas |
|-----------|-------------|
| 🌐 OSINT | theHarvester, SpiderFoot, sn0int, dnspython, python-whois |
| 📱 SOCMINT | Sherlock, Maigret |
| 🛰️ GEOINT / IMINT / ORBINT | OpenStreetMap Nominatim, OpenSky Network |
| 🌑 DARKINT / DARKWEBINT | ThreatFox, psbdmp.ws |
| 💰 FININT / BLOCKINT | Blockchain.info, BlockCypher, OpenCorporates |
| ⚔️ CTI / CYBINT | URLhaus, MalwareBazaar, AbuseIPDB |
| 📡 SIGINT / ELINT / COMINT | TLS fingerprinting, BGPView, RDAP |
| 🔧 TECHINT / CRIMINT | Wayback Machine, crt.sh, HTTP fingerprinting |

---

## Instalación

### 🚀 Instalación rápida en Linux Mint / Ubuntu (automática)

Un solo comando lo hace todo (Python, entorno, dependencias y configuración):

```bash
git clone https://github.com/N0wtQ/OMNIS.git
cd OMNIS
chmod +x instalar-mint.sh
./instalar-mint.sh
```

El script instala lo necesario y, al terminar, ofrece arrancar O.M.N.I.S
directamente. Luego abre `http://localhost:5001` en el navegador.

Para volver a arrancarlo otro día:

```bash
cd OMNIS && source .venv/bin/activate && python web/app.py
```

---

### Instalación manual (cualquier sistema)

#### Requisitos previos

- Python 3.9 o superior
- pip
- git

### 1. Clonar el repositorio

```bash
git clone https://github.com/N0wtQ/OMNIS.git
cd OMNIS
```

### 2. Crear un entorno virtual (recomendado)

```bash
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
# Edita .env y añade tu clave si quieres el modo multi-agente:
#   GEMINI_API_KEY=...   (Google Gemini — https://aistudio.google.com/apikey)
#   GROQ_API_KEY=...     (Groq — https://console.groq.com, gratis)
# Si defines las dos, Gemini tiene prioridad. Sin clave, funciona el modo clásico.
```

### 5. (Opcional) Instalar herramientas externas OSINT

```bash
chmod +x setup.sh && ./setup.sh
```

### 6. Verificar la instalación

```bash
python omnis.py --list-disciplines
```

---

## Modo de uso — Interfaz Web 🌐

La interfaz web permite lanzar investigaciones desde el navegador con visualización en tiempo real.

### Arrancar el servidor

```bash
python web/app.py
# Abre http://localhost:5001 en tu navegador
```

O con gunicorn (producción):

```bash
gunicorn --chdir web app:app --bind 0.0.0.0:5001 --workers 2
```

### Funciones de la interfaz web

- **🛰️ Globo 3D** — botón en la cabecera. Geocodifica objetivos, muestra vuelos en
  vivo (ADS-B) y pinta automáticamente las coordenadas de una investigación GEOINT
  (`/globo?inv=<id>`). Desde el globo puedes "Guardar el mapa en el PDF".
- **📄 Descargar PDF** — al completar una investigación, genera un informe PDF
  profesional (portada, gráfico de confianza, tablas por disciplina, IOC, GIJN,
  recomendaciones y mapa si lo capturaste).
- **📱 Instalar como app (PWA)** — en Chrome/Edge aparece el icono de instalar en la
  barra de direcciones; en Android "Añadir a pantalla de inicio"; en iOS Safari,
  Compartir → "Añadir a pantalla de inicio". Funciona en móvil, tablet y escritorio.

### Motor Multi-Agente (MiroFish-style)

Activa el toggle **"Motor Multi-Agente"** en la interfaz web. Cada disciplina se convierte en un agente autónomo que:

1. Recibe el objetivo y el contexto de agentes anteriores
2. Razona con **Llama 3.3 70B** vía [Groq](https://console.groq.com) (tier gratuito)
3. Extrae hallazgos e IOC estructurados en JSON
4. Pasa el contexto enriquecido al siguiente agente

Al final, el **Agente Síntesis** fusiona todos los hallazgos y genera el informe AEAD.

> **¿Es gratis?** Sí. Groq ofrece 14.400 tokens/minuto sin coste con Llama 3.3 70B.
> Regístrate en https://console.groq.com → API Keys → copia tu clave en `.env`.

---

## Modo de uso — CLI

### Sintaxis general

```
python omnis.py <objetivo> [opciones]
```

| Parámetro | Descripción |
|-----------|-------------|
| `<objetivo>` | Dominio, IP, nombre de usuario o empresa |
| `--query`, `-q` | Contexto adicional en lenguaje natural |
| `--disciplines`, `-d` | Disciplinas a activar (por defecto: todas) |
| `--output`, `-o` | Fichero donde guardar el informe |
| `--verbose`, `-v` | Muestra advertencias de cada módulo |
| `--list-disciplines` | Lista disciplinas disponibles y termina |

### Ejemplos

```bash
# Investigación completa
python omnis.py ejemplo.com

# Perfil de amenaza CTI
python omnis.py malicious-domain.io --disciplines osint cybint sigint darkint

# Perfil corporativo
python omnis.py "Nombre de Empresa S.L." --disciplines osint socmint finint

# IP con guardado de informe
python omnis.py 198.51.100.42 --output reports/resultado.txt

# Usuario en redes sociales
python omnis.py johndoe --disciplines socmint osint
```

---

## Despliegue gratuito en la web (Render.com)

O.M.N.I.S incluye `render.yaml` y `Procfile` listos para desplegar en [Render.com](https://render.com) sin coste.

### Pasos

1. Haz un fork del repositorio en GitHub
2. Ve a [render.com](https://render.com) → **New Web Service** → conecta tu repo
3. Render detecta automáticamente la configuración del `render.yaml`
4. En **Environment Variables**, añade:
   - `GEMINI_API_KEY` → tu clave de Google Gemini (o `GROQ_API_KEY` para Groq)
   - `SECRET_KEY` → Render la genera automáticamente
5. Haz clic en **Deploy** → en ~2 minutos tendrás la URL pública

> El plan gratuito de Render entra en modo suspensión tras 15 min de inactividad.
> Para uso continuo, usa el plan Starter ($7/mes) o mantén el servicio activo con un ping periódico.

---

## Estructura del proyecto

```
OMNIS/
├── OMNIS.md                 # Identidad del sistema y metodología
├── README.md                # Este archivo
├── omnis.py                 # CLI entrada
├── requirements.txt         # Dependencias Python
├── instalar-mint.sh         # Instalador automático (Linux Mint / Ubuntu)
├── setup.sh                 # Instalador de herramientas externas
├── Procfile                 # Para Render/Heroku
├── render.yaml              # Blueprint de despliegue gratuito
├── .env.example             # Plantilla de variables de entorno
├── config/
│   └── tools.yaml           # Catálogo de herramientas
├── web/
│   ├── app.py               # Servidor Flask + SSE + API (PDF, globo, PWA)
│   ├── static/
│   │   ├── manifest.json    # PWA — metadatos de instalación
│   │   ├── service-worker.js# PWA — caché de shell / offline
│   │   └── icons/           # Iconos de la app (192, 512)
│   └── templates/
│       ├── index.html       # Panel de control (Tailwind, vanilla JS, PWA)
│       └── globo.html       # Globo terráqueo 3D (CesiumJS)
├── modules/
│   ├── multiagent.py        # Motor multi-agente (Gemini / Groq)
│   ├── gijn.py              # Recursos y metodología GIJN
│   ├── osint.py
│   ├── socmint.py
│   ├── geoint.py
│   ├── darkint.py
│   ├── finint.py
│   ├── cybint.py
│   ├── sigint.py
│   └── techint.py
├── core/
│   ├── orchestrator.py      # Motor AEAD clásico
│   ├── report.py            # Generador de informes (texto)
│   ├── report_data.py       # Datos estructurados para PDF/JSON
│   ├── pdf_report.py        # Generador de informes PDF (reportlab)
│   ├── ioc_extractor.py     # Extractor de IOC
│   └── confidence.py        # Puntuación de confianza
└── reports/                 # Directorio de salida
```

---

## Aviso ético y legal

1. Investiga únicamente objetivos para los que estés **autorizado**.
2. Respeta las leyes de privacidad aplicables (RGPD, CCPA, etc.).
3. Este framework genera **inteligencia**, no ejecuta acciones operativas directas.
4. El módulo DARKINT **no** se conecta a direcciones .onion directamente.
5. Documenta cada investigación para auditoría y reproducibilidad.

---

## Licencia

Licencia MIT — ver archivo LICENSE.
