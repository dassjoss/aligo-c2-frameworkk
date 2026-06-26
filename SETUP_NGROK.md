# 🌐 Setup Completo de ngrok

## Paso 1: Crear Cuenta (Gratis)

1. Ve a: **https://ngrok.com/signup**
2. Regístrate con:
   - Email
   - GitHub
   - Google
   - O lo que prefieras
3. Es **100% gratis** para uso básico

---

## Paso 2: Obtener tu Authtoken

1. Después de registrarte, ve a: **https://dashboard.ngrok.com/get-started/your-authtoken**
2. Verás algo como:
   ```
   Your Authtoken
   2hXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```
3. Copia ese token

---

## Paso 3: Instalar ngrok

### En Linux (tu sistema):

**Opción A: Snap (Recomendado)**
```bash
sudo snap install ngrok
```

**Opción B: Descarga directa**
```bash
# Descargar
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz

# Extraer
tar -xvzf ngrok-v3-stable-linux-amd64.tgz

# Mover a /usr/local/bin
sudo mv ngrok /usr/local/bin/

# Verificar
ngrok --version
```

---

## Paso 4: Configurar el Authtoken

**Solo necesitas hacer esto UNA VEZ:**

```bash
ngrok config add-authtoken TU_TOKEN_AQUI
```

Ejemplo:
```bash
ngrok config add-authtoken 2hXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Verás:
```
Authtoken saved to configuration file: /home/jose/.config/ngrok/ngrok.yml
```

✅ **¡Listo!** Ya no necesitas volver a configurarlo.

---

## Paso 5: Usar ngrok

### Para tu servidor C2:

```bash
# Iniciar túnel TCP en puerto 4444
ngrok tcp 4444
```

Verás algo como:
```
ngrok                                                          

Session Status                online
Account                       tu_email@ejemplo.com (Plan: Free)
Version                       3.5.0
Region                        United States (us)
Latency                       45ms
Web Interface                 http://127.0.0.1:4040
Forwarding                    tcp://0.tcp.ngrok.io:12345 -> localhost:4444

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

La línea importante es:
```
Forwarding: tcp://0.tcp.ngrok.io:12345 -> localhost:4444
```

**Eso significa:**
- `0.tcp.ngrok.io` = Tu host público
- `12345` = Tu puerto público
- Apunta a tu `localhost:4444` local

---

## 📋 Resumen de Comandos

### Setup inicial (una sola vez):
```bash
# 1. Instalar
sudo snap install ngrok

# 2. Configurar token (obtenerlo de https://dashboard.ngrok.com/get-started/your-authtoken)
ngrok config add-authtoken TU_TOKEN_AQUI
```

### Uso normal (cada vez que quieras exponer el servidor):
```bash
# Terminal 1: Servidor C2
cd /home/jose/ArchivoPortable/Hackatonn/aligo-c2-framework/server
python3 server.py

# Terminal 2: Túnel ngrok
ngrok tcp 4444
```

---

## 🎯 Script Automatizado

He creado un script que te guía paso a paso:
