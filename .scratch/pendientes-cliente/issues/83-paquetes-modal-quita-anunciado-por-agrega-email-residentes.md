# 83 — `/paquetes` modal "Ver": quita sección "Anunciado por" + ícono Email en Residentes

**Pedido original (cliente):**
"Mucho mejor, se ve espectacular, ahora en esta vista lo que necesito ahora
es que en el modal remuevas la seccion 'Anunciado por', ya que esta
informacion esta en la parte inferior en el historial, adicional en la
seccion 'Residentes de la unidad' necesito que agrgues todas las opciones
de notificacion por medio de un icono, hasta el momento solo tienes
telefono y whatsapp, puedes agregar email?" — seguido de la aclaración
"recuerda solo para quienes aplique" (mismo criterio ya usado con
WhatsApp/Teléfono: el ícono de Email solo aparece si esa Persona tiene el
dato).

**Status:** implementado

## Contexto

Confirma que el Historial agregado en [[82]] efectivamente reemplaza la
sección "Anunciado por" -- el hito "Anunciado" ya muestra quién anunció
(`Anunció: <nombre>`), así que la tarjeta separada quedaba duplicada.

## Implementación

- `packages/_resultados.html`:
  - Sección completa "Anunciado por" (tarjeta `bg-slate-50`, nombre +
    teléfono + whatsapp + email del anunciante) eliminada del modal "Ver".
    `p.persona_anunciante` se sigue calculando en `packages.py` -- lo sigue
    usando `_acciones.html` para el ícono Email de la columna Acciones
    (issue 81), sin relación con el modal.
  - "Residentes de la unidad": ícono nuevo de Email (`mailto:`, mismo
    patrón `{% if r.persona and r.persona.email %}` que ya usan WhatsApp y
    Teléfono -- solo aparece para el residente que tiene el dato). Color
    `indigo-500` (distinto de WhatsApp-emerald/Teléfono-slate, consistente
    con el color ya usado para Email en Acciones).
- `tests/web/test_packages.py`:
  - `test_modal_ver_muestra_datos_del_anunciante` → renombrado
    `test_modal_ver_ya_no_tiene_seccion_anunciado_por`: ahora verifica la
    AUSENCIA de "Anunciado por" y que el nombre del anunciante siga
    apareciendo, pero vía el Historial ("Anunció").
  - `test_modal_ver_residentes_icono_de_email_solo_si_existe` (nuevo): un
    residente con email en un `mailto:`, el otro sin email sin ninguno --
    único `mailto:` del modal completo (el de "Anunciado por" ya no existe;
    "Destinatario" nunca mostró email).

## Verificación

- `tests/web/test_packages.py`: 87 tests pasan.
- Verificación manual en navegador (ambiente local): modal "Ver" de un
  paquete Entregado confirma que ya no aparece "Anunciado por" (pasa
  directo de Destinatario → Residentes → Historial). Modal de un paquete
  con 4 residentes (uno Principal con WhatsApp+Teléfono+Email, otros con
  distintas combinaciones) confirma que el ícono de Email solo aparece
  junto al nombre de quien tiene el dato.
- Pendiente: `tests/` completo + deploy a test.papyrus.com.co.
