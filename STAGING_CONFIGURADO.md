# ✅ STAGING CONFIGURADO - RESUMEN COMPLETO

## 🎯 LO QUE SE HA CONFIGURADO

### ✅ Archivos Creados/Modificados:

1. **docker-compose.staging.yml** ✅
   - Solo App + Redis (mínimo necesario)
   - Puerto 8001 (app)
   - Puerto 6380 (redis)
   - Sin conflictos con producción

2. **.deploy/config/staging.conf** ✅
   - Configuración completa de staging
   - SSH: 18.214.124.14
   - Rama: staging
   - Ruta: /home/ubuntu/paqueteria-staging

3. **.deploy/templates/nginx-staging.conf** ✅
   - Nginx para staging
   - Puertos: 8080 (HTTP) y 8443 (HTTPS)
   - Dominio: staging.jemavi.co

4. **SETUP_STAGING_COMANDOS.md** ✅
   - Guía paso a paso con comandos
   - Copia y pega directo

5. **.deploy/docs/SETUP_STAGING.md** ✅
   - Documentación completa
   - Troubleshooting incluido

6. **scripts/setup-staging.sh** ✅
   - Script automatizado (opcional)

---

## 🔍 COMPARACIÓN: PRODUCCIÓN vs STAGING

| Aspecto | PRODUCCIÓN | STAGING |
|---------|------------|---------|
| **Servidor** | 18.214.124.14 | 18.214.124.14 (mismo) |
| **Dominio** | paquetex.papyrus.com.co | staging.jemavi.co |
| **Ruta** | /home/ubuntu/paqueteria | /home/ubuntu/paqueteria-staging |
| **Rama Git** | main | staging |
| **Puerto HTTP** | 80 | 8080 |
| **Puerto HTTPS** | 443 | 8443 |
| **Puerto App** | 8000 | 8001 |
| **Puerto Redis** | 6379 | 6380 |
| **Base de Datos** | RDS paqueteria_v4 | RDS paqueteria_v4 (compartida) |
| **Contenedores** | paqueteria_v1_prod_* | paqueteria_staging_* |
| **Red Docker** | paqueteria_v1_prod_network | paqueteria_staging_network |
| **Servicios** | App, Redis, Celery, Prometheus, Grafana | App, Redis (solo) |
| **Migraciones** | Habilitadas | Deshabilitadas |
| **Backups** | Deshabilitados (RDS) | Deshabilitados |
| **SSL** | Certbot (activo) | Certbot (a configurar) |

---

## 🚀 CÓMO EMPEZAR (3 PASOS SIMPLES)

### 1️⃣ Crear rama staging (local):
```bash
cd "/home/stk/Insync/dispapyrussas@gmail.com/Google Drive/PAPYRUS/EL CLUB/SERVICIO DE PAQUETERIA/PAQUETERIA v1.0"
git checkout main
git pull origin main
git checkout -b staging
git push -u origin staging
```

### 2️⃣ Configurar servidor:
```bash
ssh papyrus
cd /home/ubuntu
git clone TU_URL_GITHUB paqueteria-staging
cd paqueteria-staging
git checkout staging
sudo cp .deploy/templates/nginx-staging.conf /etc/nginx/sites-available/staging
sudo ln -s /etc/nginx/sites-available/staging /etc/nginx/sites-enabled/staging
sudo nginx -t && sudo systemctl reload nginx
sudo ufw allow 8080/tcp
sudo ufw allow 8443/tcp
exit
```

### 3️⃣ Deploy (local):
```bash
./deploy.sh --env staging --deploy
```

---

## ✅ GARANTÍAS DE NO CONFLICTO

### ✅ Puertos Separados:
- Producción: 80, 443, 8000, 6379
- Staging: 8080, 8443, 8001, 6380
- **Sin solapamiento**

### ✅ Rutas Separadas:
- Producción: `/home/ubuntu/paqueteria`
- Staging: `/home/ubuntu/paqueteria-staging`
- **Código completamente separado**

### ✅ Contenedores Separados:
- Producción: `paqueteria_v1_prod_*`
- Staging: `paqueteria_staging_*`
- **Sin conflictos de nombres**

### ✅ Redes Docker Separadas:
- Producción: `paqueteria_v1_prod_network`
- Staging: `paqueteria_staging_network`
- **Aislamiento completo**

### ✅ Volúmenes Separados:
- Producción: `redis_data`, `uploads_data`, etc.
- Staging: `redis_staging_data`, `uploads_staging_data`, etc.
- **Datos separados**

### ⚠️ Base de Datos Compartida:
- **Ambos usan la misma BD de RDS**
- **Esto es intencional** (solo cambios visuales)
- **NO ejecutar migraciones en staging**

---

## 🎯 FLUJO DE TRABAJO

```
┌─────────────────────────────────────────────────────────────┐
│                    DESARROLLO LOCAL                         │
│  1. Editar CSS, HTML, JS, templates                        │
│  2. git commit -m "Cambios estéticos"                      │
│  3. git push origin staging                                │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  DEPLOY A STAGING                           │
│  ./deploy.sh --env staging --deploy                        │
│  URL: http://staging.jemavi.co:8080                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  PROBAR Y VALIDAR                           │
│  - Ver cambios visuales                                    │
│  - Verificar responsive                                    │
│  - Probar funcionalidad                                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              SI TODO OK → PRODUCCIÓN                        │
│  git checkout main                                          │
│  git merge staging                                          │
│  git push origin main                                       │
│  ./deploy.sh --env papyrus --deploy                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 VERIFICACIÓN POST-DEPLOY

### Verificar que staging funciona:
```bash
# Estado de contenedores
./deploy.sh --env staging --status

