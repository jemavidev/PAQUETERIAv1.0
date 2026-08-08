# 67 — `/residentes`: tabla simplificada + ficha con tabs + íconos de contacto (WhatsApp/llamada)

**Pedido original (cliente):** "lo que necesito en la vista de '/residentes'
sería lo siguiente: En la vista principal tener una tabla con los datos
más importantes como 'Nombre cliente, Telefono de contacto, Torre y
Apartamento, y una sección de CRUD'. En la columna de Telefono de contacto
(este debe incluir 2 iconos uno de whatsapp y otro de un telefono), la idea
es que al presionarlo se pueda acceder a la sección de chat de whatsapp y
el telefono que permita hacer una marcación tipo html 'tel:573000000001',
la opción de whatsapp deberá usar ya sea el número de telefono o el
usuario de whatsapp si lo tiene. La idea es que se puedan actualizar
algunos de los datos de un residente con los botones CRUD, como nombre,
telefono, email, torre y apartamento. De igual forma en otra sección se
debe poder hacer crud a lo relacionado a las notificaciones en general.
Por último y por ahora se debe poder gestionar las opciones de residentes."

**Status:** implementado

## Contexto

Reemplaza la forma de la tabla del issue [[66]] (12 columnas, todo visible
de una vez) por algo más operativo para el día a día del staff: una tabla
corta con acceso directo a WhatsApp/llamada, y el resto de la edición
movida a la ficha `/residentes/{id}`, que gana tabs (mismo patrón que
`/mis-datos` y `/mis-paquetes`, issues [[54]]/[[55]]/[[58]]).

Diseño acordado en sesión de `grilling` (ver conversación) — resumen de
las decisiones:

1. **Layout**: tabs en la ficha de UN residente (`/residentes/{id}`), no
   modales lanzados desde la lista ni tabs inline en la tabla. La lista
   sigue siendo una tabla; "Ver ficha" navega a la página de detalle.
2. **3 tabs en la ficha**: Datos (nombre, teléfono, email, torre/apto,
   fusiona los 2 formularios que existían) · Notificaciones (matriz
   completa canal×evento, reemplaza el checkbox simplificado) ·
   Apartamento y Residentes (gestión de Ocupantes ya existente, reubicada
   sin cambios funcionales). Zona de peligro (eliminar, ADMIN) queda fuera
   de las tabs.
3. **Ícono de WhatsApp**: usa `Persona.whatsapp_usuario` como PRIORIDAD si
   existe — este campo es un username real de la función de usuarios de
   WhatsApp (rollout 2026, confirmado por el cliente en la sesión de
   grilling — NO es un número de teléfono con otro formato). Si no hay
   username, cae a `Persona.telefono`. Formato del link:
   `https://wa.me/<valor>` — para el caso de username, no hay fuente
   oficial que confirme el esquema exacto del deep link todavía (Meta no
   ha publicado documentación pública al respecto al momento de
   implementar esto); queda marcado como pendiente de verificar en vivo.
4. **Ícono de llamada**: `tel:+<telefono>` (formato canónico ya
   almacenado, con el `+`).
5. **Validación de `whatsapp_usuario`**: ya no es texto 100% libre — se
   valida contra las reglas publicadas por Meta para usernames (3-35
   caracteres, letras latinas/números/puntos/guion bajo), porque ahora es
   funcional (arma un link), no solo informativo.
6. **Tabla principal**: Nombre (link) · Teléfono de contacto (2 íconos) ·
   Torre y Apartamento · Acciones (solo "Ver ficha" — eliminar sigue
   exclusivo de la Zona de Peligro en la ficha, ADMIN). El resto de los
   campos (email, documento, segundo contacto, notificaciones, fechas)
   sale de la tabla — visible solo en la ficha.
7. **Eliminados**: dejan de listarse por defecto en `/residentes` (ya
   están anonimizados — nombre/teléfono reales ya no existen, así que no
   aportan nada al día a día del staff).

## Decisión de implementación no cubierta explícitamente en el pedido

**Teléfono editable desde la ficha** (nuevo — antes `/residentes/{id}` no
tenía forma de cambiar el teléfono de un cliente): reutiliza
`cambiar_telefono_propio` (`persona_service.py`) tal cual — ya valida
formato y choque con otro teléfono en uso. La única diferencia frente al
uso original (cliente cambiando el suyo desde `/mis-datos`) es que el
staff no necesita cerrar sesión ni reverificar por OTP — esa parte era
responsabilidad del *caller* en la función original, y no aplica acá
(la sesión de un cliente resuelve por `persona_id` en la cookie, no por
teléfono — confirmado en `security.py` — así que cambiar el teléfono desde
el staff no invalida ninguna sesión activa de ese residente).

## Fuera de alcance

- No se resuelve el formato exacto del link de username de WhatsApp con
  una fuente 100% oficial — no existía al momento de implementar (función
  muy reciente, rollout de 2026). Se implementa con la mejor estimación
  (`https://wa.me/<usuario>`) explícitamente marcada para verificar en
  vivo.
- No se agrega ningún flujo de invalidación de sesión al cambiar el
  teléfono de un residente desde el staff (no aplica, ver arriba).

## Verificación

- Sintaxis Jinja verificada con `Environment.parse()` (`get_template` sobre
  ambas plantillas reescritas).
- Suite completa (`tests/data_model tests/web`): 655/655, sin regresiones.
  16 tests nuevos/reescritos en `test_customers_manage.py` (links
  WhatsApp/llamada con prioridad de username, columnas fuera de la tabla,
  eliminados excluidos, validación de `whatsapp_usuario`, edición de
  teléfono con choque, matriz de notificaciones vía la nueva ruta
  `/residentes/{id}/notificaciones`, 3 tabs presentes).
- Tailwind recompilado y comiteado (clases nuevas: `col-span-2`,
  `ring-emerald-300`, etc.) — `?v=33` → `?v=34`.
- Deploy a `test.papyrus.com.co`: push directo a `jemavidev/PaqueteX`
  (copia manual de los archivos cambiados, NO `git subtree push` — arrastra
  ~800 commits de scripts legacy no relacionados, ver memoria
  `paquetex-v2-infra-topology`). Workflow `CI & Deploy to Staging` (run
  #132) completó en verde (~4 min). `/residentes` responde 200 en vivo.
- Pendiente: confirmación visual del cliente en `test.papyrus.com.co` —
  en particular si el link de WhatsApp por username realmente abre un chat
  (no hay forma de probarlo sin un username real de WhatsApp registrado).
