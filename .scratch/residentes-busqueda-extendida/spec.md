# Spec — Residentes: búsqueda extendida (Grupo 17, Ronda 2)

**Fuente:** `.scratch/ajustes-post-referencia-funcional/REQUERIMIENTOS.md`, Grupo 17.

## Qué cambia

`/residentes` (buscador de staff) amplía sus criterios de coincidencia, todos
combinados con OR sobre el mismo término de búsqueda (`_buscar_residentes`
en `customers_manage.py`):

1. Teléfono exacto de la Persona (comportamiento de siempre).
2. Nombre de la Persona (comportamiento de siempre).
3. **Nuevo:** Torre o Apartamento de su unidad (`ilike` sobre `Apartamento`,
   join vía `Persona.apartamento_actual_id`).
4. **Nuevo:** Nombre o teléfono de su segundo contacto (`Persona.
   segundo_contacto`, campo de texto libre — cubre ambos casos con el mismo
   `ilike`).
5. **Nuevo:** Nombre de cualquier Ocupante de su unidad, con o sin teléfono
   propio — un match resuelve a la Persona **principal** de ese Apartamento
   (los Ocupantes sin teléfono no tienen ficha propia).

Resultados únicos por `Persona.id` (un mismo residente no aparece duplicado
aunque varios criterios coincidan a la vez).

## Nota sobre "teléfono de Ocupante"

Un Ocupante **con** teléfono propio ya es, por diseño (`ocupante_service.
agregar_ocupante`), una `Persona` completa con su propia ficha — buscar su
teléfono exacto ya funcionaba con el criterio 1 sin cambios. Lo nuevo es que
ahora también se le puede encontrar por **nombre** vía el criterio 5, igual
que a un Ocupante sin teléfono.

## Fuera de alcance

- No se agrega un campo de búsqueda separado para Conjunto (la nota original
  solo pedía torre/apartamento) — se puede ampliar después si hace falta.
- No cambia la ficha (`/residentes/{id}`) en sí, solo el buscador.
