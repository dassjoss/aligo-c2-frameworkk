# Aligo C2 Framework

An educational software architecture project developed for the **Aligo Defensores Informáticos Hackathon**. 

The goal of this project is to design and implement a functional Command and Control (C2) system capable of coordinating remote endpoints from a central server within a closed, authorized laboratory environment.

---

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run test suite
python3 test_crypto.py
```

### Usage

```bash
# 1. Start the server
cd server
python3 server.py

# 2. Expose with ngrok (in another terminal)
ngrok http 5000

# 3. Connect agent (on target machine)
python3 agent/agent_ngrok.py https://your-ngrok-url.ngrok.io
```

### 📚 Documentation

- **[Quick Start Guide](docs/CRYPTO_QUICKSTART.md)** - Get started in 5 minutes
- **[Full Implementation Docs](docs/CRYPTO_IMPLEMENTATION.md)** - Complete technical documentation
- **[Protocol Audit Report](docs/PROTOCOL_AUDIT_REPORT.md)** - Security analysis
- **[Documentation Index](docs/INDEX.md)** - Browse all documentation

---

## 🔐 Security Features

- **RSA-2048** key exchange for secure session key establishment
- **Fernet (AES-128-CBC + HMAC-SHA256)** for payload encryption
- **Unique session keys** per agent connection
- **Zero plaintext** in transit - all commands and results encrypted

---

## 🏗️ Conceptual Architecture

The project is divided into three distinct logical components:

1. **Agent (`/agent`):** The software designed to run on the target system. It is responsible for establishing a connection with the server, receiving instructions, executing them locally, and returning the output.
2. **Server (`/server`):** The central hub of the architecture. It listens for incoming connections from agents, manages the queue of pending tasks, and coordinates the flow of information.
3. **Shared (`/shared`):** Cryptographic utilities and shared protocol definitions.

---

## 📂 Project Structure

```
aligo-c2-frameworkk/
├── agent/              # Agent implementation (HTTPS + encryption)
├── server/             # Flask server with hybrid encryption
├── shared/             # Crypto utilities (RSA + Fernet)
├── scripts/            # Deployment and testing scripts
├── docs/               # Complete documentation
├── test_crypto.py      # Cryptographic test suite
└── requirements.txt    # Python dependencies
```

---

## 🧪 Testing

```bash
# Run crypto test suite
python3 test_crypto.py

# Test HTTPS server
bash scripts/test_https.sh

# Test network connectivity
bash scripts/test_network.sh
```

---

## Team Roles & Responsibilities

* **Pablo:** Project Management, System Planning & Pitch Design
* **Natalia:** Operator Interface & Feature Integration
* **Jose:** Agent Development & Endpoint Logic
* **Alex:** Server Development & Security Protocols

---

## ⚠️ Educational Use Only

This software is developed for educational purposes within authorized laboratory environments. Unauthorized use for malicious purposes is strictly prohibited and illegal.
