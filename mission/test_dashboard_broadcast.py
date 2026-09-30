"""Test end-to-end del broadcaster del dashboard: servidor real + cliente
WebSocket real (el mismo protocolo que usa dashboard/index.html).

Uso:
    python test_dashboard_broadcast.py
"""

from __future__ import annotations

import asyncio
import json
import time

from dashboard_server import DashboardBroadcaster


async def _client_receive(url: str, timeout: float = 5.0) -> dict:
    import websockets

    async with websockets.connect(url) as ws:
        raw = await asyncio.wait_for(ws.recv(), timeout=timeout)
        return json.loads(raw)


def main() -> None:
    print("=== ARGOS-1 · Test del broadcaster de dashboard (loopback) ===\n")

    print("[1/3] Arrancando servidor WebSocket local")
    broadcaster = DashboardBroadcaster(host="127.0.0.1", port=8765)
    broadcaster.start()
    print("  [OK] Servidor arriba en ws://127.0.0.1:8765")

    print("\n[2/3] Conectando cliente y publicando un mensaje")
    payload = {
        "frame_id": 42,
        "ts": time.time(),
        "detections": [{"cls": "persona", "conf": 0.91, "bbox": [10, 10, 50, 90], "cross_confirmed": True}],
        "jpeg_b64": "ZmFrZS1qcGVnLWJ5dGVz",  # placeholder, no necesita ser un JPEG valido para este test
    }

    async def scenario():
        connect_task = asyncio.ensure_future(_client_receive("ws://127.0.0.1:8765"))
        await asyncio.sleep(0.3)  # dar tiempo a que el cliente termine el handshake antes de publicar
        broadcaster.publish(payload)
        return await connect_task

    received = asyncio.run(scenario())
    assert received == payload, "El cliente no recibio exactamente lo publicado"
    print("  [OK] El cliente WebSocket recibio el mensaje publicado, identico byte a byte (JSON).")

    print("\n[3/3] Apagando servidor")
    broadcaster.stop()
    print("  [OK] Servidor apagado limpiamente.")

    print("\n=== TODO OK: broadcaster de dashboard validado end-to-end ===")


if __name__ == "__main__":
    main()
