"""Entrenamiento de YOLOv8 sobre el dataset propio (Roboflow -> formato YOLO).

Uso:
    python -m src.train --data data/dataset.yaml --epochs 100
    python -m src.train --data data/dataset.yaml --epochs 50 --device 0   # con GPU

Flujo esperado (ver roadmap "Mes 2"):
  1. Recolectar 5,000-10,000 imagenes del entorno real (rio, selva, frontera).
  2. Etiquetar en Roboflow con las clases de config.CLASSES.
  3. Exportar el dataset en formato "YOLOv8" y descomprimir en data/
     (debe quedar images/train, images/val, labels/train, labels/val).
  4. Correr este script. Prioriza recall: mejor un falso positivo revisado
     por un operador que un objetivo real no detectado.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from ultralytics import YOLO

from config import TrainConfig


def parse_args() -> TrainConfig:
    cfg = TrainConfig()
    p = argparse.ArgumentParser(description="ARGOS-1 - entrenamiento de modelo de vision")
    p.add_argument("--data", default=cfg.dataset_yaml)
    p.add_argument("--model", default=cfg.base_model, help="checkpoint base: yolov8n/s/m/l/x.pt")
    p.add_argument("--epochs", type=int, default=cfg.epochs)
    p.add_argument("--imgsz", type=int, default=cfg.img_size)
    p.add_argument("--batch", type=int, default=cfg.batch)
    p.add_argument("--device", default=cfg.device)
    p.add_argument("--patience", type=int, default=cfg.patience)
    p.add_argument("--name", default=cfg.name)
    args = p.parse_args()

    cfg.dataset_yaml = args.data
    cfg.base_model = args.model
    cfg.epochs = args.epochs
    cfg.img_size = args.imgsz
    cfg.batch = args.batch
    cfg.device = args.device
    cfg.patience = args.patience
    cfg.name = args.name
    return cfg


def run(cfg: TrainConfig) -> Path:
    dataset_path = Path(cfg.dataset_yaml)
    if not dataset_path.exists():
        raise FileNotFoundError(
            f"No se encontro {dataset_path}. Exporta el dataset de Roboflow (formato YOLOv8) "
            "y colocalo en data/ antes de entrenar."
        )

    model = YOLO(cfg.base_model)
    results = model.train(
        data=str(dataset_path),
        epochs=cfg.epochs,
        imgsz=cfg.img_size,
        batch=cfg.batch,
        device=cfg.device,
        project=cfg.project,
        name=cfg.name,
        patience=cfg.patience,
        # recall-first: recall pesa mas que precision en la funcion de perdida percibida
        # (se ajusta via umbral de confianza bajo en inferencia, no aqui; el entrenamiento
        # en si ya optimiza mAP balanceado)
        val=True,
    )
    best_weights = Path(cfg.project) / cfg.name / "weights" / "best.pt"
    print(f"[ARGOS-1] Entrenamiento terminado. Mejor checkpoint: {best_weights}")
    return best_weights


if __name__ == "__main__":
    run(parse_args())
