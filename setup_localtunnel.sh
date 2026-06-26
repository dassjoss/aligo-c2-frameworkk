#!/bin/bash

echo "=========================================="
echo "  SETUP LOCALTUNNEL (Alternativa a ngrok)"
echo "=========================================="
echo ""
echo "LocalTunnel es como ngrok pero:"
echo "  ✅ NO requiere cuenta"
echo "  ✅ NO requiere tarjeta"
echo "  ✅ 100% gratis"
echo "  ✅ Setup en 2 minutos"
echo ""

# Verificar si npm está instalado
if ! command -v npm &> /dev/null; then
    echo "❌ npm no está instalado"
    echo ""
    echo "Instala Node.js y npm primero:"
    echo ""
    echo "Opción 1 - Fedora/RHEL:"
    echo "  sudo dnf install nodejs npm"
    echo ""
    echo "Opción 2 - Ubuntu/Debian:"
    echo "  sudo apt install nodejs npm"
    echo ""
    echo "Opción 3 - Usando nvm (recomendado):"
    echo "  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
    echo "  source ~/.bashrc"
    echo "  nvm install node"
    echo ""
    exit 1
fi

echo "✅ npm está instalado: $(npm --version)"
echo ""

# Verificar si localtunnel está instalado
if ! command -v lt &> /dev/null; then
    echo "Instalando localtunnel..."
    npm install -g localtunnel
    
    if [ $? -eq 0 ]; then
        echo "✅ localtunnel instalado correctamente"
    else
        echo "❌ Error al instalar localtunnel"
        echo ""
        echo "Intenta manualmente:"
        echo "  sudo npm install -g localtunnel"
        exit 1
    fi
else
    echo "✅ localtunnel ya está instalado"
fi

echo ""
echo "=========================================="
echo "  ✅ SETUP COMPLETO"
echo "=========================================="
echo ""
echo "CÓMO USAR:"
echo ""
echo "1. Inicia tu servidor C2:"
echo "   cd server"
echo "   python3 server.py"
echo ""
echo "2. En otra terminal, crea el túnel:"
echo "   lt --port 4444"
echo ""
echo "3. Verás algo como:"
echo "   your url is: https://random-name.loca.lt"
echo ""
echo "4. IMPORTANTE: LocalTunnel usa HTTPS, no TCP puro"
echo "   Por eso necesitarás adaptar el código (ver más abajo)"
echo ""
echo "=========================================="
echo ""

# Verificar si el servidor está corriendo
if ss -tlnp 2>/dev/null | grep -q ":4444"; then
    echo "✅ Servidor detectado en puerto 4444"
    echo ""
    read -p "¿Quieres iniciar localtunnel ahora? (s/n): " start_now
    
    if [ "$start_now" = "s" ]; then
        echo ""
        echo "⚠️  NOTA: LocalTunnel usa HTTP/HTTPS"
        echo "Tu servidor C2 actual usa TCP puro, así que esto NO funcionará directamente."
        echo ""
        echo "Opciones:"
        echo "1) Usar Serveo (túnel TCP puro)"
        echo "2) Adaptar el C2 para usar HTTP"
        echo "3) Cancelar"
        echo ""
        read -p "Selecciona [1/2/3]: " opcion
        
        if [ "$opcion" = "1" ]; then
            echo ""
            echo "Intentando Serveo (túnel TCP)..."
            echo "Esto creará un túnel SSH..."
            echo ""
            ssh -R 4444:localhost:4444 serveo.net
        else
            echo ""
            echo "Para más información, revisa: ALTERNATIVAS_NGROK.md"
        fi
    fi
else
    echo "⚠️  No hay servidor corriendo en puerto 4444"
    echo ""
    echo "Inicia el servidor primero:"
    echo "  cd server"
    echo "  python3 server.py"
fi

echo ""
echo "=========================================="
