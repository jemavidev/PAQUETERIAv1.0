# 📚 Índice de Documentación - BetterAgentX en PAQUETEX

## 🎯 Inicio Rápido

¿Primera vez? Empieza aquí:

1. **[QUICKSTART-BETTERAGENTX.md](QUICKSTART-BETTERAGENTX.md)** ⚡
   - Inicialización en 3 pasos
   - Comandos esenciales
   - Workflow típico

2. **Ejecuta los scripts:**
   ```bash
   ./init-betteragentx.sh      # Inicializar
   ./verify-betteragentx.sh    # Verificar
   ```

3. **Usa en Kiro:**
   ```bash
   @agentx "Ayúdame con el proyecto"
   ```

---

## 📖 Documentación Completa

### Documentación Local (PAQUETEX)

| Archivo | Descripción | Cuándo Leer |
|---------|-------------|-------------|
| **[QUICKSTART-BETTERAGENTX.md](QUICKSTART-BETTERAGENTX.md)** | Inicio rápido en 3 pasos | Primera vez |
| **[README-BETTERAGENTX.md](README-BETTERAGENTX.md)** | Guía completa de uso | Referencia general |
| **[BETTERAGENTX-INTEGRATION.md](BETTERAGENTX-INTEGRATION.md)** | Detalles de integración | Troubleshooting |
| **[INDEX-BETTERAGENTX.md](INDEX-BETTERAGENTX.md)** | Este archivo - Índice | Navegación |

### Documentación de BetterAgentX

| Archivo | Descripción |
|---------|-------------|
| [BetterAgentX/README.md](BetterAgentX/README.md) | README principal de BetterAgentX |
| [BetterAgentX/docs/guides/getting-started.md](BetterAgentX/docs/guides/getting-started.md) | Guía de inicio |
| [BetterAgentX/docs/agents/README.md](BetterAgentX/docs/agents/README.md) | Sistema de agentes |
| [BetterAgentX/docs/guides/workflows.md](BetterAgentX/docs/guides/workflows.md) | Workflows |
| [BetterAgentX/docs/guides/skills-management.md](BetterAgentX/docs/guides/skills-management.md) | Gestión de skills |

---

## 🛠️ Scripts Disponibles

| Script | Propósito | Cuándo Usar |
|--------|-----------|-------------|
| `init-betteragentx.sh` | Inicializa BetterAgentX | Primera vez o re-inicializar |
| `verify-betteragentx.sh` | Verifica configuración | Después de inicializar o troubleshooting |

### Uso de Scripts

```bash
# Inicializar (primera vez)
./init-betteragentx.sh

# Verificar que todo está OK
./verify-betteragentx.sh

# Re-inicializar (si hay problemas)
./init-betteragentx.sh
```

---

## 🤖 Referencia de Agentes

### Orquestador

| Agente | Comando | Uso |
|--------|---------|-----|
| **AgentX** | `@agentx` | Punto de entrada principal - Enruta automáticamente |

### Agentes Core

| Agente | Comando | Especialidad |
|--------|---------|--------------|
| **Architect** | `@architect` | Diseño de sistemas y arquitectura |
| **Coder** | `@coder` | Implementación y refactorización |
| **Critic** | `@critic` | Análisis crítico y revisión |
| **Tester** | `@tester` | Testing y QA |
| **Writer** | `@writer` | Documentación técnica |
| **Researcher** | `@researcher` | Investigación tecnológica |
| **Teacher** | `@teacher` | Explicaciones y tutoriales |

### Agentes Especializados

| Agente | Comando | Especialidad |
|--------|---------|--------------|
| **DevOps** | `@devops` | CI/CD e infraestructura |
| **Security** | `@security` | Auditoría de seguridad |
| **UX Designer** | `@ux-designer` | Diseño UI/UX |
| **Data Scientist** | `@data-scientist` | Análisis de datos y ML |
| **Product Manager** | `@product-manager` | Gestión de producto |

---

## 💾 Sistema de Memoria

### Archivos de Memoria (`.kiro/memory/`)

| Archivo | Propósito | Actualización |
|---------|-----------|---------------|
| `active-context.md` | Contexto actual del proyecto | Manual/Auto |
| `decision-log.md` | Decisiones técnicas (ADR) | Manual/Auto |
| `progress.md` | Seguimiento de tareas | Manual/Auto |
| `patterns.md` | Patrones identificados | Manual/Auto |

### Cómo Usar la Memoria

