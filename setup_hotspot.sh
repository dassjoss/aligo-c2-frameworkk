#!/bin/bash

echo "=========================================="
echo "  Configuración de Hotspot para C2"
echo "=========================================="
echo ""
echo "PASOS PARA CREAR HOTSPOT EN TU LAPTOP:"
echo ""
echo "1. Abre 'Configuración del Sistema'"
echo "2. Ve a 'Conexiones de Red' o 'Network'"
echo "3. Busca 'Hotspot' o 'Punto de Acceso'"
echo "4. Actívalo con estos datos:"
echo "   - Nombre (SSID): Aligo-C2"
echo "   - Contraseña: hackathon2024"
echo ""
echo "5. Después de activarlo, ejecuta este script de nuevo"
echo ""
read -p "¿Ya activaste el hotspot? (s/n): " respuesta

if [ "$respuesta" != "s" ]; then
    echo "Activa el hotspot primero y vuelve a ejecutar este script"
    exit 1
fi

echo ""
echo "Buscando tu IP de hotspot..."
echo ""

# Buscar interfaces de red activas
ip -4 addr show | grep -E "inet.*ap|inet.*wl" | grep -v "127.0.0.1"

echo ""
echo "=========================================="
echo "La IP del hotspot suele ser: 10.42.0.1"
echo "=========================================="
echo ""
echo "Comparte esta información con tu equipo:"
echo "  - SSID: Aligo-C2"
echo "  - Contraseña: hackathon2024"
echo "  - IP Servidor: 10.42.0.1"
echo "  - Puerto: 4444"
echo ""
echo "En el agente (agent.py) deben poner:"
echo "  SERVER_HOST = \"10.42.0.1\""
echo ""
echo "=========================================="
