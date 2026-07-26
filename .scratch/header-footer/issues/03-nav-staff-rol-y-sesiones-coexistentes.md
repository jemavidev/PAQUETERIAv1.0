# 03 — Nav de staff con distinción de rol (OPERADOR/ADMIN) y sesiones coexistentes

**What to build:** para un `Usuario` con sesión de staff activa (`usuario_id`
en la sesión, obtenida vía `/ingresar`), el header construido en 01 muestra,
en toda pantalla de staff (`/paquetes`, `/announce`, `/residentes`,
`/administracion/*`, `/mi-sesion`):

- Enlaces a `/paquetes`, `/announce` (Declarar unidad), `/residentes` y
  `/consultar`.
- Si el rol es `ADMIN`, además enlaces a `/administracion/personal` y
  `/administracion/notificaciones`. Si el rol es `OPERADOR`, esos dos NO
  aparecen (hoy esas rutas devuelven 403 vía `require_admin` a quien no es
  ADMIN — el menú no debe insinuar acceso que no existe).
- Un botón "Cerrar sesión" que hace `POST /salir` — mismo patrón que
  `auth/me.html`.
- **Decisión de implementación (DEC-09):** `routes/auth.py`
  (`login_submit`) escribe también `request.session["rol"] =
  usuario.rol.value` junto a `usuario_id` en el momento del login.
  `base.html` lee `request.session.get("rol")` directamente para decidir si
  mostrar Administración — sin agregar una dependencia de FastAPI nueva a
  las rutas que ya renderizan páginas completas. Esto es un dato derivado
  para pintar el menú, NUNCA la fuente de autorización real: `require_admin`
  sigue siendo la única puerta de esas rutas.
- **Sesiones coexistentes:** si `persona_id` Y `usuario_id` están presentes a
  la vez en la misma sesión de navegador (el proyecto ya permite esto
  explícitamente — ver `security.py`), el header muestra AMBOS conjuntos de
  enlaces (cliente de 02 + staff de este ticket) simultáneamente, sin que
  ninguno oculte al otro.

**Blocked by:** 01 (reutiliza el esqueleto de `base.html`, el mecanismo de
enlace-activo y el breakpoint responsive). Independiente de 02 — puede
implementarse en paralelo, aunque su propio criterio de aceptación de
sesiones coexistentes requiere que el conjunto de enlaces de cliente de 02
también exista para verificarlo en conjunto.

**Status:** ready-for-agent

- [ ] `login_submit` en `routes/auth.py` guarda el rol del `Usuario` en la
      sesión junto al `usuario_id`.
- [ ] Con `usuario_id` en sesión y rol `OPERADOR`, el header muestra
      Paquetes/Declarar unidad/Residentes/Consultar + el form de
      `POST /salir`, y NO muestra Personal ni Notificaciones.
- [ ] Con `usuario_id` en sesión y rol `ADMIN`, el header muestra además
      Personal y Notificaciones.
- [ ] `require_admin` sigue siendo la única puerta real de
      `/administracion/*` — este ticket no cambia permisos, solo el menú.
- [ ] Con `persona_id` Y `usuario_id` presentes a la vez, el header muestra
      el conjunto de cliente (de 02) y el de staff juntos, sin que ninguno
      desaparezca.
- [ ] `tests/web/test_layout.py`: casos para staff OPERADOR, staff ADMIN, y
      sesión coexistente cliente+staff (login de cliente vía `_login_cliente`
      seguido de `POST /ingresar` en el mismo `TestClient`, patrón ya usado
      en `test_customer_verify.py::test_desactivar_detiene_una_notificacion_posterior`).
- [ ] Suite completa sigue en verde.
