# 02 — Tipo, condición y foto al recibir; mostrar en la línea de tiempo

**Qué construir:** El staff puede registrar tipo de paquete (Normal/Extra dimensionado), condición (Bueno/Abierto/Regular) y una foto opcional al recibir. `/consultar` muestra esto en el hito "Recibido" de la línea de tiempo.

**Bloqueado por:** 01 (comparten la plantilla de `/consultar`).

**Estado:** ready-for-agent

- [ ] Migración Alembic agrega `package_type`/`package_condition` (nullable, con default `NORMAL`/`BUENO` a nivel de servicio si no se especifican) a `paquetes`.
- [ ] Nueva tabla `paquete_fotos` (ligada a `Paquete`): `id`, `paquete_id`, `url`, `created_at`.
- [ ] Puerto `FotoStorage` (`Protocol`, mismo patrón que `OtpSender`/`NotificationSender`) + implementación de desarrollo `LocalFotoStorage` (guarda en disco local, sin S3 real — pendiente de que se confirme el bucket a usar).
- [ ] Modal "Recibir" en `/paquetes`: selects de tipo/condición (con default preseleccionado) + campo de archivo opcional.
- [ ] `/consultar` muestra tipo/condición y la foto (si existe) en el hito "Recibido".
- [ ] `tests/data_model/test_recibir_paquete.py` extendido: tipo/condición explícitos se persisten; sin especificar, usan los defaults.
- [ ] Test de `LocalFotoStorage` (guarda y devuelve URL/ruta, sin red).
- [ ] `tests/web/test_packages.py` extendido: subir una foto la asocia al Paquete.
- [ ] Suite completa (`pytest`) pasa.
