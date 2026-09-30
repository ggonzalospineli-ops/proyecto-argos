# CURRENT_ARCHITECTURE.md — Argos 1

Fase 0 · Mapa de lo que existe hoy en el repo. `vision/` está en desarrollo
activo por otro agente en paralelo a este trabajo — se documenta su
arquitectura tal como está, sin modificarla.

## Repositorio (estado actual, no es un repo git todavía)

```
argos-1/
├── empresaquevendearmasproyecto-2028.html   # documento de plan estratégico (referencia, no código)
├── vision/                                   # pipeline de visión — EN DESARROLLO (otro agente)
│   ├── README.md
│   ├── config.py
│   ├── requirements.txt
│   ├── data/
│   │   ├── dataset.yaml
│   │   ├── images/        # vacío, gitignored
│   │   └── labels/        # vacío, gitignored
│   ├── models/
│   │   └── yolov8n.pt      # modelo base pre-entrenado (COCO), 6.5 MB
│   ├── src/
│   │   ├── __init__.py
│   │   ├── fusion.py       # fusión térmico + RGB
│   │   ├── infer.py        # inferencia en tiempo real
│   │   ├── train.py        # entrenamiento sobre dataset propio
│   │   └── export.py       # export a ONNX/TensorRT
│   └── scripts/
│       └── quick_test.py   # smoke test con webcam
└── platform/                                 # ESTE trabajo — plataforma de ingeniería (nuevo)
```

## Frontend

**UNKNOWN / no existe todavía.** El HTML menciona un dashboard
React/Next.js como parte del pilar de "Vibecoder", pero no hay código de
frontend de aplicación en el repo (`empresaquevendearmasproyecto-2028.html`
es un documento estático de plan, no la app).

## Backend

**UNKNOWN / no existe todavía.** El HTML describe un "servidor de misión
en tierra" (Docker/VM, sin internet, SSD cifrado) a cargo de "Prod Dev",
pero no hay código de backend en el repo.

## IA / Visión

**KNOWN** (código real en `vision/`):
- Framework: Ultralytics YOLOv8, entrenamiento con PyTorch.
- `config.py` centraliza clases del dominio y dos configs (`InferenceConfig`,
  `TrainConfig`) como dataclasses — umbrales, rutas, device.
- `src/fusion.py`: alineación y fusión de detecciones térmico + RGB,
  produce flag `cross_confirmed` cuando una detección aparece en ambas
  fuentes.
- `src/infer.py`: inferencia en tiempo real sobre webcam/video/RTSP,
  dibuja bounding boxes, soporta segunda fuente térmica opcional.
- `src/train.py`: fine-tuning de YOLOv8 sobre dataset propio en formato
  YOLO (`data/dataset.yaml`).
- `src/export.py`: exporta el modelo entrenado a ONNX (dev) o TensorRT
  engine (despliegue en Jetson).
- `scripts/quick_test.py`: valida el pipeline end-to-end con el modelo
  COCO pre-entrenado, sin dataset propio.
- Todo corre en CPU por defecto; el despliegue de producción objetivo es
  un NVIDIA Jetson Orin Nano con TensorRT.

**TO BE DEFINED**: cómo esta pieza de IA de visión (edge, on-device) se
relaciona con el "AI Engineering Assistant" que pide la nueva plataforma
(consulta de datos estructurados de ingeniería vía LLM) — son dos IAs
distintas con propósitos distintos y no deberían confundirse en el modelo
de datos: una corre a bordo del dron sobre video, la otra corre sobre la
base de datos de ingeniería del proyecto.

## Modelos (ML)

**KNOWN**: `vision/models/yolov8n.pt` — checkpoint base de Ultralytics
(YOLOv8 nano, pre-entrenado en COCO). No hay checkpoint propio entrenado
con el dataset de dominio (`persona`, `vehiculo_4x4`, `lancha_rapida`,
`embarcacion`, `moto`, `dron`) todavía.

## Servicios

**UNKNOWN / no existen todavía.** No hay servicios desplegados,
contenedores, ni configuración de infraestructura en el repo.

## Bases de datos

**UNKNOWN / no existen todavía.** No hay ninguna base de datos en el
repo actual. Es una de las piezas centrales que esta plataforma
(`platform/`) va a definir en las fases siguientes.

## Hardware mencionado

Ver detalle en `PROJECT_CONTEXT.md` — todo lo relativo a hardware está a
nivel de mención en el documento de plan estratégico (frame, flight
controller, cámaras, cómputo de borde, radio), sin archivos CAD, BOM ni
especificaciones formales en el repo.

## Comunicaciones

**KNOWN** (solo como especificación en el HTML, sin código):
- Protocolo de telemetría: MAVLink 2.0.
- Enlace de radio propuesto: SiK Telemetry (433/915MHz) o LoRa + WiFi/4G
  privado.
- Cifrado propuesto: AES-256-GCM para telemetría; GStreamer + `srtpenc` o
  túnel WireGuard para video.
- Autenticación propuesta: handshake con certificado digital.

**UNKNOWN**: no hay ninguna implementación de esto en el repo todavía.

## Dependencias conocidas

`vision/requirements.txt`:
```
ultralytics>=8.3.0
opencv-python>=4.10.0
numpy>=1.26
pyyaml>=6.0
onnx>=1.16
onnxruntime>=1.19
```

No hay `package.json`, `docker-compose.yml`, ni configuración de base de
datos/infraestructura en el repo.
