# 147 — `/residentes` tab Dirección: mismo picker de Apartamento que `/paquetes`/`/announce`

**Pedido original:** "arréglalo para que la lógica del flujo de estas vistas [/paquetes,
/announce, /consultar] esté alineada con la lógica de la vista de /residentes... implementa esto
/paquetes + /announce (referencia) en /residentes, quita lo que no esté acorde a la referencia
para el manejo y gestión de apartamentos" -- tras un análisis previo que encontró que `/residentes`
tenía su propio picker Torre→Piso→Apartamento (JS duplicado), mientras `/paquetes` ("Asignar
apartamento"/Recibir) y `/announce` (modal Recibir compartido) ya usaban un componente unificado
con un flujo distinto (Apartamento→Torre) y trato informativo (no bloqueante) de unidades ocupadas.

**Status:** implementado

## Qué cambió

- Tab Dirección (`customers_manage/detail.html`) pasa a usar `components/_picker_apartamento.html`
  + el JS de `recursos_recibir()` -- mismo flujo Apto→Torre que la referencia, en vez del
  Torre→Piso→Apto propio (~130 líneas de JS duplicado, eliminadas).
- El bloqueo de unidades ocupadas en el cliente (botones deshabilitados, ticket 13) se retira --
  ahora es informativo (nombres reales de quién vive ahí), "mismo criterio del resto de la app"
  tal como dice el propio comentario del componente compartido. El bloqueo real de negocio se
  mantiene intacto **server-side** (`customers_manage_asignar_apartamento` sigue rechazando un
  POST directo a una unidad ocupada, sin excepción).
- Fuente de datos: `apartamentos_ocupados()` (función propia del dominio, solo para este picker,
  **eliminada** por quedar sin uso) → `residentes_por_torre_apartamento()`, la misma que ya usan
  `/paquetes` y `/announce`.
- Extensión del componente compartido: `torre_inicial`/`apartamento_inicial` (nuevo, opcional) --
  Dirección necesita precargar una asignación YA existente, algo que "Asignar apartamento" nunca
  necesitó (solo aparece cuando el paquete no tiene dirección todavía). Cero cambios de
  comportamiento para los callers existentes.
- Toggle de modales: pasa del script simple agregado en [[145]] al delegado de
  `recursos_recibir()` (mismo que usa `/paquetes`) -- cubre los mismos modales, sin dos listeners
  compitiendo.

## Verificación

- Suite completa: 1024/1024 (1027 antes -3 por los tests de `apartamentos_ocupados()` eliminada).
- Reproducido en vivo contra `localhost:8010`: precarga correcta de una asignación existente
  (Torre/Apto + resumen con nombres reales), picker en blanco para un residente sin apartamento,
  `/paquetes` y `/announce` sin cambios de comportamiento.
- Detectado y corregido en el camino un problema del entorno (no del código): el `uvicorn
  --reload` local llevaba horas sin recargar Python (los templates sí, lo que casi hace reportar
  un bug falso) -- reiniciado y re-verificado todo.
