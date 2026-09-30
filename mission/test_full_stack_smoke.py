"""Smoke test de punta a punta con los procesos REALES (no solo funciones
importadas): levanta ground_mission_station.py y drone_mission_agent.py
como subprocesos de verdad, con un video sintetico como "camara", y
confirma que un cliente WebSocket recibe frames+detecciones del dashboard.

Esto valida el wiring de CLI/argparse/rutas que los otros tests (que
importan funciones directamente) no ejercitan. No requiere hardware.

Uso:
    python test_full_stack_smoke.py
"""

from __future__ import annotations

import asyncio
import json
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

import cv2
import numpy as np

MISSION_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = MISSION_ROOT.parent
COMMS_ROOT = PROJECT_ROOT / "comms"
VISION_ROOT = PROJECT_ROOT / "vision"

sys.path.insert(0, str(MISSION_ROOT))
from loader import isolated_project  # noqa: E402

with isolated_project(COMMS_ROOT):
    from src.identity import generate_identity

TMP_KEYS = COMMS_ROOT / "keys" / "_test_fullstack"
TMP_VIDEO = MISSION_ROOT / "_test_synthetic.mp4"


def free_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def make_synthetic_video(path: Path, n_frames: int = 15) -> None:
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(path), fourcc, 5.0, (320, 240))
    for i in range(n_frames):
        frame = np.zeros((240, 320, 3), dtype=np.uint8)
        frame[:] = (30, 60, 30)
        cv2.rectangle(frame, (40 + i, 40), (200 + i, 180), (200, 200, 200), -1)
        writer.write(frame)
    writer.release()


async def wait_for_dashboard_message(ws_port: int, timeout: float) -> dict:
    import websockets

    deadline = time.time() + timeout
    last_err = None
    while time.time() < deadline:
        try:
            async with websockets.connect(f"ws://127.0.0.1:{ws_port}") as ws:
                raw = await asyncio.wait_for(ws.recv(), timeout=deadline - time.time())
                return json.loads(raw)
        except (ConnectionRefusedError, OSError, asyncio.TimeoutError) as exc:
            last_err = exc
            await asyncio.sleep(0.5)
    raise TimeoutError(f"No llego ningun mensaje del dashboard a tiempo (ultimo error: {last_err})")


def main() -> None:
    print("=== ARGOS-1 · Smoke test full-stack (procesos reales) ===\n")

    print("[1/5] Preparando identidades y video sintetico")
    TMP_KEYS.mkdir(parents=True, exist_ok=True)
    drone_priv, drone_pub = generate_identity("test_dron_fs", TMP_KEYS)
    ground_priv, ground_pub = generate_identity("test_ground_fs", TMP_KEYS)
    make_synthetic_video(TMP_VIDEO)
    link_port = free_port()
    ws_port = free_port()
    print(f"  [OK] Identidades y video listos. link_port={link_port} ws_port={ws_port}")

    ground_proc = None
    drone_proc = None
    try:
        print("\n[2/5] Levantando ground_mission_station.py (proceso real)")
        ground_proc = subprocess.Popen(
            [
                sys.executable, str(MISSION_ROOT / "ground_mission_station.py"),
                "--identity", str(ground_priv),
                "--peer-pub", str(drone_pub),
                "--listen-port", str(link_port),
                "--dashboard-port", str(ws_port),
                "--no-display",
            ],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )
        time.sleep(1.5)  # dar tiempo a bind + arranque del dashboard
        assert ground_proc.poll() is None, "ground_mission_station.py se cayo al arrancar"
        print("  [OK] Ground station corriendo.")

        print("\n[3/5] Levantando drone_mission_agent.py (proceso real, video sintetico)")
        drone_proc = subprocess.Popen(
            [
                sys.executable, str(MISSION_ROOT / "drone_mission_agent.py"),
                "--identity", str(drone_priv),
                "--peer-pub", str(ground_pub),
                "--ground-host", "127.0.0.1",
                "--ground-port", str(link_port),
                "--weights", str(VISION_ROOT / "models" / "yolov8n.pt"),
                "--source", str(TMP_VIDEO),
                "--max-fps", "5",
            ],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )
        print("  [OK] Agente del dron corriendo, transmitiendo el video sintetico.")

        print("\n[4/5] Esperando un mensaje real del dashboard via WebSocket")
        message = asyncio.run(wait_for_dashboard_message(ws_port, timeout=30.0))
        assert "frame_id" in message and "detections" in message and "jpeg_b64" in message
        print(f"  [OK] Mensaje recibido del pipeline real: frame_id={message['frame_id']}, "
              f"{len(message['detections'])} deteccion(es), "
              f"{len(message['jpeg_b64'])} bytes de imagen (base64).")

        print("\n[5/5] Verificando que ambos procesos seguian vivos (no crashearon)")
        assert ground_proc.poll() is None, "ground_mission_station.py crasheo durante la transmision"
        assert drone_proc.poll() is None, "drone_mission_agent.py crasheo durante la transmision"
        print("  [OK] Ambos procesos siguen corriendo normalmente.")

        print("\n=== TODO OK: pipeline completo (dron real -> ground real -> dashboard real) validado ===")

    finally:
        for proc, name in ((drone_proc, "dron"), (ground_proc, "ground")):
            if proc is not None and proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
        shutil.rmtree(TMP_KEYS, ignore_errors=True)
        TMP_VIDEO.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
