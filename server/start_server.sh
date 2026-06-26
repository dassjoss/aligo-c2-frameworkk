#!/bin/bash

# Script para iniciar el servidor C2 Aligo
# Muestra la configuración necesaria para los agentes

echo "=========================================="
echo "  ALIGO C2 SERVER - Configuración"
echo "=========================================="
echo ""

# Obtener IP local
SERVER_IP=$(hostname -I | awk '{print $1}')

echo "[*] Tu IP de servidor es: $SERVER_IP"
echo "[*] Puerto: 4444"
echo ""
echo "=========================================="
echo "  CONFIGURACIÓN PARA AGENTES"
echo "=========================================="
echo ""
echo "Los agentes deben editar agent.py y cambiar:"
echo ""
echo "  SERVER_HOST = \"$SERVER_IP\""
echo ""
echo "=========================================="
echo ""
read -p "Presiona ENTER para iniciar el servidor..." 

python3 server.py
