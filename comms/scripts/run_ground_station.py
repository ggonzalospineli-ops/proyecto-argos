"""Ground station: recibe telemetria cifrada del dron y la republica en
MAVLink local plano para que QGroundControl / Mission Planner se conecten.

Uso:
    python scripts/run_ground_station.py \\
        --identity keys/ground_identity.key \\
        --peer-pub keys/dron_identity.pub \\
        --listen-port 15760

Despues, apuntar QGroundControl/Mission Planner a udp:127.0.0.1:14551
(GROUND_LOCAL_MAVLINK en config.py). Ese tramo es MAVLink plano, pero nunca
sale de la maquina del ground station -- corre en loopback.
"""

from __future__ import annotations

import argparse
import logging
import socket
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import GROUND_LOCAL_MAVLINK, SECURE_LINK_PORT
from src.identity import load_private_identity, load_public_identity
from src.secure_channel import SecureChannel
from src.telemetry_relay import TelemetryRelay


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--identity", required=True, help="ruta a la clave privada propia")
    p.add_argument("--peer-pub", required=True, help="ruta a la clave publica pineada del dron")
    p.add_argument("--listen-port", type=int, default=SECURE_LINK_PORT)
    p.add_argument("--local-host", default=GROUND_LOCAL_MAVLINK[0])
    p.add_argument("--local-port", type=int, default=GROUND_LOCAL_MAVLINK[1])
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                         format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    own_identity = load_private_identity(args.identity)
    peer_pub = load_public_identity(args.peer_pub)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", args.listen_port))

    print(f"[ARGOS-1 ground] Esperando handshake del dron en puerto {args.listen_port}...")
    chan = SecureChannel.accept(sock, own_identity, peer_pub)
    print(f"[ARGOS-1 ground] Handshake OK con {chan.remote_addr}. Sesion cifrada establecida.")

    relay = TelemetryRelay((args.local_host, args.local_port), chan, local_is_source=False)
    print(f"[ARGOS-1 ground] Republicando MAVLink descifrado en {args.local_host}:{args.local_port} "
          f"para QGroundControl/Mission Planner.")
    relay.run_forever()


if __name__ == "__main__":
    main()
