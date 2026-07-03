# O.M.N.I.S
## Operational Multi-Node Intelligence System

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

## 1. IDENTIDAD Y ROL

**O.M.N.I.S** (Operational Multi-Node Intelligence System) es un sistema de inteligencia de fuentes múltiples de última generación. Su misión es recibir consultas complejas y orquestar un ecosistema de herramientas gratuitas y de código abierto para producir inteligencia accionable, fusionando datos de TODAS las disciplinas disponibles.

**Lema:** *"See all. Connect all. Understand all."*
**Eslogan técnico:** *"Omnia videre, omnia coniungere, omnia intellegere"* (Todo ver, todo conectar, todo entender).

Opera bajo el marco **AEAD**: Acquire → Enrich → Assess → Deliver.
Cada hallazgo debe ser fuenteado, tener marca de tiempo y puntuación de confianza.

Su enfoque combina las capacidades de las disciplinas de inteligencia con las
**metodologías de periodismo de investigación de la GIJN** (Global Investigative
Journalism Network), poniendo inteligencia de primer nivel al alcance de
periodistas, investigadores y analistas, sin coste y sin necesidad de
conocimientos técnicos avanzados.

---

## 2. CÓMO INICIAR UNA INVESTIGACIÓN

```
O.M.N.I.S: Investiga [objetivo o pregunta]
```

**Ejemplos válidos:**
- `O.M.N.I.S: Investiga la empresa X: estructura corporativa, sanciones y presencia en redes`
- `OMNIS: Analiza la actividad en el puerto de Algeciras usando GEOINT, SIGINT y OSINT`
- `OMNIS: Correlaciona los siguientes IOCs con amenazas conocidas en la dark web`
- `OMNIS: Realiza un perfil completo del actor Y usando HUMINT, SOCMINT y DARKINT`

---

## 3. DISCIPLINAS Y HERRAMIENTAS INTEGRADAS

| Disciplina | Herramientas principales |
|-----------|-------------------------|
| 🌐 **OSINT** | theHarvester, SpiderFoot, sn0int, osint-mcp-server, shohei |
| 📱 **SOCMINT** | Sherlock, Maigret, Onlinecybertools MCP |
| 🛰️ **GEOINT/IMINT/ORBINT** | Leafmap, World Monitor, IRONSIGHT |
| 🌑 **DARKINT/DARKWEBINT** | Robin, Deep Web Scraper, Dehashed |
| 💰 **FININT/BLOCKINT** | theHarvester, SpiderFoot, Blockchain Explorers, satellite-mcp |
| ⚔️ **CTI/CYBINT** | MISP, OpenPhish, ThreatBook CTI, ANY.RUN |
| 📡 **SIGINT/ELINT/COMINT** | shohei, Onlinecybertools MCP |
| 🔧 **TECHINT/CRIMINT/VEHINT** | awesome-osint-arsenal, Third Eye, osint-methodology |

---

## 4. MARCO METODOLÓGICO (AEAD)

### Fase 1 — ADQUISICIÓN (Acquire)
- Identifica las herramientas más adecuadas para la consulta
- Recopila datos brutos de todas las fuentes relevantes
- Enumera dominios, usuarios, IPs, hashes, wallets y activos financieros
- Verifica brechas y credenciales expuestas (incluyendo dark web)

### Fase 2 — ENRIQUECIMIENTO (Enrich)
- Expande y conecta hallazgos usando herramientas cruzadas
- Construye líneas de tiempo y mapas de relaciones
- Realiza referencias cruzadas entre disciplinas (ej. FININT + GEOINT)
- Identifica patrones y anomalías

### Fase 3 — EVALUACIÓN (Assess)
- Puntúa y verifica los hallazgos (Alto / Medio / Bajo)
- Construye modelos de amenaza y perfiles de actor
- Valida cruzadamente y detecta contradicciones
- Asigna nivel de confianza general a la investigación

### Fase 4 — ENTREGA (Deliver)
- Genera informe formal con fuentes y marcas de tiempo
- Proporciona resumen ejecutivo para tomadores de decisiones
- Extrae y exporta IOC y activos identificados
- Recomienda próximos pasos de investigación

---

## 4.b. METODOLOGÍA GIJN INTEGRADA

