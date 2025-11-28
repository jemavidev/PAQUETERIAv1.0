# 🚀 STAGING CONFIGURADO - LEE ESTO PRIMERO

## ✅ TODO ESTÁ LISTO

He configurado completamente el entorno de **staging** para tu aplicación. Todo está diseñado para **NO tener conflictos** con producción.

---

## 📋 LO QUE NECESITAS SABER

### ✅ Configuración Completada:
- **Servidor:** 18.214.124.14 (mismo que producción)
- **Dominio:** staging.jemavi.co
- **Puertos:** 8080 (HTTP), 8443 (HTTPS)
- **Ruta:** /home/ubuntu/paqueteria-staging
- **Rama Git:** staging (nueva)
- **Sin conflictos:** Puertos, contenedores, rutas, todo separado

### ⚠️ Importante:
- Staging comparte la **misma base de datos** con producción
- Solo para **cambios visuales/estéticos** (CSS, HTML, JS)
- **NO ejecutar migraciones** en staging
- **NO hacer backups** desde staging

---

## 🎯 EMPEZAR EN 3 PASOS

### 1️⃣ Crear rama staging (2 minutos)
```bash
git checkout main
git pull origin main
git checkout -b staging
git push -u origin staging
```

### 2️⃣ Configurar servidor (5 minutos)
Abre el archivo: **SETUP_STAGING_COMANDOS.md**
Copia y pega los comandos del PASO 2 y PASO 3

### 3️⃣ Hacer deploy (2 minutos)
```bash
./deploy.sh --env staging --deploy
```

**Total: 10 minutos** ⏱️

---

## 📁 ARCHIVOS IMPORTANTES

### 🔥 Para empezar rápido:
1. **SETUP_STAGING_COMANDOS.md** ← **EMPIEZA AQUÍ**
   - Comandos listos para copiar y pegar
   - Paso a paso simple

### 📚 Para entender todo:
2. **STAGING_CONFIGURADO.md**
   - Resumen completo de la configuración
   - Comparación producción vs staging
   - Garantías de no conflicto

3. **.deploy/docs/SETUP_STAGING.md**
   - Documentación técnica completa
   - Troubleshooting detallado
   - Comandos útiles

### 🔧 Archivos técnicos creados:
- `docker-compose.staging.yml` - Stack de staging
- `.deploy/config/staging.conf` - Configuración de deploy
- `.deploy/templates/nginx-staging.conf` - Configuración de Nginx
- `scripts/setup-staging.sh` - Script de setup automático

---

## 🎯 FLUJO DE TRABAJO DIARIO

Una vez configurado, tu flujo será:

```bash
# 1. Hacer cambios visuales (CSS, HTML, JS)
git checkout staging
git add .
git commit -m "Cambios estéticos: descripción"
git push origin staging

# 2. Deploy a staging
./deploy.sh --env staging --deploy

# 3. Ver en navegador
# http://staging.jemavi.co:8080

# 4. Si todo OK, llevar a producción
git checkout main
git merge staging
git push origin main
./deploy.sh --env papyrus --deploy
```

---

## ✅ GARANTÍAS DE NO CONFLICTO

| Aspecto | Producción | Staging | Conflicto |
|---------|------------|---------|-----------|
| Puerto HTTP | 80 | 8080 | ❌ NO |
| Puerto HTTPS | 443 | 8443 | ❌ NO |
| Puerto App | 8000 | 8001 | ❌ NO |
| Puerto Redis | 6379 | 6380 | ❌ NO |
| Ruta | /home/ubuntu/paqueteria | /home/ubuntu/paqueteria-staging | ❌ NO |
| Contenedores | paqueteria_v1_prod_* | paqueteria_staging_* | ❌ NO |
| Red Docker | paqueteria_v1_prod_network | paqueteria_staging_network | ❌ NO |
| Base de Datos | RDS paqueteria_v4 | RDS paqueteria_v4 | ⚠️ COMPARTIDA |

**Conclusión:** Ambos entornos pueden correr simultáneamente sin problemas.

---

## 🆘 SI TIENES DUDAS

### Pregunta: ¿Necesito crear una nueva base de datos?
**Respuesta:** NO. Staging usa la misma BD porque solo harás cambios visuales.

### Pregunta: ¿Puedo ejecutar migraciones en staging?
**Respuesta:** NO. Afectarías la BD de producción.

### Pregunta: ¿Staging afectará a producción?
**Respuesta:** NO. Todo está separado excepto la BD (que no modificarás).

### Pregunta: ¿Qué pasa si algo falla?
**Respuesta:** Producción sigue funcionando. Staging es independiente.

### Pregunta: ¿Necesito SSL?
**Respuesta:** Opcional. Puedes configurarlo después con Certbot.

---

## 📞 INFORMACIÓN QUE NECESITAS

Antes de empezar el PASO 2, necesitas:

### 1. URL de tu repositorio GitHub
Ve a GitHub → Tu repo → Botón "Code" → Copia la URL HTTPS

Ejemplo: `https://github.com/usuario/paqueteria.git`

### 2. Verificar DNS (opcional)
```bash
nslookup staging.jemavi.co
```
Debe apuntar a: `18.214.124.14`

### 3. Acceso SSH
```bash
ssh papyrus
```
Debe conectar sin pedir contraseña.

---

## 🎉 SIGUIENTE PASO

**Abre:** `SETUP_STAGING_COMANDOS.md`

Ahí encontrarás todos los comandos listos para copiar y pegar.

---

## 📊 RESUMEN TÉCNICO

**Archivos creados:**
- ✅ docker-compose.staging.yml
- ✅ .deploy/config/staging.conf (actualizado)
- ✅ .deploy/templates/nginx-staging.conf
- ✅ .deploy/docs/SETUP_STAGING.md
- ✅ scripts/setup-staging.sh
- ✅ SETUP_STAGING_COMANDOS.md
- ✅ STAGING_CONFIGURADO.md
- ✅ LEEME_PRIMERO_STAGING.md (este archivo)

**Servicios en staging:**
- ✅ App (FastAPI) - Puerto 8001
- ✅ Redis - Puerto 6380
- ❌ Celery (no necesario)
- ❌ Prometheus/Grafana (no necesario)

**Tiempo estimado de setup:** 10 minutos

---

## ✅ CHECKLIST

- [ ] Leer este archivo (LEEME_PRIMERO_STAGING.md)
- [ ] Abrir SETUP_STAGING_COMANDOS.md
- [ ] Ejecutar PASO 1: Crear rama staging
- [ ] Ejecutar PASO 2: Clonar en servidor
- [ ] Ejecutar PASO 3: Configurar Nginx
- [ ] Ejecutar PASO 4: Primer deploy
- [ ] Ejecutar PASO 5: Verificar
- [ ] (Opcional) PASO 6: Configurar SSL

---

**¿Listo para empezar?**

👉 Abre: **SETUP_STAGING_COMANDOS.md**

---

**Fecha:** 2024-11-28  
**Versión:** PAQUETERÍA v1.0  
**Servidor:** AWS Lightsail (18.214.124.14)  
**Configurado por:** Kiro AI Assistant
