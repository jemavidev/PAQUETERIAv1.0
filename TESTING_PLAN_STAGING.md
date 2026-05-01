# 📋 PLAN DE TESTING - PERFORMANCE IMPROVEMENTS EN STAGING

**Fecha Inicio:** 2026-05-01  
**Rama:** staging / PROD-STAGING  
**Commits Incluidos:** 5 performance improvements  
**Duración Recomendada:** 48 horas con carga real  

---

## 🎯 Objetivos del Testing

1. ✅ Verificar que NO hay regresiones en funcionalidad
2. ✅ Medir mejora real de performance en endpoints críticos
3. ✅ Detectar edge cases que podrían no estar en desarrollo
4. ✅ Validar comportamiento bajo carga concurrente
5. ✅ Confirmar que rollback es posible sin issues

---

## 📊 Test Cases por Formulario

### Formulario 1: RECEPCIÓN DE PAQUETES (CRÍTICO)

**Endpoint:** `POST /packages/receive-with-images`

#### Test 1.1: Recepción sin imágenes
```
Precondición: Anuncio válido en BD
Acción: Enviar POST sin archivos imagen
Esperado:
  ✅ Respuesta < 1s
  ✅ BAROTI asignado correctamente
  ✅ Paquete en estado RECIBIDO
  ✅ SMS/Email de confirmación enviado
```

#### Test 1.2: Recepción con 1 imagen OK
```
Precondición: Anuncio válido, imagen JPEG < 5MB
Acción: Enviar POST con 1 imagen
Esperado:
  ✅ Respuesta < 1.5s (era 1.2s antes)
  ✅ Imagen en S3 (verify con SDK)
  ✅ Registro FileUpload en BD
  ✅ BAROTI asignado
```

#### Test 1.3: Recepción con 3 imágenes OK (paralelo)
```
Precondición: Anuncio válido, 3 imágenes PNG/WEBP
Acción: Enviar POST con 3 imágenes
Esperado:
  ✅ Respuesta < 2s (era 2.5s antes) ← PARALELO
  ✅ Todas 3 en S3
  ✅ Todos 3 registros FileUpload
  ✅ Respuesta incluye 3 s3_url
  ✅ Timestamp progresivo (no bloqueado)
```

#### Test 1.4: Recepción con S3 temporal slow
```
Precondición: Simular S3 lento (10-20s)
Acción: Enviar POST con imagen
Esperado:
  ✅ Respuesta async (no bloqueante)
  ✅ Usuario ve respuesta OK < 2s
  ✅ Upload continúa en background
  ✅ BD se actualiza cuando completa
  ⚠️  Verificar: ¿se queda colgado o hay timeout?
```

#### Test 1.5: Recepción con S3 fallando intermitentemente
```
Precondición: S3 falla 1x de 3 intentos
Acción: Enviar POST con imagen
Esperado:
  ✅ Retry automático con backoff (no bloquea)
  ✅ Respuesta < 2-3s
  ✅ imagen se sube en 2do/3er intento
  ✅ No duplica intentos (cada uno es thread pool)
```

#### Test 1.6: BAROTI Generation Stress (99 ocupados)
```
Precondición: 99 BAROTIs en BD (posicion 00-98 ocupados)
Acción: Recibir paquete nuevo
Esperado:
  ✅ BAROTI: "99" (el único disponible)
  ✅ Tiempo < 10ms (antes era 50-100ms)
  ✅ NO se hace 200 queries
  ✅ NO se hace time.sleep(0.01)
```

#### Test 1.7: BAROTI Generation Full (100 ocupados)
```
Precondición: 100 BAROTIs ocupados
Acción: Intenta recibir paquete
Esperado:
  ✅ Error: "No hay códigos BAROTI disponibles"
  ✅ Respuesta < 100ms
  ✅ Mensaje útil en error
```

---

### Formulario 2: CREAR PAQUETE

**Endpoint:** `POST /packages/`

#### Test 2.1: Create simple
```
Esperado:
  ✅ Respuesta < 300ms
  ✅ NO regresión vs antes
```

---

### Formulario 3: VER IMÁGENES

**Endpoint:** `GET /api/images/{file_id}`

#### Test 3.1: Get image (S3 OK)
```
Esperado:
  ✅ Respuesta < 500ms
  ✅ Imagen se descarga completa
  ✅ Headers correctos (Content-Type, Cache-Control)
```

#### Test 3.2: Get image (S3 falla 1x)
```
Precondición: Simular S3 timeout en intento 1
Esperado:
  ✅ Retry automático (no bloquea event loop)
  ✅ Imagen se obtiene en intento 2-3
  ✅ Respuesta < 2-3s
  ✅ No duplica intentos innecesarios
```

