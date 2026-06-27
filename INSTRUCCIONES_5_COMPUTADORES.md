# 🚀 INSTRUCCIONES PARA 5 COMPUTADORES - ALIGO C2

## 📦 ARQUITECTURA

```
┌──────────────┐
│  COMPUTADOR  │  Rol: Cliente (Interfaz Web + Redis)
│      1       │  Ejecuta: Redis + Streamlit
│   CLIENTE    │  NO ejecuta server.py ni agent
└──────────────┘
       │
       │ Redis (coordinador central)
       │
   ┌───┴───┬────────┬────────┐
   │       │        │        │
┌──▼───┐ ┌─▼────┐ ┌─▼────┐ ┌─▼────┐
│ SRV  │ │ SRV  │ │ SRV  │ │AGENT │
│  A   │ │  B   │ │  C   │ │  5   │
│5000  │ │5001  │ │5002  │ │      │
└──────┘ └──────┘ └──────┘ └──────┘
```

- **Cliente:** Solo maneja la interfaz y Redis
- **Servidores A, B, C:** Ejecutan comandos de operadores
- **Agente:** Se conecta a servidores (NUNCA al cliente)

---

## 🔧 PASO 0: OBTENER IPS (TODAS LAS MÁQUINAS)

**Linux/Mac:**
```bash
hostname -I
```

**Windows:**
```cmd
ipconfig | findstr "IPv4"
```

**Ejemplo:**
```
Cliente:    192.168.1.100
Servidor A: 192.168.1.101  
Servidor B: 192.168.1.102
Servidor C: 192.168.1.103
Agente:     192.168.1.104
```

---

## 📦 PASO 1: INSTALAR DEPENDENCIAS (TODAS LAS MÁQUINAS)

```bash
pip3 install flask redis requests cryptography streamlit
```

O usar requirements.txt:
```bash
cd aligo-c2-frameworkk
pip3 install -r requirements.txt
pip3 install streamlit
```

---

## 🖥️ COMPUTADOR 1: CLIENTE (Interfaz Web + Redis)

### 1.1 Instalar Redis

**macOS:**
```bash
brew install redis
```

**Ubuntu/Linux:**
```bash
sudo apt-get update
sudo apt-get install redis-server
```

**Windows:**
Descargar desde: https://github.com/microsoftarchive/redis/releases

### 1.2 Configurar Redis

**Editar archivo de configuración:**

```bash
# Linux:
sudo nano /etc/redis/redis.conf

# macOS:
nano /usr/local/etc/redis.conf

# Windows: 
notepad C:\Redis\redis.conf
```

**Buscar línea `bind 127.0.0.1` y cambiar a:**
```
bind 0.0.0.0
```

**Guardar: Ctrl+X → Y → Enter**

### 1.3 Iniciar Redis (Terminal 1)

```bash
redis-server

# O con archivo de configuración:
redis-server /etc/redis/redis.conf
```

**Debe mostrar:**
```
Ready to accept connections tcp
```

### 1.4 Iniciar Interfaz Web (Terminal 2)

```bash
cd aligo-c2-frameworkk/interfaz
streamlit run cascaron.py
```

**Acceder:** http://localhost:8501

---

## 🖥️ COMPUTADOR 2: SERVIDOR A

### 2.1 Configurar Variables de Entorno

```bash
export REDIS_HOST=192.168.1.100  # IP del CLIENTE (Redis)
export REDIS_PORT=6379
```

### 2.2 Iniciar ngrok (Terminal 1)

```bash
ngrok http 5000
```

**Anotar URL:** `https://abc123.ngrok-free.app`

### 2.3 Iniciar Servidor (Terminal 2)

```bash
cd aligo-c2-frameworkk
python3 server/server.py 5000 server-A
```

**Salida esperada:**
```
============================================================
  ALIGO C2 - Servidor HTTPS con Cifrado Híbrido
============================================================
[*] Servidor: server-A
[*] Puerto: 5000
[*] Server RSA keypair generated (2048-bit)
[*] Cifrado: RSA-2048 + Fernet (AES-128-CBC)
[*] Redis: 192.168.1.100:6379 ✅
[*] Usa ngrok con: ngrok http 5000

[✓] Registrado en Redis: server-A -> https://abc123.ngrok-free.app

Consola de operador. Comandos:
  list                  -> lista agentes conectados
  servers               -> lista servidores en Redis
  use <agent_id> <cmd>  -> manda un comando a un agente
  use @agent <cmd>      -> usa el único agente (si solo hay uno)
  exit                  -> salir

> 
```

---

## 🖥️ COMPUTADOR 3: SERVIDOR B

### 3.1 Configurar Variables de Entorno

```bash
export REDIS_HOST=192.168.1.100  # IP del CLIENTE (Redis)
export REDIS_PORT=6379
```

### 3.2 Iniciar ngrok (Terminal 1)

```bash
ngrok http 5001
```

### 3.3 Iniciar Servidor (Terminal 2)

```bash
cd aligo-c2-frameworkk
python3 server/server.py 5001 server-B
```

---

## 🖥️ COMPUTADOR 4: SERVIDOR C

### 4.1 Configurar Variables de Entorno

```bash
export REDIS_HOST=192.168.1.100  # IP del CLIENTE (Redis)
export REDIS_PORT=6379
```

### 4.2 Iniciar ngrok (Terminal 1)

```bash
ngrok http 5002
```

### 4.3 Iniciar Servidor (Terminal 2)

```bash
cd aligo-c2-frameworkk
python3 server/server.py 5002 server-C
```

