"""Identidad digital de cada extremo (dron / ground station).

Para un enlace punto a punto (un dron, un ground station) una CA completa
(X.509) es sobre-ingenieria: lo que hace falta es que cada lado sepa,
de antemano, la clave publica del otro (pinning), igual que SSH
`known_hosts`. Eso es lo que implementa este modulo: pares de claves
Ed25519 (firma) para autenticar el handshake, generados una vez e
instalados manualmente en ambos extremos.

Flujo de instalacion:
  1. En el dron:   python scripts/generate_identity.py --name dron
  2. En el ground: python scripts/generate_identity.py --name ground
  3. Copiar keys/dron_identity.pub -> ground station (fuera de banda: USB, SSH)
  4. Copiar keys/ground_identity.pub -> dron (fuera de banda)
  Cada lado se queda con su privada (nunca sale del dispositivo) y la
  publica pineada del otro.
"""

from __future__ import annotations

import os
import stat
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PrivateFormat,
    PublicFormat,
    NoEncryption,
)


def generate_identity(name: str, keys_dir: Path) -> tuple[Path, Path]:
    """Genera un par de claves Ed25519 y las guarda en keys_dir.

    La privada se guarda con permisos restrictivos (0600 en POSIX; en
    Windows NTFS esto no aplica via chmod, hay que restringir por ACL si
    se necesita defensa en profundidad real fuera del prototipo).
    """
    keys_dir.mkdir(parents=True, exist_ok=True)
    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key()

    priv_path = keys_dir / f"{name}_identity.key"
    pub_path = keys_dir / f"{name}_identity.pub"

    priv_bytes = priv.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
    pub_bytes = pub.public_bytes(Encoding.Raw, PublicFormat.Raw)

    priv_path.write_bytes(priv_bytes)
    pub_path.write_bytes(pub_bytes)

    try:
        os.chmod(priv_path, stat.S_IRUSR | stat.S_IWUSR)
    except (OSError, NotImplementedError):
        pass  # best-effort en Windows

    return priv_path, pub_path


def load_private_identity(path: Path | str) -> Ed25519PrivateKey:
    data = Path(path).read_bytes()
    return Ed25519PrivateKey.from_private_bytes(data)


def load_public_identity(path: Path | str) -> Ed25519PublicKey:
    data = Path(path).read_bytes()
    return Ed25519PublicKey.from_public_bytes(data)
