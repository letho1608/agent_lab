# Pupy-NextGen

Windows post-exploitation framework and C2 server.

## Overview

Pupy-NextGen is a powerful, multi-platform remote administration tool (RAT) and post-exploitation framework focused on stealth and memory-only execution.

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Start the server: `python main.py`
3. Use the shell: `python -m pupy.cli.pupysh`

## Architecture

- **Server**: Tornado-based C2 server.
- **Agent**: Python-based agent with in-memory loading capabilities.
- **Transport**: Layered communication stack (SSL, HTTP, Obfs3, etc.).

## Modules

- **Gather**: `get_info`, `screenshot`, `creds`.
- **Exploit**: `mimikatz`, `bypassuac`.
- **Manage**: `ps`, `shell_exec`.

## Features

- **95+ post-exploitation modules** for Windows targets
- **Pure Python** credential gathering using pypykatz
- **Multiple transports** for stealthy communication
- **In-Memory execution** of Python and PE files

## License

BSD 3-Clause License
