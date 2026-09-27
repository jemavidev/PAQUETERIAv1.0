# Limpieza de ramas locales y cierre de la sesión 2026-09-26/27

Registro de la limpieza del repo local (`PAQUETERIAv1.0`, checkout `MATT`) pedida por Jesús el 2026-09-27 ("si limpialas y
documenta todo"), más un resumen de lo entregado en la sesión que la precedió.

## Criterio aplicado

- **Rama cuyo contenido ya está en un remoto** (`origin` = `jemavidev/PAQUETERIAv1.0`, o `paquetex-live` = `jemavidev/PaqueteX`,
  el repo que corre test): **borrada**. Son ramas de sincronización/deploy de un solo uso (ver la
  memoria "PaqueteX v2 infra topology"); su contenido vive en el remoto.
- **Rama que existía SOLO en local** (9 prototipos y la rama local del deploy "5 módulos"): **archivada como etiqueta local** `archivo/<rama>` y luego borrada como rama.
  No se pierde nada: la etiqueta conserva los commits. Las etiquetas NO se subieron a ningún remoto (los repos son públicos).
- **Se conservaron**: `PaqueteXv.2` (trabajo actual, sincronizada con `origin`), `main` (sigue a `paquetex-live/main`; se
  adelantó por fast-forward, estaba 32 commits atrás) y `staging` (al día con `origin/staging`).
- **Worktree eliminado**: el del prototipo de Respaldos (issue 411) en el scratchpad de otra sesión; solo tenía un `.venv` sin
  trackear. Su rama quedó archivada (`archivo/prototipo/respaldos-amigable`).

Verificación puntual: `deploy/2026-09-17-mobile-y-bloqueo` no estaba "contenida" en ningún remoto por SHA, pero `git cherry`
mostró sus commits equivalentes en `paquetex-live/main` y los 4 módulos del commit restante ("5 módulos nuevos": cobro, contactos
externos, saldo contra entrega, motivos de bloqueo) existen en el repo de deploy -- se borró.

## Ramas archivadas (etiquetas locales)

| Etiqueta | Commit | Fecha | Último commit |
|---|---|---|---|
| `archivo/deploy-5-modulos-cobro-contactos-migracion-bloqueo-dinero` | `d49b541` | 2026-09-14 | fix(residentes): nunca eliminar Teléfono/WhatsApp + saldo contra entrega + fixes de contacto/sucesión |
| `archivo/prototipo/estadisticas-cobro-dashboard` | `89a58e7` | 2026-09-20 | prototipo(estadisticas-cobro): 3 variantes visuales del dashboard (A/B/C) -- gana C |
| `archivo/prototipo/estadisticas-cobro-filtros-y-tablas` | `9aa0046` | 2026-09-21 | prototipo(estadisticas-cobro): optimizado para móviles, sin scroll lateral (issue 372) -- NO MERGEAR |
| `archivo/prototipo/estadisticas-cobro-tablero-visual` | `ef8a7ec` | 2026-09-20 | prototipo(estadisticas-cobro): 3 variantes visuales del tablero (issue 369) -- NO MERGEAR |
| `archivo/prototipo/paquetes-movil-2-lineas` | `78a9928` | 2026-09-24 | prototipo(paquetes): 3 variantes de la fila móvil en 2 líneas con acciones grandes (?variant=A/B/C) |
| `archivo/prototipo/residentes-movil-tarjetas` | `3b06aee` | 2026-09-24 | prototipo(residentes): botones con ícono y nombre en la misma línea (ronda 3) |
| `archivo/prototipo/respaldos-amigable` | `f9fbada` | 2026-09-26 | prototipo(respaldos): 3 variantes amigables de la pantalla Respaldos (issue 411) -- NO MERGEAR |
| `archivo/prototype/asignar-apartamento-buscar` | `8b735ce` | 2026-08-15 | wip: prototipo 3 variantes "Asignar apartamento" |
| `archivo/prototype/corregir-destinatario-candidatos` | `3315d95` | 2026-08-15 | wip: prototipo 3 variantes "Corregir destinatario" + trabajo de sesión |
| `archivo/prototype/menu-cuenta-categorias` | `51c0234` | 2026-09-15 | prototype(menu-cuenta): 3 variantes para agrupar el dropdown de cuenta |

Las tres `archivo/prototipo/estadisticas-cobro-*` guardan la **propuesta 370 del dashboard** (comparación, gráfico, tablas), que
NUNCA se implementó en código real: son la única copia.

**Restaurar una rama archivada:** `git branch <rama> archivo/<rama>` (ej. `git branch prototipo/estadisticas-cobro-dashboard
archivo/prototipo/estadisticas-cobro-dashboard`).

## Ramas borradas (53)

Todas con su contenido en `origin` o `paquetex-live`. Si alguna hiciera falta: `git branch <rama> <commit>` mientras el objeto
exista localmente (el reflog lo retiene ~90 días), o recrearla desde el remoto.

| Rama | Commit |
|---|---|
| `deploy-announce-auto-recepcion-y-busqueda-optimizada` | `924422c` |
| `deploy-announce-campo-unico` | `1357504` |
| `deploy-announce-torre-apto` | `bb91428` |
| `deploy-announce-whatsapp-ocupante` | `482cd8c` |
| `deploy-baja-administrativa-derecho-olvido-lazy-loading` | `5f007c7` |
| `deploy-historial-y-chip-sin-fondo` | `f10f43b` |
| `deploy-issues-100-101-172-189` | `b721b12` |
| `deploy-ocupante-principal-whatsapp` | `2828ac4` |
| `deploy-otp-codigo-acceso-y-paquetes-relacionados` | `3b4e544` |
| `deploy-paquetes-boton-flotante-y-direccion-roja` | `9183868` |
| `deploy-paquetes-codigo-acceso-chip` | `a65db27` |
| `deploy-paquetes-filtros-opacado` | `3a8dad0` |
| `deploy-paquetes-filtros-vivos` | `513ab3f` |
| `deploy-paquetes-sincronizar-hermanos` | `fa2bcd9` |
| `deploy-paquetes-tabla-y-acciones` | `15f13e5` |
| `deploy-paquetes-ver-modal-y-hora` | `4649bf0` |
| `deploy-persona-telefono-o-whatsapp` | `7d8f83f` |
| `deploy-residentes-pildora-total-paquetes` | `bcac30d` |
| `deploy-sms-anuncio-only` | `52c6a30` |
| `deploy-ssh-mount` | `37477d3` |
| `deploy-streaming-header-footer-paquetes` | `923c2c0` |
| `deploy-sync-20260828` | `f1f4eec` |
| `deploy-sync-20260830` | `61ca92b` |
| `deploy-sync-20260901` | `4241f14` |
| `deploy-sync-287-admin-sms-telefono` | `417e777` |
| `deploy-sync-288-sms-sin-tildes` | `d325573` |
| `deploy-sync-288b-nombre-sin-tildes` | `3ef18e8` |
| `deploy-sync-294-toggle-booleanos` | `f5de6d0` |
| `deploy-sync-305` | `0147e63` |
| `deploy-sync-proveedores-01-03` | `c13ce2b` |
| `deploy-torre-modal-icono` | `667f018` |
| `deploy/2026-09-17-mobile-y-bloqueo` | `f5fa338` |
| `deploy/2026-09-18-candidato-idx-fotos` | `cb56b48` |
| `deploy/2026-09-18-pago-contra-entrega-recibir` | `0e570ab` |
| `deploy/2026-09-19-perf-y-empresa` | `d43f2ce` |
| `deploy/2026-09-19-ui-fixes-351-353` | `c9ad323` |
| `deploy/2026-09-19-zxing-preload-cache` | `e5249dd` |
| `deploy/2026-09-21-captura-guia-lector-camara` | `8977b9a` |
| `deploy/2026-09-22-menu-lector-nombre-corto` | `2398071` |
| `deploy/2026-09-22-modo-lector-oculta-camara` | `269d53c` |
| `deploy/2026-09-23-auditoria-funcional` | `d14ca4a` |
| `deploy/2026-09-24-mis-datos-papyrus` | `d1006ae` |
| `deploy/2026-09-24-paquetes-movil-usuario` | `29995b2` |
| `deploy/2026-09-24-residentes-movil` | `d1245c0` |
| `deploy/paquetes-busqueda-unificada-ef02767` | `54c8d0c` |
| `deploy/paquetes-iconos-estado-e4acd1f` | `eaae7ac` |
| `deploy/paquetes-resultados-en-vivo-bb86d74` | `0d8de9d` |
| `feat-proveedores-whatsapp-llamadas` | `6b4cc6e` |
| `feat/mis-paquetes-tabs-42` | `4b5694c` |
| `fix-boolean-placeholder` | `7bf7114` |
| `fix-known-hosts-path` | `68e362f` |
| `fix-meta-pxb-env-vars` | `729ac0e` |
| `sync-ocupante-principal-escenarios` | `7a993b1` |

## Trabajo entregado en la sesión (2026-09-26/27)

Todo desplegado en `test.papyrus.com.co` y **verificado por Jesús** el 2026-09-27.

| Qué | Dónde está documentado | Deploy (`paquetex-live`) |
|---|---|---|
| Posición de almacenamiento al Recibir (grilla del estante, obligatoria, visible solo para staff) | `.scratch/posicion-almacenamiento/` (spec + tickets 01-03), término **Posición** en `CONTEXT.md` | `f17c396` |
| 414 grilla compacta · 415 zona azul 11-22 y bloque pegado 41-72 | `.scratch/pendientes-cliente/issues/414-*`, `415-*` | `f17c396` |
| 416 Administración → Posiciones (desactivar filas del estante) | `.scratch/pendientes-cliente/issues/416-*` | `f17c396` |
| 417 ✕ flotante en todos los modales | `.scratch/pendientes-cliente/issues/417-*` | `f17c396` |
| 418 sin autofocus en móvil (`data-enfocar`, solo escritorio) | `.scratch/pendientes-cliente/issues/418-*` | `f17c396` |
| 419 Corregir destinatario solo con apartamento | `.scratch/pendientes-cliente/issues/419-*` | `96bb562` |
| 420 ícono persona con intercambio | `.scratch/pendientes-cliente/issues/420-*` | `96bb562` |
| 421 en móvil no se muestra el ícono apagado de Corregir | `.scratch/pendientes-cliente/issues/421-*` | `96bb562` |

Migraciones nuevas: `0066_paquete_posicion` (columna `paquetes.posicion` con CHECK 11…72) y `0067_filas_estante_desactivadas`
(aplicadas en test y en la BD de desarrollo local).

Trampa encontrada y guardada en memoria ("Jinja cache en dev"): el servidor local de desarrollo (`uvicorn --reload`, :8010) deja
macros viejas en plantillas importadas por otra plantilla (ej. el modal Recibir) hasta reiniciar el proceso -- tras editar un
componente compartido, `touch CODE/src/app/web/templating.py`. No afecta a test/prod.

## Fuera de esta sesión (sin tocar)

Pendientes de otras sesiones en `.scratch/pendientes-cliente/spec.md`: **412** (el F7 se bloquea en los modales Recibir/Entregar)
sigue pendiente; **409-413** esperan confirmación en vivo.
