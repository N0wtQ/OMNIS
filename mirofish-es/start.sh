#!/bin/sh
# Arrancar backend Flask y nginx simultáneamente

echo "🐟 Iniciando MiroFish-ES..."

# Arrancar backend Flask
cd /app/backend
python run.py &
BACKEND_PID=$!

# Esperar a que el backend esté listo
echo "⏳ Esperando al backend..."
for i in $(seq 1 30); do
    if curl -sf http://127.0.0.1:5001/api/health > /dev/null 2>&1 || \
       curl -sf http://127.0.0.1:5001/ > /dev/null 2>&1; then
        echo "✅ Backend listo"
        break
    fi
    sleep 1
done

# Arrancar nginx (sirve el frontend en :3000)
nginx -g "daemon off;" &
NGINX_PID=$!

echo "✅ MiroFish-ES activo"
echo "   Frontend: http://localhost:3000  (interfaz en español)"
echo "   Backend:  http://localhost:5001  (API REST)"

# Esperar a que algún proceso termine
wait $BACKEND_PID $NGINX_PID
