# 50 — `/anunciar`: límite de anuncios activos por teléfono, con confirmación

**Pedido original (cliente):** "quiero que si ya existe por lo menos 1
paquete anunciado, antes de confirmar el anuncio nuevo que se quiera hacer,
se le informe al cliente que ya existe uno, dos o mas paquetes anunciados, y
preguntarle que si quiere o no anunciar otro paquete, la idea es que se
puedan anunciar maximo 10 paquetes por apartamento, esto podria evitar que
se envien mensajes de texto, adicional al hacer esta notificacion indicando
que ya existen varios anuncios, no se debe mostrar ni mencionar el codigo de
acceso de esos anuncios."

**Status:** implementado

## Contexto

Segundo pedido de la ronda "versión móvil". Se grilló con el cliente (4
preguntas) antes de tocar código, porque el pedido original mezclaba varias
decisiones reales:

1. **Por teléfono, no por apartamento** — en `/anunciar` (público, sin
   sesión) la mayoría de quien anuncia por primera vez no tiene apartamento
   asignado todavía (esa asignación es exclusiva del staff desde el issue
   48). El único dato confiable en ese punto es el teléfono. Confirmado por
   el cliente.
2. **Tope duro en 10**, no una confirmación indefinidamente superable.
3. **Solo cuenta el estado ANUNCIADO** (la cola real de paquetes pendientes
   de recibir) — Recibido/Entregado/Cancelado no suman.
4. **Pantalla intermedia** (no un checkbox en el mismo formulario) para la
   confirmación de 1-9 anuncios activos.

Modelo final de 2 umbrales:
- 0 activos → se anuncia normal, sin interrupción.
- 1-9 activos → pantalla `announce/confirmar_multiple.html`: "Ya tienes N
  paquete(s) anunciado(s) pendiente(s) de recibir. ¿Quieres anunciar otro?"
  con botón "Sí, anunciar otro" (reenvía el mismo formulario con
  `confirmar_multiple=1`) y "Cancelar" (vuelve a `/anunciar` limpio).
- 10 (el máximo) → bloqueo real, mensaje claro, sin opción de confirmar.

## Implementación

- `paquete_service.py`: `MAX_ANUNCIADOS_ACTIVOS_POR_TELEFONO = 10` +
  `contar_anunciados_activos_de_telefono(session, telefono_canonico)` —
  cuenta Paquetes `ANUNCIADO` donde ese teléfono es el Anunciante. Mismo
  espíritu que `MAX_OCUPANTES_ACTIVOS` en `ocupante_service.py`.
- `announce.py`: antes de llamar a `announce()`, normaliza el teléfono y
  consulta el conteo. Nuevo campo de formulario oculto `confirmar_multiple`.
- Nueva plantilla `announce/confirmar_multiple.html` — mismo lenguaje visual
  que el resto de `/anunciar` (logo, card, iconos outline). Solo muestra el
  CONTEO, nunca los códigos de acceso de los anuncios existentes (ninguna
  consulta de la ruta siquiera los trae a este contexto).
- Nuevo ícono `alerta` en `icons.py` (exclamación en círculo, outline).

Sin cambios de CSS/layout en ninguna vista EXISTENTE -- la pantalla nueva
sigue el mismo patrón (`max-w-md mx-auto`) que ya usan `announce/form.html`
y `announce/confirmacion.html`, así que no hay riesgo para desktop.

## Verificación

630 tests pasan (620 + 10 nuevos: 3 de dominio para
`contar_anunciados_activos_de_telefono`, 7 de la ruta web cubriendo el
modelo completo -- primer anuncio sin interrupción, segundo con pantalla
intermedia sin crear el paquete todavía, el código de acceso del primer
anuncio NUNCA aparece en el aviso del segundo intento, confirmar crea el
paquete, el conteo es por teléfono (no cruza entre dos números distintos),
el máximo bloquea incluso confirmando, y recibir uno libera espacio bajo el
límite).

Pendiente: desplegar a `test.papyrus.com.co` y que el cliente confirme en
vivo (cambia `Status` a `verificado`).
