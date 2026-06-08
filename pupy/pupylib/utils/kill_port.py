# -*- coding: utf-8 -*-
"""Giải phóng port bằng cách kill tiến trình đang listen trên port (Windows/Linux)."""

import sys
import subprocess
import time


def kill_process_on_port(port, wait_after_sec=0.5):
    """
    Tìm và kill tiến trình đang listen trên `port`.
    Trả về True nếu đã kill hoặc không có gì, False nếu lỗi.
    """
    port = int(port)
    if sys.platform == 'win32':
        return _kill_port_windows(port, wait_after_sec)
    return _kill_port_posix(port, wait_after_sec)


def _kill_port_windows(port, wait_after_sec):
    try:
        # netstat -ano: Proto, Local Address, Foreign Address, State, PID
        out = subprocess.check_output(
            ['netstat', '-ano'],
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0,
            stderr=subprocess.DEVNULL,
            universal_newlines=True,
        )
        pids = set()
        for line in out.splitlines():
            line = line.strip()
            if 'LISTENING' not in line:
                continue
            parts = line.split()
            if len(parts) < 5:
                continue
            # Local Address là cột 2 (index 1): 0.0.0.0:9000 hoặc [::]:9000
            local_addr = parts[1]
            pid_str = parts[-1]
            if ':' not in local_addr or not pid_str.isdigit():
                continue
            try:
                _, p = local_addr.rsplit(':', 1)
                if int(p) == port:
                    pids.add(int(pid_str))
            except ValueError:
                continue
        if not pids:
            return True
        for pid in pids:
            try:
                subprocess.run(
                    ['taskkill', '/F', '/PID', str(pid)],
                    capture_output=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0,
                    timeout=5,
                )
            except Exception:
                pass
        if wait_after_sec > 0:
            time.sleep(wait_after_sec)
        return True
    except Exception:
        return False


def _kill_port_posix(port, wait_after_sec):
    try:
        # fuser -k port/tcp hoặc lsof + kill
        try:
            subprocess.run(
                ['fuser', '-k', '{}/tcp'.format(port)],
                capture_output=True,
                timeout=5,
            )
        except FileNotFoundError:
            # lsof -ti:port | xargs kill -9
            out = subprocess.check_output(
                ['lsof', '-ti', ':{}'.format(port)],
                stderr=subprocess.DEVNULL,
                universal_newlines=True,
            )
            for pid in out.strip().split():
                if pid.isdigit():
                    try:
                        subprocess.run(['kill', '-9', pid], capture_output=True, timeout=3)
                    except Exception:
                        pass
        if wait_after_sec > 0:
            time.sleep(wait_after_sec)
        return True
    except Exception:
        return False
