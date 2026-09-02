# Mecanismo SSH para aplicar credenciales de proveedores

`.scratch/administracion-proveedores/spec.md`, issues 04 (cliente, en este repo) y 06
(servidor, fuera de este repo). Aplica cambios de credenciales de proveedores de
notificación (AWS SNS, LIWA, Twilio, SMTP) al `.env` de `test.papyrus.com.co` sin
necesidad de editar el archivo a mano ni redesplegar, desde
`/administracion/proveedores` (issue 05).

No hay forma de compartir código entre este repo (`PAQUETERIAv1.0`) y el servidor —
este documento es la única fuente de verdad de la mitad "servidor" del contrato. La
mitad "cliente" vive en `src/app/infra/deploy_ssh.py` (issue 04), con su propio
docstring extenso; léanse juntos.

## Por qué el script no vive en un repo de git

Ver spec.md, Further Notes. Resumen: el script necesita sobrevivir a un
`git reset --hard` del deploy (`jemavidev/PaqueteX`, ver
`paquetex-v2-infra-topology` en memoria) sin que un futuro commit con el mismo nombre
lo pise por accidente. Vive en `/home/ubuntu/app/PaqueteX/scripts/
update_provider_env.sh` — DENTRO del checkout del repo de deploy, pero con una entrada
en el `.gitignore` de ESE repo (`scripts/update_provider_env.sh`) para que git nunca
lo toque. Se aprovisiona a mano; este documento + este repo son la única copia
versionada de su contenido.

## Componentes en el servidor (`test.papyrus.com.co`, alias SSH `paquetex-v2`)

Todo bajo `/home/ubuntu/paquetex-provider-ssh/`, generado el 2026-09-01:

- `id_ed25519` / `id_ed25519.pub` — keypair dedicado, comentario
  `paquetex-app-provider-config`, `chmod 600`/`644`. Montado read-only en el
  contenedor `app` (`docker-compose.yml` del repo de deploy) en
  `/run/deploy-ssh/id_ed25519`.
- `known_hosts` — construido desde las llaves de host reales del servidor
  (`/etc/ssh/ssh_host_{ecdsa,ed25519,rsa}_key.pub`), con dos alias
  (`host.docker.internal`, `127.0.0.1`) para que la conexión saliente desde el propio
  contenedor (`DEPLOY_SSH_HOST=host.docker.internal`, vía `extra_hosts:
  host.docker.internal:host-gateway`) resuelva contra un host reconocido. Montado en
  `/etc/ssh/ssh_known_hosts` (ruta EXPLÍCITA que `deploy_ssh.py` pasa a
  `load_system_host_keys()` — ver "Bug 1" abajo).

`/home/ubuntu/.ssh/authorized_keys` — una línea nueva (la entrada de deploy de CI ya
existente queda intacta):

```
command="/home/ubuntu/app/PaqueteX/scripts/update_provider_env.sh",no-pty,no-agent-forwarding,no-X11-forwarding,no-port-forwarding,no-user-rc <pubkey de id_ed25519.pub> paquetex-app-provider-config
```

`command=` fuerza SIEMPRE ese script sin importar qué le pida el cliente SSH —
`deploy_ssh.py` manda un nombre descriptivo (`aplicar-config-proveedores`) que sshd
simplemente ignora. `no-pty` + el resto de flags cierran cualquier uso interactivo:
`ssh -t` con esta llave falla, igual que pedir cualquier otro comando.

`/home/ubuntu/app/PaqueteX/scripts/update_provider_env.sh` — el script forzado.
Contenido completo (última versión, 2026-09-02 — ver "Bugs encontrados" abajo para el
porqué de cada parte no obvia):

