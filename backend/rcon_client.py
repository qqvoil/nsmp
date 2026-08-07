import socket
import struct
import logging

class MCRconException(Exception):
    pass

class MinecraftRcon:
    """Pure Python Source/Minecraft RCON protocol client."""
    SERVERDATA_AUTH = 3
    SERVERDATA_AUTH_RESPONSE = 2
    SERVERDATA_EXECCOMMAND = 2
    SERVERDATA_RESPONSE_VALUE = 0

    def __init__(self, host: str, port: int, password: str, timeout: int = 5):
        self.host = host
        self.port = port
        self.password = password
        self.timeout = timeout
        self.sock = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect((self.host, self.port))
        self._auth()

    def disconnect(self):
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None

    def _send_packet(self, request_id: int, packet_type: int, payload: str):
        encoded = payload.encode('utf-8')
        length = len(encoded) + 10
        packet = struct.pack('<iii', length, request_id, packet_type) + encoded + b'\x00\x00'
        self.sock.sendall(packet)

    def _read_packet(self):
        header = self.sock.recv(12)
        if len(header) < 12:
            raise MCRconException("Incomplete packet header received from RCON server")
        length, request_id, packet_type = struct.unpack('<iii', header)
        body = b""
        remaining = length - 8
        while remaining > 0:
            chunk = self.sock.recv(min(remaining, 4096))
            if not chunk:
                break
            body += chunk
            remaining -= len(chunk)
        return request_id, packet_type, body.rstrip(b'\x00').decode('utf-8', errors='replace')

    def _auth(self):
        self._send_packet(1, self.SERVERDATA_AUTH, self.password)
        req_id, p_type, _ = self._read_packet()
        if req_id == -1:
            raise MCRconException("RCON Authentication failed: incorrect password")

    def command(self, cmd: str) -> str:
        if not self.sock:
            self.connect()
        self._send_packet(2, self.SERVERDATA_EXECCOMMAND, cmd)
        req_id, p_type, response = self._read_packet()
        return response

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

def execute_rcon_command(host: str, port: int, password: str, command: str) -> str:
    """Convenience helper to send a command and disconnect."""
    try:
        with MinecraftRcon(host, port, password) as rcon:
            return rcon.command(command)
    except Exception as e:
        logging.error(f"Failed to execute RCON command '{command}' on {host}:{port} - {e}")
        raise
