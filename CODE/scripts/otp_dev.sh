#!/usr/bin/env bash
# Genera un código OTP real para un teléfono, directo en la BD del ambiente
# local (paquetex_dev_up.sh) -- sin pasar por ningún proveedor SMS real.
#
# Por qué hace falta: en desarrollo local (0 proveedores SMS configurados)
# `get_otp_sender()` devuelve `DevOtpSender`, que NO manda nada por red y
# descarta el código apenas termina el request -- no hay forma de leerlo
# desde la UI. Este script llama a `otp_service.preparar_otp` (el mismo
# código que usa `/otp/solicitar`) directo contra la BD, usando el módulo de
# sesión "clean-room" (`app/web/db.py`, SIN dependencia de AWS) -- a
# diferencia del `app/database.py` legacy, que exige credenciales AWS S3
# solo para poder instanciarse.
#
# El teléfono debe ser ELEGIBLE (ver `otp_service.elegible_para_otp`): ya
# existente con un Paquete en estado RECIBIDO, u Ocupante activo de un
# Apartamento. Si no lo es, el script lo dice explícitamente -- no crea nada.
#
# Uso: ./scripts/otp_dev.sh +573002596319

set -euo pipefail

CODE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PG_PORT=5433
DB_URL="postgresql://paquetex:paquetex_dev@localhost:${PG_PORT}/paquetex_dev"

TELEFONO="${1:-}"
if [ -z "$TELEFONO" ]; then
  echo "Uso: $0 <telefono>" >&2
  exit 1
fi

cd "$CODE_DIR/src"
DATABASE_URL="$DB_URL" "$CODE_DIR/.venv/bin/python" - "$TELEFONO" <<'PYEOF'
import sys

from app.domain.otp_service import preparar_otp
from app.web.db import get_session_factory

telefono = sys.argv[1]
db = get_session_factory()()
try:
    resultado = preparar_otp(db, telefono)
    db.commit()
    if resultado is None:
        print(f"NO ELEGIBLE: {telefono} no tiene Paquete RECIBIDO ni es Ocupante activo.")
        sys.exit(1)
    telefono_canonico, codigo = resultado
    print(f"telefono={telefono_canonico} codigo={codigo} (vence en 5 min)")
finally:
    db.close()
PYEOF
