"""Canal UDP cifrado: handshake + AES-256-GCM por datagrama + anti-replay.

Es el enlace que efectivamente viaja por el radio SiK / 4G privado entre el
dron y el ground station. Uso tipico:

    # lado dron (cliente)
    chan = SecureChannel.connect(sock, remote_addr, own_identity, peer_pub)
    chan.send(mavlink_bytes)

    # lado ground (servidor)
    chan = SecureChannel.accept(sock, remote_addr, own_identity, peer_pub)
    data = chan.recv(timeout=1.0)
"""

from __future__ import annotations

import socket
import struct
from dataclasses import dataclass, field

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from src import crypto, handshake
from config import PROTOCOL_VERSION, HANDSHAKE_MAX_CLOCK_SKEW_S, REPLAY_WINDOW_SIZE

HEADER = ">BBQ"  # version(1) + msg_type(1) + counter(8, tambien va en el nonce pero se duplica para logging/debug
HEADER_LEN = struct.calcsize(HEADER)

MSG_TELEMETRY = 1
MSG_VIDEO = 2
MSG_KEEPALIVE = 3
MSG_DETECTION = 4  # metadata de detecciones del modulo de vision (JSON), correlacionada por frame_id


class ChannelError(Exception):
    pass


@dataclass
class SecureChannel:
    sock: socket.socket
    remote_addr: tuple[str, int]
    keys: handshake.SessionKeys
    _tx_nonces: crypto.NonceSequence = field(default_factory=crypto.NonceSequence)
    _rx_replay: crypto.ReplayWindow = field(default_factory=lambda: crypto.ReplayWindow(REPLAY_WINDOW_SIZE))

    @classmethod
    def connect(
        cls,
        sock: socket.socket,
        remote_addr: tuple[str, int],
        own_identity: Ed25519PrivateKey,
        peer_identity_pub: Ed25519PublicKey,
    ) -> "SecureChannel":
        """Lado cliente (tipicamente el dron): inicia el handshake."""

        def send(data: bytes) -> None:
            sock.sendto(data, remote_addr)

        def recv() -> bytes:
            data, _addr = sock.recvfrom(4096)
            return data

        keys = handshake.client_handshake(
            send, recv, own_identity, peer_identity_pub, HANDSHAKE_MAX_CLOCK_SKEW_S
        )
        return cls(sock=sock, remote_addr=remote_addr, keys=keys)

    @classmethod
    def accept(
        cls,
        sock: socket.socket,
        own_identity: Ed25519PrivateKey,
        peer_identity_pub: Ed25519PublicKey,
    ) -> "SecureChannel":
        """Lado servidor (tipicamente el ground station): espera un
        handshake entrante y aprende la direccion del peer del primer
        datagrama recibido."""
        remote_addr_holder: list[tuple[str, int]] = []

        def send(data: bytes) -> None:
            sock.sendto(data, remote_addr_holder[0])

        def recv() -> bytes:
            data, addr = sock.recvfrom(4096)
            if not remote_addr_holder:
                remote_addr_holder.append(addr)
            return data

        keys = handshake.server_handshake(
            send, recv, own_identity, peer_identity_pub, HANDSHAKE_MAX_CLOCK_SKEW_S
        )
        return cls(sock=sock, remote_addr=remote_addr_holder[0], keys=keys)

    def send(self, payload: bytes, msg_type: int = MSG_TELEMETRY) -> None:
        nonce = self._tx_nonces.next()
        counter = crypto.NonceSequence.counter_from_nonce(nonce)
        aad = struct.pack(HEADER, PROTOCOL_VERSION, msg_type, counter)
        ciphertext = crypto.encrypt(self.keys.send_key, nonce, payload, aad)
        packet = aad + nonce[: crypto.NONCE_SALT_LEN] + ciphertext
        self.sock.sendto(packet, self.remote_addr)

    def recv(self, bufsize: int = 65536) -> tuple[int, bytes]:
        """Devuelve (msg_type, payload) del proximo datagrama valido.
        Descarta silenciosamente (con excepcion loggeable) paquetes
        corruptos, de fuentes no autenticadas o repetidos."""
        data, addr = self.sock.recvfrom(bufsize)
        if addr[0] != self.remote_addr[0]:
            raise ChannelError(f"Datagrama de origen inesperado: {addr}")

        if len(data) < HEADER_LEN + crypto.NONCE_SALT_LEN:
            raise ChannelError("Datagrama demasiado corto")

        header = data[:HEADER_LEN]
        salt = data[HEADER_LEN : HEADER_LEN + crypto.NONCE_SALT_LEN]
        ciphertext = data[HEADER_LEN + crypto.NONCE_SALT_LEN :]

        version, msg_type, counter = struct.unpack(HEADER, header)
        if version != PROTOCOL_VERSION:
            raise ChannelError(f"Version de protocolo no soportada: {version}")

        if not self._rx_replay.check_and_update(counter):
            raise ChannelError(f"Paquete repetido/fuera de ventana (counter={counter}) -> descartado")

        nonce = salt + struct.pack(">Q", counter)
        try:
            payload = crypto.decrypt(self.keys.recv_key, nonce, ciphertext, aad=header)
        except InvalidTag as exc:
            raise ChannelError("Autenticacion fallida: paquete alterado o clave incorrecta") from exc

        return msg_type, payload

    def close(self) -> None:
        self.sock.close()
