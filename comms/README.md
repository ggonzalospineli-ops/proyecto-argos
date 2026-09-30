# ARGOS-1 · Comunicaciones Cifradas

Enlace cifrado dron ↔ ground station para telemetría MAVLink y video, con
autenticación mutua y sin dependencia de infraestructura externa (sin
servidores de terceros, sin CA — pensado para operar aislado, "cero bytes a
servidores externos").

Implementa el pilar "🔐 Comunicaciones Cifradas" del plan estratégico.

## Diseño

- **Autenticación mutua**: cada extremo (dron / ground station) tiene un
  par de claves Ed25519 de identidad, generado una vez e instalado
  manualmente en el otro extremo (pinning, igual que `known_hosts` de SSH —
  no hace falta una CA para un enlace punto a punto).
- **Handshake**: ECDH efímero (X25519) firmado con la identidad de largo
  plazo (patrón "signed DH", el mismo principio detrás de Signal/Noise).
  Esto evita que alguien en el medio del enlace de radio ofrezca su propia
  clave y haga MITM.
- **Cifrado de datos**: AES-256-GCM por datagrama, con nonces únicos
  (salt de sesión + contador) y claves distintas por dirección.
- **Anti-replay**: ventana deslizante de 64 paquetes (estilo IPsec/DTLS),
  tolera el reordenamiento normal de UDP pero rechaza paquetes repetidos.
- **Video**: cada frame se fragmenta para caber en datagramas UDP y cada
  fragmento se cifra individualmente; el receptor reensambla por
  `frame_id` y descarta frames incompletos viejos en vez de trabarse.

Todo esto se implementa con primitivas de la librería `cryptography`
(OpenSSL auditado) — no hay algoritmos caseros.

## Instalación

```bash
cd comms
pip install -r requirements.txt
```

## 1. Generar identidades (una vez por dispositivo)

```bash
# en la laptop/companion computer del dron
python scripts/generate_identity.py --name dron

# en la máquina del ground station
python scripts/generate_identity.py --name ground
```

Después, copiar **fuera de banda** (USB, SSH, lo que sea — nunca por el
mismo enlace que se va a cifrar) la clave pública de cada lado al otro:

- `keys/dron_identity.pub` → ground station
- `keys/ground_identity.pub` → dron

## 2. Levantar el enlace

En el ground station:

```bash
python scripts/run_ground_station.py \
    --identity keys/ground_identity.key \
    --peer-pub keys/dron_identity.pub \
    --listen-port 15760
```

En el dron (o simulando desde otra máquina/proceso):

```bash
python scripts/run_drone_agent.py \
    --identity keys/dron_identity.key \
    --peer-pub keys/ground_identity.pub \
    --ground-host <IP publica/VPN del ground station> --ground-port 15760
```

El flight controller debe estar publicando MAVLink en
`127.0.0.1:14550` (UDP). El ground station republica la telemetría
descifrada en `127.0.0.1:14551` para que QGroundControl o Mission Planner
se conecten ahí — ese tramo final es MAVLink plano, pero nunca sale de la
máquina del ground station.

## 3. Validar sin hardware (test de loopback)

Corre todo el protocolo real (handshake, cifrado, detección de manipulación,
rechazo de replay, fragmentación de video) sobre `127.0.0.1`, sin necesitar
radio ni Pixhawk ni cámara:

```bash
python scripts/test_loopback.py
```

## Estructura

```
comms/
  config.py              # puertos, timeouts, tamano de ventana anti-replay
  src/
    crypto.py             # AES-256-GCM, HKDF, nonces, ventana anti-replay
    identity.py            # generacion/carga de identidad Ed25519
    handshake.py            # ECDH efimero firmado (mutua autenticacion)
    secure_channel.py        # canal UDP cifrado (handshake + send/recv)
    telemetry_relay.py        # puente MAVLink local <-> canal cifrado
    video_relay.py             # fragmentacion/cifrado/reensamblado de video
  scripts/
    generate_identity.py       # CLI para generar claves
    run_drone_agent.py          # proceso que corre en el dron
    run_ground_station.py        # proceso que corre en tierra
    test_loopback.py              # validacion end-to-end sin hardware
```

## Notas de producción

- **Video con GStreamer/SRTP**: la implementación de `video_relay.py` es un
  fallback en Python puro que corre en cualquier lado sin dependencias
  extra. Para producción con más ancho de banda/calidad, considerar una
  pipeline GStreamer con `srtpenc`, o tunelizar el video por WireGuard y
  dejar el codec sin cifrado propio (menos overhead de CPU).
- **Radio real**: el `SECURE_LINK_PORT` es agnóstico al medio físico —
  funciona igual sobre un módem SiK con UDP-over-serial, un 4G privado, o
  loopback para pruebas.
- **Rotación de claves de sesión**: cada arranque del enlace genera un
  handshake nuevo (claves efímeras frescas). Si se necesita forward secrecy
  *dentro* de una misión larga, se puede agregar re-handshake periódico
  reusando el mismo `handshake.py`.