---

## 📈 Métricas a Recopilar (Grafana/APM)

### Latencia de Endpoints (95th percentile)
```
Métrica | Antes | Esperado | Aceptable
------|-------|----------|----------
/receive-with-images (no img) | 800ms | <750ms | <1s
/receive-with-images (1 img) | 1.2s | <900ms | <1.5s
/receive-with-images (3 img) | 2.5s | <1.5s | <2s
/receive-with-images (S3 fail) | 4.2s | <1.5s | <2.5s
GET /api/images (S3 retry) | 3s | <2s | <3.5s
/packages/ (create) | 300ms | <250ms | <400ms
```

### Throughput (requests/second)
```
Sin cambios = baseline
Con cambios = debe mejorar 10-20% en recepción con imágenes
```

### Error Rate
```
Esperado: 0% de errores nuevos
Aceptable: <0.5% (misma tasa que antes)
```

### CPU / Memory
```
No debe aumentar respecto a antes
Esperado: misma o menor (menos bloqueante sleep)
```

---

## 🔄 Test Loop (24-48 horas)

### Fase 1: Smoke Test (30 min)
```
✅ Deploy completed sin errores
✅ App boots up (no syntax errors)
✅ DB migrations ok
✅ Can access /packages, /announce, /receive
✅ S3 connection works
```

### Fase 2: Manual Tests (2 horas)
```
Ejecutar Test Cases 1.1 - 3.2 manualmente:
✅ Crear anuncio
✅ Recibir sin imágenes
✅ Recibir con 1 imagen
✅ Recibir con 3 imágenes
✅ Ver imagen
✅ Verificar BAROTI asignado
✅ Verificar imágenes en S3
```

### Fase 3: Load Test (8 horas)
```
Simular:
- 10 usuarios simultáneos en recepción
- 100 requests/min por 8 horas
- Mix: 40% sin img, 30% con 1 img, 30% con 3 img

Monitorear:
✅ Respuesta times no degradan
✅ Memory no crece (no memory leak)
✅ Errores: 0 nuevos
✅ Event loop responsiveness (otros endpoints)
```

### Fase 4: Edge Cases (8 horas)
```
✅ S3 slow/timeouts (intentional)
✅ BAROTI generación con 99 ocupados
✅ Concurrent uploads (10x 3-image requests)
✅ Network interruptions (simulate)
✅ Rollback prueba (revert commit, re-test)
```

### Fase 5: Soak Test (24 horas)
```
Mantener carga baja pero continua:
- 2 usuarios activos
- 1-2 recepciones por minuto
- Monitorear memory, DB connections, file descriptors
```

---

## ✅ Criterios de Éxito

**MUST HAVE (Bloquea merge a LIVE-PROD):**
- ✅ 0 nuevos errores funcionales
- ✅ Latencias <= aceptable (vídez arriba)
- ✅ Error rate < 0.5%
- ✅ Memory leak: NO
- ✅ DB corruption: NO
- ✅ Imágenes en S3: consistentes

**NICE TO HAVE (No bloquea pero deseable):**
- ✅ Latencias < esperado
- ✅ Throughput mejora 10-20%
- ✅ CPU usage < baseline

---

## 🚀 Rollback Plan

Si algo falla:
```bash
# Opción 1: Revert el merge commit
git revert 32bdb2a
git push origin staging
bash deploy.sh --env staging --deploy  # Select option 2

# Opción 2: Revert commit específico
git revert 677fe7b  # BAROTI optimization
git push origin staging
# Luego re-test

# Opción 3: Reset a tag pre-refactor
git reset --hard pre-perf-refactor
git push origin staging --force
```

---

## 📞 Alertas/Monitoring Recomendados

```bash
# En Grafana, crear alertas si:
1. /receive-with-images latencia > 5s (95th)
2. Error rate > 1%
3. Memory utilization > 85%
4. Database connections > 80
5. S3 errors > 5 per minute
```

---

## 📝 Log Locations

```
Staging server logs:
- Docker container: docker logs <container_id> -f
- App logs: /var/log/paqueteria/app.log
- Nginx logs: /var/log/nginx/access.log, error.log
- S3 SDK logs: Enable debug logging in config
```

---

## 🎯 Decisión Final

**Después de 48 horas de testing:**

- ✅ **Si TODO OK:** Merge a LIVE-PROD + deploy a producción
- ⚠️ **Si issues:** Fix commits, re-merge staging, repeat testing  
- ❌ **Si critical bug:** Rollback, investigate root cause

---

**Contact:** Para issues durante testing, revisar logs y reportar por:
- GitHub issues en rama staging
- Deploy logs: `tail -f /tmp/staging-deploy.log`

