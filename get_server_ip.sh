#!/bin/bash

echo "=========================================="
echo "  Buscando IP del Servidor..."
echo "=========================================="
echo ""

# Buscar todas las IPs (excepto localhost)
echo "IPs disponibles en tu sistema:"
ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v "127.0.0.1"

echo ""
echo "=========================================="
echo "Normalmente el hotspot usa IPs como:"
echo "  - 10.42.0.1 (común en Linux)"
echo "  - 192.168.x.1"
echo "=========================================="
echo ""
echo "Usa esta IP en el agente (agent.py):"
echo "  SERVER_HOST = \"TU_IP_AQUÍ\""
echo "=========================================="
