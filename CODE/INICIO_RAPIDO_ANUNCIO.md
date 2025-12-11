# 🚀 Inicio Rápido - Sistema de Anuncio Rápido

## ⚡ Empezar en 3 Pasos

### 1️⃣ Iniciar el Servidor
```bash
cd CODE
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 2️⃣ Acceder a la Vista
Abrir en el navegador:
```
http://localhost:8000/announce-quick
```

### 3️⃣ Probar el Sistema
1. Ingresar un número de teléfono de un cliente existente
2. Esperar a que aparezca el nombre del cliente
3. Aceptar términos y condiciones
4. Hacer clic en "Anunciar Paquete"
5. Ver el modal con los códigos generados

---

## 🧪 Ejecutar Pruebas

```bash
cd CODE
python scripts/testing/test_anuncio_rapido.py
```

**Nota:** Asegúrate de tener un cliente con teléfono `+573001234567` o modifica el script.

---

## 📋 Requisitos Previos

- ✅ Python 3.10+
- ✅ Servidor corriendo
- ✅ Base de datos accesible
- ✅ Al menos un cliente registrado en la BD

---

## 🔍 Verificar que Todo Funciona

### Test 1: Buscar Cliente
```bash
curl "http://localhost:8000/api/customers/search-by-phone?phone=+573001234567"
```

**Respuesta esperada:**
```json
{
  "id": "...",
  "full_name": "JUAN PEREZ",
  "phone": "+573001234567",
  ...
}
```

### Test 2: Crear Anuncio
```bash
curl -X POST "http://localhost:8000/api/announcements/quick" \
  -H "Content-Type: application/json" \
  -d '{"customer_phone": "+573001234567"}'
```

**Respuesta esperada:**
```json
{
  "success": true,
  "announcement": {
    "guide_number": "TEMP-A3B7C9",
    "tracking_code": "X7Y2",
    ...
  }
}
```

---

## 🐛 Problemas Comunes

### Error: "Cliente no encontrado"
**Solución:** Crear un cliente primero usando `/announce` o la interfaz de administración.

### Error: "Servidor no responde"
**Solución:** Verificar que el servidor esté corriendo en el puerto 8000.

### Error: "Base de datos no accesible"
**Solución:** Verificar la configuración de la base de datos en `.env`.

---

## 📚 Documentación Completa

- **Guía de Usuario:** `CODE/ANUNCIO_RAPIDO_README.md`
- **Documentación Técnica:** `CODE/docs/ANUNCIO_RAPIDO.md`
- **Resumen de Implementación:** `CODE/RESUMEN_IMPLEMENTACION.md`

---

## ✅ Checklist Rápido

- [ ] Servidor iniciado
- [ ] Vista accesible en `/announce-quick`
- [ ] Cliente de prueba creado
- [ ] Búsqueda de cliente funciona
- [ ] Anuncio se crea correctamente
- [ ] Modal de éxito se muestra
- [ ] SMS/Email se envían (opcional)

---

## 🎯 URLs Importantes

| Entorno | URL |
|---------|-----|
| **Local** | http://localhost:8000/announce-quick |
| **Staging** | https://staging.jemavi.co/announce-quick |
| **Producción** | https://jemavi.co/announce-quick |

---

## 💡 Tip

Para una experiencia óptima, usa el sistema con clientes que ya tengan paquetes anunciados previamente. Esto demuestra la velocidad y eficiencia del anuncio rápido.

---

**¡Listo para usar! 🎉**
