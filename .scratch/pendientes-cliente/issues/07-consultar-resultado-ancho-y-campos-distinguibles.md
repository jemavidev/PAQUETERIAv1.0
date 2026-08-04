# 07 — `/consultar`: ancho del resultado alineado con el formulario + campos distinguibles

**Pedido original (cliente):** "Se ve mucho mejor, pero te confirmo algunos
cambios, el ancho de esta seccion deberia ser acorde con la que esta en la
parte superior. Otra cosa es que seria bueno tener los diferentes campos
por separado, que se distinga que son campos diferentes, por ejemplo,
fecha y hora, guia y tamano o estado, o cualquier posible campo que
exista, deberia poder distinguirse a simple vista, ya que todos estan
inline en este momento, ANTES te habia pedido cambios para inline, pero
no me referi a todos los campos como estos."

**Vista:** `search/form.html` (`/consultar`, resultado tras buscar un
paquete).

**Status:** verificado

## Diagnóstico

1. **Ancho**: la tarjeta del formulario (vía `formulario_flujo()`) usa
   `max-w-md` (448px); la tarjeta del resultado tiene `max-w-lg` (512px) a
   mano en `search/form.html` — por eso no alinean, confirmado en las
   capturas que se enviaron.
2. **Campos sin distinguir**: dentro de cada paso del timeline, los chips
   de Tipo y Condición se arman como texto plano sin etiqueta ("Normal",
   "Bueno"), mientras que Guía y Motivo sí ya tienen prefijo ("Guía X",
   "Motivo: Y") — inconsistente, y por eso los primeros dos se leen como
   texto suelto en vez de un campo identificable.

## Qué hacer

1. Cambiar `max-w-lg` → `max-w-md` en la tarjeta de resultado
   (`search/form.html`), para que coincida exactamente con el ancho de la
   tarjeta del formulario.
2. Etiquetar TODOS los chips de forma consistente ("Tipo: Normal",
   "Condición: Bueno", "Guía: X", "Motivo: Y") — mismo formato "Etiqueta:
   valor" en los 4, no solo en 2.

## Verificación

- [x] Captura de pantalla (mobile + desktop) confirma que ambas tarjetas
      alinean exactamente en ancho.
- [x] Render local + captura confirman "Tipo: Normal", "Condición: Bueno",
      "Guía: TEST-ASYNC-FOTO" — mismo formato en los 3 chips.
- [x] 436/436 suite completa.
- [x] Desplegado a `test.papyrus.com.co` (commit `22a6214`) y confirmado en
      vivo con `NSFC`.

## Comments

- 2026-08-02: el pipeline de GitHub Actions falló en el deploy anterior
  (commit `87f9ce6`, paso "Setup SSH" — hiccup transitorio de red del
  runner) y se desplegó manualmente por SSH con autorización explícita del
  cliente. Este deploy (commit `22a6214`) sí funcionó automáticamente sin
  intervención.
