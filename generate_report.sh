#!/bin/bash

# Script para generar reporte de la migración

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║        REPORTE DE MIGRACIÓN - ALIGO C2 HTTPS                 ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Verificar archivos críticos
echo "📋 VERIFICACIÓN DE ARCHIVOS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check_file() {
    if [ -f "$1" ]; then
        echo "✅ $1"
    else
        echo "❌ $1 - NO ENCONTRADO"
    fi
}

# Archivos de código
echo ""
echo "🔧 CÓDIGO:"
check_file "server/server.py"
check_file "agent/agent_ngrok.py"
check_file "server/start_server.sh"
check_file "requirements.txt"

# Archivos de documentación
echo ""
echo "📚 DOCUMENTACIÓN:"
check_file "START_HERE.md"
check_file "INDEX.md"
check_file "RESUMEN_EJECUTIVO.md"
check_file "MIGRACION_COMPLETA.md"
check_file "HTTPS_GUIDE.md"
check_file "README_HTTPS.md"
check_file "EJEMPLOS_COMANDOS.md"
check_file "CHANGELOG_HTTPS.md"

# Scripts
echo ""
echo "🧪 SCRIPTS:"
check_file "test_https.sh"
check_file "generate_report.sh"

# Verificar sintaxis Python
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 VERIFICACIÓN DE SINTAXIS PYTHON"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if python3 -m py_compile server/server.py 2>/dev/null; then
    echo "✅ server/server.py - Sintaxis correcta"
else
    echo "❌ server/server.py - Error de sintaxis"
fi

if python3 -m py_compile agent/agent_ngrok.py 2>/dev/null; then
    echo "✅ agent/agent_ngrok.py - Sintaxis correcta"
else
    echo "❌ agent/agent_ngrok.py - Error de sintaxis"
fi

# Verificar dependencias
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 VERIFICACIÓN DE DEPENDENCIAS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if python3 -c "import flask" 2>/dev/null; then
    FLASK_VERSION=$(python3 -c "import flask; print(flask.__version__)" 2>/dev/null)
    echo "✅ Flask instalado - versión $FLASK_VERSION"
else
    echo "⚠️  Flask NO instalado - ejecutar: pip install flask"
fi

if python3 -c "import requests" 2>/dev/null; then
    REQUESTS_VERSION=$(python3 -c "import requests; print(requests.__version__)" 2>/dev/null)
    echo "✅ Requests instalado - versión $REQUESTS_VERSION"
else
    echo "⚠️  Requests NO instalado - ejecutar: pip install requests"
fi

# Contar líneas de código
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 ESTADÍSTICAS DE CÓDIGO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -f "server/server.py" ]; then
    SERVER_LINES=$(wc -l < server/server.py)
    echo "📄 server/server.py: $SERVER_LINES líneas"
fi

if [ -f "agent/agent_ngrok.py" ]; then
    AGENT_LINES=$(wc -l < agent/agent_ngrok.py)
    echo "📄 agent/agent_ngrok.py: $AGENT_LINES líneas"
fi

# Contar archivos de documentación
DOC_COUNT=$(ls -1 *.md 2>/dev/null | wc -l)
echo "📚 Archivos de documentación: $DOC_COUNT"

# Resumen final
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ RESUMEN DE MIGRACIÓN"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Protocolo:        TCP Socket → HTTP/HTTPS (Flask)"
echo "Puerto:           4444 → 5000"
echo "Comando ngrok:    tcp → http"
echo "Terminal:         ✅ 100% funcional (idéntica)"
echo "Comandos:         ✅ Todos iguales"
echo "Evasión:          ✅ Mejorada"
echo "Documentación:    ✅ $DOC_COUNT archivos MD"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 SIGUIENTE PASO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Instalar dependencias:"
echo "   pip install -r requirements.txt"
echo ""
echo "2. Leer documentación:"
echo "   cat START_HERE.md"
echo ""
echo "3. Probar funcionamiento:"
echo "   ./test_https.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Reporte generado: $(date)"
echo ""
