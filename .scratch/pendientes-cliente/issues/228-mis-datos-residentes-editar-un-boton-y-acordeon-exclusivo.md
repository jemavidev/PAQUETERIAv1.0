# 228 — `/mis-datos` tab Residentes: "Editar" con un solo botón + acordeón exclusivo con Notificaciones

**Pedido original (cliente):** "Sería bueno que para el botón de Editar se
tenga un solo botón de guardar, necesito que también sea para todos los
cambios realizados. Adicional si estoy modificando ya sea Notificaciones o
Editar, solo uno se mantenga abierto, o el uno o el otro, para poder ir
cambiando o el uno o el otro." (seguimiento de
[[227-mis-datos-residentes-editar-unificado]]).

**Status:** implementado

## Implementación

- **Un solo botón**: nueva ruta `POST /mis-datos/ocupantes/{id}/editar`
  reemplaza los 3 forms sueltos (Nombre+Email, Teléfono, WhatsApp) del
  issue 227 -- un solo submit aplica los 4 campos. Teléfono/WhatsApp
  agregan o editan según si la Persona ya tenía ese canal (mismo criterio
  que las rutas dedicadas, que se dejaron intactas -- `/telefono`/`/whatsapp`
  siguen con su propia cobertura de tests). Cuidado real: `editar_telefono_
  ocupante`/`editar_whatsapp_ocupante` pueden re-ligar `ocupante.persona_id`
  a una Persona DISTINTA (issue 35) -- la ruta re-consulta la Persona antes
  de aplicar Nombre/Email para no escribir sobre la Persona vieja.
  "Quitar teléfono"/"Quitar WhatsApp" se quedan fuera de ese form (HTML no
  anida forms) pero dentro del mismo panel.
- **Acordeón exclusivo**: `<details name="editar-notif-{{ ocupante.id }}">`
  en los dos paneles (Editar/Notificaciones) de cada residente -- atributo
  nativo de HTML (sin JS), mismo mecanismo que ya usa
  `admin/notificaciones.html`. Único por residente (el `name` incluye
  `ocupante.id`) para que abrir uno no cierre el de OTRO residente.
