"""Broadcaster WebSocket local para el dashboard.

ground_mission_station.py corre un loop sincrono (sockets UDP + cv2). El
dashboard necesita asyncio (websockets). En vez de reescribir el ground
station como async, este modulo corre su propio event loop en un thread
aparte y expone un metodo `publish()` thread-safe: el loop sincrono llama
`broadcaster.publish(dict)` por cada frame, y este lo reenvia a todos los
clientes del navegador conectados.

Todo corre en la red local (o loopback) -- no hay servidor externo
involucrado, consistente con el principio de soberania del proyecto.
"""

from __future__ import annotations

import asyncio
import json
import logging
import threading

import websockets

logger = logging.getLogger("argos1.dashboard_server")


class DashboardBroadcaster:
    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        self.host = host
        self.port = port
        self._clients: set = set()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._server = None
        self._thread: threading.Thread | None = None
        self._ready = threading.Event()

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        if not self._ready.wait(timeout=5):
            raise RuntimeError("El servidor de dashboard no arranco a tiempo")
        logger.info("Dashboard WebSocket escuchando en ws://%s:%d", self.host, self.port)

    def _run_loop(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._serve())

    async def _serve(self) -> None:
        async def handler(websocket, *_args):
            self._clients.add(websocket)
            logger.info("Cliente de dashboard conectado (%d activos)", len(self._clients))
            try:
                async for _ in websocket:
                    pass  # el dashboard solo recibe, no manda comandos (por ahora)
            finally:
                self._clients.discard(websocket)
                logger.info("Cliente de dashboard desconectado (%d activos)", len(self._clients))

        self._server = await websockets.serve(handler, self.host, self.port)
        self._ready.set()
        await self._server.wait_closed()

    def publish(self, data: dict) -> None:
        """Llamable desde el thread sincrono principal."""
        if self._loop is None:
            return
        message = json.dumps(data)
        asyncio.run_coroutine_threadsafe(self._broadcast(message), self._loop)

    async def _broadcast(self, message: str) -> None:
        if not self._clients:
            return
        stale = []
        for ws in list(self._clients):
            try:
                await ws.send(message)
            except Exception:
                stale.append(ws)
        for ws in stale:
            self._clients.discard(ws)

    def stop(self) -> None:
        if self._loop is None or self._server is None:
            return

        async def _shutdown():
            self._server.close()
            await self._server.wait_closed()

        future = asyncio.run_coroutine_threadsafe(_shutdown(), self._loop)
        try:
            future.result(timeout=5)
        except Exception:
            pass
