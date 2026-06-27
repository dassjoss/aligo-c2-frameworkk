#!/bin/bash

# Script de prueba rápida para verificar HTTPS C2

echo "============================================================"
echo "  TEST RÁPIDO - ALIGO C2 HTTPS"
echo "============================================================"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "[!] Python 3 no está instalado"
    exit 1
fi

echo "[✓] Python 3 encontrado: $(python3 --version)"

# Verificar Flask
if python3 -c "import flask" 2>/dev/null; then
    echo "[✓] Flask instalado"
else
    echo "[!] Flask NO instalado"
    echo "[*] Instalando..."
    pip install flask requests
fi

# Verificar requests
if python3 -c "import requests" 2>/dev/null; then
    echo "[✓] Requests instalado"
else
    echo "[!] Requests NO instalado"
    echo "[*] Instalando..."
    pip install requests
fi

echo ""
echo "============================================================"
echo "  PRUEBA DEL SERVIDOR"
echo "============================================================"
echo ""

# Iniciar servidor en background
echo "[*] Iniciando servidor en background..."
cd server
python3 server.py > /tmp/aligo_server.log 2>&1 &
SERVER_PID=$!
cd ..

# Esperar a que inicie
sleep 3

# Verificar que el servidor esté corriendo
if ps -p $SERVER_PID > /dev/null; then
    echo "[✓] Servidor iniciado (PID: $SERVER_PID)"
else
    echo "[!] Error: El servidor no pudo iniciarse"
    cat /tmp/aligo_server.log
    exit 1
fi

# Probar endpoint /health
echo "[*] Probando endpoint /health..."
HEALTH_RESPONSE=$(curl -s http://localhost:5000/health)

if echo "$HEALTH_RESPONSE" | grep -q '"status":"ok"'; then
    echo "[✓] Servidor respondiendo correctamente"
    echo "    $HEALTH_RESPONSE"
else
    echo "[!] Servidor no responde correctamente"
    echo "    $HEALTH_RESPONSE"
fi

echo ""
echo "============================================================"
echo "  INSTRUCCIONES"
echo "============================================================"
echo ""
echo "El servidor está corriendo en background (PID: $SERVER_PID)"
echo ""
echo "Para conectarte a la consola:"
echo "  cd server && python3 server.py"
echo ""
echo "Para detener el servidor de prueba:"
echo "  kill $SERVER_PID"
echo ""
echo "Para usar con ngrok:"
echo "  1. ngrok http 5000"
echo "  2. Copiar URL de ngrok"
echo "  3. python3 agent/agent_ngrok.py https://TU-URL.ngrok.io"
echo ""
echo "============================================================"

# Limpiar
kill $SERVER_PID 2>/dev/null
echo ""
echo "[✓] Test completado. Servidor de prueba detenido."
