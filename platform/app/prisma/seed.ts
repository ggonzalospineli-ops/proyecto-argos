import { PrismaClient } from "@prisma/client";
import { scryptSync, randomBytes } from "crypto";

// Seed del MVP. Carga UNICAMENTE el proyecto real (ARGOS 1, vacio de
// datos reales — ver platform/CURRENT_COMPONENTS.md) mas un puñado de
// registros de ejemplo, todos marcados "[EJEMPLO]" en el nombre para que
// nunca se confundan con inventario real de Argos. Ver
// platform/MIGRATION_PLAN.md para como cargar datos reales.

const prisma = new PrismaClient();

function hashPassword(password: string): string {
  const salt = randomBytes(16).toString("hex");
  const hash = scryptSync(password, salt, 64).toString("hex");
  return `${salt}:${hash}`;
}

async function main() {
  const admin = await prisma.user.upsert({
    where: { email: "admin@argos.local" },
    update: {},
    create: {
      email: "admin@argos.local",
      name: "Admin",
      role: "ADMIN",
      passwordHash: hashPassword("argos-admin"),
    },
  });

  const project = await prisma.project.upsert({
    where: { id: "00000000-0000-0000-0000-000000000001" },
    update: {},
    create: {
      id: "00000000-0000-0000-0000-000000000001",
      name: "ARGOS 1",
      description:
        "Proyecto raiz real de Argos. Sin componentes reales cargados todavia — ver platform/OPEN_QUESTIONS.md.",
    },
  });

  const system = await prisma.system.upsert({
    where: { id: "00000000-0000-0000-0000-000000000010" },
    update: {},
    create: {
      id: "00000000-0000-0000-0000-000000000010",
      projectId: project.id,
      name: "Airframe [EJEMPLO]",
      description:
        "System de ejemplo para navegar la plataforma. No es un system real confirmado de Argos — ver platform/CURRENT_COMPONENTS.md.",
    },
  });

  const motorMount = await prisma.component.upsert({
    where: { id: "00000000-0000-0000-0000-000000000020" },
    update: {},
    create: {
      id: "00000000-0000-0000-0000-000000000020",
      projectId: project.id,
      parentSystemId: system.id,
      name: "Motor Mount [EJEMPLO]",
      type: "HARDWARE",
      description:
        "Componente de ejemplo (ilustrativo) para validar el modelo de datos. No representa una pieza real de Argos.",
      status: "PROTOTYPE",
    },
  });

  const revisionA = await prisma.revision.upsert({
    where: { id: "00000000-0000-0000-0000-000000000030" },
    update: {},
    create: {
      id: "00000000-0000-0000-0000-000000000030",
      componentId: motorMount.id,
      label: "A",
      status: "RELEASED",
      description: "Revision de ejemplo inicial.",
      changeSummary: "Primera version de ejemplo.",
      authorId: admin.id,
    },
  });

  await prisma.component.update({
    where: { id: motorMount.id },
    data: { currentRevisionId: revisionA.id },
  });

  await prisma.document.upsert({
    where: { id: "00000000-0000-0000-0000-000000000040" },
    update: {},
    create: {
      id: "00000000-0000-0000-0000-000000000040",
      title: "Design Notes [EJEMPLO]",
      contentMarkdown:
        "# Motor Mount [EJEMPLO]\n\nEste documento es un ejemplo para validar el modelo. No contiene informacion real de Argos.",
      entityType: "COMPONENT",
      entityId: motorMount.id,
      status: "PUBLISHED",
      authorId: admin.id,
    },
  });

  const build = await prisma.build.upsert({
    where: { id: "00000000-0000-0000-0000-000000000050" },
    update: {},
    create: {
      id: "00000000-0000-0000-0000-000000000050",
      projectId: project.id,
      code: "ARGOS-01 Build #001 [EJEMPLO]",
      description: "Build de ejemplo para navegar la plataforma.",
      status: "PLANNED",
    },
  });

  await prisma.buildComponent.upsert({
    where: { id: "00000000-0000-0000-0000-000000000060" },
    update: {},
    create: {
      id: "00000000-0000-0000-0000-000000000060",
      buildId: build.id,
      componentId: motorMount.id,
      revisionId: revisionA.id,
    },
  });

  await prisma.test.upsert({
    where: { id: "00000000-0000-0000-0000-000000000070" },
    update: {},
    create: {
      id: "00000000-0000-0000-0000-000000000070",
      name: "TEST-001 — check de ejemplo [EJEMPLO]",
      targetComponentId: motorMount.id,
      buildId: build.id,
      description: "Test de ejemplo para validar el modelo.",
      result: "PASS",
      date: new Date(),
      createdById: admin.id,
    },
  });

  // ---------------------------------------------------------------------
  // DATOS REALES (no [EJEMPLO]): software que efectivamente existe en el
  // repo (vision/, comms/, mission/) y fue verificado corriendo sus tests
  // reales antes de escribir este seed (no se copio el reporte del otro
  // agente sin chequear):
  //   - vision: carga de yolov8n.pt + inferencia real sobre imagen sintetica -> OK
  //   - comms: scripts/test_loopback.py (4/4: handshake, tamper, replay, video) -> OK
  //   - mission: test_integration_loopback.py (vision+comms end-to-end) -> OK
  // Fuente de cada descripcion: el README real de cada carpeta. No se
  // inventa nada de hardware ni specs de vuelo — eso sigue UNKNOWN, ver
  // platform/OPEN_QUESTIONS.md.
  // ---------------------------------------------------------------------

  const softwareSystem = await prisma.system.upsert({
    where: { id: "00000000-0000-0000-0000-000000000100" },
    update: {},
    create: {
      id: "00000000-0000-0000-0000-000000000100",
      projectId: project.id,
      name: "Software",
      description:
        "Sistema de software real de Argos 1: pipeline de vision, comunicaciones cifradas e integracion. Codigo real en vision/, comms/ y mission/ en la raiz del repo (fuera de platform/).",
    },
  });

  const visionComponent = await prisma.component.upsert({
    where: { id: "00000000-0000-0000-0000-000000000110" },
    update: {},
    create: {
      id: "00000000-0000-0000-0000-000000000110",
      projectId: project.id,
      parentSystemId: softwareSystem.id,
      name: "Vision Pipeline (YOLOv8)",
      type: "SOFTWARE",
      description:
        "Deteccion en tiempo real (YOLOv8/Ultralytics), fusion termica+RGB con cross_confirmed, entrenamiento y export a ONNX/TensorRT. Corre hoy con pesos base yolov8n.pt (COCO) — todavia sin dataset propio del dominio (persona, vehiculo_4x4, lancha_rapida, embarcacion, moto, dron). Codigo en vision/.",
      status: "PROTOTYPE",
    },
  });

  const commsComponent = await prisma.component.upsert({
    where: { id: "00000000-0000-0000-0000-000000000111" },
    update: {},
    create: {
      id: "00000000-0000-0000-0000-000000000111",
      projectId: project.id,
      parentSystemId: softwareSystem.id,
      name: "Secure Comms Channel",
      type: "SOFTWARE",
      description:
        "Canal UDP cifrado dron<->ground: AES-256-GCM, handshake mutuamente autenticado (X25519 efimero + identidad Ed25519 de largo plazo, patron Signal/Noise), ventana anti-replay, streaming de video fragmentado y cifrado. Codigo en comms/.",
      status: "TESTING",
    },
  });

  const missionComponent = await prisma.component.upsert({
    where: { id: "00000000-0000-0000-0000-000000000112" },
    update: {},
    create: {
      id: "00000000-0000-0000-0000-000000000112",
      projectId: project.id,
      parentSystemId: softwareSystem.id,
      name: "Mission Integration Layer",
      type: "SOFTWARE",
      description:
        "Integra Vision Pipeline y Secure Comms Channel: drone_mission_agent.py detecta y envia video+detecciones cifrados correlacionados por frame_id; ground_mission_station.py reensambla y empareja. loader.py resuelve el choque de nombres de modulos (ambos proyectos usan src/config) sin modificar el codigo ya probado de cada uno. Codigo en mission/.",
      status: "TESTING",
    },
  });

  const dashboardComponent = await prisma.component.upsert({
    where: { id: "00000000-0000-0000-0000-000000000113" },
    update: {},
    create: {
      id: "00000000-0000-0000-0000-000000000113",
      projectId: project.id,
      parentSystemId: softwareSystem.id,
      name: "Mission Dashboard",
      type: "SOFTWARE",
      description:
        "Dashboard HTML/JS sin dependencias (nada de Next.js/servicios externos, a proposito: cero bytes a servidores externos), servido localmente, conectado por WebSocket (dashboard_server.py) al ground station para mostrar video+detecciones en vivo. Codigo en mission/dashboard/.",
      status: "PROTOTYPE",
    },
  });

  async function seedBaselineRevision(
    component: { id: string; name: string },
    revisionId: string,
    changeSummary: string
  ) {
    const revision = await prisma.revision.upsert({
      where: { id: revisionId },
      update: {},
      create: {
        id: revisionId,
        componentId: component.id,
        label: "baseline",
        status: "DRAFT",
        description: `Estado actual de "${component.name}" al momento de este seed. No hay versionado formal (tags/releases) todavia en el codigo fuente — este es un snapshot, no una release.`,
        changeSummary,
        authorId: admin.id,
      },
    });
    await prisma.component.update({
      where: { id: component.id },
      data: { currentRevisionId: revision.id },
    });
    return revision;
  }

  await seedBaselineRevision(
    visionComponent,
    "00000000-0000-0000-0000-000000000120",
    "Pipeline funcional (fusion.py, infer.py, train.py, export.py) verificado cargando yolov8n.pt y corriendo inferencia. Pendiente: dataset propio."
  );
  await seedBaselineRevision(
    commsComponent,
    "00000000-0000-0000-0000-000000000121",
    "Canal cifrado con test de loopback real: handshake, round-trip, deteccion de tamper, rechazo de replay y video fragmentado — 4/4 OK."
  );
  await seedBaselineRevision(
    missionComponent,
    "00000000-0000-0000-0000-000000000122",
    "Integracion vision+comms verificada con test_integration_loopback.py: handshake, inferencia real sobre frame sintetico, envio cifrado correlacionado por frame_id, y reensamblado del lado ground — todo OK."
  );
  await seedBaselineRevision(
    dashboardComponent,
    "00000000-0000-0000-0000-000000000123",
    "dashboard_server.py puentea el ground station (sync) con clientes WebSocket (async). Verificado con test_dashboard_broadcast.py segun el reporte del desarrollo de mission/ — no re-ejecutado de forma independiente en este seed."
  );

  await prisma.componentDependency.upsert({
    where: {
      fromComponentId_toComponentId_type: {
        fromComponentId: missionComponent.id,
        toComponentId: visionComponent.id,
        type: "DEPENDS_ON",
      },
    },
    update: {},
    create: {
      fromComponentId: missionComponent.id,
      toComponentId: visionComponent.id,
      type: "DEPENDS_ON",
      notes: "mission/drone_mission_agent.py importa y corre el pipeline de vision/ via loader.py.",
    },
  });

  await prisma.componentDependency.upsert({
    where: {
      fromComponentId_toComponentId_type: {
        fromComponentId: missionComponent.id,
        toComponentId: commsComponent.id,
        type: "DEPENDS_ON",
      },
    },
    update: {},
    create: {
      fromComponentId: missionComponent.id,
      toComponentId: commsComponent.id,
      type: "DEPENDS_ON",
      notes: "mission/ usa SecureChannel de comms/ para el enlace cifrado dron<->ground.",
    },
  });

  await prisma.componentDependency.upsert({
    where: {
      fromComponentId_toComponentId_type: {
        fromComponentId: dashboardComponent.id,
        toComponentId: missionComponent.id,
        type: "DEPENDS_ON",
      },
    },
    update: {},
    create: {
      fromComponentId: dashboardComponent.id,
      toComponentId: missionComponent.id,
      type: "DEPENDS_ON",
      notes: "dashboard_server.py consume el ground_mission_station.py para reenviar video+detecciones por WebSocket.",
    },
  });

  await prisma.document.upsert({
    where: { id: "00000000-0000-0000-0000-000000000130" },
    update: {},
    create: {
      id: "00000000-0000-0000-0000-000000000130",
      title: "vision/README.md (espejo)",
      contentMarkdown:
        "# Vision Pipeline\n\nPipeline de vision por computadora: deteccion en tiempo real (YOLOv8), fusion termica+RGB, entrenamiento con dataset propio y export para inferencia en el borde (Jetson Orin Nano).\n\nDecisiones de diseno reales: recall antes que precision (umbral de confianza 0.25 por defecto); fusion por confirmacion cruzada (`cross_confirmed=True` cuando una deteccion aparece en ambos espectros); CPU por defecto, TensorRT en el Jetson para produccion.\n\nFuente completa: `vision/README.md` en la raiz del repo (no copiada integra aca a proposito, para no desincronizarse).",
      entityType: "COMPONENT",
      entityId: visionComponent.id,
      status: "PUBLISHED",
      authorId: admin.id,
    },
  });

  await prisma.document.upsert({
    where: { id: "00000000-0000-0000-0000-000000000131" },
    update: {},
    create: {
      id: "00000000-0000-0000-0000-000000000131",
      title: "comms/README.md (espejo)",
      contentMarkdown:
        "# Secure Comms Channel\n\nCanal UDP cifrado AES-256-GCM entre dron y ground station, con handshake mutuamente autenticado (X25519 efimero firmado con identidad Ed25519 de largo plazo, patron Signal/Noise), ventana anti-replay, y streaming de video fragmentado y cifrado.\n\nValidado con `scripts/test_loopback.py`: handshake + round trip, deteccion de tamper (paquete alterado -> InvalidTag), rechazo de replay, y video fragmentado — las 4 pruebas en verde (verificado de nuevo al armar este seed).\n\nFuente completa: `comms/README.md` en la raiz del repo.",
      entityType: "COMPONENT",
      entityId: commsComponent.id,
      status: "PUBLISHED",
      authorId: admin.id,
    },
  });

  await prisma.document.upsert({
    where: { id: "00000000-0000-0000-0000-000000000132" },
    update: {},
    create: {
      id: "00000000-0000-0000-0000-000000000132",
      title: "mission/README.md (espejo)",
      contentMarkdown:
        "# Mission Integration Layer\n\nIntegra vision/ y comms/: el dron detecta (YOLO) y manda video+detecciones cifrados correlacionados por frame_id; el ground station los reensambla y empareja. `loader.py` aisla los imports de cada proyecto para resolver el choque de nombres (`src.config` en ambos) sin tocar codigo ya probado.\n\nValidado con `test_integration_loopback.py` (handshake, inferencia real, envio cifrado correlacionado, reensamblado del lado ground) y, segun el reporte del desarrollo de mission/, con un smoke test full-stack (`test_full_stack_smoke.py`) usando procesos reales y video sintetico.\n\nFuente completa: `mission/README.md` en la raiz del repo.",
      entityType: "COMPONENT",
      entityId: missionComponent.id,
      status: "PUBLISHED",
      authorId: admin.id,
    },
  });

  await prisma.test.upsert({
    where: { id: "00000000-0000-0000-0000-000000000150" },
    update: {},
    create: {
      id: "00000000-0000-0000-0000-000000000150",
      name: "Carga de yolov8n.pt + inferencia sobre imagen sintetica",
      targetComponentId: visionComponent.id,
      description:
        "python -c: carga models/yolov8n.pt con ultralytics.YOLO y corre .predict() sobre un array numpy (640x640x3) sin camara.",
      result: "PASS",
      notes:
        "Verificado por la plataforma de ingenieria al armar este seed, no solo copiado del reporte del otro agente. No prueba deteccion de clases del dominio (no hay dataset propio todavia).",
      date: new Date(),
      createdById: admin.id,
    },
  });

  await prisma.test.upsert({
    where: { id: "00000000-0000-0000-0000-000000000151" },
    update: {},
    create: {
      id: "00000000-0000-0000-0000-000000000151",
      name: "comms/scripts/test_loopback.py",
      targetComponentId: commsComponent.id,
      description:
        "Suite de loopback real: [1/4] handshake mutuo + round trip dron<->ground, [2/4] deteccion de tamper, [3/4] rechazo de replay, [4/4] video cifrado fragmentado.",
      result: "PASS",
      notes: "4/4 checks en verde. Re-ejecutado por la plataforma de ingenieria al armar este seed.",
      date: new Date(),
      createdById: admin.id,
    },
  });

  await prisma.test.upsert({
    where: { id: "00000000-0000-0000-0000-000000000152" },
    update: {},
    create: {
      id: "00000000-0000-0000-0000-000000000152",
      name: "mission/test_integration_loopback.py",
      targetComponentId: missionComponent.id,
      description:
        "Integracion end-to-end vision+comms en loopback: handshake cifrado, inferencia YOLO real sobre frame sintetico, envio cifrado de video+detecciones correlacionadas por frame_id, y reensamblado/correlacion del lado ground.",
      result: "PASS",
      notes: "5/5 checks en verde (incluye el extra de renderizado). Re-ejecutado por la plataforma de ingenieria al armar este seed.",
      date: new Date(),
      createdById: admin.id,
    },
  });

  console.log("Seed completo. Login: admin@argos.local / argos-admin");
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
