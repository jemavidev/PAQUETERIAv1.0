# Análisis de `/paquetes` y su conexión con `/residentes`

Contexto: análisis previo a una tanda de modificaciones sobre `/paquetes` que
debe respetar lo que ya estipula `/residentes` (padrón de residentes/ocupantes).
Conversación del 2026-09-04.

## 1. La vista `/paquetes`

**Dónde vive:** `src/app/web/routes/packages.py` (1765 líneas — vista de staff;
no confundir con `src/app/routes/packages.py`, la API REST legacy de
"PAQUETES EL CLUB") + `src/app/web/templates/packages/{list,_resultados,_acciones}.html`
(1077 líneas) + JS compartido en `components/_recibir_paquete.html::recursos_recibir()`
y `components/_busqueda_filtros.html`.

### Arquitectura

- **Ruta delgada, capa de dominio separada de verdad**: las transiciones reales
  (`receive`/`deliver`/`cancel`/`corregir_*`) viven en `paquete_lifecycle.py`
  (271 líneas), `paquete_correccion_service.py` (195) y `paquete_timeline_service.py`
  (191) — la ruta orquesta, no reimplementa reglas de negocio.
- **Batching disciplinado**: `_listar()` resuelve Personas/Usuarios/Apartamentos/
  Ocupantes/preferencias de WhatsApp en un puñado fijo de queries para toda la
  página (nunca por fila) — hay un test dedicado a que esto no regrese a N+1
  (`test_lista_no_dispara_una_query_de_persona_o_usuario_por_paquete`).
- **Búsqueda en vivo sin duplicar plantillas**: `_resultados.html` es el mismo
  fragmento que sirve tanto el `GET /paquetes` completo como el `fetch` con
  `X-Requested-With: fetch` — un solo template, dos caminos de render.
- **Modal delegation vía `document`**: los `data-open`/`data-close` se enlazan
  una sola vez sobre `document` (no sobre los elementos), para sobrevivir al
  `innerHTML` que dispara la búsqueda en vivo.
- **192 tests, todos pasando** (corridos en esta sesión, 150s) — cobertura
  real, no aspiracional.

### Puntos que más llaman la atención

1. **`packages.py` mezcla dos capas en un archivo**: ~700 de las 1765 líneas
   (todo `_listar` y sus ~15 helpers: `_personas_por_*`, `_whatsapp_url_destinatario`,
   `_duracion_transcurrida`, `_destinatario_sin_confirmar`, etc.) son
   construcción de view-model, no manejo de rutas. Funciona bien hoy; sería
   candidato natural a extraerse a un módulo propio si sigue creciendo.
2. **Atributos transitorios inyectados sobre instancias ORM**: `_listar` les
   cuelga a los `Paquete` de SQLAlchemy más de 15 atributos que no existen en
   el modelo (`p.candidatos_correccion`, `p.persona_anunciante`,
   `p.whatsapp_url_destinatario`, etc.) para que la plantilla los lea. Patrón
   consciente y consistente, pero frágil si algún otro código toca esos mismos
   objetos `Paquete` (misma sesión) esperando el modelo "limpio".