```bash
# Ver contexto actual
cat .kiro/memory/active-context.md

# Ver decisiones técnicas
cat .kiro/memory/decision-log.md

# Ver progreso
cat .kiro/memory/progress.md

# Ver patrones
cat .kiro/memory/patterns.md
```

---

## 🎯 Workflows por Caso de Uso

### 1. Desarrollo de Feature

```bash
@agentx "Quiero implementar autenticación JWT"
# AgentX coordina: architect → security → coder → tester → writer
```

**Documentación:** [README-BETTERAGENTX.md#workflows](README-BETTERAGENTX.md)

### 2. Bug Fix

```bash
@agentx "Tengo un bug en el módulo de facturas"
# AgentX coordina: critic → coder → tester
```

### 3. Refactoring

```bash
@critic "Analiza el código del servicio de facturas"
@architect "Propón mejoras de arquitectura"
@coder "Implementa el refactor"
@tester "Valida los cambios"
```

### 4. Code Review

```bash
@security "Audita este código por vulnerabilidades"
@critic "Revisa esta decisión técnica"
```

### 5. Documentación

```bash
@writer "Documenta la API de facturas"
@writer "Crea un README para el módulo de proveedores"
```

---

## 🔧 Configuración

### Archivos de Configuración

| Archivo | Ubicación | Propósito |
|---------|-----------|-----------|
| `betteragents.json` | `.kiro/settings/` | Configuración general |
| `agent-skills.json` | `.kiro/settings/` | Skills por agente |
| `.betteragentx-config` | Raíz del proyecto | Config de integración |

### Personalizar Agentes

```bash
# Editar comportamiento de un agente
nano .kiro/steering/agents/coder.md

# Editar configuración general
nano .kiro/settings/betteragents.json
```

**Documentación:** [BETTERAGENTX-INTEGRATION.md#configuración](BETTERAGENTX-INTEGRATION.md)

---

## 🔄 Actualización y Mantenimiento

### Actualizar BetterAgentX

```bash
cd BetterAgentX
git pull origin main
cd ..
# Los enlaces simbólicos se actualizan automáticamente
```

### Re-inicializar

```bash
./init-betteragentx.sh
# Hace backup automático de archivos existentes
```

### Verificar Estado

```bash
./verify-betteragentx.sh
# Muestra estado completo de la integración
```

**Documentación:** [BETTERAGENTX-INTEGRATION.md#actualización](BETTERAGENTX-INTEGRATION.md)

---

## 🐛 Troubleshooting

### Problemas Comunes

| Problema | Solución | Documentación |
|----------|----------|---------------|
| Agentes no aparecen | `./verify-betteragentx.sh` → `./init-betteragentx.sh` | [BETTERAGENTX-INTEGRATION.md#troubleshooting](BETTERAGENTX-INTEGRATION.md) |
| Enlaces rotos | `./init-betteragentx.sh` | [BETTERAGENTX-INTEGRATION.md#troubleshooting](BETTERAGENTX-INTEGRATION.md) |
| Memoria no se guarda | `chmod -R u+w .kiro/memory/` | [README-BETTERAGENTX.md#troubleshooting](README-BETTERAGENTX.md) |
| Conflictos de config | Restaurar desde backup `.backup.*` | [BETTERAGENTX-INTEGRATION.md#troubleshooting](BETTERAGENTX-INTEGRATION.md) |

### Diagnóstico

```bash
# Verificación completa
./verify-betteragentx.sh

# Ver enlaces simbólicos
ls -la .kiro/steering/

# Ver agentes disponibles
ls -la .kiro/steering/agents/

# Ver skills
ls -la .agents/skills/
```

---

## 📊 Estructura del Proyecto

```
PAQUETEX v1.0/
├── BetterAgentX/                    # Subproyecto (fuente)
│   ├── .kiro/steering/
│   │   ├── agents/                  # Agentes especializados
│   │   ├── agentx/                  # Orquestador
│   │   └── _common/                 # Configuración común
│   └── .agents/skills/              # Skills
│
├── .kiro/                           # Configuración Kiro (PAQUETEX)
│   ├── steering/
│   │   ├── agents/      → symlink   # → BetterAgentX/.kiro/steering/agents/
│   │   ├── agentx/      → symlink   # → BetterAgentX/.kiro/steering/agentx/
│   │   └── _common/     → symlink   # → BetterAgentX/.kiro/steering/_common/
│   ├── memory/                      # Memoria del proyecto (local)
│   └── settings/                    # Configuración (local)
│
├── .agents/
│   └── skills/          → symlink   # → BetterAgentX/.agents/skills/
│
├── init-betteragentx.sh             # Script de inicialización
├── verify-betteragentx.sh           # Script de verificación
├── QUICKSTART-BETTERAGENTX.md       # Inicio rápido
├── README-BETTERAGENTX.md           # Guía completa
├── BETTERAGENTX-INTEGRATION.md      # Detalles de integración
└── INDEX-BETTERAGENTX.md            # Este archivo
```

**Documentación:** [BETTERAGENTX-INTEGRATION.md#estructura](BETTERAGENTX-INTEGRATION.md)

---

## 🎓 Recursos de Aprendizaje

### Para Principiantes

1. [QUICKSTART-BETTERAGENTX.md](QUICKSTART-BETTERAGENTX.md) - Empieza aquí
2. [README-BETTERAGENTX.md#ejemplos](README-BETTERAGENTX.md) - Ejemplos prácticos
3. [BetterAgentX/docs/guides/getting-started.md](BetterAgentX/docs/guides/getting-started.md) - Guía detallada

### Para Usuarios Avanzados

1. [BETTERAGENTX-INTEGRATION.md](BETTERAGENTX-INTEGRATION.md) - Integración completa
2. [BetterAgentX/docs/guides/workflows.md](BetterAgentX/docs/guides/workflows.md) - Workflows avanzados
3. [BetterAgentX/docs/guides/skills-management.md](BetterAgentX/docs/guides/skills-management.md) - Gestión de skills

---

## 💡 Tips y Best Practices

### Tips Rápidos

1. **Usa @agentx primero** - Deja que el orquestador decida el mejor agente
2. **Revisa la memoria** - Consulta `.kiro/memory/` regularmente
3. **Combina agentes** - Usa múltiples agentes en secuencia para tareas complejas
4. **Personaliza** - Ajusta los agentes según tus necesidades

### Best Practices

- Documenta decisiones importantes en `decision-log.md`
- Mantén actualizado el `active-context.md`
- Identifica y documenta patrones en `patterns.md`
- Usa el workflow apropiado para cada tipo de tarea

**Documentación:** [README-BETTERAGENTX.md#tips](README-BETTERAGENTX.md)

---

## 🔗 Enlaces Útiles

### Documentación Local

- [Inicio Rápido](QUICKSTART-BETTERAGENTX.md)
- [Guía Completa](README-BETTERAGENTX.md)
- [Integración](BETTERAGENTX-INTEGRATION.md)

### Documentación BetterAgentX

- [README Principal](BetterAgentX/README.md)
- [Guías](BetterAgentX/docs/guides/)
- [Agentes](BetterAgentX/docs/agents/)

### Repositorio

- [BetterAgentX en GitHub](https://github.com/jemavidev/BetterAgentX)

---

## ✅ Checklist de Inicio

- [ ] Leer [QUICKSTART-BETTERAGENTX.md](QUICKSTART-BETTERAGENTX.md)
- [ ] Ejecutar `./init-betteragentx.sh`
- [ ] Ejecutar `./verify-betteragentx.sh`
- [ ] Probar `@agentx "Hola"` en Kiro
- [ ] Explorar `.kiro/memory/`
- [ ] Leer [README-BETTERAGENTX.md](README-BETTERAGENTX.md)
- [ ] Probar diferentes agentes
- [ ] Personalizar configuración (opcional)

---

## 📞 Soporte

### Problemas con la Integración

1. Ejecuta `./verify-betteragentx.sh`
2. Consulta [BETTERAGENTX-INTEGRATION.md#troubleshooting](BETTERAGENTX-INTEGRATION.md)
3. Re-inicializa con `./init-betteragentx.sh`

### Problemas con BetterAgentX

- 🐛 [Reportar Bug](https://github.com/jemavidev/BetterAgentX/issues)
- 💡 [Solicitar Feature](https://github.com/jemavidev/BetterAgentX/issues)
- 💬 [Discusiones](https://github.com/jemavidev/BetterAgentX/discussions)

---

## 🎯 Próximos Pasos

1. **Inicializa:** `./init-betteragentx.sh`
2. **Verifica:** `./verify-betteragentx.sh`
3. **Usa:** `@agentx "Tu primera solicitud"`
4. **Explora:** Lee [README-BETTERAGENTX.md](README-BETTERAGENTX.md)
5. **Personaliza:** Ajusta según tus necesidades

---

**¡Bienvenido a BetterAgentX en PAQUETEX! 🚀**

**Empieza aquí:** [QUICKSTART-BETTERAGENTX.md](QUICKSTART-BETTERAGENTX.md)
