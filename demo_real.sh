#!/bin/bash

echo "=========================================="
echo "  DEMO REALISTA CON NGROK"
echo "=========================================="
echo ""
echo "Este script te ayudará a configurar un escenario realista"
echo "donde el servidor y agentes están en redes diferentes."
echo ""

# Verificar si ngrok está instalado
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok no está instalado"
    echo ""
    echo "Instálalo con:"
    echo "  sudo snap install ngrok"
    echo "  O descarga desde: https://ngrok.com/download"
    echo ""
    exit 1
fi

echo "✅ ngrok está instalado"
echo ""

# Verificar si el servidor está corriendo
if ! ss -tlnp 2>/dev/null | grep -q ":4444"; then
    echo "⚠️  El servidor NO está corriendo en puerto 4444"
    echo ""
    echo "Inicia el servidor primero:"
    echo "  cd server"
    echo "  python3 server.py"
    echo ""
    read -p "¿Ya iniciaste el servidor? (s/n): " respuesta
    if [ "$respuesta" != "s" ]; then
        echo "Inicia el servidor primero y vuelve a ejecutar este script"
        exit 1
    fi
fi

echo "✅ Servidor corriendo en puerto 4444"
echo ""
echo "=========================================="
echo "  CREANDO TÚNEL PÚBLICO CON NGROK"
echo "=========================================="
echo ""
echo "Ejecutando: ngrok tcp 4444"
echo ""
echo "IMPORTANTE: Copia la URL de 'Forwarding' que aparecerá"
echo "Ejemplo: tcp://4.tcp.ngrok.io:15432"
echo ""
echo "Usa esa URL en los agentes:"
echo "  SERVER_HOST = \"4.tcp.ngrok.io\""
echo "  SERVER_PORT = 15432"
echo ""
echo "Presiona Ctrl+C para detener el túnel cuando termines"
echo ""
sleep 3

ngrok tcp 4444
