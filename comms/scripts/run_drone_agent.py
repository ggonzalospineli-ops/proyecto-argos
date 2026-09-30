"""Agente de a bordo: cifra la telemetria MAVLink local y la manda al ground station.

Uso:
    python scripts/run_drone_agent.py \\
        --identity keys/dron_identity.key \\
        --peer-pub keys/ground_identity.pub \\
        --ground-host 192.168.1.10 --ground-port 15760

El flight controller (Pixhawk/ArduPilot) debe estar publicando MAVLink por
UDP en 127.0.0.1:14550 (configuracion tipica de SERIAL*_PROTOCOL=2 +
salida UDP, o un mavlink-router local). Este agente escucha ahi, cifra, y
lo manda por el enlace real (radio SiK / 4G privado) al ground station.
"""

from __future__ import annotations

import argparse
import logging
import socket
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import DRONE_LOCAL_MAVLINK, SECURE_LINK_PORT
from src.identity import load_private_identity, load_public_identity
from src.secure_channel import SecureChannel
from src.telemetry_relay import TelemetryRelay


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--identity", required=True, help="ruta a la clave privada propia")
    p.add_argument("--peer-pub", required=True, help="ruta a la clave publica pineada del ground station")
    p.add_argument("--ground-host", required=True)
    p.add_argument("--ground-port", type=int, default=SECURE_LINK_PORT)
    p.add_argument("--local-host", default=DRONE_LOCAL_MAVLINK[0])
    p.add_argument("--local-port", type=int, default=DRONE_LOCAL_MAVLINK[1])
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                         format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    own_identity = load_private_identity(args.identity)
    peer_pub = load_public_identity(args.peer_pub)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", 0))  # puerto local efimero para el enlace saliente

    print(f"[ARGOS-1 dron] Iniciando handshake con ground station {args.ground_host}:{args.ground_port}...")
    chan = SecureChannel.connect(sock, (args.ground_host, args.ground_port), own_identity, peer_pub)
    print("[ARGOS-1 dron] Handshake OK. Sesion cifrada establecida (AES-256-GCM).")

    relay = TelemetryRelay((args.local_host, args.local_port), chan, local_is_source=True)
    print(f"[ARGOS-1 dron] Reenviando MAVLink de {args.local_host}:{args.local_port} cifrado hacia el ground.")
    relay.run_forever()


if __name__ == "__main__":
    main()
