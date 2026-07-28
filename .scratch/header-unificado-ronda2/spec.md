# Spec — Header unificado: login combinado, menús, Mis paquetes, logout único (Grupo 10, Ronda 2)

**Fuente:** `.scratch/ajustes-post-referencia-funcional/REQUERIMIENTOS.md`, Grupo 10.

## Qué cambia

1. **Login unificado** — nueva ruta pública `/entrar` (`entrar.py` +
   `auth/entrar.html`): dos pestañas CSS-only (radio+label, sin JS) "Soy
   residente" / "Soy del staff", cada una con el formulario de siempre
   (mismos `name` de campo, mismo `action` POST hacia `/otp/solicitar` e
   `/ingresar` respectivamente — cero cambios en esas rutas). El header
   público pasa de 2 botones ("Iniciar sesión" + "Staff") a 1 solo,
   apuntando a `/entrar`.
2. **Menú de staff renombrado y reducido** — `Paquetes · Clientes ·
   Consultar` (el link a `/residentes` se relabela "Clientes"; el texto es
   lo único que cambia). `/announce` ("Declarar unidad") sale del nav de
   escritorio — la nota del usuario dice explícitamente que ese acceso se
   moverá a un botón dedicado "más adelante"; por ahora sigue accesible
   desde el footer móvil de staff.
3. **"Mis paquetes"** — nueva ruta protegida `/mis-paquetes`
   (`customer_paquetes.py`), agregada a `_RUTAS_CLIENTE` en `app.py`. Lista
   los paquetes donde el teléfono de la sesión es `announced_by_phone` **o**
   `recipient_phone`, cada fila enlaza a `/consultar?q={access_code}`.
4. **Logout único** — nueva ruta `POST /salir-todo` (`auth.py`) que hace
   `pop` de las tres claves de sesión (`SESSION_KEY`, `ROLE_SESSION_KEY`,
   `CUSTOMER_SESSION_KEY`) de una vez. El header ahora renderiza un solo
   formulario de logout (no uno por audiencia) cuando hay cualquier sesión
   activa. Las rutas `/salir` y `/otp/salir` individuales **no se tocan**
   (siguen existiendo, sin uso desde el header).
5. **Footer móvil uniforme por audiencia** (ya no depende de si hay sesión):
   - Residente (con o sin sesión): Anunciar · Buscar · Ayuda · Whatsapp.
   - Staff: Anunciar (`/announce`) · Buscar · Paquetes · Clientes.
   - Nueva ruta pública `/ayuda` (`ayuda.py` + `ayuda/form.html`) — FAQ
     estática, contenido mantenido a mano en el template (no generado desde
     el `.md` en runtime).
   - Enlace de WhatsApp condicional: `whatsapp_soporte_numero()` en
     `config.py` lee `WHATSAPP_SOPORTE_NUMERO` del entorno; sin configurar,
     el ítem simplemente no se muestra (nunca se publica un enlace roto).
     Expuesto como *función* (no valor) en `templates.env.globals` para que
     se evalúe en cada request, no una sola vez al importar el módulo.

## Por qué

Instrucción explícita del usuario, con un matiz importante: el logout único
**revierte** el mecanismo de DEC-09 (Ronda 1) — las sesiones cliente/staff
siguen siendo cookies independientes por dentro, pero ahora un solo botón
las cierra ambas a la vez, en vez de que cada una tenga su propio control.

## Decisiones de diseño (AgentX)

- El toggle Cliente/Staff de `/entrar` es 100% CSS (radio+label+selector de
  hermanos), sin JavaScript nuevo — consistente con ADR-0004 (clean-room,
  sin Tailwind/Alpine) y con el resto de esta capa web.
- "Ayuda" y "Whatsapp" no existían en ningún lado antes de este grupo — se
  resolvieron con defaults sensatos en vez de bloquear el grupo completo
  (ver REQUERIMIENTOS.md Grupo 10): Ayuda es contenido propio del sistema,
  Whatsapp se activa/desactiva por variable de entorno sin tocar código.

## Fuera de alcance

- El botón dedicado para `/announce` en el nav de escritorio de staff queda
  explícitamente para más adelante (palabras del propio usuario).
- No se tocan las plantillas de notificación (Grupo 19, aparte) ni el CRUD
  de staff (Grupo 18, aparte), aunque ambos viven en pantallas enlazadas
  desde este mismo nav.