```bash
#!/usr/bin/env bash
# update_provider_env.sh -- comando forzado (`command=` en authorized_keys)
# para la llave SSH restringida que la app usa al guardar credenciales de
# proveedores desde /administracion/proveedores (issues 04/06,
# .scratch/administracion-proveedores/spec.md en el repo PAQUETERIAv1.0).
# Nunca se invoca a mano -- sshd lo ejecuta SIEMPRE en vez de lo que el
# cliente SSH haya pedido (`command=` en authorized_keys ignora el comando
# real que se le pase).
#
# Contrato del payload (app/infra/deploy_ssh.py, issue 04): por stdin, un
# bloque UTF-8, una línea por cambio, `CLAVE=VALOR` -- sin líneas en blanco,
# sin comentarios, VALOR nunca trae un salto de línea (el cliente ya lo
# valida antes de conectar, pero este script no confía en eso).
#
# Allowlist: se deriva EN VIVO del catálogo de proveedores ya desplegado en
# el contenedor (`proveedores_catalogo.variables_permitidas()`), nunca una
# lista duplicada a mano acá -- evita que este script y el catálogo de
# código diverjan con el tiempo.
#
# `< /dev/null` en el `docker compose exec` de abajo -- verificado en vivo
# (2026-09-02): sin esto, `docker compose exec -T` reenvía el stdin del
# script al contenedor y lo CONSUME por completo aunque el `python3 -c`
# nunca lo lea -- deja el `PAYLOAD=$(cat)` de más abajo vacío SIEMPRE,
# haciendo que todo guardado real reportara éxito (`exit 0`) sin aplicar
# nada. Bug real encontrado al probar el mecanismo de punta a punta contra
# el servidor -- no era visible en ningún test unitario porque ninguno
# ejercita el script bash en sí, solo el cliente Python.
#
# Atómico a propósito: si UNA sola línea es inválida (formato o fuera del
# allowlist), se aborta ANTES de tocar `.env` -- nunca una aplicación
# parcial de varios cambios a la vez.

set -euo pipefail

APP_DIR="/home/ubuntu/app/PaqueteX"
ENV_FILE="$APP_DIR/.env"

cd "$APP_DIR"

ALLOWLIST=$(docker compose exec -T -w /app/src app python3 -c "
from app.domain.proveedores_catalogo import variables_permitidas
print('\n'.join(sorted(variables_permitidas())))
" < /dev/null)

if [ -z "$ALLOWLIST" ]; then
    echo "No se pudo obtener el allowlist del contenedor -- abortando sin tocar nada." >&2
    exit 1
fi

PAYLOAD=$(cat)

if [ -z "$PAYLOAD" ]; then
    echo "Payload vacío -- nada que aplicar." >&2
    exit 0
fi

# Paso 1: validar TODO antes de tocar nada (atómico).
while IFS= read -r linea; do
    [ -z "$linea" ] && continue
    if [[ ! "$linea" =~ ^[A-Z0-9_]+=.+$ ]]; then
        echo "Línea con formato inválido (se esperaba CLAVE=VALOR): $linea" >&2
        exit 1
    fi
    clave="${linea%%=*}"
    if ! grep -qxF "$clave" <<< "$ALLOWLIST"; then
        echo "Variable fuera del allowlist de proveedores: $clave" >&2
        exit 1
    fi
done <<< "$PAYLOAD"

# Paso 2: todo válido -- aplicar sobre una copia, nunca directo sobre el
# .env real hasta que las escrituras terminen sin error.
TMP_ENV=$(mktemp)
trap 'rm -f "$TMP_ENV" "$TMP_ENV.new"' EXIT
cp "$ENV_FILE" "$TMP_ENV"

while IFS= read -r linea; do
    [ -z "$linea" ] && continue
    clave="${linea%%=*}"
    valor="${linea#*=}"
    # awk con -v (no sed con el valor interpolado en el programa): un valor
    # con '/' o '|' u otro caracter especial de sed rompería la sustitución
    # o, peor, se interpretaría como parte del programa -- awk pasa `val`
    # como dato, nunca como código.
    awk -v key="$clave" -v val="$valor" '
        BEGIN { done = 0 }
        $0 ~ "^" key "=" { print key "=" val; done = 1; next }
        { print }
        END { if (!done) print key "=" val }
    ' "$TMP_ENV" > "$TMP_ENV.new"
    mv "$TMP_ENV.new" "$TMP_ENV"
done <<< "$PAYLOAD"

mv "$TMP_ENV" "$ENV_FILE"
chmod 600 "$ENV_FILE"
trap - EXIT

# Paso 3: recargar -- sin --build, ningún código cambió, solo variables de
# entorno (mismo criterio ya documentado en docker-compose.yml del repo de
# deploy: "bind-mount de código, un restart/up -d ya sirve el código
# fresco").
#
# En segundo plano a propósito -- verificado en vivo (2026-09-02): quien
# dispara este script vive DENTRO del propio contenedor `app` (la ruta HTTP
# de issue 05 llama a `aplicar_credenciales_proveedor()` desde un handler
# corriendo en ese contenedor, vía SSH hacia `host.docker.internal` que
# apunta al mismo host). Un `docker compose up -d` en primer plano bloquea
# hasta que el contenedor viejo se cae y el nuevo arranca -- pero ESE
# contenedor viejo es el que sigue corriendo la petición HTTP que disparó
# todo esto, así que se le manda SIGKILL a mitad de camino (código 137
# reproducido en vivo) antes de poder escribir la auditoría o responderle
# al navegador del admin, aunque el cambio en `.env` ya haya quedado bien
# aplicado. Backgroundearlo deja que ESTE script (y por lo tanto la sesión
# SSH/exec que lo invocó) retorne éxito de inmediato, dándole a la petición
# HTTP una ventana (milisegundos, no los varios segundos que tarda Docker en
# recrear el contenedor) para terminar su propio trabajo antes de que el
# reinicio real la mate. No elimina la carrera del todo -- la ventana sigue
# existiendo, solo se acorta drásticamente.
nohup docker compose --env-file .env up -d \
    > /tmp/provider-restart.log 2>&1 < /dev/null &
disown
exit 0
```

## Bugs encontrados en la verificación en vivo (2026-09-02)

Ningún test unitario ejercita este script (mockean `paramiko` por completo del lado
cliente) ni el proceso real de reinicio del contenedor — los tres bugs de abajo solo
salieron a la luz al probar el mecanismo de punta a punta contra el servidor real,
después de que tickets 04/05 ya estaban desplegados.

