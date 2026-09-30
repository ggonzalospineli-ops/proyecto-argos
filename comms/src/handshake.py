"""Handshake mutuamente autenticado: ECDH efimero (X25519) firmado con la
identidad de largo plazo (Ed25519), al estilo del patron "signed DH" de
Signal/Noise. Dos mensajes, un round trip:

  cliente (dron) -> servidor (ground): ClientHello(eph_pub_c, sig_c, ts_c)
  servidor (ground) -> cliente (dron): ServerHello(eph_pub_s, sig_s, ts_s)

Cada lado firma su clave efimera + la del otro (una vez la conoce) + un
timestamp, con su clave de identidad Ed25519 de largo plazo. El receptor
verifica la firma contra la clave publica *pineada* del emisor (ver
identity.py) antes de confiar en la clave efimera. Sin esto, un atacante
en el medio podria ofrecer su propia clave efimera (clasico MITM sobre
Diffie-Hellman puro).

Tras el handshake, ambos calculan el mismo secreto compartido via X25519 y
derivan las claves de sesion AES-256 con HKDF (crypto.derive_session_keys).

`send`/`recv` son funciones inyectadas (no un socket concreto) para poder
testear el protocolo en memoria sin red real.
"""

from __future__ import annotations

import struct
import time
from dataclasses import dataclass
from typing import Callable

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)

from src.crypto import derive_session_keys

HELLO_STRUCT = ">32s32sd64s"  # eph_pub(32) + signed_peer_eph(32, 0 si no aplica) + timestamp(8) + firma(64)


class HandshakeError(Exception):
    pass


@dataclass
class SessionKeys:
    key_c2s: bytes
    key_s2c: bytes
    is_client: bool

    @property
    def send_key(self) -> bytes:
        return self.key_c2s if self.is_client else self.key_s2c

    @property
    def recv_key(self) -> bytes:
        return self.key_s2c if self.is_client else self.key_c2s


def _pack_hello(eph_pub: bytes, peer_eph_ref: bytes, ts: float, sig: bytes) -> bytes:
    return struct.pack(HELLO_STRUCT, eph_pub, peer_eph_ref, ts, sig)


def _unpack_hello(data: bytes) -> tuple[bytes, bytes, float, bytes]:
    if len(data) != struct.calcsize(HELLO_STRUCT):
        raise HandshakeError("Mensaje de handshake con tamano invalido")
    return struct.unpack(HELLO_STRUCT, data)


def _check_freshness(ts: float, max_skew: float) -> None:
    if abs(time.time() - ts) > max_skew:
        raise HandshakeError("Timestamp de handshake fuera de ventana (posible replay)")


def client_handshake(
    send: Callable[[bytes], None],
    recv: Callable[[], bytes],
    own_identity: Ed25519PrivateKey,
    peer_identity_pub: Ed25519PublicKey,
    max_skew: float = 30.0,
) -> SessionKeys:
    eph_priv = X25519PrivateKey.generate()
    eph_pub_bytes = eph_priv.public_key().public_bytes_raw()

    ts_c = time.time()
    # Firma sobre (eph_pub_c || ts_c): el servidor todavia no tiene eph_pub_s para incluir
    sig_c = own_identity.sign(eph_pub_bytes + struct.pack(">d", ts_c))
    send(_pack_hello(eph_pub_bytes, b"\x00" * 32, ts_c, sig_c))

    server_eph_pub_bytes, echoed_client_eph, ts_s, sig_s = _unpack_hello(recv())
    _check_freshness(ts_s, max_skew)
    if echoed_client_eph != eph_pub_bytes:
        raise HandshakeError("El servidor no confirmo la clave efimera del cliente (posible MITM)")

    try:
        peer_identity_pub.verify(
            sig_s, server_eph_pub_bytes + eph_pub_bytes + struct.pack(">d", ts_s)
        )
    except InvalidSignature as exc:
        raise HandshakeError("Firma del servidor invalida: identidad no confiable") from exc

    server_eph_pub = X25519PublicKey.from_public_bytes(server_eph_pub_bytes)
    shared_secret = eph_priv.exchange(server_eph_pub)
    transcript = eph_pub_bytes + server_eph_pub_bytes
    key_c2s, key_s2c = derive_session_keys(shared_secret, transcript)
    return SessionKeys(key_c2s, key_s2c, is_client=True)


def server_handshake(
    send: Callable[[bytes], None],
    recv: Callable[[], bytes],
    own_identity: Ed25519PrivateKey,
    peer_identity_pub: Ed25519PublicKey,
    max_skew: float = 30.0,
) -> SessionKeys:
    client_eph_pub_bytes, _unused, ts_c, sig_c = _unpack_hello(recv())
    _check_freshness(ts_c, max_skew)

    try:
        peer_identity_pub.verify(sig_c, client_eph_pub_bytes + struct.pack(">d", ts_c))
    except InvalidSignature as exc:
        raise HandshakeError("Firma del cliente invalida: identidad no confiable") from exc

    eph_priv = X25519PrivateKey.generate()
    eph_pub_bytes = eph_priv.public_key().public_bytes_raw()

    ts_s = time.time()
    sig_s = own_identity.sign(eph_pub_bytes + client_eph_pub_bytes + struct.pack(">d", ts_s))
    send(_pack_hello(eph_pub_bytes, client_eph_pub_bytes, ts_s, sig_s))

    client_eph_pub = X25519PublicKey.from_public_bytes(client_eph_pub_bytes)
    shared_secret = eph_priv.exchange(client_eph_pub)
    transcript = client_eph_pub_bytes + eph_pub_bytes
    key_c2s, key_s2c = derive_session_keys(shared_secret, transcript)
    return SessionKeys(key_c2s, key_s2c, is_client=False)
