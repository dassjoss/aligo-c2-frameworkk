# ⚡ RÁPIDO - 5 COMPUTADORES (COPIA Y PEGA)

## Tu setup:
```
🖥️ Máquina 1: Redis SOLO
🖥️ Máquina 2: Server-A + ngrok
🖥️ Máquina 3: Server-B + ngrok
🖥️ Máquina 4: Server-C + ngrok
🖥️ Máquina 5: Agente (cliente)
```

---

## PASO 1: Las 5 IPs (OBLIGATORIO)

En cada máquina, ejecuta:
```bash
# Linux/Mac:
hostname -I

# Windows:
ipconfig | findstr "IPv4"
```

**Ej:**
```
Redis:  192.168.1.100
Srv-A:  192.168.1.101
Srv-B:  192.168.1.102
Srv-C:  192.168.1.103
Agente: 192.168.1.104
```

👉 **ANOTA ESTAS IPs, las necesitas ahora.**

---

## PASO 2: Instalar en TODAS las máquinas

```bash
pip install flask redis requests --break-system-packages
```

---

## PASO 3: MÁQUINA REDIS (Máquina 1)

### 3.1 Instalar Redis

```bash
# macOS:
brew install redis

# Ubuntu/Linux:
sudo apt-get update
sudo apt-get install redis-server

# Windows: descarga https://github.com/microsoftarchive/redis/releases
```

### 3.2 Editar configuración

```bash
# Linux:
sudo nano /etc/redis/redis.conf

# macOS:
nano /usr/local/etc/redis.conf

# Windows: editar redis.conf en la carpeta de instalación
```

**Buscar línea `bind 127.0.0.1` y cambiar a:**
```
bind 0.0.0.0
```

**Guardar: Ctrl+X → Y → Enter**

### 3.3 Iniciar Redis

```bash
redis-server /etc/redis/redis.conf
# O:
redis-server
```

**Debería mostrar:**
```
Ready to accept connections
```

✅ **LISTO**

---

## PASO 4: MÁQUINA A (Máquina 2)

### 4.1 Copiar archivos aquí:
- `server_redis_MODIFICADO.py` (renombrar a `server_redis.py`)

### 4.2 Crear `config_A.py`:

```python
REDIS_HOST = "192.168.1.100"  # IP DE TU REDIS
REDIS_PORT = 6379
SERVER_NAME = "server-A"
HTTP_PORT = 5000
```

### 4.3 Ejecutar servidor (Terminal 1):

```bash
python3 server_redis.py
```

**Debe mostrar:**
```
[✓] Conectado a Redis en 192.168.1.100:6379
[✓] Configuración cargada: server-A
```

### 4.4 Ejecutar ngrok (Terminal 2):

```bash
ngrok http 5000
```

**Anotar URL: `https://abc123.ngrok-free.app`**

✅ **LISTO**

---

## PASO 5: MÁQUINA B (Máquina 3)

### 5.1 Copiar archivos aquí:
- `server_redis_MODIFICADO.py` (renombrar a `server_redis.py`)

### 5.2 Crear `config_B.py`:

```python
REDIS_HOST = "192.168.1.100"  # IP DE TU REDIS
REDIS_PORT = 6379
SERVER_NAME = "server-B"
HTTP_PORT = 5001
```

### 5.3 Ejecutar servidor (Terminal 1):

```bash
python3 server_redis.py
```

### 5.4 Ejecutar ngrok (Terminal 2):

```bash
ngrok http 5001
```

**Anotar URL**

✅ **LISTO**

---

## PASO 6: MÁQUINA C (Máquina 4)

### 6.1 Copiar archivos aquí:
- `server_redis_MODIFICADO.py` (renombrar a `server_redis.py`)

### 6.2 Crear `config_C.py`:

```python
REDIS_HOST = "192.168.1.100"  # IP DE TU REDIS
REDIS_PORT = 6379
SERVER_NAME = "server-C"
HTTP_PORT = 5002
```

### 6.3 Ejecutar servidor (Terminal 1):

```bash
python3 server_redis.py
```

### 6.4 Ejecutar ngrok (Terminal 2):

```bash
ngrok http 5002
```

**Anotar URL**

✅ **LISTO**

---

## PASO 7: MÁQUINA AGENTE (Máquina 5)

### 7.1 Copiar archivos aquí:
- `agent_redis.py`

### 7.2 Modificar `agent_redis.py` - Línea ~80

**BUSCAR:**
```python
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
```

**REEMPLAZAR POR:**
```python
REDIS_HOST = "192.168.1.100"  # IP DE TU REDIS
REDIS_PORT = 6379
```

### 7.3 Ejecutar agente (Terminal 1):

```bash
python3 agent_redis.py
```

**Debe mostrar:**
```
[✓] Conectado a Redis en 192.168.1.100:6379
[*] Servidores encontrados en Redis: 3
    0: server-A -> https://abc123.ngrok-free.app
    1: server-B -> https://def456.ngrok-free.app
    2: server-C -> https://ghi789.ngrok-free.app
[+] ✅ Conectado a server-A
```

✅ **LISTO**

---

## VERIFICACIÓN

### En máquina Redis, otra terminal:

```bash
redis-cli
```

```
127.0.0.1:6379> KEYS *
1) "server:server-A:ngrok_url"
2) "server:server-A:timestamp"
3) "server:server-B:ngrok_url"
4) "server:server-B:timestamp"
5) "server:server-C:ngrok_url"
6) "server:server-C:timestamp"
```

**✅ Si ves 6 claves = FUNCIONA**

---

## PRUEBA DE COMANDOS

### En máquina A, consola:

```
> list
 - agent-abc123 | hostname | Windows 11 | 14:32:45

> use @agent whoami
[enviado] id=xyz789 -> agent-abc123: whoami
```

### En máquina agente, debería ejecutarse comando

### En máquina A, debería ver resultado

```
[resultado de agent-abc123] (id=xyz789):
root
```

✅ **FUNCIONA**

---

## ⚠️ SI NO FUNCIONA

**Error: "Connection refused"**
```
Solución: Verifica que Redis está corriendo en máquina 1
redis-cli PING → PONG ✅
```

**Error: "Connection timed out"**
```
Solución: La IP es incorrecta o Red no conecta
ping 192.168.1.100 → debe responder
```

**No hay servidores en Redis**
```
Solución: Los servidores A, B, C no conectan a Redis
- Verifica IP en config_A.py, config_B.py, config_C.py
- Verifica redis.conf: bind 0.0.0.0
```

---

## 📋 CHECKLIST

- [ ] 5 IPs anotadas
- [ ] Redis corriendo: `redis-cli PING` = PONG
- [ ] Server-A corriendo, ngrok activo
- [ ] Server-B corriendo, ngrok activo
- [ ] Server-C corriendo, ngrok activo
- [ ] Agente corriendo, ve 3 servidores
- [ ] `redis-cli KEYS *` = 6 claves
- [ ] Comando `whoami` funciona

**Listo para la hackathon!** 🚀

