# 32 — Mayúsculas consistentes en nombres/guías (guardar, modificar, buscar)

**Pedido original (cliente):** "auto-mayúsculas, sería bueno que se maneje
todo esto para búsquedas y demás, ya que en la base de datos la idea es que
coincida mayúsculas y minúsculas, como podrás manejar esto para que no se
tenga ningún problema (al guardar, al modificar, al buscar) con mayúsculas."

**Decisiones confirmadas con el cliente (AskUserQuestion):**

1. Forma canónica: MAYÚSCULAS (coincide con el comportamiento verificado de
   producción — `customer_name`/`guide_number` se autocapitalizan ahí con
   `oninput`).
2. Backfill: SÍ — normalizar también los registros ya existentes, no solo
   los nuevos.

**Status:** verificado

## Diagnóstico

Búsqueda YA era segura: `customers_manage._buscar_residentes` usa
`ilike` (Postgres, case-insensitive) para nombre/torre/apartamento — sin
cambios ahí. El gap real era solo de ESCRITURA: cada ruta guardaba el texto
tal cual lo tipeó el usuario, así que la misma Persona podía terminar con
"Camila"/"CAMILA"/"camila " según por dónde se creó/editó.

`Apartamento` (conjunto/torre/apartamento) YA tenía este problema resuelto
de antes (`apartamento.normalizar_terna` / `_normalizar_componente`,
invocado siempre desde `apartamento_service`) — no necesitó cambios, solo
se refactorizó para reusar el nuevo normalizador compartido.

## Qué se hizo

- **`app/domain/texto.py`** (nuevo): `normalizar_nombre(valor)` — strip +
  colapso de espacios + MAYÚSCULAS. Mismo patrón que `telefono.
  normalizar_telefono()` ya establecía para teléfonos; `apartamento.
  _normalizar_componente` ahora delega acá (DRY).
- Aplicado en cada write-site real del dominio: `persona_service.
  get_or_create_persona`/`update_datos_personales`, `ocupante_service.
  agregar_ocupante`, `staff_service._crear_usuario`/`editar_staff`,
  `paquete_service.announce` (recipient_name), `paquete_lifecycle.
  receive` (guide_number) / `corregir_destinatario` (recipient_name).
  Email NO se toca (ya usa su propia convención en minúsculas,
  `staff_service._normalizar_email` — ortogonal a este cambio).
  `_NOMBRE_ANONIMIZADO` ("Cliente eliminado", centinela de
  `anonimizar_persona`) tampoco se toca — no es dato de usuario.
- **Complemento visual**: `oninput="this.value = this.value.toUpperCase()"`
  en los campos de nombre/guía de `/anunciar`, `/announce`, `/mis-datos`,
  `/residentes/{id}`, `/administracion/personal` (alta + editar), el modal
  "Corregir destinatario" y los inputs de guía en `/paquetes` (recibir +
  confirmar con escáner) — mismo comportamiento verificado en producción.
  También en el campo de búsqueda de `/consultar` (mismo tratamiento que
  `paquetex.papyrus.com.co/search`).
- Efecto secundario correcto: la comparación JS del escáner de guía en
  `/paquetes` (`guia-check-msg`) ahora compara con `.toUpperCase()` de
  ambos lados — si no, una guía escaneada en minúscula generaría una
  advertencia falsa de no-coincidencia contra el valor ya normalizado.
- **`alembic/versions/0017_normalizar_casing_nombres.py`** (nueva
  migración, solo datos): backfill de `personas.nombre`,
  `ocupantes.nombre`, `usuarios.nombre`, `paquetes.recipient_name`,
  `paquetes.guide_number` a la forma canónica. Excluye a propósito
  `personas.eliminado_en IS NOT NULL` (el centinela de anonimizadas).
  Verificado manualmente contra un Postgres efímero (vía el mismo arnés
  de `tests/_harness.py`): filas con espacios/casing sucios pasan a
  MAYÚSCULAS tras `alembic upgrade head`; la Persona anonimizada queda
  intacta.

## Verificación

- [x] Suite completa sin regresiones tras actualizar los ~50 asserts que
      pincheaban el casing original de nombres de prueba (454 passed).
- [x] Migración 0017 verificada en un Postgres efímero aislado (no el de
      los tests normales, que nunca tiene datos "sucios" porque todo pasa
      ya por los write-sites nuevos).
- [x] Desplegado (push a `paquetex-live/main`, `9a4dc59..c1a4c4a`) y
      confirmado en vivo en test.papyrus.com.co: `oninput` de mayúsculas
      presente en `/anunciar` y `/consultar`.
