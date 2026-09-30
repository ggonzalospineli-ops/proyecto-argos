# PROJECT_CONTEXT.md — Argos 1

Fase 0 · Reconocimiento. Todo lo que sigue está basado únicamente en el
material existente en el repo (`empresaquevendearmasproyecto-2028.html` y
`vision/`). Donde no hay información se marca explícitamente.

## Qué es Argos 1, según la documentación existente

**KNOWN**
- Argos 1 es el producto insignia (Año 1) de una startup argentina de
  tecnología de defensa/seguridad. Fuente: `empresaquevendearmasproyecto-2028.html`.
- Es un "sistema de reconocimiento aéreo autónomo con visión térmica y
  facial": dron comercial modificado + software propio.
- Funciones declaradas: visión térmica + RGB fusionada, reconocimiento en
  tiempo real (edge computing), tracking de objetivos múltiples,
  geolocalización.
- Clientes objetivo: empresas de seguridad privada, Gendarmería Nacional
  (piloto de frontera), Prefectura (vigilancia fluvial).
- Precio objetivo: USD 15,000–25,000 por unidad; costo de hardware estimado
  USD 5,000–7,000.
- Regla explícita del equipo: **no fabricar armas de fuego** — foco en
  plataformas de sensores y software de misión, todo lo que no requiera
  licencia ANMaC.
- El nombre "ARGOS-1" también es el nombre del pipeline de visión que ya
  tiene código real en `vision/` (ver `CURRENT_ARCHITECTURE.md`).

**UNKNOWN**
- Especificaciones exactas del frame/dron base (marca, modelo, peso real,
  autonomía de vuelo, alcance de radio).
- Estado real de avance (el HTML es un plan/roadmap, no un reporte de
  estado; no hay evidencia en el repo de que el hardware exista físicamente).
- Composición real del equipo actual (el HTML describe 3 roles genéricos:
  "Prod Dev", "Vibecoder", "Ingeniero" — no hay nombres ni confirmación de
  quién ocupa cada rol hoy).

**TO BE DEFINED**
- Si "Argos 1" en la nueva plataforma de ingeniería es el proyecto raíz
  completo (dron + software + hardware) o si hay/habrá otros proyectos
  hermanos (p. ej. "Sentinel-1", mencionado como producto de Año 2-3).

## Objetivo actual del proyecto

**KNOWN**
- Objetivo de negocio declarado: construir una startup de defensa que
  compita en "soberanía, seguridad y soporte local" en vez de precio,
  vendiendo sistemas de vigilancia a fuerzas de seguridad argentinas.
- Roadmap de 3 fases a 3-5 años:
  1. Año 1 — ARGOS-1 (vigilancia aérea) → cash flow y credibilidad.
  2. Año 2-3 — SENTINEL-1 (detección/clasificación de drones, anti-drone
     pasivo) → entrar al ecosistema de defensa (CITEDEF, INVAP, Fuerza
     Aérea).
  3. Año 3-5 — componentes críticos de "sistemas de fuego y misiles"
     (guiado inercial/GPS, seeker térmico/óptico, navegación terminal),
     integrados con un socio que ya tenga licencia ANMaC (Fabricaciones
     Militares o Tecnojet), **no** fabricación de un misil completo propio.
- Objetivo inmediato declarado (plan de 90 días): esqueleto físico +
  video/detección funcionando + comunicación cifrada, culminando en una
  demo de vuelo y el inicio del trámite REID.

**UNKNOWN**
- Fecha de inicio real del proyecto ni en qué punto del plan de 90 días
  está el equipo hoy.
- Si el objetivo de negocio del HTML (empresa de defensa) sigue vigente sin
  cambios, o si esta nueva iniciativa (plataforma de ingeniería con IA)
  representa un pivot/expansión de alcance.

## Software existente

**KNOWN** — carpeta `vision/` (activamente en desarrollo por otro agente
en este momento; no se modifica desde esta tarea):
- Pipeline de visión por computadora en Python para el "pilar" de software
  de visión propio del plan.
- Basado en Ultralytics YOLOv8 (`yolov8n.pt` presente en `vision/models/`
  como modelo base pre-entrenado, no entrenado con datos propios todavía).
- Módulos: `src/fusion.py` (fusión térmico+RGB), `src/infer.py` (inferencia
  en tiempo real), `src/train.py` (entrenamiento), `src/export.py` (export
  a ONNX/TensorRT), `scripts/quick_test.py` (smoke test con modelo COCO
  genérico).
