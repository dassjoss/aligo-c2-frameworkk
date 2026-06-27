"""
Crypto Utilities for ALIGO C2 Framework
Hybrid Encryption: RSA-2048 key exchange + Fernet session encryption

This module provides cryptographic primitives for secure C2 communications:
- RSA-2048 asymmetric encryption for session key exchange
- Fernet (AES-128-CBC + HMAC-SHA256) symmetric encryption for payload encryption
"""

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64


class C2Crypto:
    """
    Cryptographic operations for C2 framework using hybrid encryption.
    
    Architecture:
    1. Server generates RSA-2048 keypair on startup
    2. Agent fetches server's public key
    3. Agent generates Fernet session key
    4. Agent encrypts session key with server's RSA public key
    5. All subsequent messages encrypted with Fernet session key
    """
    
    @staticmethod
    def generate_rsa_keypair():
        """
        Generate a new RSA-2048 keypair.
        
        Returns:
            tuple: (private_key, public_key) as cryptography key objects
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        return private_key, public_key
    
    @staticmethod
    def serialize_public_key(public_key):
        """
        Serialize RSA public key to PEM format for transmission.
        
        Args:
            public_key: RSA public key object
            
        Returns:
            str: PEM-encoded public key as UTF-8 string
        """
        # CORRECTED: Changed 'public_key_bytes' to 'public_bytes'
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode('utf-8')
    
    @staticmethod
    def deserialize_public_key(pem_data):
        """
        Deserialize PEM-encoded RSA public key.
        
        Args:
            pem_data (str or bytes): PEM-encoded public key
            
        Returns:
            RSA public key object
        """
        if isinstance(pem_data, str):
            pem_data = pem_data.encode('utf-8')
        
        public_key = serialization.load_pem_public_key(
            pem_data,
            backend=default_backend()
        )
        return public_key
    
    @staticmethod
    def rsa_encrypt(public_key, plaintext):
        """
        Encrypt data using RSA-OAEP with SHA256.
        
        Args:
            public_key: RSA public key object
            plaintext (bytes): Data to encrypt
            
        Returns:
            str: Base64-encoded ciphertext
        """
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
        
        ciphertext = public_key.encrypt(
            plaintext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return base64.b64encode(ciphertext).decode('utf-8')
    
    @staticmethod
    def rsa_decrypt(private_key, ciphertext_b64):
        """
        Decrypt data using RSA-OAEP with SHA256.
        
        Args:
            private_key: RSA private key object
            ciphertext_b64 (str): Base64-encoded ciphertext
            
        Returns:
            bytes: Decrypted plaintext
        """
        ciphertext = base64.b64decode(ciphertext_b64)
        
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext
    
    @staticmethod
    def generate_session_key():
        """
        Generate a new Fernet symmetric encryption key.
        
        Returns:
            bytes: 32-byte Fernet key (URL-safe base64-encoded)
        """
        return Fernet.generate_key()
    
    @staticmethod
    def fernet_encrypt(key, plaintext):
        """
        Encrypt data using Fernet symmetric encryption.
        
        Args:
            key (bytes): Fernet encryption key
            plaintext (str or bytes): Data to encrypt
            
        Returns:
            str: Base64-encoded encrypted payload
        """
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
        
        f = Fernet(key)
        ciphertext = f.encrypt(plaintext)
        return base64.b64encode(ciphertext).decode('utf-8')
    
    @staticmethod
    def fernet_decrypt(key, ciphertext_b64):
        """
        Decrypt data using Fernet symmetric encryption.
        
        Args:
            key (bytes): Fernet encryption key
            ciphertext_b64 (str): Base64-encoded ciphertext
            
        Returns:
            bytes: Decrypted plaintext
        """
        ciphertext = base64.b64decode(ciphertext_b64)
        f = Fernet(key)
        plaintext = f.decrypt(ciphertext)
        return plaintext