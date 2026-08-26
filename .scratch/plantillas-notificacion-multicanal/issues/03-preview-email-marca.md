# 03 — Vista previa en vivo del correo con marca (logo + enlaces)

**Qué construir:** dentro de la pestaña Email (ticket 02), un preview que muestra el asunto y el cuerpo ya resueltos con datos de ejemplo (nombre, código de acceso, motivo según el evento) — no placeholders crudos — envueltos en un layout de marca fijo (logo de Papyrus, enlaces a los sitios de la empresa). El layout vive en una función pura reutilizable (ej. `envolver_html(asunto, cuerpo_texto) -> str`) que será la misma que use el envío real de Email el día que se conecte (fuera de esta rebanada) — no se duplica el layout entre preview y envío real.

**Bloqueado por:** 02.

**Estado:** ready-for-agent

- [ ] Existe una función pura que envuelve asunto+cuerpo en el layout HTML de marca (logo de Papyrus, enlaces del sitio).
- [ ] La pestaña Email muestra un preview que refleja el texto/asunto recién escritos, con los placeholders ya resueltos usando datos de ejemplo.
- [ ] El preview incluye el logo y los enlaces esperados.
- [ ] Test de dominio: la función de envoltura incluye el asunto, el cuerpo con placeholders resueltos, y el logo/enlaces esperados (aserción sobre presencia de esos elementos, no sobre el markup exacto).
- [ ] Test web: la pestaña Email de `/administracion/notificaciones` muestra el preview con datos de ejemplo resueltos (no placeholders sin resolver).
- [ ] Suite completa (`pytest`) pasa.