- Clases de dominio definidas en `config.py`: `persona`, `vehiculo_4x4`,
  `lancha_rapida`, `embarcacion`, `moto`, `dron`.
- Decisión de diseño explícita: prioriza recall sobre precisión (umbral de
  confianza bajo, 0.25) y usa "cross_confirmed" (detección confirmada en
  ambos espectros) como señal de alta confianza.
- Corre en CPU por defecto; diseñado para exportar a TensorRT en un NVIDIA
  Jetson Orin Nano para producción en el dron.
- No hay dataset propio todavía (`data/images/`, `data/labels/` existen
  como carpetas pero están vacías / gitignored).

**UNKNOWN**
- Estado de avance real del entrenamiento (si ya se grabó/etiquetó dataset
  propio).
- Existencia de software de comunicaciones cifradas o backend de misión
  (el HTML los describe como pilar de "Prod Dev" pero no hay carpeta ni
  código de eso en el repo).
- Existencia de dashboard (React/Next.js mencionado en el HTML) — no hay
  código de frontend en el repo.

## Hardware mencionado

**KNOWN** (mencionado en el HTML, sin evidencia de implementación en el
repo):
- Frame de fibra de carbono, ~2kg, modular.
- Flight controller basado en ArduPilot / Pixhawk, frame de referencia
  F450/S500.
- Cámara térmica (FLIR mencionado como ejemplo) + cámara RGB.
- Cómputo de borde: NVIDIA Jetson Orin Nano o Raspberry Pi 5.
- Radio: SiK Telemetry (433/915MHz) o LoRa + WiFi/4G privado, protocolo
  MAVLink 2.0.

**UNKNOWN**
- Modelos/proveedores exactos finalmente elegidos.
- Cualquier CAD real (no hay archivos CAD en el repo).

## IA mencionada

**KNOWN**
- Visión por computadora: YOLOv8/YOLOv11 vía Ultralytics + PyTorch,
  etiquetado en Roboflow (ver `vision/`).
- El HTML también menciona, como visión de producto (no implementado
  aún), reconocimiento facial en tiempo real — esto es un requisito de
  producto declarado, no una capacidad confirmada en el código actual
  (el `vision/` actual hace detección/clasificación de objetos, no
  reconocimiento facial).
- La solicitud que motiva este trabajo (prompts del usuario) pide además
  un "AI Engineering Assistant" de solo lectura sobre los datos
  estructurados del proyecto — esto es una capa nueva, todavía no
  construida, objeto de este mismo esfuerzo.

**UNKNOWN**
- Si "reconocimiento facial" sigue siendo un requisito vigente o fue
  descartado.

## Tecnologías existentes

**KNOWN**
- Python (`vision/`), Ultralytics YOLOv8, OpenCV, ONNX/ONNX Runtime.
- HTML/CSS/JS estático para el documento de plan estratégico (no es parte
  de la aplicación, es un documento de referencia).

**UNKNOWN / TO BE DEFINED**
- Stack de la futura plataforma de ingeniería (propuesto por el usuario:
  Next.js + PostgreSQL + almacenamiento de objetos + LLM API — todavía no
  implementado, a decidir en fases siguientes).
- Stack de comunicaciones cifradas, backend, dashboard.

## Conceptos importantes / terminología usada

- **ARGOS 1**: nombre de proyecto raíz / producto insignia.
- **SENTINEL-1**: producto de fase 2, detección/clasificación de drones.
- **REID / REPRO-DEF**: Registro de Industria de Defensa — necesario para
  vender al Ministerio de Defensa, no requiere ANMaC.
- **ANMaC**: organismo que regula armas/municiones/componentes críticos;
  la estrategia del equipo es evitar deliberadamente quedar bajo su
  regulación en las fases 1 y 2.
- **cross_confirmed**: en `vision/`, detección confirmada simultáneamente
  en espectro térmico y RGB.
- **Recall-first**: decisión de diseño en la visión — preferir falsos
  positivos a falsos negativos.

## Nota de alcance para este esfuerzo (plataforma de ingeniería)

Este trabajo de reconocimiento y el modelo de datos que sigue se limitan a
construir la infraestructura de gestión de ingeniería (componentes,
revisiones, documentos, BOM, builds, tests, asistente de IA de solo
lectura). No incluye, y no se van a generar como parte de este esfuerzo,
especificaciones técnicas de sistemas de guiado de misiles, seekers, u
otro contenido de armamento mencionado como fase futura (Año 3-5) en el
plan estratégico.
