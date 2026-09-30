# ARGOS-1 · Software de Visión

Pipeline de visión por computadora para el dron ARGOS-1: detección en tiempo
real (YOLOv8), fusión térmica+RGB, entrenamiento con dataset propio y export
para inferencia en el borde (Jetson Orin Nano).

Implementa el pilar "🧠 Software de Visión Propio" del plan estratégico.

## Instalación

```bash
cd vision
pip install -r requirements.txt
```

## 1. Smoke test (esta semana, sin dataset propio)

Valida que todo funciona con un modelo pre-entrenado (COCO) antes de invertir
en recolección de datos:

```bash
python scripts/quick_test.py --seconds 30
```

Abre la webcam, detecta clases genéricas (persona, auto, bote, etc.) durante
30 segundos y muestra FPS + conteo de detecciones.

## 2. Dataset propio

1. Grabar video en el entorno real (Río de la Plata, frontera, Patagonia): 5,000–10,000 imágenes.
2. Etiquetar en [Roboflow](https://roboflow.com) con las clases de `config.py::CLASSES`
   (`persona`, `vehiculo_4x4`, `lancha_rapida`, `embarcacion`, `moto`, `dron`).
3. Exportar el dataset en formato **YOLOv8** y descomprimir en `data/` de modo que quede:

```
data/
  images/train/*.jpg
  images/val/*.jpg
  labels/train/*.txt
  labels/val/*.txt
  dataset.yaml
```

## 3. Entrenamiento

```bash
python -m src.train --data data/dataset.yaml --epochs 100 --device cpu
# con GPU: --device 0
```

El mejor checkpoint queda en `runs/train/argos1/weights/best.pt`.

## 4. Inferencia en tiempo real

```bash
# webcam, con el modelo propio
python -m src.infer --weights runs/train/argos1/weights/best.pt --source 0

# video de prueba, con umbral de confianza más permisivo (recall)
python -m src.infer --weights runs/train/argos1/weights/best.pt --source clip.mp4 --conf 0.2

# con fusión térmica+RGB (segunda fuente de video)
python -m src.infer --weights runs/train/argos1/weights/best.pt --source 0 --thermal 1
```

Las cajas verdes (`cross_confirmed`) indican detección confirmada en ambos
espectros (térmico + RGB) — señal de alta confianza, ideal para reducir falsos
positivos en operación real.

## 5. Export para el Jetson (edge)

```bash
python -m src.export --weights runs/train/argos1/weights/best.pt --format onnx
# en el Jetson: --format engine (TensorRT)
```

## Estructura

```
vision/
  config.py          # umbrales, clases, rutas — único lugar para tunear
  data/dataset.yaml   # definición del dataset YOLO
  src/
    fusion.py         # alineación y fusión térmico+RGB
    infer.py           # inferencia en tiempo real, dibuja bounding boxes
    train.py            # entrenamiento sobre dataset propio
    export.py            # export a ONNX/TensorRT para el Jetson
  scripts/quick_test.py  # smoke test sin dataset propio
```

## Decisiones de diseño

- **Recall antes que precisión** (`conf_threshold` bajo por defecto, 0.25):
  para vigilancia, un falso positivo lo descarta un operador; un falso
  negativo es un objetivo perdido.
- **Fusión por confirmación cruzada**: cuando una detección aparece en ambos
  espectros (térmico + RGB) se marca `cross_confirmed=True` — es la señal más
  confiable del sistema y la que debería disparar alertas automáticas.
- **CPU por defecto**: el código corre sin GPU para poder prototipar en
  cualquier notebook; para producción en el dron, usar `--device 0` y exportar
  a TensorRT en el Jetson.
