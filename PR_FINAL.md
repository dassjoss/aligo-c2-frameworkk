# Pull Request: Migración HTTPS + Cifrado + Arquitectura Distribuida

## 🎯 Resumen

Migración completa del framework ALIGO C2 de socket TCP a HTTPS con cifrado híbrido (RSA-2048 + Fernet), arquitectura distribuida con Redis y failover automático.

---

## 📦 Cambios Principales

### 1. **Migración TCP → HTTPS** ✅
- ✅ Servidor migrado de socket TCP (puerto 4444) a Flask HTTP/HTTPS (puerto 5000+)
- ✅ Agente migrado de socket TCP a requests HTTP
- ✅ Compatible con ngrok: `ngrok http 5000` (antes: `ngrok tcp 4444`)
- ✅ Terminal interactiva conservada 100% funcional
- ✅ Comandos idénticos: `list`, `use <agent_id> <cmd>`, `use @agent <cmd>`, `exit`

### 2. **Cifrado Híbrido** 🔐
- ✅ RSA-2048 para intercambio de claves (key exchange)
- ✅ Fernet (AES-128-CBC) para cifrado de sesión
- ✅ Handshake criptográfico automático en checkin
- ✅ Cada agente tiene session key única
- ✅ Cifrado end-to-end en comandos y resultados

### 3. **Arquitectura Distribuida con Redis** 🌐
- ✅ Redis como coordinador central
- ✅ Descubrimiento automático de servidores
- ✅ 3 servidores (A, B, C) con failover automático
- ✅ Puerto configurable: `python3 server.py 5000 server-A`
- ✅ Auto-detección y registro de URLs de ngrok
- ✅ TTL de 10 minutos para registro en Redis

### 4. **Failover Automático** 🔄
- ✅ Agente detecta servidores disponibles vía Redis
- ✅ Si servidor cae, cambia automáticamente a otro
- ✅ 3 intentos antes de hacer failover
- ✅ Reconexión inteligente
- ✅ Lista de servidores actualizada cada 60 segundos

### 5. **Interfaz Web con Streamlit** 🖥️
- ✅ Dashboard profesional con tema ALIGO
- ✅ Visualización de agentes en tiempo real
- ✅ Centro de control para comandos
- ✅ Estadísticas y métricas
- ✅ Accesible en http://localhost:8501

### 6. **Optimizaciones** ⚡
- ✅ Comando `list` solo muestra agentes activos (<30 segundos)
- ✅ Limpieza automática de agentes inactivos (>2 minutos)
- ✅ Nuevo comando `servers` para listar servidores en Redis
- ✅ Variables de entorno: `REDIS_HOST`, `REDIS_PORT`
- ✅ Redis opcional (funciona sin Redis en modo standalone)

---

## 🏗️ Arquitectura Final

```
┌─────────────────────┐
│  COMPUTADOR 1       │
│  CLIENTE            │
│  - Redis Server     │  ← Coordinador central
│  - Interfaz Web     │  ← Streamlit
└──────────┬──────────┘
           │
           │ Redis Registry
           │
    ┌──────┼──────┬──────┐
    │      │      │      │
┌───▼──┐ ┌─▼───┐ ┌─▼───┐ ┌────▼────┐
│SRV-A │ │SRV-B│ │SRV-C│ │ AGENTE  │
│:5000 │ │:5001│ │:5002│ │   5     │
│+ngrok│ │+ngrok│+ngrok│ │Ejecuta  │
│      │ │     │ │     │ │Comandos │
└──────┘ └─────┘ └─────┘ └─────────┘
   ▲                         │
   └─────────────────────────┘
        Cifrado E2E
```

---

## 📊 Commits Incluidos

```
b818411 feat: Agregar interfaz Streamlit y documentación de comandos
31a4552 feat: Integración Redis + Failover automático + Arquitectura 5 PCs
243cb95 chore: Limpiar archivos obsoletos de documentación y scripts
238b6c5 feat: Integrar cifrado híbrido RSA-2048 + Fernet en servidor HTTPS
534ab5c feat: Mejorar comando list - solo muestra agentes activos (últimos 30s)
c21f1f0 merge: Sincronizar con upstream (cifrado implementado)
```

---

## 🚀 Comandos de Uso

