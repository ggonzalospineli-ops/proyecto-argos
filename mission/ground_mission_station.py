"""Ground station de mision: recibe video + detecciones cifradas, reensambla
y dibuja las cajas sobre el video en tiempo real.

Uso:
    python ground_mission_station.py \\
        --identity ../comms/keys/ground_identity.key \\
        --peer-pub ../comms/keys/dron_identity.pub \\
        --listen-port 15761
"""

from __future__ import annotations

import argparse
import base64
import json
import socket
import sys
import time
from pathlib import Path

import cv2

MISSION_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = MISSION_ROOT.parent
COMMS_ROOT = PROJECT_ROOT / "comms"

sys.path.insert(0, str(MISSION_ROOT))
from loader import isolated_project  # noqa: E402
from dashboard_server import DashboardBroadcaster  # noqa: E402

with isolated_project(COMMS_ROOT):
    from src.identity import load_private_identity, load_public_identity
    from src.secure_channel import SecureChannel, MSG_VIDEO, MSG_DETECTION, ChannelError
    from src.video_relay import VideoReceiver
    from config import SECURE_VIDEO_PORT


def draw_detections(frame, detections: list[dict]):
    for det in detections:
        x1, y1, x2, y2 = [int(v) for v in det["bbox"]]
        label = f"{det['cls']} {det['conf']:.2f}"
        color = (0, 255, 0) if det.get("cross_confirmed") else (0, 200, 255)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(frame, (x1, y1 - th - 8), (x1 + tw + 4, y1), color, -1)
        cv2.putText(frame, label, (x1 + 2, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    return frame


def main() -> None:
    p = argparse.ArgumentParser(description="ARGOS-1 - ground station de mision (vision + comms)")
    p.add_argument("--identity", required=True)
    p.add_argument("--peer-pub", required=True)
    p.add_argument("--listen-port", type=int, default=SECURE_VIDEO_PORT)
    p.add_argument("--no-display", action="store_true", help="no abrir ventana (headless)")
    p.add_argument("--pending-detection-ttl", type=float, default=2.0,
                   help="segundos que se guarda un frame/deteccion esperando su par")
    p.add_argument("--no-dashboard", action="store_true", help="no levantar el servidor WebSocket del dashboard")
    p.add_argument("--dashboard-host", default="0.0.0.0")
    p.add_argument("--dashboard-port", type=int, default=8765)
    p.add_argument("--dashboard-jpeg-quality", type=int, default=70)
    args = p.parse_args()

    own_identity = load_private_identity(args.identity)
    peer_pub = load_public_identity(args.peer_pub)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", args.listen_port))

    print(f"[ARGOS-1 ground] Esperando handshake del dron en puerto {args.listen_port}...")
    chan = SecureChannel.accept(sock, own_identity, peer_pub)
    print(f"[ARGOS-1 ground] Handshake OK con {chan.remote_addr}.")

    receiver = VideoReceiver(chan)

    broadcaster = None
    if not args.no_dashboard:
        broadcaster = DashboardBroadcaster(args.dashboard_host, args.dashboard_port)
        broadcaster.start()
        print(f"[ARGOS-1 ground] Dashboard disponible: abrir dashboard/index.html "
              f"(o servirlo) apuntando a ws://<esta-ip>:{args.dashboard_port}")

    pending_frames: dict[int, tuple[float, "np.ndarray"]] = {}
    pending_detections: dict[int, tuple[float, list]] = {}

    def _evict_stale(d: dict) -> None:
        now = time.time()
        stale = [k for k, (ts, _) in d.items() if now - ts > args.pending_detection_ttl]
        for k in stale:
            del d[k]

    print("[ARGOS-1 ground] Recibiendo. Ctrl+C para cortar (o 'q' en la ventana).")
    chan.sock.settimeout(0.5)
    try:
        while True:
            try:
                msg_type, payload = chan.recv()
            except socket.timeout:
                continue
            except ChannelError as exc:
                print(f"[ARGOS-1 ground] Paquete descartado: {exc}")
                continue

            if msg_type == MSG_VIDEO:
                result = receiver.feed(payload)
                if result is None:
                    continue
                frame_id, frame = result
                if frame is None:
                    continue
                pending_frames[frame_id] = (time.time(), frame)

            elif msg_type == MSG_DETECTION:
                data = json.loads(payload.decode("utf-8"))
                pending_detections[data["frame_id"]] = (time.time(), data["detections"])

            _evict_stale(pending_frames)
            _evict_stale(pending_detections)

            # Emparejar por frame_id: mostrar apenas tengamos ambas partes
            ready = set(pending_frames) & set(pending_detections)
            for frame_id in sorted(ready):
                _, frame = pending_frames.pop(frame_id)
                _, detections = pending_detections.pop(frame_id)
                annotated = draw_detections(frame.copy(), detections)
                cv2.putText(annotated, f"frame {frame_id} | {len(detections)} det.",
                            (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                if detections:
                    print(f"[ARGOS-1 ground] frame {frame_id}: {len(detections)} deteccion(es) -> "
                          + ", ".join(f"{d['cls']} ({d['conf']:.2f})" for d in detections))

                if not args.no_display:
                    cv2.imshow("ARGOS-1 Ground Station", annotated)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        raise KeyboardInterrupt

                if broadcaster is not None:
                    ok, buf = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, args.dashboard_jpeg_quality])
                    if ok:
                        broadcaster.publish({
                            "frame_id": frame_id,
                            "ts": time.time(),
                            "detections": detections,
                            "jpeg_b64": base64.b64encode(buf).decode("ascii"),
                        })
    except KeyboardInterrupt:
        pass
    finally:
        chan.close()
        cv2.destroyAllWindows()
        if broadcaster is not None:
            broadcaster.stop()
        print("[ARGOS-1 ground] Recepcion cortada.")


if __name__ == "__main__":
    main()
