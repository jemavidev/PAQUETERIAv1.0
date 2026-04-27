# 🤖 BetterAgentX en PAQUETEX

## ¿Qué es BetterAgentX?

BetterAgentX es un sistema inteligente de agentes especializados integrado en tu proyecto PAQUETEX. Proporciona 13 agentes expertos que te ayudan en diferentes aspectos del desarrollo.

## 🚀 Inicialización

### Primera vez

```bash
./init-betteragentx.sh
```

Este script:
- ✅ Crea enlaces simbólicos a los agentes de BetterAgentX
- ✅ Inicializa el sistema de memoria
- ✅ Configura el entorno de Kiro
- ✅ No duplica archivos (usa symlinks)

### Verificar instalación

```bash
ls -la .kiro/steering/
ls -la .agents/skills/
```

Deberías ver enlaces simbólicos a BetterAgentX.

## 🤖 Agentes Disponibles

### AgentX - Orquestador Central
El cerebro que analiza tu solicitud y la enruta al agente apropiado.

```
@agentx "Necesito diseñar un sistema de autenticación"
```

### Agentes Especializados

| Agente | Uso | Ejemplo |
|--------|-----|---------|
| **@architect** | Diseño de sistemas | `@architect "Diseña arquitectura de microservicios"` |
| **@coder** | Implementación de código | `@coder "Implementa autenticación JWT en Flask"` |
| **@critic** | Análisis crítico | `@critic "Revisa esta decisión técnica"` |
| **@security** | Auditoría de seguridad | `@security "Audita este código por vulnerabilidades"` |
| **@tester** | Testing y QA | `@tester "Crea estrategia de testing para API"` |
| **@ux-designer** | Diseño UI/UX | `@ux-designer "Mejora la interfaz de facturas"` |
| **@writer** | Documentación | `@writer "Documenta esta API REST"` |
| **@teacher** | Explicaciones | `@teacher "Explica cómo funciona Flask Blueprints"` |
| **@product-manager** | Gestión de producto | `@product-manager "Prioriza estas features"` |
| **@devops** | CI/CD e infraestructura | `@devops "Configura pipeline de deployment"` |
| **@data-scientist** | Análisis de datos | `@data-scientist "Analiza patrones en facturas"` |
| **@researcher** | Investigación técnica | `@researcher "Compara frameworks de PDF parsing"` |

## 💾 Sistema de Memoria

BetterAgentX mantiene memoria persistente de tu proyecto en `.kiro/memory/`:

### Archivos de Memoria

- **`active-context.md`** - Contexto actual del proyecto
- **`decision-log.md`** - Decisiones técnicas (ADR)
- **`progress.md`** - Seguimiento de tareas
- **`patterns.md`** - Patrones reutilizables

### Gestión Automática

AgentX documenta automáticamente:
- ✅ Decisiones técnicas importantes
- ✅ Tareas completadas
- ✅ Patrones identificados
- ✅ Cambios de contexto

## 📖 Ejemplos de Uso

### Ejemplo 1: Desarrollo de Feature

```bash
# AgentX analiza y enruta automáticamente
@agentx "Necesito agregar autenticación JWT a la API"

# AgentX detecta que necesitas:
# - Architect para diseño
# - Security para revisión
# - Coder para implementación
# - Tester para pruebas
```

### Ejemplo 2: Revisión de Código

```bash
@agentx "Revisa este código por problemas de seguridad"

# AgentX enruta a Security
# Security audita y sugiere mejoras
# AgentX documenta hallazgos en memoria
```

### Ejemplo 3: Uso Directo de Agente

```bash
# Si sabes exactamente qué agente necesitas
@coder "Refactoriza el servicio de facturas para mejor performance"
@security "Audita el endpoint de login"
@writer "Documenta el módulo de proveedores"
```

## 🎯 Workflows Comunes

### Nuevo Feature
1. `@agentx "Quiero implementar [feature]"` - Análisis y planificación
2. `@architect` - Diseño de arquitectura
3. `@coder` - Implementación
4. `@tester` - Estrategia de testing
5. `@writer` - Documentación

### Bug Fix
1. `@agentx "Tengo un bug en [módulo]"` - Análisis
2. `@critic` - Análisis de causa raíz
3. `@coder` - Fix
4. `@tester` - Tests de regresión

### Refactoring
1. `@critic` - Identificar problemas
2. `@architect` - Proponer mejoras
3. `@coder` - Implementar refactor
4. `@tester` - Validar cambios

## 🔧 Configuración

### Personalizar Agentes

Edita los archivos en `.kiro/steering/agents/` para personalizar el comportamiento de cada agente.

### Configuración del Sistema

```json
// .kiro/settings/betteragents.json
{
  "agents": {
    "enabled": true,
    "default_agent": "agentx"
  },
  "memory": {
    "auto_save": true,
    "sync_interval": 300
  }
}
```

## 🎨 Skills Integrados

BetterAgentX incluye skills especializados en `.agents/skills/`:

- **ui-ux-pro-max** - Diseño UI/UX avanzado con datos de componentes, colores, tipografía

Para ver todos los skills disponibles:
```bash
ls -la .agents/skills/
```

## 📁 Estructura de Archivos

```
.
├── .kiro/
│   ├── steering/
│   │   ├── agents/          → Agentes especializados (symlink)
│   │   ├── agentx/          → Orquestador (symlink)
│   │   └── _common/         → Configuración común (symlink)
│   ├── memory/
│   │   ├── active-context.md
│   │   ├── decision-log.md
│   │   ├── progress.md
│   │   └── patterns.md
│   └── settings/
│       ├── betteragents.json
│       └── agent-skills.json
├── .agents/
│   └── skills/              → Skills especializados (symlink)
├── BetterAgentX/            → Subproyecto original
└── init-betteragentx.sh     → Script de inicialización
```

## 🔄 Actualización

Para actualizar BetterAgentX:

```bash
cd BetterAgentX
git pull origin main
cd ..
# Los enlaces simbólicos se actualizan automáticamente
```

## 🐛 Troubleshooting

### Los agentes no aparecen

```bash
# Verifica los enlaces simbólicos
ls -la .kiro/steering/

# Re-inicializa si es necesario
./init-betteragentx.sh
```

### Memoria no se guarda

```bash
# Verifica permisos
chmod -R u+w .kiro/memory/

# Verifica que los archivos existen
ls -la .kiro/memory/
```

### Conflictos con configuración existente

El script hace backup automático de archivos existentes con timestamp:
```
archivo.backup.20260213_143022
```

## 📚 Documentación Adicional

- [BetterAgentX README](BetterAgentX/README.md)
- [Guía de Inicio](BetterAgentX/docs/guides/getting-started.md)
- [Sistema de Agentes](BetterAgentX/docs/agents/README.md)
- [Workflows](BetterAgentX/docs/guides/workflows.md)

## 💡 Tips

1. **Usa @agentx primero** - Deja que el orquestador decida el mejor agente
2. **Revisa la memoria** - Consulta `.kiro/memory/` para ver el contexto
3. **Combina agentes** - Usa múltiples agentes en secuencia para tareas complejas
4. **Personaliza** - Ajusta los agentes en `.kiro/steering/agents/` según tus necesidades

## 🤝 Soporte

- 📖 [Documentación completa](BetterAgentX/docs/)
- 🐛 [Reportar Bug](https://github.com/jemavidev/BetterAgentX/issues)
- 💡 [Solicitar Feature](https://github.com/jemavidev/BetterAgentX/issues)

---

**¡Listo para usar BetterAgentX en PAQUETEX! 🚀**
