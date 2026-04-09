import os
import json
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
STATE_DIR = ROOT_DIR / '.state'
LOGS_DIR = ROOT_DIR / 'logs'
SERVER_PID_FILE = STATE_DIR / 'server.pid'
SERVER_PORT = 3000

class ServerManager:
    def __init__(self):
        STATE_DIR.mkdir(exist_ok=True)
        LOGS_DIR.mkdir(exist_ok=True)

    def _get_log_path(self) -> str:
        from datetime import datetime
        date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        return str(LOGS_DIR / f'server_{date_str}.log')

    def _write_log(self, log_path: str, message: str) -> None:
        from datetime import datetime
        timestamp = datetime.now().isoformat()
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f'[{timestamp}] {message}\n')

    def _is_port_in_use(self, port: int) -> bool:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return False
            except OSError:
                return True

    def _wait_for_server(self, timeout: int = 10) -> bool:
        import socket
        start = time.time()
        while time.time() - start < timeout:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    s.connect(('localhost', SERVER_PORT))
                    return True
            except Exception:
                time.sleep(0.5)
        return False

    def _get_pid_from_file(self) -> Optional[int]:
        if not SERVER_PID_FILE.exists():
            return None
        try:
            pid_text = SERVER_PID_FILE.read_text().strip()
            if not pid_text:
                return None
            pid = int(pid_text)
            if pid <= 0:
                return None
            if sys.platform == 'win32':
                import ctypes
                kernel = ctypes.windll.kernel32
                PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
                handle = kernel.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
                if handle:
                    kernel.CloseHandle(handle)
                    return pid
                return None
            else:
                os.kill(pid, 0)
                return pid
        except (ValueError, ProcessLookupError, PermissionError, OSError):
            if SERVER_PID_FILE.exists():
                SERVER_PID_FILE.unlink()
            return None

    def start(self) -> dict:
        existing_pid = self._get_pid_from_file()
        if existing_pid:
            return {'status': 'error', 'message': 'Server is already running', 'pid': existing_pid, 'port': SERVER_PORT}

        if self._is_port_in_use(SERVER_PORT):
            return {'status': 'error', 'message': f'Port {SERVER_PORT} is already in use'}

        log_path = self._get_log_path()
        self._write_log(log_path, f'Starting server on port {SERVER_PORT}...')

        server_script = ROOT_DIR / 'src' / 'webui' / 'server' / 'src' / 'index.ts'
        if not server_script.exists():
            return {'status': 'error', 'message': f'Server script not found: {server_script}'}

        log_file = open(log_path, 'a', encoding='utf-8')

        try:
            import platform
            if platform.system() == 'Windows':
                cmd_to_run = ['cmd', '/c', 'npx.cmd', 'tsx', 'watch', str(server_script)]
            else:
                cmd_to_run = ['npx', 'tsx', 'watch', str(server_script)]

            self._write_log(log_path, f'Executing: {" ".join(cmd_to_run)}')

            process = subprocess.Popen(
                cmd_to_run,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                cwd=str(ROOT_DIR),
                env={**os.environ, 'NODE_ENV': 'development'}
            )

            SERVER_PID_FILE.write_text(str(process.pid))
            self._write_log(log_path, f'Server process started with PID: {process.pid}')

            if self._wait_for_server(timeout=15):
                self._write_log(log_path, f'Server is ready on port {SERVER_PORT}')
                return {
                    'status': 'started',
                    'pid': process.pid,
                    'port': SERVER_PORT,
                    'logPath': log_path,
                    'message': f'Server started on http://localhost:{SERVER_PORT}'
                }
            else:
                self._write_log(log_path, 'Server failed to start within timeout')
                return {'status': 'error', 'message': 'Server failed to start within timeout', 'logPath': log_path}
        except Exception as e:
            self._write_log(log_path, f'Failed to start server: {e}')
            return {'status': 'error', 'message': str(e), 'logPath': log_path}

    def stop(self) -> dict:
        pid = self._get_pid_from_file()
        if not pid:
            return {'status': 'not_running', 'message': 'Server is not running'}

        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(1)
            try:
                os.kill(pid, 0)
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            if SERVER_PID_FILE.exists():
                SERVER_PID_FILE.unlink()
            return {'status': 'stopped', 'message': 'Server stopped'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def status(self) -> dict:
        pid = self._get_pid_from_file()
        if pid and self._is_port_in_use(SERVER_PORT):
            log_files = sorted(LOGS_DIR.glob('server_*.log'), reverse=True)
            log_path = str(log_files[0]) if log_files else None
            return {'status': 'running', 'pid': pid, 'port': SERVER_PORT, 'logPath': log_path}
        elif pid:
            if SERVER_PID_FILE.exists():
                SERVER_PID_FILE.unlink()
            return {'status': 'not_running', 'message': 'Server process not found'}
        return {'status': 'not_running', 'message': 'Server is not running'}

    def logs(self, lines: int = 100) -> dict:
        log_files = sorted(LOGS_DIR.glob('server_*.log'), reverse=True)
        if not log_files:
            return {'status': 'ok', 'logs': [], 'message': 'No logs found'}

        log_path = str(log_files[0])
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
            log_entries = all_lines[-lines:] if len(all_lines) > lines else all_lines
            return {'status': 'ok', 'logs': [l.strip() for l in log_entries if l.strip()], 'logPath': log_path}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
