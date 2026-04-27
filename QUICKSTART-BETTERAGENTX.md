# ⚡ BetterAgentX - Inicio Rápido

## 🎯 Inicialización en 3 pasos

### 1️⃣ Ejecuta el script de inicialización

```bash
./init-betteragentx.sh
```

### 2️⃣ Verifica la instalación

```bash
ls -la .kiro/steering/agents/
```

Deberías ver enlaces simbólicos a los agentes.

### 3️⃣ ¡Empieza a usar!

```bash
# En Kiro, usa el prefijo @ para invocar agentes
@agentx "Ayúdame a mejorar el sistema de facturas"
```

## 🚀 Comandos Esenciales

### Usar el Orquestador (Recomendado)
```bash
@agentx "Tu solicitud aquí"
```
AgentX analiza y enruta automáticamente al agente correcto.

### Usar Agentes Directamente
```bash
@architect "Diseña arquitectura de microservicios"
@coder "Implementa autenticación JWT"
@security "Audita este código"
@tester "Crea tests para el módulo de facturas"
```

## 📋 Agentes Más Usados

| Agente | Cuándo Usarlo |
|--------|---------------|
| `@agentx` | No estás seguro qué agente necesitas |
| `@architect` | Diseño de sistemas, arquitectura |
| `@coder` | Escribir o refactorizar código |
| `@security` | Revisar seguridad |
| `@tester` | Crear o mejorar tests |
| `@writer` | Documentar código o APIs |

## 💾 Memoria del Proyecto

BetterAgentX guarda automáticamente:
- Decisiones técnicas en `.kiro/memory/decision-log.md`
- Progreso en `.kiro/memory/progress.md`
- Contexto en `.kiro/memory/active-context.md`
- Patrones en `.kiro/memory/patterns.md`

## 🔄 Workflow Típico

```bash
# 1. Planificación
@agentx "Quiero agregar autenticación de dos factores"

# 2. Diseño (si es necesario)
@architect "Diseña la arquitectura para 2FA"

# 3. Implementación
@coder "Implementa 2FA usando TOTP"

# 4. Seguridad
@security "Revisa la implementación de 2FA"

# 5. Testing
@tester "Crea tests para 2FA"

# 6. Documentación
@writer "Documenta cómo usar 2FA"
```

## 📚 Más Información

- [README completo](README-BETTERAGENTX.md)
- [Documentación BetterAgentX](BetterAgentX/README.md)

## 🆘 Ayuda Rápida

### ¿Los agentes no funcionan?
```bash
# Re-inicializa
./init-betteragentx.sh
```

### ¿Quieres ver todos los agentes?
```bash
ls -la .kiro/steering/agents/
```

### ¿Necesitas actualizar BetterAgentX?
```bash
cd BetterAgentX
git pull
cd ..
# Los enlaces simbólicos se actualizan automáticamente
```

---

**¡Listo! Ahora tienes 13 agentes especializados a tu disposición 🎉**
