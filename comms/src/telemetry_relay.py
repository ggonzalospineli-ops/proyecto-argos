"""Puente MAVLink local <-> canal cifrado.

Lado dron:   Flight Controller --MAVLink/UDP local--> [este relay] --cifrado--> radio/4G
Lado ground: radio/4G --cifrado--> [este relay] --MAVLink/UDP local--> QGroundControl / Mission Planner

El relay es agnostico al contenido MAVLink: reenvia los bytes tal cual,
cifrados. Opcionalmente usa pymavlink (si esta instalado) solo para logging
human-friendly del tipo de mensaje -- nunca para decidir si reenviar o no.
"""

from __future__ import annotations

import logging
import socket
import threading

from src.secure_channel import SecureChannel, MSG_TELEMETRY, ChannelError

logger = logging.getLogger("argos1.telemetry_relay")

try:
    from pymavlink import mavutil

    _HAS_PYMAVLINK = True
except ImportError:  # pymavlink es opcional, solo para logging enriquecido
    _HAS_PYMAVLINK = False


def _describe_mavlink(raw: bytes) -> str:
    if not _HAS_PYMAVLINK:
        return f"{len(raw)} bytes"
    try:
        # decodeo "best effort" solo para el log; nunca bloquea el reenvio
        mav = mavutil.mavlink.MAVLink(None)
        msg = mav.decode(bytearray(raw))
        return f"{msg.get_type()} ({len(raw)} bytes)"
    except Exception:
        return f"{len(raw)} bytes (no decodificable, se reenvia igual)"


class TelemetryRelay:
    """Bombea datagramas en ambas direcciones entre un socket MAVLink local
    y un SecureChannel, hasta que se llama a stop()."""

    def __init__(self, local_addr: tuple[str, int], secure_channel: SecureChannel, local_is_source: bool):
        """local_is_source=True en el dron (el FC empuja datos por UDP local,
        el relay escucha ahi). local_is_source=False en el ground (el relay
        reenvia HACIA ese puerto para que el GCS se conecte como cliente)."""
        self.local_addr = local_addr
        self.chan = secure_channel
        self.local_is_source = local_is_source
        self._stop = threading.Event()
        self._local_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._gcs_peer: tuple[str, int] | None = None

        if local_is_source:
            # dron: escuchamos lo que publica el flight controller
            self._local_sock.bind(local_addr)
        else:
            # ground: no bind fijo; aprendemos la direccion del GCS cuando
            # nos mande el primer paquete (QGroundControl/Mission Planner
            # inician conversacion hacia este puerto)
            self._local_sock.bind(local_addr)

    def _pump_local_to_secure(self) -> None:
        self._local_sock.settimeout(0.5)
        while not self._stop.is_set():
            try:
                data, addr = self._local_sock.recvfrom(4096)
            except socket.timeout:
                continue
            except OSError:
                break
            if not self.local_is_source:
                self._gcs_peer = addr  # el GCS local nos escribio primero
            logger.debug("local -> secure: %s", _describe_mavlink(data))
            try:
                self.chan.send(data, MSG_TELEMETRY)
            except OSError as exc:
                logger.warning("Error enviando por el canal cifrado: %s", exc)

    def _pump_secure_to_local(self) -> None:
        self.chan.sock.settimeout(0.5)
        while not self._stop.is_set():
            try:
                msg_type, payload = self.chan.recv()
            except socket.timeout:
                continue
            except ChannelError as exc:
                logger.warning("Paquete descartado: %s", exc)
                continue
            except OSError:
                break

            if msg_type != MSG_TELEMETRY:
                continue

            logger.debug("secure -> local: %s", _describe_mavlink(payload))
            if self.local_is_source:
                # dron: esto viene del ground station (comandos), reenviar al FC
                self._local_sock.sendto(payload, self.local_addr)
            else:
                # ground: reenviar al GCS que se registro localmente
                if self._gcs_peer is not None:
                    self._local_sock.sendto(payload, self._gcs_peer)

    def run_forever(self) -> None:
        t1 = threading.Thread(target=self._pump_local_to_secure, daemon=True)
        t2 = threading.Thread(target=self._pump_secure_to_local, daemon=True)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

    def start(self) -> None:
        threading.Thread(target=self._pump_local_to_secure, daemon=True).start()
        threading.Thread(target=self._pump_secure_to_local, daemon=True).start()

    def stop(self) -> None:
        self._stop.set()
        self._local_sock.close()
