# 📚 Guía Completa de Deployment en Producción
## PaqueTex - Sistema de Paquetería v1.0

**Fecha:** 15-16 de Noviembre 2025  
**Versión:** 1.0  
**Servidor:** AWS Lightsail (papyrus)  
**Dominio:** paquetex.papyrus.com.co  

---

## 📋 Tabla de Contenidos

1. [Preparación del Servidor](#preparación-del-servidor)
2. [Instalación de Dependencias](#instalación-de-dependencias)
3. [Configuración del Proyecto](#configuración-del-proyecto)
4. [Variables de Entorno](#variables-de-entorno)
5. [Configuración de Nginx](#configuración-de-nginx)
6. [Configuración de S3](#configuración-de-s3)
7. [Configuración de SSL/HTTPS](#configuración-de-sslhttps)
8. [Migraciones de Base de Datos](#migraciones-de-base-de-datos)
9. [Despliegue de Servicios](#despliegue-de-servicios)
10. [Verificación y Troubleshooting](#verificación-y-troubleshooting)
11. [Mantenimiento](#mantenimiento)

---

## 🔧 Preparación del Servidor

### Especificaciones del Servidor

- **Proveedor:** AWS Lightsail
- **Nombre:** papyrus
- **IP Pública:** 18.214.124.14
- **RAM:** 914 MB
- **CPU:** 2 vCPUs
- **Disco:** 40 GB
- **SO:** Ubuntu 24.04

Para ver el contenido completo, consulta: [DOCS/documentacion/GUIA_DEPLOYMENT_PRODUCCION_COMPLETA.md]

---

## ✅ Checklist de Deployment Completado

- [x] Servidor configurado (SWAP, límites de archivos)
- [x] Docker y Docker Compose instalados
- [x] Repositorio clonado
- [x] Archivo `.env` creado y configurado
- [x] Variables críticas configuradas:
  - [x] DATABASE_URL (con URL encoding)
  - [x] AWS S3 (bucket: elclub-paqueteria)
  - [x] SMTP (servidor: taylor.mxrouting.net)
  - [x] LIWA.co (credenciales SMS)
  - [x] SECRET_KEY generada
- [x] Nginx configurado y funcionando
- [x] Bucket S3 verificado y accesible
- [x] Certificado SSL instalado
- [x] Migraciones de base de datos aplicadas
- [x] Servicios Docker levantados y saludables
- [x] Health check respondiendo correctamente
- [x] HTTPS funcionando
- [x] Redirección HTTP → HTTPS activa

---

## 📊 Resumen de URLs y Puertos

### URLs Públicas

- **Aplicación:** https://paquetex.papyrus.com.co
- **Health Check:** https://paquetex.papyrus.com.co/health
- **API Docs:** https://paquetex.papyrus.com.co/docs

### URLs Internas (Solo desde servidor)

- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3000
- **FastAPI (directo):** http://localhost:8000

---

## 🔐 Problemas Resueltos Durante el Deployment

### 1. DATABASE_URL con Caracteres Especiales

**Problema:** La contraseña contenía caracteres especiales (`?`, `!`, `*`, `#`, `[`, `]`, `=`, `|`, `)`, `$`)

**Solución:** Codificar la contraseña usando URL-encoding con Python:

```python
import urllib.parse
password = "a?HC!2.*1#?[==:|289qAI=)#V4kDzl$"
encoded = urllib.parse.quote_plus(password)
# Resultado: a%3FHC%212.%2A1%23%3F%5B%3D%3D%3A%7C289qAI%3D%29%23V4kDzl%24
```

### 2. Bucket S3 Incorrecto

**Problema:** Variable `.env` tenía bucket `paqueteria-uploads` que no existía

**Solución:** Actualizar a bucket existente `elclub-paqueteria`:

```bash
sed -i 's|^AWS_S3_BUCKET_NAME=.*|AWS_S3_BUCKET_NAME=elclub-paqueteria|' .env
```

### 3. Nginx No Conectaba a FastAPI

**Problema:** Uso de `docker-compose.lightsail.yml` personalizado causaba problemas

**Solución:** Usar `docker-compose.prod.yml` original del repositorio que ya está probado

---

## 📝 Configuraciones Finales

### Variables Críticas Configuradas

1. **DATABASE_URL:** `postgresql://jveyes:a%3FHC%212...@ls-abe25e9bea57818f0ee32555c0e7b4a10e361535...us-east-1.rds.amazonaws.com:5432/paqueteria_v4`

2. **AWS S3:**
   - Bucket: `elclub-paqueteria`
   - Región: `us-east-1`
   - Credenciales: Configuradas en `.env`

3. **SMTP:**
   - Host: `taylor.mxrouting.net`
   - Puerto: `587`
   - Usuario: `paquetex@papyrus.com.co`

4. **SSL/HTTPS:**
   - Certificado: Let's Encrypt
   - Auto-renovación: Configurada
   - Válido hasta: 2026-02-13

5. **Base de Datos:**
   - Total tablas: 14
   - Migración actual: 61567198240c (HEAD)
   - Todas las migraciones aplicadas

---

## 🎯 Próximos Pasos Recomendados

1. **Optimizar Base de Datos** - Ejecutar `optimize_database.sql` en RDS
2. **Configurar Backups** - Automatizar backups de la base de datos
3. **Monitoreo** - Configurar alertas en Grafana
4. **Documentación API** - Acceder a `/docs` para ver Swagger

---

**Documentación creada el:** 16 de Noviembre 2025  
**Última actualización:** 16 de Noviembre 2025  
**Versión del documento:** 1.0
