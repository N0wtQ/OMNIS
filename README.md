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

O.M.N.I.S es un framework de fusión de inteligencia multidisciplinar de código abierto. Orquesta herramientas OSINT gratuitas y APIs públicas bajo un único flujo de trabajo AEAD:

**Adquirir → Enriquecer → Evaluar → Entregar**

Cada hallazgo es fuenteado, marcado con timestamp y puntuado con un nivel de confianza (Alto / Medio / Bajo). El resultado es un informe de inteligencia estructurado con correlación cruzada entre disciplinas y extracción automática de IOC.

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

Todas las herramientas y APIs utilizadas son **gratuitas y de código abierto**.

---

## Instalación

### Requisitos previos

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

### 3. Instalar dependencias Python

```bash
pip install -r requirements.txt
```

### 4. Instalar herramientas externas (opcional pero recomendado)

El script `setup.sh` clona e instala automáticamente theHarvester, SpiderFoot, Sherlock, Maigret y otros repositorios en la carpeta `tools/`.

```bash
chmod +x setup.sh
./setup.sh
```

> En Windows usa Git Bash o WSL para ejecutar el script.

### 5. Verificar la instalación

```bash
python omnis.py --list-disciplines
```

Si ves las 8 disciplinas listadas, la instalación es correcta.

---

## Modo de uso

### Sintaxis general

```
python omnis.py <objetivo> [opciones]
```

| Parámetro | Descripción |
|-----------|-------------|
| `<objetivo>` | Dominio, dirección IP, nombre de usuario o empresa a investigar |
| `--query`, `-q` | Contexto adicional en lenguaje natural para orientar la investigación |
| `--disciplines`, `-d` | Lista de disciplinas a activar (por defecto: todas) |
| `--output`, `-o` | Ruta de fichero donde guardar el informe generado |
| `--verbose`, `-v` | Muestra errores y advertencias de cada módulo durante la ejecución |
| `--list-disciplines` | Lista las disciplinas disponibles y termina |

### Disciplinas disponibles

```
osint · socmint · geoint · darkint · finint · cybint · sigint · techint
```

---

### Ejemplos de uso

**Investigación completa de un dominio** (todas las disciplinas):
```bash
python omnis.py ejemplo.com
```

**Perfil de amenaza — dominio con foco en ciberinteligencia:**
```bash
python omnis.py malicious-domain.io --disciplines osint cybint sigint darkint
```

**Perfil corporativo — empresa con análisis financiero y redes sociales:**
```bash
python omnis.py "Nombre de Empresa S.L." --disciplines osint socmint finint
```

**Investigación de una dirección IP:**
```bash
python omnis.py 198.51.100.42 --disciplines osint cybint sigint darkint
```

**Búsqueda de usuario en redes sociales:**
```bash
python omnis.py johndoe --disciplines socmint osint
```

**Investigación con contexto adicional y guardado de informe:**
```bash
python omnis.py ejemplo.com \
  --query "Verificar posibles sanciones OFAC y presencia en dark web" \
  --disciplines osint finint darkint cybint \
  --output reports/ejemplo_com.txt
```

**Modo detallado para depuración:**
```bash
python omnis.py ejemplo.com --verbose
```

---

### Formato del informe generado

Cada investigación produce un informe estructurado con las siguientes secciones:

```
📄 INFORME DE INTELIGENCIA — O.M.N.I.S
├── Resumen ejecutivo          ← hallazgos clave, disciplinas y herramientas usadas
├── Análisis por disciplina    ← resultados desglosados por OSINT, SOCMINT, GEOINT…
├── Correlación cruzada        ← patrones, contradicciones e hipótesis entre disciplinas
├── Extracción de IOC          ← IPs, dominios, hashes, emails, wallets, usuarios
├── Recomendaciones            ← próximos pasos para el analista
└── Fuentes                    ← cada hallazgo con fuente y timestamp
```

---

## Estructura del proyecto

```
OMNIS/
├── OMNIS.md             # Identidad del sistema y metodología
├── README.md            # Este archivo
├── omnis.py             # Punto de entrada CLI
├── requirements.txt     # Dependencias Python
├── setup.sh             # Instalador de herramientas externas
├── config/
│   └── tools.yaml       # Catálogo de herramientas
├── modules/             # Módulos por disciplina ALLINT
│   ├── osint.py
│   ├── socmint.py
│   ├── geoint.py
│   ├── darkint.py
│   ├── finint.py
│   ├── cybint.py
│   ├── sigint.py
│   └── techint.py
├── core/
│   ├── orchestrator.py  # Motor de orquestación AEAD
│   ├── report.py        # Generador de informes
│   ├── ioc_extractor.py # Extractor de IOC por expresiones regulares
│   └── confidence.py    # Motor de puntuación de confianza
└── reports/             # Directorio de salida de informes
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