### Servidor:
```bash
# Puerto por defecto (5000):
python3 server/server.py

# Puerto personalizado:
python3 server/server.py 5001 server-B

# Con Redis:
REDIS_HOST=192.168.1.55 python3 server/server.py 5000 server-A
```

### Agente:
```bash
# Descubrimiento automático vía Redis:
REDIS_HOST=192.168.1.55 python3 agent/agent_ngrok.py

# URL directa (sin Redis):
python3 agent/agent_ngrok.py https://abc123.ngrok-free.app
```

### Interfaz:
```bash
cd interfaz
streamlit run cascaron.py
# Acceder: http://localhost:8501
```

---

## 📝 Archivos Modificados

### Core:
- `server/server.py` - Servidor HTTPS con cifrado + Redis
- `agent/agent_ngrok.py` - Agente con descubrimiento Redis + failover
- `shared/crypto_utils.py` - Utilidades de cifrado híbrido
- `requirements.txt` - Agregado `cryptography==41.0.7`

### Interfaz:
- `interfaz/cascaron.py` - Dashboard web Streamlit

### Documentación:
- `INSTRUCCIONES_5_COMPUTADORES.md` - Guía completa paso a paso
- `COMANDOS_EJECUTAR.md` - Comandos rápidos para cada PC
- `README.md` - Actualizado

---

## ✅ Testing Realizado

- ✅ Servidor corriendo en puerto 5000, 5001, 5002
- ✅ ngrok funcionando con URLs dinámicas
- ✅ Agentes conectados exitosamente (Windows y Linux)
- ✅ Cifrado verificado (handshake RSA + Fernet)
- ✅ Redis registro/descubrimiento funcional
- ✅ Failover automático probado (servidor A → B)
- ✅ Comandos ejecutados correctamente
- ✅ Migración de agentes entre servidores funcional
- ✅ Interfaz Streamlit operativa

---

## 🔐 Seguridad

- ✅ Cifrado end-to-end RSA-2048 + Fernet (AES-128-CBC)
- ✅ Session keys únicas por agente
- ✅ Handshake criptográfico automático
- ✅ Sin credenciales hardcodeadas
- ✅ Compatible con HTTPS/TLS de ngrok

---

## 📚 Documentación

Documentación completa disponible en:
- `INSTRUCCIONES_5_COMPUTADORES.md` - Setup de 5 computadores
- `COMANDOS_EJECUTAR.md` - Comandos rápidos
- Ejemplos de uso incluidos en cada archivo

---

## 🎯 Breaking Changes

### ⚠️ Cambios que afectan retrocompatibilidad:

1. **Protocolo de red:**
   - Antes: Socket TCP directo (puerto 4444)
   - Ahora: HTTP/HTTPS REST API (puerto 5000+)

2. **Comando de agente:**
   - Antes: `python agent.py HOST PORT`
   - Ahora: `python agent_ngrok.py https://URL` o `python agent_ngrok.py` (con Redis)

3. **ngrok:**
   - Antes: `ngrok tcp 4444`
   - Ahora: `ngrok http 5000`

4. **Dependencias nuevas:**
   - `cryptography==41.0.7` (cifrado)
   - `redis` (opcional, para arquitectura distribuida)
   - `streamlit` (opcional, para interfaz web)

### ✅ Compatibilidad mantenida:

- ✅ Comandos de terminal idénticos (`list`, `use`, `exit`)
- ✅ Capacidades de ejecución de comandos
- ✅ Multiplataforma (Windows, Linux, macOS)

---

## 🔮 Próximos Pasos / Future Work

- [ ] Autenticación multi-operador
- [ ] Persistencia de historial en Redis
- [ ] Logs centralizados
- [ ] API REST para integración externa
- [ ] Panel de métricas en tiempo real
- [ ] Alertas automáticas
- [ ] Soporte para plugins personalizados

---

## 👥 Colaboradores

- @dassjoss - Desarrollo principal
- @SiririComun - Upstream (cifrado original)

---

## 📄 Licencia

Mantiene la licencia del proyecto original.

---

**Ready for merge! 🚀**

Este PR contiene una migración completa y funcional del framework ALIGO C2, probada en múltiples computadores con diferentes sistemas operativos. Todo el código está documentado y listo para producción.
