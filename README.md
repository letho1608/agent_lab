# Pupy-NextGen
```text
  _____  _    _  _____ __     __
 |  __ \| |  | ||  __ \\ \   / /
 | |__) | |  | || |__) |\ \_/ / 
 |  ___/| |  | ||  ___/  \   /  
 | |    | |__| || |       | |   
 |_|     \____/ |_|       |_|   
  Memory-Only Remote Administration
```

## Overview

**Pupy-NextGen** is a stealth-focused, multi-platform remote administration tool (RAT) and post-exploitation framework built entirely in Python. Designed for security professionals and red teamers, it prioritizes **memory-only execution** and **fileless operations** to bypass modern defensive mechanisms like EDR and AV.

Unlike traditional C2 frameworks that rely on heavy binary payloads, Pupy-NextGen leverages an advanced in-memory Python environment, allowing you to interact with remote targets as if they were local Python objects.

---

## Key Features

### 🛡️ Advanced Stealth (OPSEC)
- **RAM-Only Execution**: Python modules and compiled extensions (.pyd/.so) are loaded directly into memory using `pupyimporter`. No temporary files are written to disk.
- **Pure Python Post-Ex**: Core capabilities (SAM/LSA dumping, credential gathering) have been migrated to pure Python (`pypykatz`, `impacket`), removing the need for detectable binaries like `mimikatz.exe`.
- **Reflective Injection**: Supports reflective DLL and PE loading directly into target processes.
- **Zero Legacy Bloat**: Entirely ported to Python 3.9+, removing all Python 2 compatibility layers for a smaller, faster, and cleaner agent.

### 🌐 Secure & Hidden Communication
- **Layered Transports**: Modular protocol stack allowing you to chain transports (e.g., `ssl(http(tcp))`).
- **Obfuscation**: Built-in support for `obfs3`, `RSA`, and custom scrambled protocols to bypass Deep Packet Inspection (DPI).
- **HTTP/DNS C2**: Wrap your C2 traffic in standard web traffic or DNS queries to stay under the radar.

### ⚡ Powerful Interaction
- **RPYC Foundation**: Real-time interaction using Remote Python Call (RPYC). Access remote file systems, registries, and processes using native Python syntax.
- **Unified Credential Module**: A single `creds` module that replaces multiple fragmented tools, providing a consistent workflow for gathering secrets.
- **Interactive Shell**: A feature-rich CLI (`pupysh`) with autocompletion, job management, and multi-session control.

---

## Architecture

1.  **C2 Server**: A Tornado-based asynchronous server managing multiple listeners and active sessions.
2.  **Pupy Agent**: A lightweight Python-based agent that bootstraps itself into memory and handles remote execution requests.
3.  **Transport Stack**: A flexible pipeline that encrypts and obfuscates data before it leaves the host.
4.  **Module System**: Standardized Python classes that define both server-side logic and client-side dependencies.

---

## Quick Start

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/letho1608/agent_lab.git
cd agent_lab

# Install dependencies
pip install -r requirements.txt
pip install .
```

### 2. Start the C2 Server
```bash
python main.py
```

### 3. Generate a Payload
```bash
# Example: Generate a Windows x64 executable
pupygen -f client -o windows -a x64 -c config/pupy.conf
```

---

## Core Modules

| Category | Description |
| :--- | :--- |
| **Gather** | `get_info`, `screenshot`, `keylogger`, `creds` (SAM/LSA/LSASS) |
| **Exploit** | `bypassuac`, `getsystem`, `impersonate`, `shellcode_exec` |
| **Manage** | `ps`, `ls`, `shell_exec`, `interactive_shell`, `migrate` |
| **Network** | `port_scan`, `socks5proxy`, `tcpdump`, `dns` |

---

## Disclaimer

This tool is intended **strictly for lawful, authorized security testing and educational purposes only**. Unauthorized access to computer systems is illegal. Users are responsible for complying with all applicable local, state, and federal laws.

## License

Pupy-NextGen is released under the **BSD 3-Clause License**. See `LICENSE` for details.
