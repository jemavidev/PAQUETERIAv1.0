# Captura de guía en "Recibir paquete": decisiones acordadas (grilling, 2026-09-21)

**Estado:** entendimiento compartido CONFIRMADO por Jesús. Falta `/to-spec` → `/to-tickets` (los invoca él). Ningún código tocado.

**Base de hechos:** `investigacion-oficial.md` (esta misma carpeta). Análisis previo del comportamiento actual, verificado en
navegador contra el servidor dev: un lector tipo teclado con Enter final envía el form y recibe el paquete al instante; al abrir
el modal el foco queda en el botón de la fila y no en Guía (una lectura sin tocar antes el campo se pierde); rechazo de
`getUserMedia` sin mensaje (queda un cuadro negro de video); doble clic en "Escanear" deja un stream vivo al cerrar el modal;
`guide_number` es `varchar(50)` sin validación (>50 → 500 en Postgres); sin unicidad y `/consultar` usa `.one_or_none()`
(500 esperado con 2 paquetes de la misma guía, semántica probada aislada, no de punta a punta). "Confirmar guía" de Entregar y de
`/consultar` está FUERA del `<form>`: un Enter ahí no envía nada (el riesgo del Enter es solo del modal Recibir).

**Requisito del cliente:** captura de guía (A) en celulares normales con la cámara y (B) en equipos Farset F7 con lector Honeywell
N6603 integrado.

## Decisiones de Jesús

1. **Tras leer, solo llenar.** La lectura (cámara o lector) escribe la guía y nada más. Un Enter/Tab del lector NO envía el
   formulario; el operador confirma con "Recibir".
2. **Orden: todo junto, F7 probado al final.** (Elegido en vez de las dos entregas recomendadas.) Riesgo aceptado: lo específico
   del F7 puede necesitar ajuste tras la prueba de campo, por eso se mantiene pequeño y aislado.
3. **Interruptor por equipo "Este equipo tiene lector"** (localStorage), apagado por defecto. Activo: al abrir el modal, foco en
   Guía con `inputmode="none"` (sin teclado en pantalla). Respeta el issue 284 (sin autofocus por defecto).
4. **El interruptor vive en el menú de cuenta** del encabezado (no en el modal, que está apretado de espacio).
5. **Cámara: ZXing 0.19.1 con arreglos y mejor captura.** Mensaje visible si falla el permiso o no hay cámara; botón deshabilitado
   mientras escanea (sin doble clic) y botón para detener; resolución ideal 1280x720 vía `decodeFromConstraints`; linterna si
   `getCapabilities().torch` existe; reintentos espaciados. NO cambiar de librería ni de versión.
6. **Formatos: todos, sin restringir.** El campo siempre muestra lo leído. Riesgo conocido: una etiqueta con QR + 1D puede devolver
   el QR (p. ej. 32 dígitos) que no coincide con el número impreso.
7. **Más de 50 caracteres: rechazar con mensaje.** Cámara: no lo escribe y avisa. Lector/teclado: el campo marca el error y
   "Recibir" no deja enviar. Servidor: valida igual y responde con el error normal del modal (no 500). SIN `maxlength` a propósito
   (cortaría en silencio lo que inyecta el F7). Nunca truncar.
8. **Guías repetidas: permitir con aviso que no bloquea** ("Ya hay N paquete(s) con esta guía"); arreglar el 500 de `/consultar`.
9. **`/consultar` con una guía en varios paquetes:** con sesión de staff, lista de coincidencias (código de acceso, destinatario,
   estado) para elegir; sin sesión, mensaje neutro ("corresponde a más de un paquete; consulta con el código de acceso de cada
   uno") sin mostrar datos de nadie.
10. **Alcance del modo lector: Recibir y "Confirmar guía" de Entregar** (foco automático en ese campo si el paquete tiene guía). Las
    mejoras de cámara, mensajes y guardas viven en el JS compartido (`recursos_recibir()`), así que llegan solas a Recibir
    (incluido /announce y el Recibir de /consultar), Entregar y /consultar.

## Detalles asumidos (Jesús no objetó)

- Guardia del Enter en `keydown` Y en el envío del form, por si el F7 inyecta el terminador de otra forma que no dispare `keydown`.
- En modo lector, tocar el campo muestra el teclado normal (teclear a mano); al enfocar se selecciona todo el contenido para que
  una segunda lectura reemplace en vez de concatenarse (con `FOCUS` sin overwrite el F7 anexaría).
- Aviso de repetida: consulta al servidor al terminar de leer/escribir (con pausa breve); muestra cantidad y estados; solo staff.
- El manual del operador (`docs/manual-usuario/02-staff-operador.md`, hoy solo dice "número de guía (opcional)") suma una sección
  corta de captura de guía (cámara, lector, configuración del F7).
- Verificación: pruebas automáticas (pytest) + Playwright con cámara simulada (canvas.captureStream con un QR generado con el propio
  ZXing). Celulares y F7 reales quedan para la prueba de campo (protocolo al final de `investigacion-oficial.md`). Despliegue a
  `test.papyrus.com.co` SOLO cuando Jesús lo pida.

## Fuera del diseño (configuración del equipo, no de la web)

- El F7 viene en modo `BROADCAST` + terminador `NONE` (según el PDF "User Guide" del listado de Amazon, sin marca ni modelo): de
  fábrica NO escribe en ninguna página web. Configuración recomendada: send mode `FOCUS_OVERWRITE`, terminador `NONE`
  (`ENTER`/`TAB` se toleran por la decisión 1). Se cambia en Ajustes → Scanning Tools → Scanning Settings de cada equipo.

## Sin verificar (solo con el equipo físico)

- Si `FOCUS`/`FOCUS_OVERWRITE` escribe en un `<input>` de Chrome y con qué mecanismo (¿eventos de teclado?).
- Si el F7 trae Chrome y Google Play Services; modelo exacto (¿"F7", "F7-Pro", "F7T"?).
- Si el gatillo físico funciona con un formulario web.
- Qué transportadoras llegan y qué código traen sus etiquetas (no hay fuente primaria; una muestra de Coordinadora de 2019 trae solo
  un QR de 32 dígitos). No bloquea el diseño: la decisión 6 no restringe formatos.
- Lectura real en cámaras de celulares Android/iPhone (calidad, luz, etiquetas arrugadas).

## Siguiente paso

`/to-spec` (sin argumentos, sintetiza esta conversación y este archivo) → `/to-tickets`. Los tickets deben respetar la regla del
proyecto de que los pasos del F7 queden aislados.
