"""Genera el par de claves Ed25519 de un extremo (dron o ground station).

Uso:
    python scripts/generate_identity.py --name dron
    python scripts/generate_identity.py --name ground

Despues hay que copiar manualmente (USB, SSH, lo que sea *fuera de banda*)
la .pub de cada lado al otro:
    dron keys/dron_identity.pub     -> ground station
    ground keys/ground_identity.pub -> dron
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import KEYS_DIR
from src.identity import generate_identity


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--name", required=True, help='"dron" o "ground" (o cualquier nombre de extremo)')
    args = p.parse_args()

    priv_path, pub_path = generate_identity(args.name, KEYS_DIR)
    print(f"[ARGOS-1] Identidad generada para '{args.name}':")
    print(f"  privada: {priv_path}  (NO sale de este dispositivo)")
    print(f"  publica: {pub_path}  (copiar al otro extremo, fuera de banda)")


if __name__ == "__main__":
    main()
