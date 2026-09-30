"""Primitivas criptograficas para el enlace ARGOS-1.

Todo se apoya en `cryptography` (implementaciones auditadas de OpenSSL) -
no hay crypto casera. Este modulo solo compone:
  - AES-256-GCM para cifrado autenticado de cada datagrama.
  - HKDF-SHA256 para derivar claves de sesion a partir del secreto ECDH.
  - Una secuencia de nonces unica por sesion (evita el desastre clasico de
    reusar nonce con AES-GCM, que rompe la confidencialidad).
  - Una ventana anti-replay deslizante (estilo IPsec/DTLS) que tolera el
    reordering normal de UDP sin aceptar paquetes repetidos.
"""

from __future__ import annotations

import os
import struct

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

NONCE_SALT_LEN = 4    # aleatorio, fijo por sesion/direccion
NONCE_COUNTER_LEN = 8  # contador monotonico de 64 bits
NONCE_LEN = NONCE_SALT_LEN + NONCE_COUNTER_LEN  # 12 bytes, tamano estandar de GCM


class NonceSequence:
    """Genera nonces unicos de 12 bytes para una direccion de una sesion.

    salt aleatorio (4B) + contador monotonico (8B). Mientras el contador no
    de la vuelta (2^64 mensajes) el nonce nunca se repite para esta clave,
    que es la unica invariante que AES-GCM exige.
    """

    def __init__(self) -> None:
        self._salt = os.urandom(NONCE_SALT_LEN)
        self._counter = 0

    def next(self) -> bytes:
        nonce = self._salt + struct.pack(">Q", self._counter)
        self._counter += 1
        if self._counter >= 2**64:
            raise RuntimeError("Nonce counter agotado: renegociar sesion")
        return nonce

    @staticmethod
    def counter_from_nonce(nonce: bytes) -> int:
        return struct.unpack(">Q", nonce[NONCE_SALT_LEN:])[0]


class ReplayWindow:
    """Ventana deslizante anti-replay (bitmap), tolera reordering de UDP."""

    def __init__(self, size: int = 64) -> None:
        self._size = size
        self._highest = -1
        self._bitmap = 0

    def check_and_update(self, counter: int) -> bool:
        """True si el mensaje es valido (no repetido, dentro de ventana o mas nuevo)."""
        if counter > self._highest:
            shift = counter - self._highest
            self._bitmap = (self._bitmap << shift) & ((1 << self._size) - 1)
            self._bitmap |= 1
            self._highest = counter
            return True

        diff = self._highest - counter
        if diff >= self._size:
            return False  # demasiado viejo, fuera de la ventana
        if (self._bitmap >> diff) & 1:
            return False  # ya visto -> replay
        self._bitmap |= 1 << diff
        return True


def derive_session_keys(shared_secret: bytes, transcript: bytes) -> tuple[bytes, bytes]:
    """Deriva dos claves de 32 bytes (AES-256) a partir del secreto ECDH.

    `transcript` ata la derivacion a esta sesion especifica (claves efimeras
    de ambos lados) para que dos handshakes nunca produzcan las mismas
    claves. Se derivan claves separadas por direccion (client->server /
    server->client) para no compartir espacio de nonces entre ambos lados.
    """
    key_c2s = HKDF(
        algorithm=hashes.SHA256(), length=32, salt=transcript, info=b"argos1-c2s"
    ).derive(shared_secret)
    key_s2c = HKDF(
        algorithm=hashes.SHA256(), length=32, salt=transcript, info=b"argos1-s2c"
    ).derive(shared_secret)
    return key_c2s, key_s2c


def encrypt(key: bytes, nonce: bytes, plaintext: bytes, aad: bytes = b"") -> bytes:
    return AESGCM(key).encrypt(nonce, plaintext, aad)


def decrypt(key: bytes, nonce: bytes, ciphertext: bytes, aad: bytes = b"") -> bytes:
    """Lanza cryptography.exceptions.InvalidTag si el mensaje fue alterado
    o la clave/nonce no corresponden. Nunca falla "silenciosamente"."""
    return AESGCM(key).decrypt(nonce, ciphertext, aad)