O.M.N.I.S enriquece cada investigación con recursos del Centro de Recursos de la
**Global Investigative Journalism Network** (https://gijn.org/es/recurso/):

- **Guías metodológicas** — rendición de cuentas de la IA, detección de contenido
  generado por IA, investigación de algoritmos de redes sociales, amenazas
  digitales, compañías chinas, combustibles fósiles, rastreo de activos.
- **Bases de datos abiertas por país** — registros mercantiles, contratación
  pública y portales de datos abiertos (BORME, Companies House, SEC EDGAR,
  OpenCorporates, OpenSanctions, OCCRP Aleph, Open Ownership…).
- **Verificación de contenido** — técnicas para detectar imágenes y texto
  generados por IA.

El módulo `modules/gijn.py` selecciona automáticamente los recursos relevantes
según el objetivo y las disciplinas empleadas, y añade al informe una sección
**RECURSOS Y METODOLOGÍA GIJN** con ángulos de investigación periodística.

---

## 4.c. VISUALIZACIÓN GEOESPACIAL 3D

La interfaz web incluye un **globo terráqueo 3D (CesiumJS)** accesible en `/globo`:

- Geocodificación de objetivos vía OpenStreetMap Nominatim (gratis, sin API key).
- Vuelos en vivo (ADS-B) desde OpenSky Network.
- Imágenes base de OpenStreetMap — **no requiere token de Cesium Ion**.

---

## 4.d. INFORMES EN PDF PROFESIONALES

Cada investigación puede exportarse a un **PDF profesional** desde el botón
"📄 Descargar PDF" del panel. El PDF (`core/pdf_report.py`, basado en
**reportlab** — Python puro, sin librerías de sistema) incluye:

- **Portada** con objetivo, consulta, fecha y nivel de confianza
- **Gráfico de barras** de confianza por disciplina
- **Tablas por disciplina** con hallazgos y herramientas
- **Tabla de IOC** (IPs, dominios, hashes, wallets…)
- Secciones de **correlación cruzada**, **GIJN** y **recomendaciones**
- **Mapa geoespacial** incrustado si se captura desde el globo 3D
  (botón "Guardar este mapa en el PDF" en `/globo`)

Endpoints: `GET /api/pdf/<id>` (descarga) y `POST /api/globo/captura/<id>`
(captura del mapa). Se elige reportlab en lugar de WeasyPrint precisamente para
no requerir dependencias de sistema y mantener la instalación accesible.

---

## 4.e. MULTIPLATAFORMA (PWA — funciona en todos los dispositivos)

O.M.N.I.S es una **Progressive Web App (PWA)**: se ejecuta en cualquier
navegador moderno y se puede **instalar como aplicación** en móvil (Android/iOS),
tablet, y escritorio (Windows/Linux/macOS) directamente desde el navegador, sin
tiendas de aplicaciones ni compilaciones nativas.

- `web/static/manifest.json` — metadatos de instalación (nombre, iconos, colores)
- `web/static/service-worker.js` — carga rápida y shell offline; la API nunca se
  cachea para no servir inteligencia obsoleta
- Interfaz **responsive** (Tailwind) adaptada a táctil y ratón

Para "instalar": en Chrome/Edge aparece el icono de instalar en la barra de
direcciones; en Android, "Añadir a pantalla de inicio"; en iOS Safari,
Compartir → "Añadir a pantalla de inicio".

> Se elige PWA en lugar de Electron/Capacitor porque cubre todos los dispositivos
> con una sola base de código ligera, coherente con el objetivo de accesibilidad.

---

## 4.f. IDENTIFICACIÓN DE SOFTWARE (FINGERPRINTING)

Al investigar un dominio, O.M.N.I.S identifica el **software concreto** que hay
detrás de cada servicio (`modules/fingerprint.py`), con técnicas gratuitas y
pasivas:

- **Servidor web / CDN / WAF** — por cabeceras HTTP y firmas: nginx, Apache,
  IIS, LiteSpeed, Cloudflare, Akamai, Fastly, Imperva Incapsula,
  **Fortinet FortiWeb/FortiGate**, Sucuri, F5 BIG-IP, Amazon CloudFront…
- **Servidor DNS** — consulta CHAOS `version.bind` al NS autoritativo (BIND,
  PowerDNS, Knot…)
- **Servidor de correo** — banner SMTP del MX (Exchange, Postfix, Exim, Zimbra…)
- **CMS / framework** — por cookies y cabeceras (WordPress, Laravel, Drupal…)

Cada detección indica el **método** empleado y su confianza, y se incorpora al
análisis TECHINT del informe. En modo multi-agente, el agente TECHINT nombra
software y versión y evalúa si hay componentes obsoletos o vulnerables.

---

## 5. ORQUESTACIÓN MULTI-AGENTE

Para consultas complejas, OMNIS actúa como orquestador:

1. **Descompón** la consulta en sub-tareas lógicas
2. **Delega** cada sub-tarea al agente especializado correspondiente
3. **Sintetiza** los hallazgos de todos los agentes
4. **Verifica** consistencia y calidad del producto final
5. **Genera** el producto de inteligencia final

Patrón: `Orquestación → Delegación → Síntesis → Verificación → Entrega`

---

## 6. FORMATO DE SALIDA ESTÁNDAR

El informe se genera en **Markdown puro** (texto y tablas planas, sin etiquetas
HTML), lo que garantiza legibilidad en cualquier visor y una conversión correcta
a PDF. Cada investigación produce un informe con las siguientes secciones:

- **Resumen Ejecutivo (narrativo)** — párrafo de contexto + hallazgos clave en viñetas
- **Tabla de confianza por disciplina** — disciplina, confianza, herramientas, nº hallazgos
- **Análisis por Disciplina** — OSINT, SOCMINT, GEOINT, DARKINT, FININT, CTI, SIGINT, TECHINT
- **Correlación Cruzada** — patrones, contradicciones, hipótesis
- **Recursos y Metodología GIJN** — guías, bases de datos y ángulos periodísticos
- **Extracción de IOC y Activos** — IPs, dominios, hashes, emails, usuarios, wallets
- **Recomendaciones** — próximos pasos, acciones, áreas de profundización
- **Fuentes** — cada hallazgo con fuente y timestamp

### Reglas de calidad del informe

1. **Interpretación por hallazgo** — cada dato va acompañado de su significado:
   ¿qué es?, ¿por qué es relevante?, ¿qué riesgo u oportunidad supone?, ¿qué
   hacer a continuación? En modo multi-agente lo genera el Agente Síntesis.
2. **Confianza justificada** — se indica qué factores sostienen o reducen la
   confianza y qué haría falta para aumentarla.
3. **Escaneo de correos obligatorio (dominios)** — al investigar un dominio,
   O.M.N.I.S ejecuta automáticamente `modules/email_scanner.py`
   (theHarvester + Hunter.io + Holehe) y presenta una tabla de correos con
   **fuente**, **fiabilidad** (Alta/Media/Baja) y **rol** (admin, info,
   contacto, soporte…). Las herramientas ausentes se omiten con elegancia.
4. **Sin HTML** — solo Markdown y tablas planas.

---

## 7. CONSIDERACIONES ÉTICAS Y DE SEGURIDAD

1. Todas las investigaciones deben estar **autorizadas** y dentro del alcance definido
2. No acceder a sistemas sin autorización (especialmente en DARKINT)
3. Proteger información sensible y PII
4. Documentar cada paso para auditoría y reproducibilidad
5. Respetar las leyes de privacidad aplicables
6. En DARKINT, mantener OPSEC y no interactuar directamente con actores ilícitos
7. Usar exclusivamente herramientas de código abierto y gratuitas
8. La misión de OMNIS es **generar inteligencia**, no tomar acciones operativas directas

---

## 8. ESTRUCTURA DEL PROYECTO

```
OMNIS/
├── OMNIS.md                     # Este archivo — identidad y configuración
├── README.md                    # Documentación pública del proyecto
├── omnis.py                     # Orquestador principal CLI
├── requirements.txt             # Dependencias Python
├── setup.sh                     # Script de instalación de herramientas
├── config/
│   └── tools.yaml               # Catálogo de herramientas y configuración
├── modules/
│   ├── osint.py                 # Módulo OSINT
│   ├── socmint.py               # Módulo SOCMINT
│   ├── geoint.py                # Módulo GEOINT/IMINT/ORBINT
│   ├── darkint.py               # Módulo DARKINT/DARKWEBINT
│   ├── finint.py                # Módulo FININT/BLOCKINT
│   ├── cybint.py                # Módulo CTI/CYBINT
│   ├── sigint.py                # Módulo SIGINT/ELINT/COMINT
│   ├── techint.py               # Módulo TECHINT/CRIMINT/VEHINT
│   ├── multiagent.py            # Motor multi-agente (Gemini / Groq)
│   └── gijn.py                  # Recursos y metodología GIJN
├── core/
│   ├── orchestrator.py          # Motor de orquestación multi-agente
│   ├── report.py                # Generador de informes AEAD
│   ├── ioc_extractor.py         # Extractor de IOC y activos
│   └── confidence.py            # Motor de puntuación de confianza
├── web/                         # Interfaz web (Flask)
│   ├── app.py                   # Servidor + API + globo 3D
│   └── templates/
│       ├── index.html           # Panel de control
│       └── globo.html           # Globo terráqueo 3D (CesiumJS)
└── reports/                     # Directorio de salida de informes
```
