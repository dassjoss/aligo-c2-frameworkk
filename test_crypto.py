#!/usr/bin/env python3
"""
Test script for ALIGO C2 hybrid encryption implementation
Run this after installing: pip install -r requirements.txt
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from shared.crypto_utils import C2Crypto
import json

def test_rsa_operations():
    """Test RSA key generation and encryption/decryption"""
    print("\n[TEST 1] RSA-2048 Operations")
    print("=" * 50)
    
    # Generate keypair
    print("[*] Generating RSA-2048 keypair...")
    private_key, public_key = C2Crypto.generate_rsa_keypair()
    print("✓ Keypair generated")
    
    # Serialize public key
    print("[*] Serializing public key to PEM...")
    pem_key = C2Crypto.serialize_public_key(public_key)
    print("✓ Public key serialized")
    print(f"    PEM length: {len(pem_key)} bytes")
    
    # Deserialize public key
    print("[*] Deserializing public key from PEM...")
    restored_key = C2Crypto.deserialize_public_key(pem_key)
    print("✓ Public key deserialized")
    
    # Test encryption/decryption
    test_data = b"Hello, this is a test session key!"
    print(f"[*] Testing RSA encryption of: {test_data.decode()}")
    
    encrypted = C2Crypto.rsa_encrypt(public_key, test_data)
    print(f"✓ Encrypted (base64 length: {len(encrypted)})")
    
    decrypted = C2Crypto.rsa_decrypt(private_key, encrypted)
    print(f"✓ Decrypted: {decrypted.decode()}")
    
    assert test_data == decrypted, "RSA encryption/decryption failed!"
    print("✅ RSA operations: PASS\n")


def test_fernet_operations():
    """Test Fernet symmetric encryption/decryption"""
    print("[TEST 2] Fernet Symmetric Encryption")
    print("=" * 50)
    
    # Generate session key
    print("[*] Generating Fernet session key...")
    session_key = C2Crypto.generate_session_key()
    print(f"✓ Session key generated (length: {len(session_key)} bytes)")
    
    # Test JSON payload encryption
    test_payload = {
        "type": "cmd",
        "id": "test-123",
        "command": "whoami"
    }
    payload_json = json.dumps(test_payload)
    
    print(f"[*] Encrypting JSON payload: {payload_json}")
    encrypted = C2Crypto.fernet_encrypt(session_key, payload_json)
    print(f"✓ Encrypted (base64 length: {len(encrypted)})")
    
    decrypted = C2Crypto.fernet_decrypt(session_key, encrypted)
    decrypted_json = json.loads(decrypted)
    print(f"✓ Decrypted: {decrypted_json}")
    
    assert test_payload == decrypted_json, "Fernet encryption/decryption failed!"
    print("✅ Fernet operations: PASS\n")


def test_hybrid_flow():
    """Test complete hybrid encryption flow (RSA + Fernet)"""
    print("[TEST 3] Hybrid Encryption Flow (RSA + Fernet)")
    print("=" * 50)
    
    # Server side: Generate RSA keypair
    print("[SERVER] Generating RSA keypair...")
    server_private, server_public = C2Crypto.generate_rsa_keypair()
    server_public_pem = C2Crypto.serialize_public_key(server_public)
    print("✓ Server keypair ready")
    
    # Agent side: Fetch public key and generate session key
    print("\n[AGENT] Fetching server public key...")
    agent_server_public = C2Crypto.deserialize_public_key(server_public_pem)
    print("✓ Server public key received")
    
    print("[AGENT] Generating session key...")
    agent_session_key = C2Crypto.generate_session_key()
    print("✓ Agent session key generated")
    
    # Agent encrypts session key with server's public key
    print("[AGENT] Encrypting session key with server's public key...")
    encrypted_session_key = C2Crypto.rsa_encrypt(agent_server_public, agent_session_key)
    print("✓ Session key encrypted")
    
    # Server decrypts session key
    print("\n[SERVER] Decrypting agent's session key...")
    server_session_key = C2Crypto.rsa_decrypt(server_private, encrypted_session_key)
    print("✓ Session key decrypted")
    
    assert agent_session_key == server_session_key, "Session key mismatch!"
    print("✓ Session keys match!")
    
    # Server sends encrypted command
    print("\n[SERVER] Sending encrypted command to agent...")
    command = {"type": "cmd", "id": "abc123", "command": "whoami"}
    encrypted_cmd = C2Crypto.fernet_encrypt(server_session_key, json.dumps(command))
    print(f"✓ Command encrypted: {encrypted_cmd[:50]}...")
    
    # Agent receives and decrypts command
    print("[AGENT] Decrypting command...")
    decrypted_cmd = C2Crypto.fernet_decrypt(agent_session_key, encrypted_cmd)
    decrypted_cmd_json = json.loads(decrypted_cmd)
    print(f"✓ Command decrypted: {decrypted_cmd_json}")
    
    assert command == decrypted_cmd_json, "Command decryption failed!"
    
    # Agent sends encrypted result
    print("\n[AGENT] Sending encrypted result...")
    result = {"id": "abc123", "output": "els4nchez", "status": "ok"}
    encrypted_result = C2Crypto.fernet_encrypt(agent_session_key, json.dumps(result))
    print(f"✓ Result encrypted: {encrypted_result[:50]}...")
    
    # Server receives and decrypts result
    print("[SERVER] Decrypting result...")
    decrypted_result = C2Crypto.fernet_decrypt(server_session_key, encrypted_result)
    decrypted_result_json = json.loads(decrypted_result)
    print(f"✓ Result decrypted: {decrypted_result_json}")
    
    assert result == decrypted_result_json, "Result decryption failed!"
    
    print("\n✅ Complete hybrid encryption flow: PASS\n")


def main():
    print("╔" + "=" * 58 + "╗")
    print("║  ALIGO C2 - Crypto Implementation Test Suite           ║")
    print("╚" + "=" * 58 + "╝")
    
    try:
        test_rsa_operations()
        test_fernet_operations()
        test_hybrid_flow()
        
        print("╔" + "=" * 58 + "╗")
        print("║  🎉 ALL TESTS PASSED! Encryption ready for deployment ║")
        print("╚" + "=" * 58 + "╝")
        print()
        print("Next steps:")
        print("  1. Start server: cd server && python3 server.py")
        print("  2. Expose via ngrok: ngrok http 5000")
        print("  3. Connect agent: python3 agent/agent_ngrok.py <ngrok-url>")
        print()
        
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("\n[!] Missing dependencies. Install with:")
        print("    pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
