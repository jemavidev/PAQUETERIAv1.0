# MATT / PaqueteX

El sistema de orquestación "AgentX" (persona, protocolo de 4-D, dispatch automático a sub-agentes,
escrituras obligatorias de memoria) fue desactivado a petición explícita del usuario el 2026-07-29.

Claude Code debe operar en modo estándar para este proyecto: sin encabezados de identidad, sin
scoring de dispatch obligatorio, sin invocación automática de sub-agentes ni escritura automática
en `.claude/memory/`. Los archivos de memoria existentes (`decision-log.json`, `progress.json`,
`patterns.json`, `active-context.json`) se conservan como historial de referencia del proyecto,
pero ya no se actualizan de forma automática — solo si el usuario lo pide explícitamente.

El contenido original de AgentX quedó archivado en `.claude/archive/CLAUDE.md.agentx-2026-07-29.bak`
por si se quiere consultar o restaurar más adelante.

## Agent skills

### Tracking de pedidos (obligatorio, liviano — no es AgentX)

El 2026-08-01 se detectó que pedidos puntuales del cliente sobre vistas ya desplegadas (retoques de
texto, estilo, comportamiento) se estaban perdiendo — no quedaban en ningún archivo, solo en la
memoria de la conversación, así que una compactación o una sesión nueva los borraba sin dejar rastro.

Regla: **todo pedido del cliente, sin importar el tamaño, se registra en `.scratch/pendientes-cliente/
issues/<NN>-<slug>.md` ANTES de tocar código**, usando el mismo formato que usa `to-tickets` en el
resto del repo (ver `docs/agents/issue-tracker.md`). `Status:` pasa por `pendiente` →
`implementado` → `verificado` — solo se considera cerrado tras confirmarlo desplegado en
`test.papyrus.com.co` (o el entorno que aplique). El índice vive en
`.scratch/pendientes-cliente/spec.md`.

Esto es deliberadamente más liviano que el resto del pipeline de skills (sin triage formal, sin
romper el trabajo en tickets vertical-slice) — es solo un log escrito para no depender de memoria
conversacional. Para trabajo grande (una vista nueva, un refactor, cualquier cosa que amerite
desglosarse) se sigue usando `/to-spec` → `/to-tickets`, que el cliente invoca directamente.

### Ruteo por tipo de pedido

**Gate obligatorio de primer paso: toda petición del cliente se contrasta contra esta tabla antes de
tocar código o registrar nada.** Lo que sigue siendo situacional es la EJECUCIÓN, no la revisión — la
mayoría de los pedidos chicos (como los del tracking de arriba) no van a encontrar ningún skill
aplicable, y ahí el camino sigue siendo el de siempre: registro + implementar + verificar en vivo, sin
desglosar en tickets ni triage formal. Lo que ya no es opcional es pasar por la tabla para decidir eso
— no se asume de entrada que un pedido es "chico" sin haberlo contrastado primero.

Columna "Quién invoca": los skills marcados **Claude** los puedo arrancar yo solo, sin que el cliente
escriba nada; los marcados **Cliente (`/comando`)** tienen `disable-model-invocation` — solo arrancan
si el cliente escribe el slash command. Para esos, mi rol es sugerir cuándo aplican y, si el cliente
quiere, dejar el terreno preparado (ej. resumir la conversación) para que el comando tenga con qué
trabajar.

| Situación | Skill | Quién invoca |
|---|---|---|
| Pantalla o feature nueva desde cero, hay que acordar diseño | `grilling` para interview → `/to-spec` para formalizar lo acordado → `/to-tickets` para desglosar | Claude arranca `grilling`; cliente invoca `/to-spec` y `/to-tickets` |
| Igual, pero además quieres que queden ADR/glosario del dominio documentados sobre la marcha | `/grill-with-docs` en vez de `grilling` | Cliente |
| Algo está roto, lanza error, o va lento sin explicación | `diagnosing-bugs` | Claude |
| Duda de diseño de un módulo: interfaz, dónde va una costura, cómo hacerlo más testeable | `codebase-design` | Claude |
| Escaneo general del código buscando dónde profundizar o refactorizar, sin un punto de partida claro | `/improve-codebase-architecture` | Cliente |
| No estás seguro si un modelo de estados, una lógica, o un look de UI se siente bien antes de comprometerte a implementarlo | `prototype` | Claude |
| Investigar algo contra fuentes primarias (una librería, una API, un proveedor externo) | `research` | Claude |
| Revisar un conjunto de cambios antes de darlos por buenos, en dos ejes (cumple el estándar del repo / cumple lo que se pidió) | `code-review` | Claude |
| Construir algo con lógica nueva y delicada donde vale la pena fijar el comportamiento con tests primero | `tdd` | Claude |
| Conflicto de merge/rebase en curso | `resolving-merge-conflicts` | Claude |
| Trabajo tan grande que no cabe en una sola sesión (ej. terminar TODO el recorrido pantalla por pantalla) | `/wayfinder` | Cliente |
| Issue o PR externo que hay que clasificar antes de tocarlo | `/triage` | Cliente |
| No tienes claro qué skill aplica | `/ask-matt` | Cliente |

### Issue tracker

Tracker local en markdown bajo `.scratch/<feature>/`. Ver `docs/agents/issue-tracker.md`.

### Domain docs

Layout single-context (`CONTEXT.md` + `docs/adr/` en la raíz). Ver `docs/agents/domain.md`.
