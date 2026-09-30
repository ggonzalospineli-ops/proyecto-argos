"""Configuracion central del pipeline de vision ARGOS-1."""

from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
MODELS_DIR = ROOT / "models"

# Clases del dominio (entorno rio/costa/frontera). Ajustar segun dataset real.
CLASSES = [
    "persona",
    "vehiculo_4x4",
    "lancha_rapida",
    "embarcacion",
    "moto",
    "dron",
]


@dataclass
class InferenceConfig:
    weights: str = str(MODELS_DIR / "yolov8n.pt")  # pretrained por defecto, reemplazar por el propio
    source: str = "0"  # "0" = webcam, o ruta a video/RTSP
    img_size: int = 640
    conf_threshold: float = 0.25  # bajo para priorizar recall (evitar falsos negativos)
    iou_threshold: float = 0.45
    device: str = "cpu"  # "0" para GPU, "cpu" en notebook sin GPU
    save_output: bool = True
    output_dir: str = str(ROOT / "runs" / "detect")
    thermal_source: str | None = None  # segunda fuente para fusion termica, opcional


@dataclass
class TrainConfig:
    dataset_yaml: str = str(DATA_DIR / "dataset.yaml")
    base_model: str = "yolov8n.pt"
    epochs: int = 100
    img_size: int = 640
    batch: int = 16
    device: str = "cpu"
    project: str = str(ROOT / "runs" / "train")
    name: str = "argos1"
    # Recall-first: bajamos el peso de precision en favor de no perder detecciones
    patience: int = 30
