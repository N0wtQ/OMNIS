# MiroFish-ES — MiroFish en español

Integración de [MiroFish](https://github.com/666ghj/MiroFish) con la interfaz
traducida al español, empaquetada en Docker. Replica el arranque oficial de
MiroFish (frontend Vite en el puerto 3000 + backend en el 5001, vía
`npm run dev`) e inyecta la traducción `locales/es.json`.

## Requisitos

- **Docker** y **Docker Compose** instalados
- Una **API key de LLM** (Groq gratis, o Gemini)
- Una **API key de Zep Cloud** (gratis) — **obligatoria**, sin ella el backend
  de MiroFish no arranca

## Puesta en marcha

Desde la raíz del proyecto O.M.N.I.S:

```bash
# 1. Crear el fichero de entorno de MiroFish
cp mirofish-es/.env.example mirofish-es/.env
nano mirofish-es/.env          # rellena LLM_API_KEY y ZEP_API_KEY

# 2. Levantar el stack completo (OMNIS + MiroFish-ES)
docker compose -f docker-compose.full.yml up --build
```

Accesos:

| Servicio | URL |
|----------|-----|
| O.M.N.I.S | http://localhost:5001 |
| MiroFish-ES | http://localhost:3000 |

> El primer arranque tarda varios minutos: clona MiroFish, instala dependencias
> de Node y Python y arranca el servidor de desarrollo. Ten paciencia.

## Solución de problemas ("no arranca")

1. **Falta el fichero `.env`** — asegúrate de haber copiado
   `mirofish-es/.env.example` a `mirofish-es/.env` y rellenado las claves.
2. **`ZEP_API_KEY` vacía** — es obligatoria; el backend se cierra sin ella.
   Consíguela gratis en https://app.getzep.com.
3. **`LLM_API_KEY` inválida** — verifica la clave y que `LLM_BASE_URL` /
   `LLM_MODEL_NAME` coincidan con tu proveedor (Groq o Gemini).
4. **Sigue sin arrancar** — mira los registros para ver el error real:
   ```bash
   docker compose -f docker-compose.full.yml logs mirofish
   ```
5. **El primer build falla por red** — reintenta; la clonación de MiroFish o
   `npm ci` pueden fallar por cortes de red puntuales.

## Solo MiroFish-ES (sin O.M.N.I.S)

```bash
docker build -t mirofish-es ./mirofish-es
docker run --env-file mirofish-es/.env -p 3000:3000 mirofish-es
```
