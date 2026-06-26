# 🌐 Solución para Red Pública (Universidad)

## Problema
Las redes públicas tienen aislamiento de clientes - los dispositivos no pueden comunicarse directamente entre sí.

---

## ✅ Solución 1: Usar ngrok (Túnel Reverso)

### Qué es ngrok:
Crea un túnel seguro desde tu servidor local hacia internet, dándote una URL pública temporal.

### Pasos:

1. **Instala ngrok:**
   ```bash
   # Descarga desde https://ngrok.com/download
   # O usa snap:
   sudo snap install ngrok
   ```

2. **Inicia tu servidor C2:**
   ```bash
   cd /home/jose/ArchivoPortable/Hackatonn/aligo-c2-framework/server
   python3 server.py
   ```

3. **En otra terminal, crea el túnel:**
   ```bash
   ngrok tcp 4444
   ```

4. **ngrok te dará una URL como:**
   ```
   Forwarding: tcp://0.tcp.ngrok.io:12345 -> localhost:4444
   ```

5. **En los agentes, usa:**
   ```python
   SERVER_HOST = "0.tcp.ngrok.io"  # El host que te dio ngrok
   SERVER_PORT = 12345              # El puerto que te dio ngrok
   ```

### Ventajas:
✅ Funciona en cualquier red (incluso con NAT/firewall)
✅ No necesitas configurar nada en la red
✅ Los agentes pueden estar en cualquier red

### Desventajas:
⚠️ Requiere internet
⚠️ El túnel gratuito puede ser lento
⚠️ La URL cambia cada vez que reinicias ngrok

---

## ✅ Solución 2: Red Local con Switch/Router Propio

### Materiales:
- 1 router WiFi portátil o switch Ethernet
- Cables Ethernet (si usas switch)

### Pasos:
1. Configura el router en modo AP (Access Point)
2. Todos se conectan a ESE router
3. Usa la IP local del servidor (ej: 192.168.1.100)

### Ventajas:
✅ Control total de la red
✅ No depende de internet
✅ Velocidad óptima

### Desventajas:
⚠️ Necesitas hardware adicional

---

## ✅ Solución 3: Verificar si la Red de Universidad Permite Conexiones

### Prueba primero:

1. **Conecta todos los dispositivos a la red de la universidad**

2. **Obtén tu IP:**
   ```bash
   hostname -I | awk '{print $1}'
   ```

3. **Desde otro dispositivo, haz ping:**
   ```bash
   ping TU_IP_AQUI
   ```

4. **Si el ping funciona:**
   ✅ La red permite conexiones directas
   - Configura los agentes con tu IP
   - Asegúrate que el firewall permita el puerto 4444

5. **Si el ping NO funciona:**
   ❌ Hay aislamiento de clientes
   - Usa ngrok (Solución 1)
   - O consigue un router propio (Solución 2)

---

## 🎯 Recomendación para el Hackathon

**Mejor opción:** ngrok con cuenta gratuita

Es la más confiable y funciona en cualquier escenario de red.
