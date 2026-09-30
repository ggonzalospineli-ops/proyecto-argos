"""Fusion de frames termico + RGB.

En ARGOS-1 el dron lleva dos camaras (termica + RGB) que no estan perfectamente
alineadas. Este modulo resuelve el registro (alineacion) y la fusion visual/
de deteccion entre ambas fuentes.

Modos soportados:
  - "overlay": el termico se recolorea (colormap) y se mezcla sobre el RGB
    con transparencia alpha. Util para inspeccion humana.
  - "sidebyside": ambos frames lado a lado, mismo tamano. Util para debug.
  - "detection_merge": corre deteccion en ambos frames por separado y fusiona
    las cajas por IoU, priorizando el termico de noche / RGB de dia.
"""

from __future__ import annotations

import cv2
import numpy as np


def align_thermal_to_rgb(
    thermal: np.ndarray,
    rgb_shape: tuple[int, int],
    homography: np.ndarray | None = None,
) -> np.ndarray:
    """Reescala/transforma el frame termico al plano de la camara RGB.

    Si no hay homografia calibrada (caso tipico al arrancar), se usa un
    resize simple: es una aproximacion valida cuando las camaras estan
    montadas paralelas y cerca una de otra (como en un gimbal dual F450).
    Cuando se calibre el rig con un patron de tablero de ajedrez visible en
    ambos espectros, pasar la homografia 3x3 real aqui.
    """
    h, w = rgb_shape[:2]
    if homography is not None:
        return cv2.warpPerspective(thermal, homography, (w, h))
    return cv2.resize(thermal, (w, h), interpolation=cv2.INTER_LINEAR)


def thermal_to_colormap(thermal_gray: np.ndarray, colormap: int = cv2.COLORMAP_INFERNO) -> np.ndarray:
    """Convierte un frame termico de 1 canal (o 3 iguales) a una imagen de color falso."""
    if thermal_gray.ndim == 3:
        thermal_gray = cv2.cvtColor(thermal_gray, cv2.COLOR_BGR2GRAY)
    normalized = cv2.normalize(thermal_gray, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return cv2.applyColorMap(normalized, colormap)


def overlay_fusion(rgb: np.ndarray, thermal: np.ndarray, alpha: float = 0.45) -> np.ndarray:
    """Superpone el termico (colorizado) sobre el RGB con blending alpha."""
    thermal_aligned = align_thermal_to_rgb(thermal, rgb.shape)
    thermal_color = thermal_to_colormap(thermal_aligned)
    return cv2.addWeighted(thermal_color, alpha, rgb, 1 - alpha, 0)


def sidebyside_fusion(rgb: np.ndarray, thermal: np.ndarray) -> np.ndarray:
    thermal_aligned = align_thermal_to_rgb(thermal, rgb.shape)
    thermal_color = thermal_to_colormap(thermal_aligned)
    return np.hstack([rgb, thermal_color])


def _iou(box_a: tuple[float, float, float, float], box_b: tuple[float, float, float, float]) -> float:
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def merge_detections(
    rgb_boxes: list[dict],
    thermal_boxes: list[dict],
    iou_threshold: float = 0.4,
) -> list[dict]:
    """Fusiona detecciones de ambas fuentes.

    Cada box es un dict {"bbox": (x1,y1,x2,y2), "cls": str, "conf": float, "source": str}.
    Si dos cajas (una de cada fuente) se solapan por encima del umbral, se
    quedan con la de mayor confianza y se marca "cross_confirmed": True
    (senal fuerte: confirmado en ambos espectros, reduce falsos positivos).
    Las que no matchean se conservan igual (para no perder recall).
    """
    merged: list[dict] = []
    used_thermal = set()

    for rbox in rgb_boxes:
        best_match, best_iou = None, 0.0
        for i, tbox in enumerate(thermal_boxes):
            if i in used_thermal:
                continue
            iou = _iou(rbox["bbox"], tbox["bbox"])
            if iou > best_iou:
                best_match, best_iou = i, iou

        if best_match is not None and best_iou >= iou_threshold:
            tbox = thermal_boxes[best_match]
            used_thermal.add(best_match)
            winner = rbox if rbox["conf"] >= tbox["conf"] else tbox
            merged.append({**winner, "cross_confirmed": True})
        else:
            merged.append({**rbox, "cross_confirmed": False})

    for i, tbox in enumerate(thermal_boxes):
        if i not in used_thermal:
            merged.append({**tbox, "cross_confirmed": False})

    return merged
