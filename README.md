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

## Tech Stack & Focus
- **Core**: RPYC-based interaction (Treat remote targets as local Python objects).
- **Stealth**: `pupyimporter` for RAM-only module loading. No disk writes, no temporary files.
- **OPSEC**: Removed all legacy binary bloat. Post-ex relies on **Pure Python** (pypykatz, impacket).
- **Transport**: Layered protocols (SSL, Obfs3, Scrambled, HTTP-wrapped) to bypass Deep Packet Inspection.

## Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Start C2 Server
python main.py

# Interactive Shell
python -m pupy.cli.pupysh
```

## Features
- **Fileless Execution**: Run Python modules and PE binaries directly in memory.
- **Unified Credentials**: One-stop module `creds` using pypykatz (no Mimikatz.exe needed).
- **Windows/Linux**: Multi-platform support with consistent API.
- **Reflective Injection**: Advanced DLL/PE loading techniques.

## License
BSD 3-Clause
