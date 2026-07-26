# Consultar: rediseño (solo access_code/guía, timeline con fotos)

Fuente: `.scratch/ajustes-post-referencia-funcional/REQUERIMIENTOS.md`, Grupo 2. Depende del Grupo 1 (ya implementado: `access_code` de 4 caracteres, `tracking_number` eliminado).

## Problem Statement

`/consultar` hoy permite buscar por teléfono, lo cual expone (a quien conozca el número) los paquetes de otra persona — el usuario pidió explícitamente que la búsqueda sea SOLO por el código de acceso (que únicamente conoce quien anunció) o por el código de guía. Además, la línea de tiempo no muestra suficiente detalle (tipo de paquete, condición, fotos de la recepción) y no ofrece un camino para completar los datos del cliente si le faltan.

## Solution

`/consultar` busca exclusivamente por `access_code` (exacto) o `guide_number` (exacto) — se elimina la búsqueda por teléfono. El resultado muestra: nombre del destinatario, teléfono, estado actual, torre/apartamento (con enlace a actualizar datos si faltan), y la línea de tiempo completa con fecha/hora de cada hito, tipo de paquete y condición (capturados por el staff al recibir), y foto(s) de la recepción si se subieron.

## User Stories

1. Como residente, quiero consultar mi paquete solo con el código de acceso o la guía, para que nadie más pueda ver mis paquetes sabiendo mi teléfono.
2. Como residente, quiero ver mi teléfono y mi torre/apartamento en el resultado, para confirmar que son correctos.
3. Como residente, quiero un enlace para actualizar mis datos si me falta el apartamento, para completarlo sin salir de la consulta.
4. Como residente, quiero ver el tipo de paquete y su condición al recibirlo, para saber en qué estado llegó.
5. Como residente, quiero ver una foto de mi paquete si el staff la subió al recibirlo, para confirmar visualmente que es el correcto.
6. Como miembro del staff, quiero registrar el tipo de paquete (Normal / Extra dimensionado) y su condición (Bueno / Abierto / Regular) al recibirlo, para dejar constancia de cómo llegó.
7. Como miembro del staff, quiero poder subir una foto opcional al recibir un paquete, para dejar evidencia visual.
8. Como desarrollador, quiero que la búsqueda por teléfono deje de existir en `/consultar`, para cerrar la filtración de información entre residentes.

## Implementation Decisions

- **Búsqueda** (`search.py`): elimina por completo la rama de búsqueda por teléfono. `q` se compara contra `access_code` O `guide_number` (exacto); sin match, "no encontramos ningún paquete con ese dato" — sin distinguir cuál de los dos falló (mismo principio de mensajes genéricos que login/OTP).
- **Tipo y condición** (nuevas columnas en `Paquete`, migración Alembic): `package_type` (`NORMAL` / `EXTRA_DIMENSIONADO`) y `package_condition` (`BUENO` / `ABIERTO` / `REGULAR`) — mismas categorías que el sistema legacy (`app/models/package.py`, `PackageType`/`PackageCondition`), ambas **nullable** (opcionales, se capturan al **recibir**, no al anunciar) y ambas con default `NORMAL`/`BUENO` cuando el staff no las cambia explícitamente.
- **Fotos** (nueva tabla `paquete_fotos`, ligada a `Paquete`): mismo patrón de puerto/adaptador que `OtpSender`/`NotificationSender` — un `Protocol` `FotoStorage` con un método `guardar(archivo) -> url`, y una implementación de desarrollo (`LocalFotoStorage`, guarda en disco local) hasta que se conecte S3 real. **Necesito que confirmes** si se reutiliza el bucket S3 del sistema legacy (bajo un prefijo nuevo, p.ej. `paquetex-v2/`) o uno separado, antes de cablear la implementación real de S3 — el puerto y el flujo completo funcionan igual con `LocalFotoStorage` mientras tanto (mismo principio que `DevOtpSender`/`ConsoleNotificationSender`).
- **Modal "Recibir"** (`/paquetes`): agrega selects para tipo/condición (con default preseleccionado) y un campo de archivo opcional para la foto.
- **Línea de tiempo** (`/consultar`): cada hito ya mostraba fecha/hora; se agrega tipo/condición en el hito "Recibido", y la(s) foto(s) si existen.

## Testing Decisions

- Seam de dominio: `receive` (`paquete_lifecycle.py`) acepta `package_type`/`package_condition` opcionales; defaults si no se pasan.
- Seam web (`tests/web/test_search.py`, reescribir la sección de búsqueda por teléfono — ya no aplica): buscar por `access_code`, por `guide_number`, combinación inválida dando "sin resultados"; **ya no** hay tests de búsqueda por teléfono (comportamiento eliminado a propósito).
- Seam web (`tests/web/test_packages.py`, extender): recibir con tipo/condición explícitos los persiste; recibir sin especificarlos usa los defaults; subir una foto la asocia al Paquete.
- `LocalFotoStorage`: test de que guarda el archivo y devuelve una URL/ruta usable, sin depender de red.

## Out of Scope

- Conectar el bucket S3 real — depende de tu confirmación (bucket a reutilizar o nuevo) y de credenciales reales, igual que LIWA (Grupo 8).
- Cambiar las categorías de tipo/condición más allá de las 2+3 heredadas del legacy.

## Further Notes

El Grupo 8 (LIWA) tiene el mismo patrón de "puerto real pendiente de credenciales" — ambos quedan con su implementación de desarrollo funcionando end-to-end, listos para intercambiar la implementación real sin tocar el resto del código el día que haya credenciales/bucket confirmados.
