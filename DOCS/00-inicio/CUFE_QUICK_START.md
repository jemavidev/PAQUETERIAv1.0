# 🚀 CUFE - Guía Rápida de Inicio

## ⚡ Despliegue Rápido (3 pasos)

### 1️⃣ Ejecutar Migración
```bash
cd CODE
alembic upgrade head
```

### 2️⃣ Reiniciar Servicios
```bash
# Desarrollo
docker-compose restart web

# Staging
./deploy.sh staging
```

### 3️⃣ Verificar
Ir a: `https://staging.jemavi.co/invoices` → Tab **CUFE**

---

## 📖 Cómo Usar

### Agregar un CUFE

1. **Clic en "Agregar CUFE"**
2. **Pegar código CUFE** (96 caracteres)
   ```
   Ejemplo:
   9a08220827564c03bbc2c9dea3d682b50e70391b873c1ef5450af089f8eaad65909182eb584ffd1cde11c18614b27f31
   ```
3. **Clic en "Abrir en DIAN"**
   - Se abre página de DIAN automáticamente
4. **Resolver captcha** (manual)
5. **Descargar PDF** desde DIAN
6. **Subir PDF** en el modal que aparece
7. **¡Listo!** Factura importada automáticamente

---

## 🎯 Características

✅ Búsqueda en tiempo real  
✅ Filtros por estado  
✅ Estadísticas actualizadas  
✅ Copiar CUFE al portapapeles  
✅ Procesamiento automático de PDF  
✅ Vinculación con facturas  

---

## 🔍 Estados

| Estado | Descripción |
|--------|-------------|
| 🟡 Pendiente | Esperando descarga |
| 🔵 Descargando | En proceso |
| 🟢 Descargado | Listo para procesar |
| 🟣 Procesando | Extrayendo datos |
| ✅ Procesado | Factura importada |
| 🔴 Error | Falló el proceso |

---

## 🐛 Solución de Problemas

### Tabla no existe
```bash
cd CODE
alembic upgrade head
```

### CUFE inválido
- Debe tener **exactamente 96 caracteres**
- Sin espacios ni saltos de línea

### Error al procesar PDF
- Verificar que sea el PDF de la DIAN
- Revisar logs: `docker logs paqueteria-web`

---

## 📚 Documentación Completa

Ver: `IMPLEMENTACION_TAB_CUFE.md`

---

## ✅ Checklist

- [ ] Migración ejecutada
- [ ] Servicios reiniciados
- [ ] Tab CUFE visible
- [ ] Agregar CUFE funciona
- [ ] Abrir DIAN funciona
- [ ] Subir PDF funciona
- [ ] Procesamiento funciona

---

## 🎉 ¡Listo!

El sistema está configurado para gestionar CUFEs de forma semi-automática.

**Único paso manual:** Resolver captcha en la página de la DIAN.

Todo lo demás es automático. 🚀
