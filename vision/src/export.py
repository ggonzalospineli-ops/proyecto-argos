"""Exporta un modelo entrenado a ONNX / TensorRT para inferencia en el borde.

En el dron el computo corre en un Jetson Orin Nano (o similar) con recursos
limitados: hace falta exportar el modelo .pt a un runtime optimizado para
mantener ~30 FPS.

Uso:
    python -m src.export --weights runs/train/argos1/weights/best.pt --format onnx
    python -m src.export --weights runs/train/argos1/weights/best.pt --format engine  # TensorRT, requiere Jetson/GPU NVIDIA
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from ultralytics import YOLO


def main() -> None:
    p = argparse.ArgumentParser(description="ARGOS-1 - export de modelo a runtime de borde")
    p.add_argument("--weights", required=True, help="ruta al .pt entrenado")
    p.add_argument("--format", default="onnx", choices=["onnx", "engine", "openvino"],
                    help="onnx = portable (CPU/GPU), engine = TensorRT (Jetson), openvino = Intel")
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--half", action="store_true", help="precision FP16 (mas rapido, requiere GPU compatible)")
    args = p.parse_args()

    model = YOLO(args.weights)
    exported_path = model.export(format=args.format, imgsz=args.imgsz, half=args.half)
    print(f"[ARGOS-1] Modelo exportado a: {exported_path}")


if __name__ == "__main__":
    main()
