"""Inferencia en tiempo real: bounding boxes sobre webcam/video/RTSP.

Uso:
    python -m src.infer --source 0                      # webcam
    python -m src.infer --source ruta/video.mp4          # archivo
    python -m src.infer --source rtsp://192.168.1.50/live --thermal 1
    python -m src.infer --weights models/argos1_best.pt --conf 0.2

Con --thermal se activa fusion termica+RGB (ver src/fusion.py). La fuente
termica se espera como un segundo stream de video (webcam index o RTSP);
en el gimbal real del dron esto sale de la camara FLIR.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import cv2
from ultralytics import YOLO

from config import InferenceConfig
from src.fusion import overlay_fusion


def parse_args() -> InferenceConfig:
    cfg = InferenceConfig()
    p = argparse.ArgumentParser(description="ARGOS-1 - inferencia de vision en tiempo real")
    p.add_argument("--weights", default=cfg.weights)
    p.add_argument("--source", default=cfg.source, help='"0" para webcam, o ruta/URL de video')
    p.add_argument("--thermal", default=cfg.thermal_source, help="fuente termica opcional (index/ruta/RTSP)")
    p.add_argument("--imgsz", type=int, default=cfg.img_size)
    p.add_argument("--conf", type=float, default=cfg.conf_threshold)
    p.add_argument("--iou", type=float, default=cfg.iou_threshold)
    p.add_argument("--device", default=cfg.device)
    p.add_argument("--no-display", action="store_true", help="no abrir ventana (headless, ej. Jetson sin monitor)")
    p.add_argument("--save", action="store_true", default=cfg.save_output)
    p.add_argument("--output-dir", default=cfg.output_dir)
    args = p.parse_args()

    cfg.weights = args.weights
    cfg.source = args.source
    cfg.thermal_source = args.thermal
    cfg.img_size = args.imgsz
    cfg.conf_threshold = args.conf
    cfg.iou_threshold = args.iou
    cfg.device = args.device
    cfg.save_output = args.save
    cfg.output_dir = args.output_dir
    cfg.no_display = args.no_display  # type: ignore[attr-defined]
    return cfg


def _open_source(src: str) -> cv2.VideoCapture:
    # cv2.VideoCapture acepta int (index de camara) o string (ruta/URL)
    index = int(src) if src.isdigit() else src
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        raise RuntimeError(f"No se pudo abrir la fuente de video: {src}")
    return cap


def draw_detections(frame, result, cross_confirmed_ids: set[int] | None = None):
    names = result.names
    for i, box in enumerate(result.boxes):
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        label = f"{names.get(cls_id, cls_id)} {conf:.2f}"

        confirmed = cross_confirmed_ids is not None and i in cross_confirmed_ids
        color = (0, 255, 0) if confirmed else (0, 200, 255)
        thickness = 3 if confirmed else 2

        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, thickness)
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(frame, (int(x1), int(y1) - th - 8), (int(x1) + tw + 4, int(y1)), color, -1)
        cv2.putText(frame, label, (int(x1) + 2, int(y1) - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    return frame


def run(cfg: InferenceConfig) -> None:
    model = YOLO(cfg.weights)
    cap = _open_source(cfg.source)

    thermal_cap = None
    if cfg.thermal_source:
        thermal_cap = _open_source(cfg.thermal_source)

    writer = None
    if cfg.save_output:
        out_dir = Path(cfg.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"argos1_{int(time.time())}.mp4"
        fps = cap.get(cv2.CAP_PROP_FPS) or 20
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        writer = cv2.VideoWriter(str(out_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
        print(f"[ARGOS-1] Guardando salida en {out_path}")

    frame_count = 0
    t0 = time.time()

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            display_frame = frame
            if thermal_cap is not None:
                ok_t, thermal_frame = thermal_cap.read()
                if ok_t:
                    display_frame = overlay_fusion(frame, thermal_frame)

            results = model.predict(
                display_frame,
                imgsz=cfg.img_size,
                conf=cfg.conf_threshold,
                iou=cfg.iou_threshold,
                device=cfg.device,
                verbose=False,
            )
            result = results[0]
            annotated = draw_detections(display_frame.copy(), result)

            frame_count += 1
            elapsed = time.time() - t0
            fps_live = frame_count / elapsed if elapsed > 0 else 0.0
            cv2.putText(
                annotated,
                f"ARGOS-1 | {fps_live:.1f} FPS | {len(result.boxes)} detecciones",
                (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
            )

            if writer is not None:
                writer.write(annotated)

            if not getattr(cfg, "no_display", False):
                cv2.imshow("ARGOS-1 Vision", annotated)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    finally:
        cap.release()
        if thermal_cap is not None:
            thermal_cap.release()
        if writer is not None:
            writer.release()
        cv2.destroyAllWindows()
        print(f"[ARGOS-1] Fin. {frame_count} frames procesados en {time.time() - t0:.1f}s")


if __name__ == "__main__":
    run(parse_args())
