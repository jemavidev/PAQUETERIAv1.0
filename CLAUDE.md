# MATT / PaqueteX

El sistema de orquestación "AgentX" (persona, protocolo de 4-D, dispatch automático a sub-agentes,
escrituras obligatorias de memoria, más el resto del aparataje "BetterAgents" —
`.claude/agents/`, `.claude/commands/`, `.claude/protocols/`, `.claude/scripts/`, `.claude/memory/`,
`.claude/cache/`) pertenecía a un proyecto anterior, no a este. Se retiró por completo el
2026-08-04 a petición explícita del usuario — no es una desactivación reversible, no queda backup:
ese aparataje nunca fue parte de PaqueteX.

Claude Code opera en modo estándar para este proyecto: sin encabezados de identidad, sin scoring de
dispatch obligatorio, sin invocación automática de sub-agentes ni escritura automática de memoria de
sesión. Los skills reales que usa este proyecto (`grilling`, `/to-spec`, `/to-tickets`, `tdd`,
`diagnosing-bugs`, `code-review`, etc. — ver la tabla de ruteo abajo) son globales, viven en
`~/.claude/skills/`, y no tienen relación con el aparataje retirado.

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

**Gate obligatorio de primer paso: toda petición sustantiva se contrasta contra esta tabla antes de
tocar código o registrar nada.** "Sustantiva" es trabajo real — feature, bug, refactor, duda de
diseño, revisión de código — no mensajes puramente conversacionales o de coordinación, esos no pasan
por el gate. Aplica sin importar el origen: una petición que Jesús (quien opera este repo) hace
directamente, o un pedido del cliente final de PaqueteX que Jesús relaya — el gate mira la sustancia
del trabajo, no quién lo pidió.

**El calce tiene que ser con la situación concreta, no con la categoría.** Que un pedido "toque
código" o "sea un feature" en sentido amplio no alcanza — tiene que calzar con la columna "Situación"
de una fila puntual: diseño por acordar, bug no obvio, decisión de interfaz pendiente, diff grande que
amerita revisión en dos ejes, etc. Un cambio de color, texto, espaciado, o de comportamiento puntual en
una vista que ya existe **no calza con ninguna fila**, aunque sea técnicamente un "feature" — el
default es que ningún skill aplica, y ese pedido sigue el camino de siempre (ver el párrafo siguiente),
sin mencionarlo ni invocar nada.

Lo que sigue siendo situacional es la EJECUCIÓN, no la revisión — la mayoría de los pedidos chicos
(como los del tracking de arriba) no van a encontrar ningún skill aplicable, y ahí el camino sigue
siendo el de siempre: registro + implementar + verificar en vivo, sin desglosar en tickets ni triage
formal. Lo que ya no es opcional es pasar por la tabla para decidir eso — no se asume de entrada que un
pedido es "chico" sin haberlo contrastado primero.

Este gate y los skills que rutea son un mecanismo propio de este proyecto, sin relación con el
aparataje AgentX retirado (ver arriba) — no se mezclan.

**Cómo se ve en la respuesta.** Cuando la tabla arroja uno o más skills aplicables, la respuesta abre
con el plan paso a paso antes de ejecutar nada — qué skill(s), en qué orden, y para qué parte del
pedido resuelve cada uno. Ej.: "Usaré `grilling` para acordar el diseño, luego pasaré cada punto
resuelto por `/to-tickets` para desglosarlo en tickets." Cuando ningún skill aplica, el gate no se
menciona — se procede directo, sin ruido.

Columna "Quién invoca": los skills marcados **Claude** los puedo arrancar yo solo, sin que el cliente
escriba nada; los marcados **Cliente (`/comando`)** tienen `disable-model-invocation` — solo arrancan
si el cliente escribe el slash command. Para esos, mi rol es sugerir cuándo aplican y, si el cliente
quiere, dejar el terreno preparado (ej. resumir la conversación) para que el comando tenga con qué
trabajar.

**Encadenar pasos sin fricción.** Cuando un pedido resuelve varios pasos de la tabla en secuencia (ej.
`grilling` → `/to-spec` → `/to-tickets`), los pasos marcados **Claude** se encadenan solos, sin pausar
a preguntar — la respuesta ya mostró el plan completo al arrancar (ver arriba), así que avanzar al
siguiente paso Claude de esa misma secuencia no pide confirmación extra. Al llegar a un paso marcado
**Cliente** — bloqueado por `disable-model-invocation` en el propio skill, no algo que yo pueda decidir
saltarme — dejo el terreno listo automáticamente y sin que haya que pedírmelo: resumo lo resuelto hasta
ahí (ej. las respuestas dadas durante `grilling`) y entrego el comando exacto con sus argumentos ya
armados a partir de la conversación, listo para copiar y pegar. El único paso tuyo en esos casos es
pegarlo — no redactarlo.

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
