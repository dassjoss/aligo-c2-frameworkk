# 🚀 Guía de Setup - Aligo C2 Framework

## Roles del Equipo (ACTUALIZADO)
- **Pablo:** Project Management & Pitch
- **Natalia:** Operator Interface
- **Jose:** Server Development (tú) ✅
- **Alex:** Agent Development

---

## 📡 Configuración del Servidor (Jose)

### Paso 1: Obtén tu IP
```bash
hostname -I | awk '{print $1}'
```

### Paso 2: Inicia el servidor
```bash
cd /home/jose/ArchivoPortable/Hackatonn/aligo-c2-framework/server
./start_server.sh
```

O directamente:
```bash
python3 server.py
```

El servidor escuchará en: `0.0.0.0:4444`

---

## 🎯 Configuración de Agentes (Alex o equipos objetivo)

### Paso 1: Edita agent.py
Cambia la línea:
```python
SERVER_HOST = "127.0.0.1"
```

Por la IP del servidor de Jose:
```python
SERVER_HOST = "10.1.83.160"  # Cambia por la IP actual
```

### Paso 2: Ejecuta el agente
```bash
cd /home/jose/ArchivoPortable/Hackatonn/aligo-c2-framework/agent
python3 agent.py
```

---

## 🌐 Opciones de Red

### Opción A: Punto de Acceso Móvil (RECOMENDADO)
1. Jose activa hotspot en su computadora
2. Los equipos con agentes se conectan al hotspot
3. Control total de la red

### Opción B: Red WiFi Compartida
1. Todos se conectan a la misma WiFi
2. Jose comparte su IP local
3. Los agentes se conectan

---

## 🎮 Comandos del Operador

Una vez que los agentes se conecten, usa estos comandos:

- `list` - Ver agentes conectados
- `use <agent_id> whoami` - Ejecutar comando
- `use <agent_id> ls -la` - Listar archivos
- `use <agent_id> pwd` - Ver directorio actual
- `exit` - Cerrar servidor

---

## ⚠️ Checklist Pre-Demo

- [ ] Servidor ejecutándose
- [ ] IP del servidor compartida con el equipo
- [ ] Agentes configurados con IP correcta
- [ ] Todos en la misma red (WiFi o hotspot)
- [ ] Puerto 4444 accesible
- [ ] Probar comando básico: `whoami`

---

## 🐛 Troubleshooting

**Agente no se conecta:**
- Verifica que la IP sea correcta
- Verifica que estén en la misma red
- Verifica que el firewall permita puerto 4444

**Error "Address already in use":**
```bash
# Mata el proceso usando el puerto
sudo lsof -ti:4444 | xargs kill -9
```

**Ver agentes conectados:**
Desde la consola del servidor, escribe: `list`
