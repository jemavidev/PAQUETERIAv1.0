# 69 — `/residentes`: revisión punto por punto de [[68]] tras probar en vivo

**Pedido original (cliente):** el cliente probó [[68]] en `test.papyrus.com.co`
y repasó cada uno de los 14 puntos, confirmando la mayoría y pidiendo ajustes
en varios. Resumen de lo que cambia (los puntos confirmados "OK" sin más no
se repiten acá):

4. Recepción automática: en vez de (o adicional a) el badge, quiere una
   señal de fondo de color en la fila (lista) y en la ficha para distinguir
   Residentes Secundarios -- el texto del pedido mezcla "Recepción
   automática" (título) con "Principal" (contenido); se interpreta como
   fondo rojizo tenue para Secundarios (ver Decisiones).
5. El picker de Dirección bloquea reasignar a un cliente que es Principal
   con otros Residentes activos en su unidad -- comportamiento YA existente
   (guard previo a [[67]], protege contra huérfanos), pero sin ninguna
   explicación visible antes de intentar guardar. Pide además señalización
   de qué apartamentos ya tienen un Principal asignado.
8. "Zona de peligro" no debe repetirse debajo de cada tab -- vive fuera de
   los `tab-panel` así que queda visible sin importar cuál tab esté activa
   (se ve como "está en todos los tabs"). Debe vivir en un solo lugar.
9. Columna Acciones: "Ver ficha" debe ser ícono, no texto -- toda la
   columna debe ser solo íconos.
10. Tab "Residentes" debe mostrar la referencia del apartamento cuando
    aplica (ej. "T 05 - APT 102"), y solo decir "Residentes" cuando el
    cliente no tiene apartamento asignado.
11. Los badges (Auto/Manual, Principal/Secundario) deben ocultarse en el
    caso "negativo" (Manual, Secundario) -- solo se muestran Auto y
    Principal.
12/13. Bug real: el campo "Usuario de WhatsApp" no se puede vaciar una vez
    tiene un valor -- el formulario lo trata como "no tocar" cuando llega
    vacío, igual que nombre/email/segundo_contacto.
14. La barra de búsqueda rediseñada no se parece a lo que pidió -- pendiente
    de una captura de pantalla real de `/customers/manage` para clonarla
    esta vez con la referencia correcta en mano.

**Status:** implementado (pendiente punto 14, sin nueva referencia visual)

## Decisiones de implementación

- **Punto 4**: fondo rojizo (`bg-red-50`/similar) SOLO para Residentes
  Secundarios -- ni para "Manual" de recepción automática (evita mezclar 2
  señales de color con 2 significados distintos en el mismo elemento).
  Aplica a la fila de `/residentes` y a un contenedor visible en la ficha.
  Marcado explícitamente como interpretación a confirmar.
- **Punto 5**: el guard de reasignación NO se relaja (protege integridad --
  evita dejar Ocupantes huérfanos). Se agrega: (a) aviso visible en la tab
  Dirección explicando la razón exacta cuando aplica, ANTES de intentar
  guardar; (b) señalización visual en los botones de Apartamento del picker
  para las unidades que ya tienen un Principal activo (nueva función batch
  `apartamentos_con_principal`, issue 69).
- **Punto 8**: "Zona de peligro" se mueve DENTRO de `tab-panel[data-panel="datos"]`
  -- un solo lugar fijo (la tab por default), ya no aparece bajo las otras 3.
- **Punto 12/13**: `update_datos_personales` distingue ahora `""` (borrar
  explícitamente) de `None` (no tocar) para `whatsapp_usuario` -- el resto
  de campos (nombre/email/segundo_contacto) NO se tocan, mismo bug
  potencial ahí pero fuera de alcance de lo reportado.
- **Punto 14**: sin nueva implementación todavía -- se necesita una
  captura de pantalla real antes de intentar un tercer rediseño a ciegas.

## Verificación

- Sintaxis Jinja verificada con `Environment.parse()`.
- Verificación visual en navegador real (Playwright) con datos que cubren
  los 4 casos relevantes: principal solo (aviso "dalo de baja"), principal
  con acompañante (aviso "convierte a otro"), secundario (sin badge, fondo
  rojizo en las 4 tabs), sin apartamento (tab "Residentes" a secas, sin
  aviso). Confirmado el marcado ámbar de apartamentos con principal en el
  picker inspeccionando el DOM directamente (`classList`/`title`), no solo
  a simple vista -- el punto/borde es sutil en una captura completa. Sin
  errores de consola.
- Suite completa (`tests/data_model tests/web`): 687/687, sin regresiones.
  19 tests nuevos/reescritos: borrado real de `whatsapp_usuario` (bug),
  `apartamentos_con_principal`/`hay_otro_ocupante_activo` (dominio),
  badges condicionales + fondo rojizo, ícono "ver" sin texto, tab label
  dinámico, aviso de reasignación bloqueada, Zona de peligro en un solo
  lugar.
- Tailwind recompilado y comiteado (clases nuevas: `border-amber-400`,
  `bg-red-50 hover:bg-red-100`, etc.) — `?v=35` → `?v=36`.
- Pendiente: punto 14 (barra de búsqueda) sigue sin la referencia visual
  real de `/customers/manage` -- no se tocó en esta ronda.
