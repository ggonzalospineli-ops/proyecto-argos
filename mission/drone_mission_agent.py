"""Agente de mision a bordo del dron: camara -> YOLO -> canal cifrado.

Junta los dos pilares ya construidos:
  - vision/  : deteccion en tiempo real (YOLOv8), fusion termica opcional
  - comms/   : canal UDP cifrado (AES-256-GCM) con autenticacion mutua

Por cada frame: se manda el video (fragmentado y cifrado) y, aparte, un
mensaje MSG_DETECTION con las cajas detectadas en JSON, correlacionado por
frame_id. El ground station reensambla el video y superpone las cajas al
recibir ambos mensajes -- asi el enlace de video no carga con el overhead
del dibujo, y el operador puede ver las detecciones incluso si un frame de
video se perdio en el camino.

Uso:
    python drone_mission_agent.py \\
        --identity ../comms/keys/dron_identity.key \\
        --peer-pub ../comms/keys/ground_identity.pub \\
        --ground-host 192.168.1.10 \\
        --weights ../vision/models/yolov8n.pt \\
        --source 0
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import cv2

MISSION_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = MISSION_ROOT.parent
VISION_ROOT = PROJECT_ROOT / "vision"
COMMS_ROOT = PROJECT_ROOT / "comms"

sys.path.insert(0, str(MISSION_ROOT))
from loader import isolated_project  # noqa: E402

with isolated_project(COMMS_ROOT):
    from src.identity import load_private_identity, load_public_identity
    from src.secure_channel import SecureChannel, MSG_DETECTION
    from src.video_relay import VideoSender
    from config import SECURE_VIDEO_PORT

with isolated_project(VISION_ROOT):
    from ultralytics import YOLO


def build_detections(result, cross_confirmed: bool = False) -> list[dict]:
    names = result.names
    detections = []
    for box in result.boxes:
        x1, y1, x2, y2 = [round(v, 1) for v in box.xyxy[0].tolist()]
        cls_id = int(box.cls[0])
        detections.append(
            {
                "cls": names.get(cls_id, str(cls_id)),
                "conf": round(float(box.conf[0]), 3),
                "bbox": [x1, y1, x2, y2],
                "cross_confirmed": cross_confirmed,
            }
        )
    return detections


def main() -> None:
    p = argparse.ArgumentParser(description="ARGOS-1 - agente de mision (vision + comms)")
    p.add_argument("--identity", required=True)
    p.add_argument("--peer-pub", required=True)
    p.add_argument("--ground-host", required=True)
    p.add_argument("--ground-port", type=int, default=SECURE_VIDEO_PORT)
    p.add_argument("--weights", default=str(VISION_ROOT / "models" / "yolov8n.pt"))
    p.add_argument("--source", default="0")
    p.add_argument("--conf", type=float, default=0.25)
    p.add_argument("--jpeg-quality", type=int, default=70)
    p.add_argument("--max-fps", type=float, default=10.0, help="limite de FPS enviados por el enlace (ancho de banda)")
    args = p.parse_args()

    own_identity = load_private_identity(args.identity)
    peer_pub = load_public_identity(args.peer_pub)

    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", 0))

    print(f"[ARGOS-1 dron] Handshake con ground station {args.ground_host}:{args.ground_port}...")
    chan = SecureChannel.connect(sock, (args.ground_host, args.ground_port), own_identity, peer_pub)
    print("[ARGOS-1 dron] Canal cifrado establecido.")

    video_sender = VideoSender(chan, jpeg_quality=args.jpeg_quality)

    print(f"[ARGOS-1 dron] Cargando modelo de vision: {args.weights}")
    model = YOLO(args.weights)

    src = int(args.source) if args.source.isdigit() else args.source
    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        raise RuntimeError(f"No se pudo abrir la fuente de video: {args.source}")

    min_interval = 1.0 / args.max_fps if args.max_fps > 0 else 0.0
    last_sent = 0.0

    print("[ARGOS-1 dron] Transmitiendo video + detecciones cifradas. Ctrl+C para cortar.")
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            now = time.time()
            if now - last_sent < min_interval:
                continue
            last_sent = now

            results = model.predict(frame, conf=args.conf, verbose=False)
            detections = build_detections(results[0])

            frame_id = video_sender.send_frame(frame)
            if frame_id is None:
                continue

            payload = json.dumps({"frame_id": frame_id, "ts": now, "detections": detections}).encode("utf-8")
            chan.send(payload, MSG_DETECTION)

            if detections:
                print(f"[ARGOS-1 dron] frame {frame_id}: {len(detections)} deteccion(es)")
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        chan.close()
        print("[ARGOS-1 dron] Transmision cortada.")


if __name__ == "__main__":
    main()
