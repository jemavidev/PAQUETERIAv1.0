# 224 — `/residentes` tab Residentes: igualar a `/mis-datos` + navegar entre fichas por nombre

**Pedido original (cliente):** "sí, iguálalo con todos sus nombres y demás.
Adicional necesito que al hacer click en el nombre de cualquiera de los
residentes pueda ir directo al tab de residentes de este usuario, de esta
forma poder cambiar o no datos aquí en caso que sea el residente principal
o el staff, la idea de esto es poder tener una vista unificada del mismo
feature y que se pueda interactuar entre los diferentes residentes, dime si
es posible." (seguimiento de la comparación pedida entre
`/mis-datos` y `/residentes`, tab Residentes).

**Status:** implementado

## Alcance confirmado con el cliente

- Igualar `/residentes`: chips ícono+palabra (Confirmar/Rechazar-Eliminar/
  Principal/✕Teléfono/✕WhatsApp), modal para Confirmar/Rechazar-Eliminar en
  `/mis-datos` (para que las dos vistas usen el mismo mecanismo, no solo
  `/residentes`), sugerir canal faltante (+Teléfono/+WhatsApp) en
  `/residentes`, tarjeta del Principal resaltada en `/residentes`.
- Navegación por nombre: **solo tiene sentido del lado staff** -- un cliente
  no tiene una ruta para ver la ficha de OTRO residente (su sesión ES su
  propia identidad, `/mis-datos` no tiene equivalente a
  `/residentes/{id}`); construir eso violaría además la regla ya existente
  ("los residentes simples no pueden modificar la información de otros").
  En `/residentes`, cada nombre de Ocupante con `persona_id` propio enlaza a
  `/residentes/{ese persona_id}?tab=residentes` -- mismo mecanismo
  `?tab=` que ya usa el link de Torre/Apto (issue 100/172).
