"""Streaming de video cifrado sobre el mismo SecureChannel.

Implementacion en Python puro (funciona en cualquier lado sin depender de
GStreamer). Cada frame se codifica JPEG, se fragmenta en trozos que caben
en un datagrama UDP, y cada fragmento se cifra individualmente via
SecureChannel (AES-256-GCM). El lado receptor reensambla por frame_id y
descarta frames incompletos viejos (mejor perder un frame que trabar el
video esperando un fragmento que se perdio).

Para produccion con GPU/hardware dedicado, la alternativa recomendada en el
plan es una pipeline GStreamer con `srtpenc`, o tunelizar todo el enlace de
video por WireGuard y dejar el codec sin cifrado propio (mas eficiente en
CPU, pero agrega esa dependencia externa). Esta implementacion es el
fallback universal que corre en cualquier notebook/Jetson sin instalar
nada mas alla de opencv.
"""

from __future__ import annotations

import logging
import socket
import struct
import time
from collections import defaultdict

import cv2
import numpy as np

from src.secure_channel import SecureChannel, MSG_VIDEO, ChannelError
from config import UDP_SAFE_PAYLOAD, VIDEO_JPEG_QUALITY

logger = logging.getLogger("argos1.video_relay")

FRAG_HEADER = ">IHH"  # frame_id(4) + frag_index(2) + frag_total(2)
FRAG_HEADER_LEN = struct.calcsize(FRAG_HEADER)
CHUNK_SIZE = UDP_SAFE_PAYLOAD - FRAG_HEADER_LEN


class VideoSender:
    def __init__(self, chan: SecureChannel, jpeg_quality: int = VIDEO_JPEG_QUALITY):
        self.chan = chan
        self.jpeg_quality = jpeg_quality
        self._frame_id = 0

    def send_frame(self, frame: np.ndarray) -> int | None:
        """Envia el frame fragmentado y cifrado. Devuelve el frame_id usado
        (para poder correlacionar, por ejemplo, con un mensaje MSG_DETECTION
        del mismo frame) o None si no se pudo codificar."""
        ok, encoded = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, self.jpeg_quality])
        if not ok:
            logger.warning("No se pudo codificar el frame a JPEG, se descarta")
            return None

        data = encoded.tobytes()
        chunks = [data[i : i + CHUNK_SIZE] for i in range(0, len(data), CHUNK_SIZE)]
        total = len(chunks)
        frame_id = self._frame_id
        self._frame_id = (self._frame_id + 1) % (2**32)

        for idx, chunk in enumerate(chunks):
            header = struct.pack(FRAG_HEADER, frame_id, idx, total)
            self.chan.send(header + chunk, MSG_VIDEO)

        return frame_id


class VideoReceiver:
    """Reensambla frames a partir de fragmentos cifrados.

    Mantiene como maximo `max_pending` frames incompletos en memoria; los
    mas viejos se descartan si llega uno nuevo antes de completarse (evita
    que un fragmento perdido trabe el video para siempre).
    """

    def __init__(self, chan: SecureChannel, max_pending: int = 8):
        self.chan = chan
        self.max_pending = max_pending
        self._pending: dict[int, dict[int, bytes]] = defaultdict(dict)
        self._expected_total: dict[int, int] = {}
        self._order: list[int] = []

    def _evict_if_needed(self) -> None:
        while len(self._order) > self.max_pending:
            oldest = self._order.pop(0)
            self._pending.pop(oldest, None)
            self._expected_total.pop(oldest, None)

    def feed(self, payload: bytes) -> tuple[int, np.ndarray] | None:
        """Procesa el payload YA DESCIFRADO de un mensaje MSG_VIDEO (el
        llamador es responsable de despachar por msg_type primero, para
        poder intercalar MSG_DETECTION u otros tipos en el mismo canal).
        Devuelve (frame_id, frame) si se completo el reensamblado, o None
        si todavia faltan fragmentos."""
        header, chunk = payload[:FRAG_HEADER_LEN], payload[FRAG_HEADER_LEN:]
        frame_id, idx, total = struct.unpack(FRAG_HEADER, header)

        if frame_id not in self._pending:
            self._order.append(frame_id)
            self._evict_if_needed()
        self._pending[frame_id][idx] = chunk
        self._expected_total[frame_id] = total

        if len(self._pending[frame_id]) == total:
            fragments = self._pending.pop(frame_id)
            self._expected_total.pop(frame_id, None)
            if frame_id in self._order:
                self._order.remove(frame_id)
            data = b"".join(fragments[i] for i in range(total))
            arr = np.frombuffer(data, dtype=np.uint8)
            frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            return frame_id, frame

        return None

    def poll_frame(self) -> np.ndarray | None:
        """Atajo para el caso de un canal dedicado solo a video: recibe un
        datagrama del canal el mismo, y descarta cualquier tipo que no sea
        MSG_VIDEO. Para canales que mezclan video con otros tipos de
        mensaje (ver mission/), despachar manualmente con chan.recv() +
        feed()."""
        try:
            msg_type, payload = self.chan.recv()
        except (socket.timeout, ChannelError):
            return None

        if msg_type != MSG_VIDEO:
            return None

        result = self.feed(payload)
        return result[1] if result is not None else None
