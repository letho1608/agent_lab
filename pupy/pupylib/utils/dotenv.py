# -*- coding: utf-8 -*-
"""
Load .env file into os.environ. No external dependency.
GIST_RAW_URL, GIST_TOKEN (and others) read from .env.
Khi path=None: thử .env ở thư mục gốc project (pupy), rồi fallback os.getcwd().
"""

import os

# Thư mục gốc project: pupy/pupylib/utils/dotenv.py -> 3 cấp lên
_PROJECT_ROOT = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir, os.pardir)
)


def _default_env_path():
    """Đường dẫn .env mặc định: project root rồi cwd."""
    for base in (_PROJECT_ROOT, os.getcwd()):
        p = os.path.join(base, ".env")
        if os.path.isfile(p):
            return p
    return os.path.join(os.getcwd(), ".env")


def load_dotenv(path=None):
    """Load KEY=VALUE from .env file into os.environ. Skip empty lines and # comments."""
    if path is None:
        path = _default_env_path()
    elif os.path.isdir(path):
        path = os.path.join(path, ".env")
    if not os.path.isfile(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key:
                    os.environ.setdefault(key, value)
