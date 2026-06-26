"""
Capa de cifrado para el canal C2.

Usa AES-256-GCM con clave precompartida (PSK):
- GCM da confidencialidad Y integridad (detecta si alguien modificó el mensaje)
- La clave debe ser la misma en server.py y agent.py (en un entorno real,
  esto se distribuiría de forma segura antes de desplegar el agente)

Formato del mensaje cifrado en el socket (todo en una línea, base64 + "\n"):
    nonce (12 bytes) + ciphertext+tag  -> todo junto, codificado en base64
"""

import json
import base64
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# --- CLAVE COMPARTIDA ---
# En producción esto NUNCA se hardcodea así. Para el reto, generamos una
# clave fija de 32 bytes (AES-256) que server.py y agent.py deben compartir.
# Se puede generar una nueva con: AESGCM.generate_key(bit_length=256)
SHARED_KEY = bytes.fromhex(
    "6998539d68277c74ff9a11f1749941837589c79ea24f66f36d6103e527359b14"
)

_aesgcm = AESGCM(SHARED_KEY)


def encrypt_json(data: dict) -> bytes:
    """Convierte un dict a JSON, lo cifra, y lo devuelve listo para mandar por socket (con \\n al final)."""
    plaintext = json.dumps(data).encode()
    nonce = os.urandom(12)  # nonce aleatorio de 12 bytes, requerido por GCM
    ciphertext = _aesgcm.encrypt(nonce, plaintext, associated_data=None)
    blob = nonce + ciphertext
    encoded = base64.b64encode(blob).decode()
    return (encoded + "\n").encode()


def decrypt_line(line: str) -> dict:
    """Toma una línea base64 recibida del socket y devuelve el dict original."""
    blob = base64.b64decode(line)
    nonce, ciphertext = blob[:12], blob[12:]
    plaintext = _aesgcm.decrypt(nonce, ciphertext, associated_data=None)
    return json.loads(plaintext)