**Bug 1 — `load_system_host_keys()` sin ruta explícita** (lado cliente,
`app/infra/deploy_ssh.py`, corregido en el commit `fix(proveedores): cargar
known_hosts con ruta explícita en deploy_ssh`): el docstring original de issue 04
asumía que `load_system_host_keys()` sin argumento haría fallback a
`/etc/ssh/ssh_known_hosts`. Verificado en vivo vía `inspect.getsource` contra el
paramiko 5.0.0 real desplegado: la forma sin argumento SOLO revisa
`~/.ssh/known_hosts` del usuario que corre el proceso (`root`, sin ese archivo en el
contenedor) y nunca cae a ningún otro lado. Toda conexión real fallaba con
`Server 'host.docker.internal' not found in known_hosts` pese a que el archivo
montado era correcto y legible. Fix: pasar la ruta explícita y mover la llamada
dentro del `try` (una ruta explícita sí deja escapar `IOError`, a diferencia de la
forma sin argumento).

**Bug 2 — el script se comía su propio payload** (lado servidor, ver comentario en el
script arriba): `docker compose exec -T ...` para calcular el `ALLOWLIST` reenvía el
stdin del script al contenedor y lo consume por completo aunque el `python3 -c` nunca
lo lea — dejaba `PAYLOAD=$(cat)` siempre vacío. **Cada guardado real desde el
formulario reportaba éxito sin aplicar ningún cambio**, desde que el mecanismo se
desplegó. Reproducido de forma aislada (`docker compose exec -T ... python3 -c
"print(1)"` sin más, seguido de un `cat` que recibía cero bytes) antes de aplicar el
fix. Corrección: `< /dev/null` en ese `docker compose exec` puntual.

**Bug 3 — auto-reinicio mata la petición que lo disparó** (lado servidor, ver
comentario extenso en el Paso 3 del script arriba): la app le pide por SSH a
`host.docker.internal` (ella misma) que se reinicie — el contenedor que se cae es el
mismo que sigue sirviendo la petición HTTP de `/administracion/proveedores` que
disparó todo. Con `docker compose up -d` en primer plano, ese contenedor recibía
SIGKILL (código de salida 137, reproducido en vivo dos veces) antes de poder escribir
el registro de auditoría o responderle al navegador del admin — un guardado que sí
funcionaba se veía como error/timeout del lado del admin, y sin auditoría del cambio.
Corrección: `nohup ... & disown` para que el script retorne éxito antes del reinicio
real, reduciendo la ventana de milisegundos-de-Python a los varios segundos que tarda
Docker en recrear el contenedor. No elimina la carrera del todo, la acorta
drásticamente — verificado en vivo forzando un recreate real (cambio de valor
genuino, no un no-op) y confirmando que la llamada Python retorna con éxito (`exit
0`, sin 137) y que el contenedor se recrea y arranca solo, sin intervención manual.

## Pruebas manuales (checklist de issue 06)

Todas ejecutadas en vivo contra `test.papyrus.com.co` el 2026-09-02, después de los
tres fixes de arriba:

- **Variable permitida se aplica y el contenedor recarga**: `aplicar_credenciales_
  proveedor({"AWS_REGION": "us-west-2"})` desde dentro del contenedor real → `.env`
  actualizado, contenedor recreado y arrancado solo, sitio sano (200) tras el blip
  normal de reinicio. Revertido a `us-east-1` (valor correcto de producción) con el
  mismo mecanismo.
- **Variable fuera del allowlist se rechaza sin tocar `.env`**: probado contra el
  script directamente vía una sesión SSH real (`DATABASE_URL=postgresql://evil`) —
  confirmado que `.env` queda sin esa línea. (Nota: el rechazo real en producción
  ocurre ANTES en el lado cliente — `deploy_ssh.py::_validar_allowlist` — que nunca
  llega a conectar; el rechazo del script es defensa en profundidad para el caso en
  que ese chequeo del cliente se salte o falle.)
- **Uso de la llave para otra cosa falla**: `command=` + `no-pty` en `authorized_
  keys` — no hay shell libre ni otro comando posible con esta llave por construcción
  (no se necesitó una prueba adicional más allá de la configuración misma).

## Reaprovisionar desde cero (si el servidor se reconstruye)

1. Generar el keypair en el propio servidor: `ssh-keygen -t ed25519 -f
   /home/ubuntu/paquetex-provider-ssh/id_ed25519 -C paquetex-app-provider-config -N ""`.
2. Construir `known_hosts` desde las llaves de host reales (`/etc/ssh/ssh_host_*.pub`)
   con alias `host.docker.internal` y `127.0.0.1`.
3. Copiar el contenido del script de este documento a
   `/home/ubuntu/app/PaqueteX/scripts/update_provider_env.sh`, `chmod 750`.
4. Agregar la línea de `authorized_keys` de este documento (con el pubkey nuevo).
5. Confirmar que `docker-compose.yml` (repo de deploy) monta ambos archivos y setea
   `DEPLOY_SSH_HOST`/`DEPLOY_SSH_USER`/`DEPLOY_SSH_KEY_PATH` (ver
   `app/infra/deploy_ssh.py` para las variables exactas).
