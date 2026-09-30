# ARGOS_SYSTEM_MODEL.md — Fase 1

Define cómo representamos Argos como sistema de ingeniería. Alcance
gobernado por el "Practical MVP Boundary" del usuario: la jerarquía real
que se implementa en el MVP es `Project → System → Subsystem → Component`.
`Assembly` y `Artifact` se documentan como niveles conceptuales pero
`Assembly` se modela como un `Component` que contiene otros `Component`
(vía BOM), no como una tabla/entidad separada — ver `DATABASE_SCHEMA.md`.

## Jerarquía

```
Project
 └─ System
     └─ Subsystem
         └─ Component
             └─ Revision
                 └─ Artifact
```

| Nivel | Significado | Cuándo usarlo | Ejemplo (ilustrativo, no confirmado en Argos real) |
|---|---|---|---|
| Project | Producto/iniciativa raíz. Único proyecto real hoy: `ARGOS 1`. | Un proyecto por producto con vida propia (si `SENTINEL-1` avanza, es un Project separado — ver `OPEN_QUESTIONS.md`). | `ARGOS 1` |
| System | Agrupación funcional de alto nivel dentro de un Project. | Cuando un conjunto de componentes cumple una función coherente del producto (propulsión, energía, aviónica, software). | `Propulsion` [EJEMPLO] |
| Subsystem | Subdivisión de un System cuando el System es grande. Opcional: un System puede tener Components directamente si no necesita ese nivel intermedio. | Cuando un System agrupa varias líneas de componentes independientes entre sí. | `Flight Software` dentro de `Software` [EJEMPLO] |
| Component | Entidad de ingeniería versionable: una pieza física, un módulo de software, un conjunto. | Para cualquier cosa que necesite historial de revisiones propio. | `Motor Mount` [EJEMPLO — no confirmado] |
| Revision | Estado versionado inmutable de un Component en el tiempo. | Cada vez que cambia el diseño/implementación de un Component. | `Motor Mount Rev A` [EJEMPLO] |
| Artifact | Archivo binario asociado a una Revision (CAD, imagen, firmware, doc exportado). | Cuando hay un archivo real que respalda una Revision. | `motor-mount-rev-b.step` [EJEMPLO] |

`Component` es recursivo (un Component puede tener Components hijos vía la
relación de BOM `contains`), lo que cubre el caso "Assembly" sin agregar
una tabla nueva: una Assembly es simplemente un Component cuyo BOM tiene
hijos.

## Por qué no más niveles todavía

El segundo y tercer bloque de instrucciones del usuario proponen niveles
adicionales (`Interface` como entidad propia, taxonomías más profundas).
Fase 1 los evalúa en `ENTITY_CATALOG.md` pero el MVP los deja fuera
(regla explícita: "Practical MVP Boundary" > secc. 1-2, "Do NOT implement
unlimited arbitrary entity types initially"). Si en el futuro se necesita
un nivel más granular, se agrega sin romper el modelo porque `Component`
ya es autorreferente.

## Reglas del modelo

1. Un `System` y un `Subsystem` **no** tienen revisiones propias ni
   artifacts — son agrupadores organizacionales. Solo `Component` versiona.
2. Un `Component` siempre pertenece a exactamente un `parent`
   (System, Subsystem, u otro Component, vía `parent_id` polimórfico —
   ver `DATABASE_SCHEMA.md`).
3. `current_revision` de un Component apunta siempre a la Revision activa;
   las revisiones anteriores nunca se borran ni se sobreescriben
   (ver `VERSIONING_MODEL.md`).
4. No existe today ningún dato real de Argos para poblar `System`,
   `Subsystem` o `Component` más allá de lo que ya está en
   `CURRENT_COMPONENTS.md` — el modelo se valida con datos de ejemplo
   marcados `[EJEMPLO]`, nunca presentados como reales.
