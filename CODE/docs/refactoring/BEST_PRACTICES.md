# Best Practices - Refactorización de Vistas

Estándares para refactorizar vistas en PAQUETEX.

---

## 🏗️ Estructura

```
src/templates/
├── [módulo]/
│   ├── list.html
│   ├── detail.html
│   ├── create.html
│   ├── update.html
│   └── _components/
```

---

## 💄 HTML/CSS

### Nomenclatura

- Archivos: `snake_case.html` (ej: `package_detail.html`)
- Clases CSS: `kebab-case` (ej: `.package-card`)
- IDs: `kebab-case` (ej: `id="package-123"`)
- Variables Jinja2: `snake_case` (ej: `{{ package_list }}`)

### Estructura Base

```html
<div class="container mx-auto px-4 py-6">
  <!-- Encabezado -->
  <header class="mb-6">
    <h1 class="text-3xl font-bold">{{ title }}</h1>
  </header>

  <!-- Contenido -->
  <main class="space-y-6">
    {% include 'module/_component.html' %}
  </main>
</div>
```

### Tailwind

- Usar clases de espaciado: `px-4`, `py-6`, `mb-6`
- Responsive: `sm:`, `md:`, `lg:`, `xl:`
- Dark mode: `dark:bg-gray-900`

---

## 🔧 Jinja2 / Backend

### Variables
- Singular para objetos: `package`
- Plural para listados: `packages`
- Booleanos con prefijo: `is_admin`

### Formularios

```html
<form method="POST" action="{{ url_for('create') }}" class="space-y-6">
  <div>
    <label for="name" class="block text-sm font-medium mb-1">
      Nombre
    </label>
    <input type="text" id="name" name="name" required />
  </div>
  <button type="submit" class="btn btn-primary">Guardar</button>
</form>
```

---

## ⚡ HTMX & JavaScript

### HTMX

```html
<!-- GET -->
<div hx-get="/api/items" hx-trigger="load">Cargando...</div>

<!-- POST -->
<form hx-post="/api/items" hx-target="#response">...</form>

<!-- Trigger con delay -->
<input hx-post="/search" hx-trigger="keyup delay:500ms" />
```

### Alpine.js

```html
<div x-data="{ open: false }">
  <button @click="open = !open">Toggle</button>
  <div x-show="open">Contenido</div>
</div>
```

---

## 🧪 Testing

**Checklist antes de commit:**

- [ ] HTML válido
- [ ] Clases Tailwind consistentes
- [ ] Variables Jinja2 correctas
- [ ] Testing manual completo
- [ ] Responsive verificado (desktop, tablet, mobile)
- [ ] Sin regresos en otras vistas
- [ ] Commit message descriptivo

---

## 📞 Preguntas?

Ver documentación completa en:
- [REFACTORING_PLAN.md](REFACTORING_PLAN.md)
- [VIEWS_STATUS.md](VIEWS_STATUS.md)
- [../backups/](../backups/)
