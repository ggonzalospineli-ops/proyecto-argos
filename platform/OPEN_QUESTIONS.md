# OPEN_QUESTIONS.md — Argos 1

Fase 0 · Lista explícita de información que falta, para no rellenar huecos
con suposiciones en las fases siguientes.

## Producto / hardware

- Hardware exacto del dron (frame, motores, ESC, batería, propelas) →
  **UNKNOWN**
- Arquitectura de vuelo (flight controller final, firmware, stack de
  control) → **TO BE DEFINED**
- Formato(s) CAD que se van a usar realmente (STEP/STL/3MF/otro) →
  **TO BE DEFINED**
- Si "reconocimiento facial" sigue siendo un requisito vigente del
  producto → **UNKNOWN**
- Especificaciones de cámara térmica/RGB finalmente elegidas → **UNKNOWN**
- Si existe ya algún prototipo físico o el proyecto está 100% en etapa de
  diseño/software → **UNKNOWN**

## Alcance y relación entre proyectos

- Si "Argos 1" en la nueva plataforma es el proyecto raíz único, o si
  SENTINEL-1 y los componentes de Fase 3 del roadmap de negocio deben
  modelarse como proyectos separados → **TO BE DEFINED**
- Si el pipeline de `vision/` se va a integrar dentro del modelo de la
  plataforma de ingeniería como "Software / Component" versionado, o si
  sigue siendo un repo/carpeta independiente → **TO BE DEFINED**
- Estado real de avance del proyecto respecto al plan de 90 días del HTML
  (en qué mes/hito está el equipo hoy) → **UNKNOWN**

## Organización / equipo

- Quiénes ocupan hoy los roles "Prod Dev", "Vibecoder", "Ingeniero" →
  **UNKNOWN**
- Si hay otras personas/agentes trabajando en paralelo además del agente
  de `vision/` mencionado por el usuario → **UNKNOWN** (se sabe que existe
  al menos 1: el agente de YOLO/vision)

## Plataforma de ingeniería (este esfuerzo)

- Confirmación del alcance MVP tal como está detallado en los prompts del
  usuario (Project → System → Component, revisiones, dependencias,
  documentos, artifacts, BOM, builds, tests, búsqueda, AI assistant
  read-only) → pendiente de confirmación explícita antes de Fase 1
- Stack tecnológico final (Next.js + PostgreSQL + object storage + LLM API
  es la propuesta del usuario, no una decisión confirmada) →
  **TO BE DEFINED**
- Si el sistema de autenticación/roles (ADMIN/MEMBER/VIEWER) tiene
  requisitos concretos de la organización real, o se puede usar el mínimo
  propuesto → **TO BE DEFINED**
- Proveedor de LLM/embeddings a usar para el AI assistant →
  **TO BE DEFINED**

## Fuera de alcance explícito (no son preguntas a resolver, son límites)

- Contenido técnico de sistemas de guiado de misiles / seekers (Fase 3 del
  roadmap de negocio) — explícitamente fuera del alcance de este esfuerzo
  de plataforma de ingeniería. Ver nota en `PROJECT_CONTEXT.md`.