# Health check
curl http://staging.jemavi.co:8080/health

# Ver logs
./deploy.sh --env staging --logs
```

### Verificar que producción sigue funcionando:
```bash
# Estado de producción
./deploy.sh --env papyrus --status

# Health check producción
curl https://paquetex.papyrus.com.co/health

# Ver logs producción
./deploy.sh --env papyrus --logs
```

---

## 🔧 COMANDOS ÚTILES

```bash
# Cambiar entre entornos
./deploy.sh  # Modo interactivo

# Deploy rápido
./deploy.sh --env staging --deploy
./deploy.sh --env papyrus --deploy

# Ver estado
./deploy.sh --env staging --status

# Ver logs
./deploy.sh --env staging --logs

# Restart
./deploy.sh --env staging --restart

# Pull última versión
./deploy.sh --env staging --pull

# Health check
./deploy.sh --env staging --health
```

---

## 📁 ESTRUCTURA DE ARCHIVOS

```
PAQUETERIA v1.0/
├── docker-compose.prod.yml          # Producción (existente)
├── docker-compose.staging.yml       # Staging (NUEVO) ✅
├── deploy.sh                        # Script principal
├── .deploy/
│   ├── config/
│   │   ├── papyrus.conf            # Config producción
│   │   └── staging.conf            # Config staging (ACTUALIZADO) ✅
│   ├── templates/
│   │   └── nginx-staging.conf      # Nginx staging (NUEVO) ✅
│   └── docs/
│       └── SETUP_STAGING.md        # Documentación (NUEVO) ✅
├── scripts/
│   └── setup-staging.sh            # Setup automático (NUEVO) ✅
├── SETUP_STAGING_COMANDOS.md       # Guía rápida (NUEVO) ✅
└── STAGING_CONFIGURADO.md          # Este archivo (NUEVO) ✅
```

---

## ⚠️ IMPORTANTE - LEER ANTES DE EMPEZAR

### ✅ LO QUE PUEDES HACER EN STAGING:
- Cambios en CSS
- Cambios en HTML/Templates
- Cambios en JavaScript
- Cambios en imágenes/assets
- Probar nuevas vistas
- Ajustes de diseño

### ❌ LO QUE NO DEBES HACER EN STAGING:
- Ejecutar migraciones de BD
- Hacer backups de BD
- Cambiar estructura de BD
- Modificar datos de producción
- Ejecutar scripts de BD

### 🔒 SEGURIDAD:
- Staging comparte BD con producción
- Solo cambios visuales/estéticos
- No afecta datos de producción
- Código separado completamente

---

## 🆘 SOPORTE

### Archivos de ayuda:
1. **SETUP_STAGING_COMANDOS.md** - Comandos paso a paso
2. **.deploy/docs/SETUP_STAGING.md** - Documentación completa
3. **scripts/setup-staging.sh** - Script automatizado

### Si algo falla:
1. Revisa los logs: `./deploy.sh --env staging --logs`
2. Verifica puertos: `ssh papyrus "ss -tlnp | grep -E '8001|6380|8080'"`
3. Verifica Nginx: `ssh papyrus "sudo nginx -t"`
4. Verifica contenedores: `ssh papyrus "docker ps | grep staging"`

---

## 📞 INFORMACIÓN ADICIONAL NECESARIA

### Antes de empezar, necesitas:
1. **URL de tu repositorio GitHub**
   - Ejemplo: `https://github.com/usuario/paqueteria.git`
   - La necesitas para clonar en el servidor

2. **Verificar DNS**
   - `staging.jemavi.co` debe apuntar a `18.214.124.14`
   - Verifica con: `nslookup staging.jemavi.co`

3. **Acceso SSH**
   - Debes poder hacer: `ssh papyrus`
   - Sin pedir contraseña

---

## ✅ CHECKLIST FINAL

Antes de empezar, verifica:
- [ ] Tienes acceso SSH al servidor (`ssh papyrus`)
- [ ] Conoces la URL de tu repositorio GitHub
- [ ] El DNS `staging.jemavi.co` apunta a `18.214.124.14`
- [ ] Producción está funcionando correctamente
- [ ] Tienes permisos sudo en el servidor

Durante el setup:
- [ ] Rama staging creada y pusheada
- [ ] Proyecto clonado en `/home/ubuntu/paqueteria-staging`
- [ ] Nginx configurado
- [ ] Puertos 8080 y 8443 abiertos en firewall
- [ ] Primer deploy exitoso

Después del setup:
- [ ] Staging accesible en `http://staging.jemavi.co:8080`
- [ ] Health check funciona
- [ ] Contenedores corriendo
- [ ] Producción sigue funcionando sin problemas

---

## 🎉 ¡TODO LISTO!

Ahora tienes:
- ✅ Staging completamente configurado
- ✅ Sin conflictos con producción
- ✅ Sistema de deploy unificado
- ✅ Documentación completa
- ✅ Scripts automatizados

**Siguiente paso:** Abre `SETUP_STAGING_COMANDOS.md` y sigue los pasos.

---

**Fecha de configuración:** 2024-11-28
**Versión:** PAQUETERÍA v1.0
**Entorno:** AWS Lightsail (18.214.124.14)