3. **JS duplicado por fila**: cada paquete en pantalla (hasta 20) recibe su
   propio `<script>` inline en `_resultados.html` (preview de "+ Nuevo
   residente", toggle de "Otro" en Cancelar) en vez de un solo listener
   delegado como ya hace `recursos_recibir()`.
4. **Complejidad de negocio real, bien documentada pero densa**:
   `_destinatario_sin_confirmar` / `_destinatario_coincide_con_candidato_real`
   encapsulan reglas afinadas a partir de varios bugs reales en vivo
   (FANTASMA 1-4, CAMILA OSPINA, etc.) — los docstrings explican el porqué de
   cada rama, pero exige leer el historial completo para tocarla con confianza.
5. **Naming engañoso menor**: `components/_recibir_paquete.html::recursos_recibir()`
   en realidad contiene la infraestructura JS de *toda* la página (modal
   delegation genérico + picker de apartamento compartido con "Asignar
   apartamento"), no solo "recibir". Cosmético, no funcional.

### En resumen

Vista con mucha superficie (11 endpoints, ~15 estados de UI/modal por fila)
pero madura: separación dominio/vista respetada, batch queries correctas, 192
tests verdes, y decisiones de diseño documentadas con su motivo real. El costo
de esa madurez es el tamaño del archivo de rutas y la densidad de las reglas
de "destinatario confirmado". El punto de mayor apalancamiento si se quiere
invertir en claridad: extraer el view-model builder (`_listar` + helpers) de
`packages.py` a su propio módulo.

## 2. Cómo se conecta con `/residentes`

La relación es **asimétrica**: `/residentes` nunca toca la tabla `Paquete`
(no hay un solo `db.query(Paquete)` en `customers_manage.py`), mientras que
`/paquetes` sí lee y escribe intensamente sobre el dominio de `/residentes`
(`Persona`/`Ocupante`/`Apartamento`). Es decir: **`/residentes` es la fuente
de verdad del padrón de residentes; `/paquetes` es un consumidor pesado que
además puede escribir en ese padrón** a través de sus propios mini-flujos
embebidos (Recibir, Asignar apartamento, Corregir destinatario).

### 2.1 Capa de datos — el punto de fricción real

- `Paquete.snapshot_conjunto/torre/apartamento` es un **snapshot congelado**
  en el momento de anunciar (ADR-0001) — nunca se re-resuelve solo cuando
  alguien se muda.
- `Persona.apartamento_actual_id` + las filas de `Ocupante` son el **estado
  vivo**, mantenido por `/residentes`.
- Todo el bloque de `_listar()` en `packages.py` (líneas ~700-805) existe para
  tender un puente entre esos dos mundos: `_apartamento_id_residentes`
  prioriza el domicilio ACTUAL del destinatario sobre el snapshot viejo para
  la caja "Residentes de la unidad", `cambios_recientes_de_apartamento` pinta
  el 🔄 cuando el residente se mudó hace poco, etc.

  **Cualquier cambio en `/paquetes` que toque "a quién pertenece este
  paquete" tiene que decidir explícitamente si mira el snapshot o el estado
  vivo** — no son intercambiables, y ya hubo varios bugs reales (FANTASMA 1-4)
  por confundir los dos.

### 2.2 Capa de dominio — el "shared kernel"

Ambas rutas importan del **mismo módulo** `ocupante_service.py`:
`agregar_ocupante`, `mover_ocupante`, `promover_a_principal`,
`listar_ocupantes`, `residentes_por_torre_apartamento`,
`identificar_contacto_para_unidad`, `ocupante_activo_por_contacto`,
`mensaje_ya_ocupante_activo`. Esto garantiza que "+ Nuevo residente" en
`/paquetes` y "Agregar Residente" en `/residentes` apliquen exactamente las
mismas reglas (máx. 5 ocupantes activos, un teléfono no puede estar en dos
unidades, degradar Principal automático al mover, etc.)

**Si se cambia una regla de negocio en `ocupante_service`, afecta a las dos
vistas a la vez** — no hay una copia separada.

En cambio, `paquete_correccion_service.candidatos_correccion` (quién puede
ser el destinatario de un paquete) es de uso exclusivo de `/paquetes` —
`/residentes` no lo necesita porque no tiene el concepto de "destinatario de
un paquete".

`preferencia_notificacion_service`: `/residentes` es donde se **edita** la
matriz Canal×Evento (`matriz_preferencias`/`guardar_matriz_preferencias`);
`/paquetes` solo la **lee** (`preferencias_activas_por_persona`) para decidir
si el ícono de WhatsApp de Acciones queda habilitado.

### 2.3 Capa de presentación — componentes literalmente compartidos

- `components/_busqueda_filtros.html`: el MISMO macro arma la barra de
  búsqueda de las dos vistas (`mostrar_estado=False` en `/residentes` porque
  no hay Estado de paquete que filtrar).
- `components/_recibir_paquete.html::recursos_recibir()`: el MISMO `<script>`
  de delegación de modales (`data-open`/`data-close` sobre `document`) y el
  picker Torre→Apartamento se cargan una vez en cada vista — a pesar del
  nombre ("recibir paquete"), es infraestructura genérica que también usa
  `/residentes`.
- `identificar_contacto_para_unidad`: la MISMA lógica de "vista previa en vivo
  del contacto" sirve a dos endpoints paralelos e independientes —
  `/paquetes/{id}/nuevo-residente/identificar` y
  `/residentes/{id}/ocupantes/identificar` — cada uno con su propio JS inline
  casi calcado (duplicación real de plantilla/JS, no de lógica de servidor).
- `badge_ocupante`, mayúsculas forzadas en nombres, el mismo lenguaje visual
  de "Promover a principal" — unificados por pedido explícito del cliente
  ("que la parte superior de `/paquetes` y `/residentes` sea igual").

### 2.4 Navegación cruzada — un solo sentido

`/paquetes` enlaza hacia `/residentes/{persona_destino_id}` (título del modal
Ver) y `/residentes/{persona_destino_id}?tab=residentes` (Torre/Apto), **solo
cuando el destinatario está confirmado** (`not p.advertencia_nombre`). No
existe el enlace inverso — `/residentes` no tiene ningún link ni tab hacia los
paquetes de ese residente (eso vive del lado cliente, en `/mis-paquetes`, no
en la vista de staff).

### 2.5 Implicación práctica

Si se va a modificar `/paquetes` "basado en lo que estipula `/residentes`",
el lugar donde eso se vuelve real no es la plantilla — es `ocupante_service.py`
y `apartamento_service.py` (el shared kernel) y las funciones
`_apartamento_id_residentes` / `candidatos_correccion` /
`_destinatario_coincide_con_candidato_real` que traducen ese padrón al
lenguaje de "destinatario de un paquete". Antes de tocar código conviene
precisar **qué comportamiento concreto de `/residentes` debe empezar a
respetar `/paquetes`**, para ubicar la costura exacta (dominio vs. vista vs.
JS duplicado) en vez de conjeturar.
