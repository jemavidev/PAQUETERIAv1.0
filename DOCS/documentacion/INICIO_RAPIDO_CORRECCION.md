# 🚀 Inicio Rápido - Corrección de Imágenes

## ⚡ Solución en 1 Comando

Si quieres aplicar la corrección directamente al servidor:

```bash
./deploy-static-fix-to-server.sh
```

## 📋 O usa el Menú Interactivo

Para una experiencia guiada paso a paso:

```bash
./menu-correccion-imagenes.sh
```

El menú te permite:
- 📋 Ver resumen del problema
- 🔍 Ejecutar diagnóstico
- 🧪 Probar localmente
- 🚀 Desplegar al servidor
- 📚 Ver documentación
- ❓ Obtener ayuda

## 🎯 ¿Qué hace la corrección?

Corrige la configuración de volúmenes en Docker para que las imágenes y archivos estáticos se visualicen correctamente en el servidor.

**Antes:** ❌ Imágenes no se ven (error 404)  
**Después:** ✅ Imágenes se visualizan correctamente

## 📁 Archivos Importantes

- `CORRECCION_IMAGENES_ESTATICAS.md` - Guía completa
- `RESUMEN_CORRECCION.txt` - Resumen ejecutivo
- `menu-correccion-imagenes.sh` - Menú interactivo
- `deploy-static-fix-to-server.sh` - Despliegue al servidor
- `diagnose-static-files.sh` - Diagnóstico

## ✅ Verificación Rápida

Después de aplicar la corrección:

```bash
# Verificar que las imágenes sean accesibles
curl -I http://TU_SERVIDOR:8000/static/images/favicon.png

# Debe retornar: HTTP/1.1 200 OK
```

## 🆘 ¿Necesitas Ayuda?

1. Ejecuta el menú: `./menu-correccion-imagenes.sh`
2. Selecciona opción 6 (Ayuda y troubleshooting)
3. O lee: `DOCS/SOLUCION_IMAGENES_ESTATICAS.md`

---

**¿Listo?** Ejecuta: `./menu-correccion-imagenes.sh`
