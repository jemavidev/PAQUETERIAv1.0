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
