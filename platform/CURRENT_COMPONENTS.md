# CURRENT_COMPONENTS.md — Argos 1

Fase 0 · Inventario de todos los componentes/conceptos identificados en el
material existente (`empresaquevendearmasproyecto-2028.html` y `vision/`),
clasificados preliminarmente según la jerarquía propuesta:
`System / Subsystem / Assembly / Component / Software / Service / Artifact
/ Unknown`.

Clasificación preliminar — sujeta a revisión en Fase 1 (modelo conceptual).
No se agregó ningún dato técnico (dimensiones, especificaciones, modelos
exactos) que no esté explícitamente en la fuente.

| Nombre | Clasificación preliminar | Fuente | Estado / notas |
|---|---|---|---|
| ARGOS 1 | Project | HTML | Producto/proyecto raíz, Año 1 del roadmap |
| SENTINEL-1 | Project (futuro) | HTML | Producto de Año 2-3, detección/clasificación de drones. No confirmado si es un proyecto hermano o un módulo de ARGOS 1 |
| Airframe / Frame | System | HTML (inferido) | Mencionado como "frame de fibra de carbono, modular" — no hay descomposición en subsistemas/piezas en la fuente |
| Flight Controller | Component | HTML | ArduPilot / Pixhawk mencionados como ejemplo de referencia, no como elección confirmada |
| Cámara térmica | Component | HTML | FLIR mencionado como ejemplo |
| Cámara RGB | Component | HTML | Sin modelo especificado |
| Cómputo de borde (edge compute) | Component | HTML | Jetson Orin Nano o Raspberry Pi 5 mencionados como alternativas, no decisión final |
| Radio / enlace de telemetría | Component | HTML | SiK Telemetry o LoRa+WiFi/4G, no decisión final |
| Software de Visión (pipeline) | Software | `vision/` | Existe como código real, en desarrollo activo (otro agente) |
| `vision/src/fusion.py` | Software (module) | `vision/` | Fusión térmico+RGB |
| `vision/src/infer.py` | Software (module) | `vision/` | Inferencia en tiempo real |
| `vision/src/train.py` | Software (module) | `vision/` | Entrenamiento |
| `vision/src/export.py` | Software (module) | `vision/` | Export ONNX/TensorRT |
| Modelo YOLOv8n (COCO) | Artifact | `vision/models/yolov8n.pt` | Checkpoint base pre-entrenado, no específico del dominio |
| Modelo entrenado propio | Artifact (futuro) | `vision/README.md` | Todavía no existe — pendiente de dataset propio |
| Dataset de dominio | Artifact (futuro) | `vision/data/` | Carpetas presentes, vacías; clases definidas en `config.py` |
| Comunicaciones cifradas (telemetría) | Software (futuro) | HTML | Descripto (MAVLink + AES-256-GCM), sin código en el repo |
| Comunicaciones cifradas (video) | Software (futuro) | HTML | Descripto (GStreamer/WireGuard), sin código en el repo |
| Estación terrestre / servidor de misión | Service (futuro) | HTML | Descripto conceptualmente, sin código |
| Dashboard | Software (futuro) | HTML | Mencionado como React/Next.js, sin código |
| Reconocimiento facial | Software (futuro / requisito) | HTML | Mencionado como capacidad de producto; no implementado en `vision/` actual (que hace detección de objetos, no reconocimiento facial) |
| SENTINEL-1 (SDR + antenas) | System (futuro) | HTML | Fase 2, detección/fingerprinting de señales de drones — solo descripción conceptual |
| Componentes de guiado/seeker (Fase 3) | Unknown / fuera de alcance | HTML | Mencionados como fase futura (Año 3-5) del roadmap de negocio; fuera del alcance de esta plataforma de ingeniería (ver nota en `PROJECT_CONTEXT.md`) |

## Notas de clasificación

- Ningún componente de hardware tiene todavía un ID, revisión, o archivo
  CAD asociado — son solo menciones textuales en el plan estratégico.
- El único conjunto de "componentes" con evidencia real de implementación
  (código, estructura de módulos) es el pipeline de visión en `vision/`.
- La distinción `System → Subsystem → Assembly → Component` de la
  jerarquía propuesta no se puede aplicar todavía con precisión: la fuente
  no descompone el dron en subsistemas formales (ej. no dice si
  "Motor Mount" existe, es un ejemplo ilustrativo de los prompts del
  usuario, no un componente real documentado de Argos).
- **Importante**: los ejemplos "Motor Mount", "Arm", "Fuselage",
  "Battery Mount", etc. que aparecen en los prompts del usuario (mensajes
  de este chat) son ejemplos genéricos para ilustrar el modelo de datos
  propuesto — **no son componentes reales de Argos confirmados en la
  documentación** y no deben tratarse como tal en las fases siguientes.
