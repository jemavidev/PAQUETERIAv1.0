# 01 — `/announce` completo: apartamento + residentes (Ocupantes) + anunciar

**Qué construir:** `/announce` (staff) reemplaza el formulario de declarar-unidad-en-lote por uno con 3 bloques: Apartamento (opcional en bloque), Residentes de la unidad (filas dinámicas, teléfono ahora opcional por fila, usando la entidad Ocupante), y Anunciar un paquete (opcional, con más datos que `/anunciar`).

**Bloqueado por:** Ninguno — Grupo 1 (Anunciar simplificado) y la entidad Ocupante ya están implementados.

**Estado:** ready-for-agent

- [ ] Bloque Apartamento: Conjunto/Torre/Apartamento, los 3 vacíos o los 3 llenos (error si solo alguno).
- [ ] Bloque Residentes: filas dinámicas Nombre + Teléfono (Teléfono opcional por fila). Cada fila con datos llama `agregar_ocupante`. El primer residente de una unidad SIN Ocupantes previos debe tener teléfono (mensaje de error claro si no).
- [ ] Cada fila de residente CON teléfono también actualiza el `apartamento_actual` de su Persona (`set_apartamento_actual`) — sincroniza Ocupante y el mecanismo existente.
- [ ] Bloque Anunciar (opcional): Teléfono, Nombre, Teléfono de notificación (si se deja vacío, usa el mismo teléfono). Llama a `announce(...)` con `Destinatario.declarado_por_cliente`, usando el Apartamento del bloque 1 como override si se llenó.
- [ ] Declarar solo la unidad sin anunciar ningún paquete es un caso válido (bloque Anunciar puede quedar vacío).
- [ ] `tests/data_model/test_declarar_unidad.py` extendido con los casos de residentes con/sin teléfono y sincronización de `apartamento_actual`.
- [ ] Tests web de `/announce` actualizados/nuevos para los 3 bloques y sus validaciones.
- [ ] Suite completa (`pytest`) pasa.
