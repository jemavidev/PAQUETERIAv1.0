# 185 — `/residentes`: texto del placeholder de búsqueda

**Pedido original:** convertir "Nombre, teléfono, WhatsApp, email, torre o apt302" a "Nombre,
Teléfono, WhatsApp, Email, APT302".

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Cambio

- `customers_manage/search.html`: `placeholder_q` actualizado -- "teléfono"/"email" capitalizados,
  "torre o " quitado, "apt302" en mayúsculas ("APT302").

## Verificación

- Cambio de texto puro, sin lógica ni CSS -- sin tests afectados (confirmado, ningún test depende
  del string exacto).
- Verificado en local (`localhost:8010`).
- Pendiente: verificar en test.papyrus.com.co tras deploy.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
