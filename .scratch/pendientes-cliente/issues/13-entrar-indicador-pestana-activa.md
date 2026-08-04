# 13 — `/entrar`: indicador de pestaña activa

**Pedido original (cliente, sesión de `/grilling` sobre `/entrar`):** no
existe forma de saber si está seleccionado "Soy residente" o "Soy del
staff".

**Vista:** `auth/entrar.html`.

**Status:** verificado

## Qué hacer

Fondo azul sólido + texto blanco en la pestaña activa (opción confirmada
en grilling), reemplazando el tratamiento actual (azul claro tenue, poco
perceptible).

## Qué se hizo

El primer intento (commit `ac6bcda`) solo cambió las clases de color y
falló silenciosamente en vivo — dos causas encontradas y corregidas en
despliegues de seguimiento:

1. `tailwind.css` no se había recompilado tras el cambio de plantilla —
   las clases nuevas (`peer-checked/cliente:bg-blue-800`,
   `peer-checked/cliente:text-white`) no existían en el bundle servido
   (commit `9f8f254`, cache-busting `v=13` → `v=14`).
2. Causa raíz real: `peer-checked/{name}` compila a un selector CSS de
   hermano general (`~`), que no atraviesa un `<div>` envolvente. Los
   `<label>` estaban anidados dentro de un `<div class="flex ...">` que
   a su vez era hermano del `<input>` — el indicador **nunca** funcionó,
   ni en versiones anteriores a esta ronda de tickets. Se reestructuró
   el DOM para que `input` y `label` sean hermanos directos (`flex
   flex-wrap` en el contenedor, `basis-0` en los labels, `w-full` en los
   paneles de contenido para forzarlos a la siguiente línea) — commit
   `b19d71a`, `v=15`. Verificado primero con un render aislado
   (`file://`) antes de tocar el sitio en vivo de nuevo.

## Verificación

- [x] Captura confirma la pestaña activa con fondo sólido (ambas
      direcciones: "Soy residente" y "Soy del staff").
- [x] Suite de tests sin regresiones (437 passed).
- [x] Desplegado a `test.papyrus.com.co` y confirmado en vivo vía
      Playwright.
