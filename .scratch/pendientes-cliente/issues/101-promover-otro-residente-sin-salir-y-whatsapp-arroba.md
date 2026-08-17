# 101 — "Promover a otro residente" sin salir del modal + WhatsApp acepta "@"

**Pedido original (cliente):**
1. "Que posibilidad existe en que al presionar el boton 'Degradarlo' en el
   modal de Corregir destinatario, me permita hacer esta degradacion de un
   cliente y poder regresar donde estaba en el modal inicial? posiblemente
   creando una version redusida de degradar donde solo se seleccione el
   nuevo principal de todos los que existen y listo, tu que dices?" --
   confirmado factible (reusa 3 patrones ya construidos esta sesión) y el
   cliente confirmó: "Yes build it as you just said".
2. "Para finalizar con esta vista necesito que para los usuarios de
   whatsapp hagas lo mismo que en los numeros de telefono... necesito que
   para los clientes de whatsapp al validarlos quiero que se validen con
   la @ y sin la @ y que nos lleven al mismo resultado."

**Status:** implementado

## Implementación

### Parte 1 — "Promover a otro residente"

- Nuevo modal `modal-promover-<id>` (por paquete, `_resultados.html`):
  lista de un clic con los demás Ocupantes activos de la unidad del
  conflicto (excluye al principal actual, no tiene sentido "promoverlo" a
  lo que ya es). Se abre ENCIMA de "Corregir destinatario" (definido
  DESPUÉS en el DOM, mismo truco de layering que Ver/Corregir, issue 96)
  -- "Degradarlo" pasó de `<a target="_blank">` a `<button data-open=...>`.
- `GET /paquetes/promover-candidatos?torre=&apartamento=` -- candidatos de
  una unidad (excluye al principal). `POST /paquetes/promover-principal`
  -- promueve (`promover_a_principal`, degrada al anterior automático) y
  redirige a `/paquetes?corregir=<paquete_id>&recontactar=<contacto>` si
  esos datos venían en el form (siempre que se abrió desde un paquete
  puntual).
- `GET /paquetes` gana `corregir`/`recontactar`: reabre el modal
  "Corregir" de ESE paquete (mismo patrón que `ver`/`error_paquete_id`) Y
  re-tipea el contacto solo, disparando la vista previa de nuevo -- sin
  esto el staff tendría que volver a escribir el mismo número para ver
  que ahora sí puede "Mudar residente" (ya no bloqueado por ser Principal).
- **Bug real encontrado en vivo mientras se probaba**: el `<script>` que
  arma el modal "Promover" vive DENTRO del `<form>` de "Corregir" (antes,
  en el DOM), pero el modal "Promover" mismo vive DESPUÉS (necesario para
  el layering) -- buscar sus elementos (`getElementById`) al cargar la
  página siempre devolvía `null`, porque el navegador todavía no había
  parseado esa parte del HTML. Corregido: esos elementos se buscan DENTRO
  del listener de clic (al momento de abrir el modal), no al cargar.

### Parte 2 — WhatsApp acepta "@" y sin "@"

- `domain/contacto.py`, `clasificar_contacto`: mismo hueco que el `+57`
  de teléfono (issue 92), pero para WhatsApp -- `"@ana.whats"` no empieza
  con una letra (empieza con `@`), así que nunca clasificaba como
  `"whatsapp"`, aunque `persona_service.py` ya sabía buscar/crear la
  Persona indistintamente con o sin `@` (`.lstrip("@")` interno). Ahora
  `clasificar_contacto` quita un `@` inicial antes de evaluar -- el
  mínimo de 3 caracteres se mide sobre el usuario, no contando el `@`.
  Mismos 4 lugares beneficiados que en issue 92 (comparten el
  clasificador): `/announce`, "+ Nuevo residente" de `/paquetes`,
  `/residentes`, verificación OTP de cliente.

## Verificación

- `tests/web/test_packages.py`: 6 tests nuevos para "Promover" (candidatos
  excluye al principal, unidad vacía, unidad inválida, promueve y degrada,
  redirige a `?corregir=&recontactar=`, ocupante inexistente da 404).
- `tests/data_model/test_clasificar_contacto.py`: 6 tests nuevos para
  `@usuario` (con y sin arroba llevan al mismo resultado, mínimo de 3
  caracteres medido sobre el usuario sin la arroba).
- Playwright contra el servidor local real: flujo completo de "Promover"
  de punta a punta (clic en Degradarlo → modal encima de Corregir →
  elegir candidato → confirmado en la base de datos que degradó al
  anterior y promovió al nuevo → vuelta a Corregir con el contacto
  re-tecleado y "Mudar residente" ya disponible); `/announce` y "+ Nuevo
  residente" resolviendo el mismo resultado con `@usuario` y sin `@`.
- Suite completa: ver commit para el conteo final.
- Pendiente: deploy a test.papyrus.com.co.
