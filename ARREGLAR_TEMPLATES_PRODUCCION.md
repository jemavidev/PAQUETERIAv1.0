# 🚨 ARREGLO RÁPIDO: Templates no sincronizados en Producción

## ⚡ Solución Rápida (5 minutos)

### Si estás en tu máquina LOCAL:

```bash
# 1. Ejecutar script de sincronización
./sincronizar-templates.sh
```

### Si estás en el SERVIDOR de PRODUCCIÓN:

```bash
# 1. Verificar que los archivos existen
ls -lh CODE/src/templates/general/terms.html
ls -lh CODE/src/templates/general/privacy.html

# 2. Si NO existen, subirlos desde tu máquina local:
# (ejecutar esto desde tu máquina local)
scp CODE/src/templates/general/terms.html usuario@servidor:/ruta/proyecto/CODE/src/templates/general/
scp CODE/src/templates/general/privacy.html usuario@servidor:/ruta/proyecto/CODE/src/templates/general/

# 3. Reiniciar el contenedor (en el servidor)
docker compose -f docker-compose.prod.yml restart app

# 4. Esperar 10 segundos
sleep 10

# 5. Verificar que funciona
curl -I http://localhost:8000/terms
curl -I http://localhost:8000/privacy
```

## 🎯 ¿Qué pasó?

Los archivos `terms.html` y `privacy.html` fueron creados localmente pero:

1. ❌ No se subieron al servidor de producción, O
2. ❌ El contenedor no se reinició después de crearlos

## ✅ Verificación Final

Después de ejecutar los comandos, verifica:

```bash
# Debe responder "HTTP/1.1 200 OK"
curl -I http://localhost:8000/terms
curl -I http://localhost:8000/privacy
```

## 📞 URLs Finales

Una vez arreglado, las URLs estarán disponibles:

- `https://tu-dominio.com/terms`
- `https://tu-dominio.com/privacy`
- `https://tu-dominio.com/help` (con enlaces a las anteriores)

---

**Tiempo estimado:** 5 minutos  
**Dificultad:** Baja  
**Requiere:** Acceso SSH al servidor