---

## 🖥️ COMPUTADOR 5: AGENTE

### 5.1 Configurar Variables de Entorno

```bash
export REDIS_HOST=192.168.1.100  # IP del CLIENTE (Redis)
export REDIS_PORT=6379
```

### 5.2 Ejecutar Agente

**Opción A: Descubrimiento automático vía Redis (RECOMENDADO)**
```bash
cd aligo-c2-frameworkk
python3 agent/agent_ngrok.py
```

El agente:
1. Se conecta a Redis
2. Obtiene lista de servidores disponibles
3. Se conecta al primero
4. Si falla, hace failover automático a otro servidor

**Opción B: URL directa (sin Redis)**
```bash
python3 agent/agent_ngrok.py https://abc123.ngrok-free.app
```

**Salida esperada:**
```
==================================================
  ALIGO C2 - Agente HTTPS con Cifrado Híbrido
==================================================

[i] Modo: Descubrimiento automático vía Redis
[i] Redis: 192.168.1.100:6379

[*] Agente ID: agent-abc123
[*] Cifrado: RSA-2048 + Fernet (AES-128-CBC)
[*] Modo: Descubrimiento vía Redis (192.168.1.100:6379)
[*] Presiona Ctrl+C para detener

[✓] Conectado a Redis en 192.168.1.100:6379
[*] 3 servidores encontrados en Redis:
    0: server-A -> https://abc123.ngrok-free.app
    1: server-B -> https://def456.ngrok-free.app
    2: server-C -> https://ghi789.ngrok-free.app
[*] Conectando a https://abc123.ngrok-free.app...
[*] Estableciendo handshake criptográfico con https://abc123.ngrok-free.app...
[+] ✅ Conectado como agent-abc123
[+] 🔒 Canal cifrado establecido
```

---

## ✅ VERIFICACIÓN

### En CLIENTE (Redis):

```bash
redis-cli
127.0.0.1:6379> KEYS *
```

**Debe mostrar:**
```
1) "server:server-A:ngrok_url"
2) "server:server-A:timestamp"
3) "server:server-B:ngrok_url"
4) "server:server-B:timestamp"
5) "server:server-C:ngrok_url"
6) "server:server-C:timestamp"
```

### En SERVIDOR A (Consola):

```bash
> servers
Servidores activos (3):
 🟢 server-A: https://abc123.ngrok-free.app (2026-06-27T03:00:00)
 ⚪ server-B: https://def456.ngrok-free.app (2026-06-27T03:00:00)
 ⚪ server-C: https://ghi789.ngrok-free.app (2026-06-27T03:00:00)

> list
 - agent-abc123 | hostname | Windows | last_seen: 03:00:45
```

---

## 🧪 PRUEBA DE COMANDOS

### En SERVIDOR A:

```bash
> use @agent whoami
[enviado] id=xyz789 -> agent-abc123: whoami

[resultado de agent-abc123] (id=xyz789):
jose
```

### Prueba de Failover:

1. Detener Servidor A (Ctrl+C)
2. El agente detectará el fallo
3. Se conectará automáticamente a Servidor B
4. Enviar comando desde Servidor B

---

## 📋 RESUMEN DE COMANDOS POR COMPUTADOR

| Computador | Terminal 1 | Terminal 2 |
|------------|------------|------------|
| **1-Cliente** | `redis-server` | `streamlit run interfaz/cascaron.py` |
| **2-Srv-A** | `ngrok http 5000` | `REDIS_HOST=<ip> python3 server/server.py 5000 server-A` |
| **3-Srv-B** | `ngrok http 5001` | `REDIS_HOST=<ip> python3 server/server.py 5001 server-B` |
| **4-Srv-C** | `ngrok http 5002` | `REDIS_HOST=<ip> python3 server/server.py 5002 server-C` |
| **5-Agente** | `REDIS_HOST=<ip> python3 agent/agent_ngrok.py` | - |

---

## ⚠️ TROUBLESHOOTING

### Error: "Redis connection refused"
```bash
# Verificar que Redis está corriendo:
redis-cli PING
# Debe responder: PONG

# Verificar IP en redis.conf:
grep "^bind" /etc/redis/redis.conf
# Debe ser: bind 0.0.0.0
```

### Error: "No hay servidores en Redis"
```bash
# Verificar que servidores están registrados:
redis-cli KEYS server:*

# Verificar variable de entorno en servidores:
echo $REDIS_HOST
# Debe ser la IP del Cliente
```

### Agente no se conecta
```bash
# Verificar que ngrok está corriendo en servidor
# Verificar URL en Redis:
redis-cli GET server:server-A:ngrok_url
```

---

## 🎯 ARQUITECTURA DE CIFRADO

```
AGENTE                         SERVIDOR
  |                               |
  |--GET /public-key------------->|  RSA-2048 public key
  |<--public_key------------------|
  |                               |
  | Generate Fernet session key   |
  | Encrypt with RSA public key   |
  |                               |
  |--POST /checkin--------------->|  {encrypted_session_key}
  |   encrypted session key       |  Decrypt with RSA private key
  |<--OK--------------------------|
  |                               |
  |--POST /poll------------------>|
  |<--Fernet encrypted command----|  Command encrypted with session key
  |                               |
  | Execute command               |
  | Encrypt result with Fernet    |
  |                               |
  |--POST /result---------------->|  {payload: encrypted}
  |   encrypted result            |  Decrypt with session key
  |<--OK--------------------------|
```

**Cada agente tiene su propia session key única.**

---

**Listo para Hackathon! 🚀**
