# ARGOS-1 · Integración Visión + Comunicaciones + Dashboard

Junta `vision/` (detección YOLOv8) y `comms/` (canal UDP cifrado con
autenticación mutua) en el agente de misión real: el dron detecta objetos
y manda video + detecciones cifradas al ground station, que las reensambla,
las superpone en tiempo real, y las expone a un dashboard web local.

## Arquitectura

```
   DRON                                    GROUND STATION                 OPERADOR
┌──────────────┐  MSG_VIDEO (fragmentado)┌──────────────────────┐  WebSocket  ┌───────────┐
│ camara -> cv2│ ───────────────────────►│ reensambla video      │  (local)   │ dashboard/ │
│ YOLO (vision)│                          │                        │──────────►│ index.html │
│      │       │  MSG_DETECTION (JSON)   │ reensambla detecciones │           │ (navegador)│
│      └───────┼──────────────────────────►│                        │           └───────────┘
│  SecureChannel│  (mismo canal AES-256-  │ correlaciona por        │
│  (comms)      │   GCM, correl. frame_id)│ frame_id, dibuja y      │
└──────────────┘                          │ publica al dashboard    │
                                           └──────────────────────┘
```

El tramo dron↔ground viaja cifrado (AES-256-GCM). El tramo ground↔dashboard
es un WebSocket **local** (`ws://<ip-ground>:8765`, red local o loopback) —
no hay ningún servidor externo ni nube involucrada en ningún tramo,
consistente con "cero bytes a servidores externos" del plan.

Video y detecciones viajan por el **mismo canal cifrado**, pero como
mensajes separados (`MSG_VIDEO` / `MSG_DETECTION`), correlacionados por
`frame_id`. Esto es deliberado: si se pierde un fragmento de video, las
detecciones de otros frames siguen llegando sin bloquearse, y el ground
station solo dibuja cuando tiene ambas partes del mismo frame.

## Por qué un `loader.py`

`vision/` y `comms/` son proyectos standalone, cada uno con su propio
`config.py` y paquete `src/`. Para poder importarlos juntos en un mismo
proceso sin chocar nombres (y sin tocar el código ya probado de cada uno),
`loader.py` provee `isolated_project(root)`: un context manager que aísla
el `sys.path`/`sys.modules` mientras se hacen los imports de cada proyecto.
Ver el docstring de `loader.py` para el detalle.

## Uso

```bash
pip install -r ../vision/requirements.txt
pip install -r ../comms/requirements.txt
pip install -r requirements.txt   # websockets, para el dashboard

# una vez, en cada maquina:
python ../comms/scripts/generate_identity.py --name dron   # en el dron
python ../comms/scripts/generate_identity.py --name ground # en el ground
# copiar las .pub cruzadas (USB/SSH, fuera de banda)

# ground station (levanta ademas el servidor del dashboard en :8765):
python ground_mission_station.py \
    --identity ../comms/keys/ground_identity.key \
    --peer-pub ../comms/keys/dron_identity.pub

# dron:
python drone_mission_agent.py \
    --identity ../comms/keys/dron_identity.key \
    --peer-pub ../comms/keys/ground_identity.pub \
    --ground-host <IP del ground station> \
    --source 0
```

Después, abrir `dashboard/index.html` directamente en el navegador (doble
clic, o `file://`) desde la máquina del ground station — se conecta solo a
`ws://127.0.0.1:8765`. Para verlo desde otra máquina de la red local, abrirlo
con `?ws=ws://<ip-del-ground>:8765` en la URL, o servir la carpeta
`dashboard/` con cualquier servidor estático (`python -m http.server`).

Usar `--no-dashboard` en `ground_mission_station.py` para desactivar el
servidor WebSocket si no hace falta.

## Validar sin hardware

```bash
python test_integration_loopback.py    # vision + comms: video+detecciones cifradas, correlacion por frame_id
python test_dashboard_broadcast.py     # dashboard: servidor WebSocket real + cliente real
```

`test_integration_loopback.py` corre el modelo YOLO real sobre un frame
sintético, lo manda cifrado y fragmentado por un `SecureChannel` real en
`127.0.0.1`, junto con las detecciones en un mensaje separado, y verifica
que el lado receptor reensambla ambos y los correlaciona correctamente por
`frame_id`. `test_dashboard_broadcast.py` valida el mismo formato de
mensaje que consume `dashboard/index.html`, con un cliente WebSocket real.

## Próximos pasos naturales

- **Fusión térmica**: el agente del dron puede usar `vision/src/fusion.py`
  antes de `video_sender.send_frame()` si hay una segunda cámara térmica.
- **Telemetría MAVLink en el mismo enlace**: hoy `comms/scripts/run_drone_agent.py`
  usa un puerto separado (`SECURE_LINK_PORT`) para MAVLink; se puede fusionar
  con este agente de misión si conviene operar todo por un solo `SecureChannel`.
- **Autenticación del dashboard**: hoy cualquiera en la red local que
  conozca el puerto puede conectarse al WebSocket del dashboard (de
  lectura, no puede mandar comandos). Si el ground station va a estar en
  una red compartida, agregar un token compartido en la URL o TLS local.
