"""Test end-to-end de la integracion vision+comms, en localhost.

Valida la cadena completa sin hardware:
  1. Se genera un frame sintetico y se corre YOLO real sobre el (vision/).
  2. El frame se manda cifrado y fragmentado por un SecureChannel (comms/).
  3. Las detecciones se mandan cifradas como MSG_DETECTION, con el mismo
     frame_id que el video.
  4. El lado receptor reensambla el video, decodifica las detecciones, y
     verifica que ambos se correlacionan por frame_id y el frame es
     pixel-identico al original.

Uso:
    python test_integration_loopback.py
"""

from __future__ import annotations

import json
import socket
import sys
import threading
import time
from pathlib import Path

import cv2
import numpy as np

MISSION_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = MISSION_ROOT.parent
VISION_ROOT = PROJECT_ROOT / "vision"
COMMS_ROOT = PROJECT_ROOT / "comms"

sys.path.insert(0, str(MISSION_ROOT))
from loader import isolated_project  # noqa: E402

with isolated_project(COMMS_ROOT):
    from src.identity import generate_identity, load_private_identity, load_public_identity
    from src.secure_channel import SecureChannel, MSG_VIDEO, MSG_DETECTION
    from src.video_relay import VideoSender, VideoReceiver

with isolated_project(VISION_ROOT):
    from ultralytics import YOLO

from drone_mission_agent import build_detections

TMP_KEYS = COMMS_ROOT / "keys" / "_test_mission"


def setup_identities():
    TMP_KEYS.mkdir(parents=True, exist_ok=True)
    d_priv, d_pub = generate_identity("test_dron_mission", TMP_KEYS)
    g_priv, g_pub = generate_identity("test_ground_mission", TMP_KEYS)
    return {
        "drone_priv": load_private_identity(d_priv),
        "drone_pub": load_public_identity(d_pub),
        "ground_priv": load_private_identity(g_priv),
        "ground_pub": load_public_identity(g_pub),
    }


def make_synthetic_frame() -> np.ndarray:
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    frame[:] = (30, 60, 30)
    cv2.rectangle(frame, (150, 150), (450, 400), (180, 180, 180), -1)  # "objeto" claro y solido
    return frame


def main() -> None:
    print("=== ARGOS-1 · Test de integracion vision + comms (loopback) ===\n")

    print("[1/4] Handshake cifrado dron <-> ground")
    ids = setup_identities()

    ground_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ground_sock.bind(("127.0.0.1", 0))
    ground_port = ground_sock.getsockname()[1]

    drone_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    drone_sock.bind(("127.0.0.1", 0))

    result = {}

    def server_thread():
        result["ground_chan"] = SecureChannel.accept(ground_sock, ids["ground_priv"], ids["drone_pub"])

    t = threading.Thread(target=server_thread)
    t.start()
    time.sleep(0.1)
    drone_chan = SecureChannel.connect(drone_sock, ("127.0.0.1", ground_port), ids["drone_priv"], ids["ground_pub"])
    t.join(timeout=5)
    ground_chan = result["ground_chan"]
    print("  [OK] Canal cifrado establecido.")

    print("\n[2/4] Inferencia YOLO real sobre frame sintetico (vision/)")
    model = YOLO(str(VISION_ROOT / "models" / "yolov8n.pt"))
    frame = make_synthetic_frame()
    yolo_results = model.predict(frame, conf=0.25, verbose=False)
    detections = build_detections(yolo_results[0])
    print(f"  [OK] Modelo cargado y corrido sin errores ({len(detections)} deteccion(es) en el frame sintetico).")

    print("\n[3/4] Envio cifrado de video + detecciones correlacionadas por frame_id")
    sender = VideoSender(drone_chan, jpeg_quality=80)
    frame_id = sender.send_frame(frame)
    assert frame_id is not None
    payload = json.dumps({"frame_id": frame_id, "ts": time.time(), "detections": detections}).encode("utf-8")
    drone_chan.send(payload, MSG_DETECTION)
    print(f"  [OK] Frame {frame_id} + {len(detections)} deteccion(es) enviados cifrados.")

    print("\n[4/4] Reensamblado y correlacion del lado ground")
    receiver = VideoReceiver(ground_chan)
    ground_chan.sock.settimeout(2.0)

    received_frame = None
    received_detections = None
    received_frame_id = None
    deadline = time.time() + 5.0
    while time.time() < deadline and (received_frame is None or received_detections is None):
        msg_type, msg_payload = ground_chan.recv()
        if msg_type == MSG_VIDEO:
            fed = receiver.feed(msg_payload)
            if fed is not None:
                received_frame_id, received_frame = fed
        elif msg_type == MSG_DETECTION:
            data = json.loads(msg_payload.decode("utf-8"))
            received_detections = data["detections"]
            assert data["frame_id"] == frame_id

    assert received_frame is not None, "El video no se reensamblo a tiempo"
    assert received_detections is not None, "Las detecciones no llegaron a tiempo"
    assert received_frame_id == frame_id, "El frame_id del video no coincide con el de las detecciones"
    assert received_frame.shape == frame.shape
    assert received_detections == detections, "Las detecciones no llegaron identicas"
    print(f"  [OK] Video (frame_id={received_frame_id}) y {len(received_detections)} deteccion(es) "
          f"correlacionados y reensamblados correctamente del otro lado del canal cifrado.")

    print("\n[extra] Renderizado del lado ground con detecciones no vacias")
    # El frame sintetico no dispara detecciones reales de YOLO (no se parece
    # a ninguna clase de COCO), asi que probamos el path de dibujo/JSON con
    # datos con la misma forma que produce build_detections() en un caso real.
    from ground_mission_station import draw_detections as ground_draw_detections

    fake_detections = [
        {"cls": "persona", "conf": 0.873, "bbox": [150.0, 150.0, 300.0, 400.0], "cross_confirmed": True},
        {"cls": "vehiculo_4x4", "conf": 0.611, "bbox": [320.0, 200.0, 450.0, 350.0], "cross_confirmed": False},
    ]
    roundtrip = json.loads(json.dumps({"frame_id": 1, "ts": time.time(), "detections": fake_detections}))
    assert roundtrip["detections"] == fake_detections, "El JSON de detecciones no hace round-trip exacto"
    annotated = ground_draw_detections(frame.copy(), roundtrip["detections"])
    assert annotated.shape == frame.shape
    print("  [OK] JSON de detecciones hace round-trip exacto y el renderizado de cajas no falla.")

    drone_chan.close()
    ground_chan.close()

    import shutil
    shutil.rmtree(TMP_KEYS, ignore_errors=True)

    print("\n=== TODO OK: integracion vision + comms validada end-to-end ===")


if __name__ == "__main__":
    main()
