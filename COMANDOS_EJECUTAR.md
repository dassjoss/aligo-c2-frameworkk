# ⚡ COMANDOS RÁPIDOS - COPIAR Y PEGAR

## 📋 TUS 5 COMPUTADORES

Primero OBTÉN LAS IPs de cada máquina:

```bash
# Linux/Mac:
hostname -I

# Windows:
ipconfig | findstr "IPv4"
```

**Anota aquí:**
```
Cliente (Redis):    ___.___.___.___
Servidor A:         ___.___.___.___
Servidor B:         ___.___.___.___
Servidor C:         ___.___.___.___
Agente:             ___.___.___.___
```

---

## 🖥️ COMPUTADOR 1: CLIENTE

```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Interfaz Web
cd ~/aligo-c2-frameworkk/interfaz
streamlit run cascaron.py
```

Acceder interfaz: http://localhost:8501

---

## 🖥️ COMPUTADOR 2: SERVIDOR A

```bash
# IMPORTANTE: Cambia <IP_CLIENTE> por la IP real del cliente
export REDIS_HOST=<IP_CLIENTE>
export REDIS_PORT=6379

# Terminal 1: ngrok
ngrok http 5000

# Terminal 2: Servidor
cd ~/aligo-c2-frameworkk
python3 server/server.py 5000 server-A
```

---

## 🖥️ COMPUTADOR 3: SERVIDOR B

```bash
# IMPORTANTE: Cambia <IP_CLIENTE> por la IP real del cliente
export REDIS_HOST=<IP_CLIENTE>
export REDIS_PORT=6379

# Terminal 1: ngrok
ngrok http 5001

# Terminal 2: Servidor
cd ~/aligo-c2-frameworkk
python3 server/server.py 5001 server-B
```

---

## 🖥️ COMPUTADOR 4: SERVIDOR C

```bash
# IMPORTANTE: Cambia <IP_CLIENTE> por la IP real del cliente
export REDIS_HOST=<IP_CLIENTE>
export REDIS_PORT=6379

# Terminal 1: ngrok
ngrok http 5002

# Terminal 2: Servidor
cd ~/aligo-c2-frameworkk
python3 server/server.py 5002 server-C
```

---

## 🖥️ COMPUTADOR 5: AGENTE

```bash
# IMPORTANTE: Cambia <IP_CLIENTE> por la IP real del cliente
export REDIS_HOST=<IP_CLIENTE>
export REDIS_PORT=6379

# Ejecutar agente (descubrimiento automático)
cd ~/aligo-c2-frameworkk
python3 agent/agent_ngrok.py
```

---

## ✅ VERIFICAR QUE TODO FUNCIONA

### 1. En Cliente (Terminal 3):
```bash
redis-cli KEYS server:*
```
Debe mostrar 6 claves (3 URLs + 3 timestamps)

### 2. En Servidor A (Consola):
```bash
> servers
```
Debe mostrar los 3 servidores

```bash
> list
```
Debe mostrar el agente conectado

### 3. Probar comando:
```bash
> use @agent whoami
```
Debe ejecutarse en el agente y ver resultado

---

## 🔥 COMANDOS ÚTILES

### En Consola de Servidor:
```bash
list                    # Ver agentes conectados
servers                 # Ver servidores registrados
use @agent whoami       # Ejecutar comando (auto-selecciona único agente)
use agent-xxx pwd       # Ejecutar en agente específico
exit                    # Salir
```

### Verificar Redis:
```bash
redis-cli
> PING                              # Debe responder PONG
> KEYS *                            # Ver todas las claves
> GET server:server-A:ngrok_url     # Ver URL de servidor A
> TTL server:server-A:ngrok_url     # Ver tiempo restante (600 seg)
> exit
```

### Si algo falla:
```bash
# Verificar que Redis escucha en todas las IPs:
grep "^bind" /etc/redis/redis.conf
# Debe decir: bind 0.0.0.0

# Reiniciar Redis:
sudo systemctl restart redis
# O:
redis-server /etc/redis/redis.conf

# Verificar conectividad:
ping <IP_CLIENTE>
```

---

## 🎯 EJEMPLO COMPLETO (Copiar y pegar)

Suponiendo que Cliente está en **192.168.1.100**:

### Servidor A:
```bash
export REDIS_HOST=192.168.1.100
python3 server/server.py 5000 server-A
```

### Servidor B:
```bash
export REDIS_HOST=192.168.1.100
python3 server/server.py 5001 server-B
```

### Servidor C:
```bash
export REDIS_HOST=192.168.1.100
python3 server/server.py 5002 server-C
```

### Agente:
```bash
export REDIS_HOST=192.168.1.100
python3 agent/agent_ngrok.py
```

---

## 📱 ORDEN DE INICIO RECOMENDADO

1. ✅ Cliente: Redis + Interfaz
2. ✅ Servidor A: ngrok + server.py
3. ✅ Servidor B: ngrok + server.py
4. ✅ Servidor C: ngrok + server.py
5. ✅ Agente: agent_ngrok.py

**Espera 10 segundos entre cada paso para que se registren en Redis.**

---

## 🚨 TROUBLESHOOTING RÁPIDO

| Error | Solución |
|-------|----------|
| `Connection refused` | Redis no está corriendo en Cliente |
| `bind 127.0.0.1` | Cambiar a `bind 0.0.0.0` en redis.conf |
| `No hay servidores` | Servidores no tienen variable REDIS_HOST |
| `ngrok not found` | Instalar ngrok o verificar PATH |
| `No module named redis` | `pip3 install redis` |
| `No module named cryptography` | `pip3 install cryptography` |

---

**¡Listo para el demo! 🎉**
