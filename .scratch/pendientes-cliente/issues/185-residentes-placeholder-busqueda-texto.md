# 185 — `/residentes`: texto del placeholder de búsqueda

**Pedido original:** convertir "Nombre, teléfono, WhatsApp, email, torre o apt302" a "Nombre,
Teléfono, WhatsApp, Email, APT302".

**Status:** implementado

## Cambio

- `customers_manage/search.html`: `placeholder_q` actualizado -- "teléfono"/"email" capitalizados,
  "torre o " quitado, "apt302" en mayúsculas ("APT302").

## Verificación

- Cambio de texto puro, sin lógica ni CSS -- sin tests afectados (confirmado, ningún test depende
  del string exacto).
- Verificado en local (`localhost:8010`).
- Pendiente: verificar en test.papyrus.com.co tras deploy.
