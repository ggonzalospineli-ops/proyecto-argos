"""Configuracion central de comunicaciones cifradas ARGOS-1."""

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).parent
KEYS_DIR = ROOT / "keys"

PROTOCOL_VERSION = 1

# --- Enlace de telemetria (MAVLink) ---
# El dron habla MAVLink por UDP local (SiK radio -> modem -> udpin, o la
# salida UDP del flight controller/companion computer). Este proceso lo
# intercepta, cifra, y lo manda por el enlace real (radio/4G privado) al
# ground station, que lo vuelve a exponer como MAVLink UDP local para que
# QGroundControl/Mission Planner se conecten normalmente.
DRONE_LOCAL_MAVLINK = ("127.0.0.1", 14550)       # donde el flight controller publica MAVLink en el dron
GROUND_LOCAL_MAVLINK = ("127.0.0.1", 14551)      # donde el ground station republica MAVLink descifrado para el GCS

SECURE_LINK_PORT = 15760       # puerto del enlace cifrado dron <-> ground (el que "viaja" por el radio/4G)

# --- Enlace de video ---
SECURE_VIDEO_PORT = 15761
VIDEO_JPEG_QUALITY = 70
UDP_SAFE_PAYLOAD = 1200         # bytes por fragmento, por debajo del MTU tipico (evita fragmentacion IP)

# --- Handshake / anti-replay ---
HANDSHAKE_TIMEOUT_S = 5.0
HANDSHAKE_MAX_CLOCK_SKEW_S = 30.0   # ventana de frescura para el timestamp firmado
REPLAY_WINDOW_SIZE = 64             # ventana deslizante estilo IPsec/DTLS, tolera reordering de UDP


@dataclass
class LinkConfig:
    role: str                    # "drone" o "ground"
    remote_host: str = "127.0.0.1"
    remote_port: int = SECURE_LINK_PORT
    local_port: int = SECURE_LINK_PORT
    identity_key: str = ""       # ruta a la clave privada propia (keys/<nombre>_identity.key)
    peer_public_key: str = ""    # ruta a la clave publica del otro extremo, pineada de antemano
