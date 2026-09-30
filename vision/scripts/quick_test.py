"""Smoke test: valida que la instalacion funciona antes de tener dataset propio.

Corre YOLOv8n pre-entrenado (COCO, detecta "car", "person", "boat", etc.) sobre
la webcam o un video de prueba, sin necesitar entrenamiento propio todavia.
Esto es exactamente el objetivo de "esta semana" del plan: ver deteccion
funcionando end-to-end antes de invertir en el dataset propio.

Uso:
    python scripts/quick_test.py                       # webcam, 30s
    python scripts/quick_test.py --source video.mp4 --seconds 60
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import cv2
from ultralytics import YOLO


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--source", default="0")
    p.add_argument("--seconds", type=int, default=30)
    p.add_argument("--no-display", action="store_true")
    args = p.parse_args()

    print("[ARGOS-1] Descargando/cargando yolov8n.pt (pre-entrenado en COCO)...")
    model = YOLO("yolov8n.pt")  # se descarga solo la primera vez (~6MB)

    src = int(args.source) if args.source.isdigit() else args.source
    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        raise RuntimeError(f"No se pudo abrir la fuente: {args.source}")

    print(f"[ARGOS-1] Corriendo deteccion por {args.seconds}s. Presiona 'q' para cortar antes.")
    t0 = time.time()
    frames = 0
    total_detections = 0

    while time.time() - t0 < args.seconds:
        ok, frame = cap.read()
        if not ok:
            break
        results = model.predict(frame, conf=0.25, verbose=False)
        annotated = results[0].plot()
        total_detections += len(results[0].boxes)
        frames += 1

        if not args.no_display:
            cv2.imshow("ARGOS-1 - Quick Test", annotated)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()

    elapsed = time.time() - t0
    print(f"[ARGOS-1] OK: {frames} frames en {elapsed:.1f}s ({frames/elapsed:.1f} FPS), "
          f"{total_detections} detecciones totales.")
    print("[ARGOS-1] Instalacion validada. Siguiente paso: recolectar dataset propio (src/train.py).")


if __name__ == "__main__":
    main()
